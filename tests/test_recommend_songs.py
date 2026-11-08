import pytest

from src.recommender import load_songs, recommend_songs, score_song

PREFS = {"favorite_genre": "pop", "target_energy": 0.5}


def make_song(song_id, **overrides):
    song = {
        "id": song_id,
        "title": f"Song {song_id}",
        "artist": f"Artist {song_id % 8}",
        "genre": "pop" if song_id % 2 else "lofi",
        "mood": "happy",
        "energy": round(0.1 + 0.07 * song_id, 2),
        "tempo_bpm": 100.0,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.5,
    }
    song.update(overrides)
    return song


# 12 songs, 8 artists (Artist 1 to 4 have two songs each), none flagged.
CATALOG = [make_song(song_id) for song_id in range(1, 13)]


def with_flags(songs, song_id, **flags):
    return [{**song, **flags} if song["id"] == song_id else song for song in songs]


def ids_of(results):
    return [song["id"] for song, _, _ in results]


def top_id(songs, **kwargs):
    return ids_of(recommend_songs(PREFS, songs, k=1, jitter=0, **kwargs))[0]


# --- shape of the result -----------------------------------------------------------------


def test_returns_song_score_explanation_tuples_best_first():
    results = recommend_songs(PREFS, CATALOG, k=5, jitter=0)

    assert len(results) == 5
    for song, score, explanation in results:
        assert isinstance(song, dict)
        assert isinstance(score, float)
        assert isinstance(explanation, str) and explanation
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)


def test_returned_score_is_the_real_score_not_the_randomized_one():
    for song, score, _ in recommend_songs(PREFS, CATALOG, k=5, seed=1, jitter=5.0):
        assert score == score_song(PREFS, song)[0]


def test_k_larger_than_the_catalog_returns_every_eligible_song():
    assert len(recommend_songs(PREFS, CATALOG, k=100)) == len(CATALOG)


def test_k_zero_returns_nothing():
    assert recommend_songs(PREFS, CATALOG, k=0) == []


@pytest.mark.parametrize(
    "kwargs",
    [{"k": -1}, {"jitter": -0.1}, {"max_per_artist": 0}],
)
def test_invalid_arguments_raise_value_error(kwargs):
    with pytest.raises(ValueError):
        recommend_songs(PREFS, CATALOG, **kwargs)


# --- is_liked and is_disliked ------------------------------------------------------------


def test_a_liked_song_is_never_recommended_even_when_it_is_the_best_match():
    best = top_id(CATALOG)
    songs = with_flags(CATALOG, best, is_liked=True)

    for seed in range(50):
        assert best not in ids_of(recommend_songs(PREFS, songs, k=11, seed=seed))


def test_a_disliked_song_is_never_recommended_even_when_it_is_the_best_match():
    best = top_id(CATALOG)
    songs = with_flags(CATALOG, best, is_disliked=True)

    for seed in range(50):
        assert best not in ids_of(recommend_songs(PREFS, songs, k=11, seed=seed))


def test_a_song_that_is_both_liked_and_disliked_is_never_recommended():
    best = top_id(CATALOG)
    songs = with_flags(CATALOG, best, is_liked=True, is_disliked=True)

    assert best not in ids_of(recommend_songs(PREFS, songs, k=100))


def test_flagged_songs_are_excluded_even_when_backfilling_to_reach_k():
    songs = with_flags(with_flags(CATALOG, 1, is_liked=True), 2, is_disliked=True)

    results = ids_of(recommend_songs(PREFS, songs, k=100, max_per_artist=1))

    assert 1 not in results and 2 not in results
    assert len(results) == len(CATALOG) - 2


def test_flagged_songs_shrink_the_list_instead_of_being_used_as_filler():
    songs = [make_song(1), make_song(2, is_liked=True), make_song(3, is_disliked=True)]

    assert ids_of(recommend_songs(PREFS, songs, k=3)) == [1]


def test_every_song_flagged_returns_nothing():
    songs = [make_song(1, is_liked=True), make_song(2, is_disliked=True)]

    assert recommend_songs(PREFS, songs, k=5) == []


def test_unflagged_songs_stay_eligible_when_flag_keys_are_false_or_missing():
    songs = [make_song(1, is_liked=False, is_disliked=False), make_song(2)]

    assert sorted(ids_of(recommend_songs(PREFS, songs, k=2))) == [1, 2]


def test_flag_rules_hold_with_extreme_randomness_and_no_artist_limit():
    songs = with_flags(with_flags(CATALOG, 5, is_liked=True), 6, is_disliked=True)

    for seed in range(50):
        results = ids_of(recommend_songs(PREFS, songs, k=12, seed=seed, jitter=100.0, max_per_artist=12))
        assert 5 not in results and 6 not in results


def test_flags_in_a_csv_are_loaded_and_respected(tmp_path):
    csv_path = tmp_path / "songs.csv"
    csv_path.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness,is_liked,is_disliked\n"
        "1,Liked One,A,pop,happy,0.5,100,0.5,0.5,0.5,true,\n"
        "2,Disliked One,B,pop,happy,0.5,100,0.5,0.5,0.5,,yes\n"
        "3,Fine One,C,pop,happy,0.5,100,0.5,0.5,0.5,false,no\n"
        "4,Blank Flags,D,pop,happy,0.5,100,0.5,0.5,0.5,,\n"
    )

    songs = load_songs(str(csv_path))

    assert [(s["is_liked"], s["is_disliked"]) for s in songs] == [
        (True, False),
        (False, True),
        (False, False),
        (False, False),
    ]
    assert sorted(ids_of(recommend_songs(PREFS, songs, k=10))) == [3, 4]


def test_flag_columns_are_optional_in_the_csv(tmp_path):
    csv_path = tmp_path / "songs.csv"
    csv_path.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
        "1,Plain,A,pop,happy,0.5,100,0.5,0.5,0.5\n"
    )

    song = load_songs(str(csv_path))[0]

    assert song["is_liked"] is False and song["is_disliked"] is False


def test_an_unreadable_flag_value_in_the_csv_raises_with_the_line_number(tmp_path):
    csv_path = tmp_path / "songs.csv"
    csv_path.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness,is_liked\n"
        "1,Plain,A,pop,happy,0.5,100,0.5,0.5,0.5,maybe\n"
    )

    with pytest.raises(ValueError, match="line 2: is_liked"):
        load_songs(str(csv_path))


# --- randomness and seeds ----------------------------------------------------------------


def test_the_same_seed_gives_the_same_list():
    first = recommend_songs(PREFS, CATALOG, k=5, seed=42)
    second = recommend_songs(PREFS, CATALOG, k=5, seed=42)

    assert ids_of(first) == ids_of(second)


def test_different_seeds_do_not_all_give_the_same_list():
    lists = {tuple(ids_of(recommend_songs(PREFS, CATALOG, k=5, seed=seed))) for seed in range(30)}

    assert len(lists) > 1


def test_with_no_jitter_the_result_is_fixed_and_ordered_by_score():
    first = recommend_songs(PREFS, CATALOG, k=5, jitter=0)
    second = recommend_songs(PREFS, CATALOG, k=5, jitter=0)

    assert ids_of(first) == ids_of(second)


def test_a_clearly_better_song_stays_on_top_despite_the_randomness():
    songs = CATALOG + [make_song(99, artist="Solo", genre="pop", energy=0.5)]

    for seed in range(50):
        assert ids_of(recommend_songs(PREFS, songs, k=1, seed=seed, jitter=0.1)) == [99]


# --- the same list never appears twice in a row ------------------------------------------


def test_the_list_never_repeats_exactly_across_100_unseeded_calls():
    previous = None
    for _ in range(100):
        current = ids_of(recommend_songs(PREFS, CATALOG, k=5, previous_ids=previous))
        if previous is not None:
            assert current != previous
        previous = current


def test_the_list_never_repeats_exactly_when_the_seed_is_fixed():
    previous = None
    for _ in range(50):
        current = ids_of(recommend_songs(PREFS, CATALOG, k=5, seed=7, previous_ids=previous))
        if previous is not None:
            assert current != previous
        previous = current


def test_the_list_changes_even_when_there_is_no_randomness_to_re_roll():
    first = ids_of(recommend_songs(PREFS, CATALOG, k=5, jitter=0))
    second = ids_of(recommend_songs(PREFS, CATALOG, k=5, jitter=0, previous_ids=first))

    assert second != first
    assert second[:-1] == first[:-1]
    assert len(second) == 5


def test_a_changed_list_still_respects_the_flags_and_artist_limit():
    songs = with_flags(CATALOG, 3, is_disliked=True)
    first = ids_of(recommend_songs(PREFS, songs, k=5, jitter=0))

    results = recommend_songs(PREFS, songs, k=5, jitter=0, previous_ids=first)

    assert 3 not in ids_of(results)
    artists = [song["artist"] for song, _, _ in results]
    assert len(set(artists)) == len(artists)


def test_previous_ids_that_do_not_match_leave_the_list_alone():
    expected = ids_of(recommend_songs(PREFS, CATALOG, k=5, jitter=0))

    assert ids_of(recommend_songs(PREFS, CATALOG, k=5, jitter=0, previous_ids=[999])) == expected


def test_a_catalog_with_no_spare_song_cannot_change_and_does_not_crash():
    songs = [make_song(1), make_song(2)]
    first = ids_of(recommend_songs(PREFS, songs, k=2, jitter=0))

    assert sorted(ids_of(recommend_songs(PREFS, songs, k=2, jitter=0, previous_ids=first))) == [1, 2]


# --- diversity ---------------------------------------------------------------------------


def test_each_artist_appears_at_most_once_by_default():
    for seed in range(30):
        artists = [song["artist"] for song, _, _ in recommend_songs(PREFS, CATALOG, k=6, seed=seed)]
        assert len(set(artists)) == len(artists)


def test_max_per_artist_allows_repeat_artists_when_raised():
    songs = [make_song(i, artist="Same Artist") for i in range(1, 6)]

    assert len(recommend_songs(PREFS, songs, k=5, max_per_artist=1)) == 5
    top_two = recommend_songs(PREFS, songs, k=2, max_per_artist=2, jitter=0)
    assert [song["artist"] for song, _, _ in top_two] == ["Same Artist", "Same Artist"]


def test_the_artist_limit_backfills_instead_of_returning_a_short_list():
    songs = [make_song(i, artist="Same Artist") for i in range(1, 6)]

    assert len(recommend_songs(PREFS, songs, k=5, max_per_artist=1)) == 5


def test_a_better_song_from_a_repeat_artist_is_passed_over_for_a_different_artist():
    songs = [
        make_song(1, artist="Star", genre="pop", energy=0.5),
        make_song(2, artist="Star", genre="pop", energy=0.5),
        make_song(3, artist="Other", genre="lofi", energy=0.1),
    ]

    results = ids_of(recommend_songs(PREFS, songs, k=2, jitter=0))

    assert results == [1, 3]
