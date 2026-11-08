import pytest

from src.recommender import USER_PREF_KEYS, score_song

# Matches FULL_PREFS exactly: acousticness 0.8 is the target for likes_acoustic=True,
# and 80 bpm is the target tempo.
PERFECT_SONG = {
    "id": 1,
    "title": "Perfect Match",
    "artist": "Test Artist",
    "genre": "lofi",
    "mood": "chill",
    "energy": 0.4,
    "tempo_bpm": 80.0,
    "valence": 0.5,
    "danceability": 0.6,
    "acousticness": 0.8,
}

FULL_PREFS = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.4,
    "likes_acoustic": True,
    "target_valence": 0.5,
    "target_danceability": 0.6,
    "target_bpm": 80.0,
}

MAX_SCORE = 8.0


def make_song(**overrides):
    return {**PERFECT_SONG, **overrides}


def test_full_prefs_use_every_pref_key():
    assert set(FULL_PREFS) == set(USER_PREF_KEYS)


def test_perfect_match_scores_the_maximum():
    score, reasons = score_song(FULL_PREFS, PERFECT_SONG)

    assert score == pytest.approx(MAX_SCORE)
    assert len(reasons) == len(USER_PREF_KEYS)


def test_no_prefs_scores_zero_with_no_reasons():
    assert score_song({}, PERFECT_SONG) == (0.0, [])


def test_all_none_prefs_behave_like_no_prefs():
    prefs = {key: None for key in USER_PREF_KEYS}

    assert score_song(prefs, PERFECT_SONG) == (0.0, [])


@pytest.mark.parametrize(
    "prefs, expected_score",
    [
        ({"target_energy": 0.4}, 2.0),
        ({"favorite_genre": "lofi"}, 2.0),
        ({"favorite_mood": "chill"}, 1.0),
        ({"likes_acoustic": True}, 1.0),
        ({"target_valence": 0.5}, 1.0),
        ({"target_danceability": 0.6}, 0.5),
        ({"target_bpm": 80.0}, 0.5),
    ],
)
def test_single_pref_awards_its_own_weight(prefs, expected_score):
    score, reasons = score_song(prefs, PERFECT_SONG)

    assert score == pytest.approx(expected_score)
    assert len(reasons) == 1


def test_only_given_prefs_produce_reasons():
    prefs = {"favorite_genre": "lofi", "target_energy": 0.4}

    _, reasons = score_song(prefs, PERFECT_SONG)

    assert len(reasons) == 2
    assert any("genre" in reason for reason in reasons)
    assert any("energy" in reason for reason in reasons)


def test_genre_mismatch_adds_nothing_and_says_so():
    score, reasons = score_song({"favorite_genre": "rock"}, PERFECT_SONG)

    assert score == 0.0
    assert reasons == ["genre lofi is not rock (+0.00)"]


def test_mood_mismatch_adds_nothing_and_says_so():
    score, reasons = score_song({"favorite_mood": "intense"}, PERFECT_SONG)

    assert score == 0.0
    assert reasons == ["mood chill is not intense (+0.00)"]


def test_genre_match_outweighs_mood_match():
    genre_score, _ = score_song({"favorite_genre": "lofi"}, PERFECT_SONG)
    mood_score, _ = score_song({"favorite_mood": "chill"}, PERFECT_SONG)

    assert genre_score > mood_score


def test_energy_misses_above_and_below_the_target_score_the_same():
    prefs = {"target_energy": 0.5}
    above, _ = score_song(prefs, make_song(energy=0.7))
    below, _ = score_song(prefs, make_song(energy=0.3))

    assert above == pytest.approx(below)
    assert above < score_song(prefs, make_song(energy=0.5))[0]


def test_energy_score_drops_as_the_song_gets_further_from_the_target():
    prefs = {"target_energy": 0.2}
    scores = [score_song(prefs, make_song(energy=energy))[0] for energy in (0.2, 0.4, 0.6, 0.9)]

    assert scores == sorted(scores, reverse=True)
    assert len(set(scores)) == len(scores)


def test_likes_acoustic_true_prefers_the_acoustic_song():
    acoustic = make_song(acousticness=0.9)
    electronic = make_song(acousticness=0.1)

    assert score_song({"likes_acoustic": True}, acoustic)[0] > score_song({"likes_acoustic": True}, electronic)[0]


def test_likes_acoustic_false_prefers_the_electronic_song():
    acoustic = make_song(acousticness=0.9)
    electronic = make_song(acousticness=0.1)

    assert score_song({"likes_acoustic": False}, electronic)[0] > score_song({"likes_acoustic": False}, acoustic)[0]


def test_likes_acoustic_false_is_a_preference_not_neutral():
    # False maps to a target of 0.2, so it is not the same as leaving the pref out.
    score, reasons = score_song({"likes_acoustic": False}, make_song(acousticness=0.9))

    assert score < 1.0
    assert len(reasons) == 1


def test_tempo_is_normalized_so_it_cannot_swamp_other_terms():
    score, _ = score_song({"target_bpm": 60.0}, make_song(tempo_bpm=200.0))

    assert 0.0 <= score <= 0.5


def test_tempo_far_outside_the_range_is_clamped():
    prefs = {"target_bpm": 180.0}
    at_ceiling, _ = score_song(prefs, make_song(tempo_bpm=180.0))
    beyond_ceiling, _ = score_song(prefs, make_song(tempo_bpm=300.0))

    assert beyond_ceiling == pytest.approx(at_ceiling)


@pytest.mark.parametrize(
    "prefs",
    [
        FULL_PREFS,
        {**FULL_PREFS, "favorite_genre": "metal", "favorite_mood": "angry"},
        {**FULL_PREFS, "target_energy": 0.0, "target_valence": 1.0, "target_danceability": 1.0, "target_bpm": 400.0},
        {"favorite_genre": "pop", "target_energy": 0.9},
        {"likes_acoustic": False, "target_bpm": 60.0},
    ],
)
def test_score_stays_between_zero_and_the_maximum(prefs):
    score, _ = score_song(prefs, make_song(energy=1.0, valence=0.0, danceability=0.0, tempo_bpm=60.0))

    assert 0.0 <= score <= MAX_SCORE


def test_different_profiles_rank_the_same_two_songs_in_opposite_orders():
    calm = make_song(title="Calm", genre="lofi", mood="chill", energy=0.3, acousticness=0.9, tempo_bpm=70.0)
    loud = make_song(title="Loud", genre="rock", mood="intense", energy=0.95, acousticness=0.1, tempo_bpm=150.0)
    studier = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.3,
        "likes_acoustic": True,
        "target_bpm": 70.0,
    }
    gym_goer = {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": False,
        "target_bpm": 150.0,
    }

    assert score_song(studier, calm)[0] > score_song(studier, loud)[0]
    assert score_song(gym_goer, loud)[0] > score_song(gym_goer, calm)[0]


def test_unknown_pref_keys_are_ignored():
    with_extra = {**FULL_PREFS, "favorite_artist": "Nobody"}

    assert score_song(with_extra, PERFECT_SONG) == score_song(FULL_PREFS, PERFECT_SONG)


def test_does_not_modify_the_prefs_it_is_given():
    prefs = {"target_energy": 0.4}

    score_song(prefs, PERFECT_SONG)

    assert prefs == {"target_energy": 0.4}


def test_none_inputs_raise_value_error():
    with pytest.raises(ValueError):
        score_song(None, PERFECT_SONG)
    with pytest.raises(ValueError):
        score_song(FULL_PREFS, None)


def test_non_dict_inputs_raise_type_error():
    with pytest.raises(TypeError):
        score_song(["target_energy", 0.4], PERFECT_SONG)
    with pytest.raises(TypeError):
        score_song(FULL_PREFS, ("lofi", "chill"))


@pytest.mark.parametrize("field", ["title", "genre", "energy", "acousticness"])
def test_song_with_a_missing_field_raises_value_error(field):
    song = {key: value for key, value in PERFECT_SONG.items() if key != field}

    with pytest.raises(ValueError, match=field):
        score_song(FULL_PREFS, song)


@pytest.mark.parametrize("blank", [None, ""])
def test_song_with_a_blank_field_raises_value_error(blank):
    with pytest.raises(ValueError, match="mood"):
        score_song(FULL_PREFS, make_song(mood=blank))


# --- Edge-case profiles: unusual combinations that try to trick the scoring ---

SAD_BANGER = make_song(title="Sad Banger", mood="sad", energy=0.9)
SAD_LULLABY = make_song(title="Sad Lullaby", mood="sad", energy=0.2)
HAPPY_BANGER = make_song(title="Happy Banger", mood="happy", energy=0.9)


def test_edge_profile_high_energy_but_sad_prefers_the_song_that_satisfies_both():
    prefs = {"target_energy": 0.9, "favorite_mood": "sad"}

    banger = score_song(prefs, SAD_BANGER)[0]

    assert banger > score_song(prefs, SAD_LULLABY)[0]
    assert banger > score_song(prefs, HAPPY_BANGER)[0]


def test_edge_profile_high_energy_but_sad_lets_energy_outvote_mood():
    # Contradictory taste: the 2.0 energy weight beats the 1.0 mood weight,
    # so a happy banger outranks a sad lullaby. Documents the trade-off.
    prefs = {"target_energy": 0.9, "favorite_mood": "sad"}

    assert score_song(prefs, HAPPY_BANGER)[0] > score_song(prefs, SAD_LULLABY)[0]


def test_edge_profile_impossible_targets_cannot_push_the_score_negative():
    prefs = {"target_energy": 0, "target_valence": -3.0, "target_danceability": 0}

    score, _ = score_song(prefs, PERFECT_SONG)

    assert score >= 0.0


def test_edge_profile_zero_targets_still_count_as_preferences():
    # 0.0 and False are falsy, so a lazy `if target:` check would skip them.
    prefs = {"target_energy": 0.0, "target_valence": 0.0, "target_danceability": 0.0, "likes_acoustic": False}
    silent = make_song(energy=0.0, valence=0.0, danceability=0.0, acousticness=0.2)

    score, reasons = score_song(prefs, silent)

    assert score == pytest.approx(2.0 + 1.0 + 0.5 + 1.0)
    assert len(reasons) == 4


def test_edge_profile_loud_cased_genre_and_mood_still_match():
    prefs = {"favorite_genre": "LoFi", "favorite_mood": " Chill "}

    score, _ = score_song(prefs, PERFECT_SONG)

    assert score == pytest.approx(3.0)


def test_edge_profile_acoustic_metalhead_cannot_game_genre_with_acousticness():
    # Likes acoustic sound but only metal: genre (2.0) should beat acousticness (1.0).
    prefs = {"favorite_genre": "metal", "likes_acoustic": True, "target_energy": 1.0}
    loud_metal = make_song(genre="metal", energy=1.0, acousticness=0.1)
    mellow_lofi = make_song(genre="lofi", energy=0.3, acousticness=0.9)

    assert score_song(prefs, loud_metal)[0] > score_song(prefs, mellow_lofi)[0]
