from typing import List, Dict, Tuple

try:
    from .song import SONG_FIELDS
    from .user_profile import USER_PREF_KEYS
except ImportError:  # run as a script (python src/main.py), where src/ is the top level
    from song import SONG_FIELDS
    from user_profile import USER_PREF_KEYS

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    if user_prefs is None or song is None:
        raise ValueError("user_prefs and song must not be None")

    if not isinstance(user_prefs, dict) or not isinstance(song, dict):
        raise TypeError("user_prefs and song must be dictionaries")

    missing_fields = [name for name in SONG_FIELDS if song.get(name) in (None, "")]
    if missing_fields:
        raise ValueError(f"song is missing values for: {', '.join(missing_fields)}")

    # Preferences are all optional: any key the user did not give is present with value None.
    user_prefs = {**{key: None for key in USER_PREF_KEYS}, **user_prefs}

    def closeness(value, target):
        """Returns 1.0 for an exact match, falling toward 0.0 as the gap grows."""
        return max(0.0, 1 - abs(value - target))

    def normalize_bpm(bpm):
        """Maps a tempo onto 0.0-1.0, clamping 60 bpm and below to 0 and 180 bpm and above to 1."""
        return max(0.0, min(1.0, (bpm - 60) / 120))

    score = 0.0
    reasons = []

    # Each check below only runs if the user gave that preference (None means "no preference").

    # Energy (max +2.0)
    target_energy = user_prefs["target_energy"]
    if target_energy is not None:
        points = 2.0 * closeness(song["energy"], target_energy)
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{points:.2f} of 2.00)")

    # Genre (max +2.0)
    favorite_genre = user_prefs["favorite_genre"]
    if favorite_genre is not None:
        if song["genre"] == favorite_genre:
            score += 2.0
            reasons.append(f"genre matches {favorite_genre} (+2.00)")
        else:
            reasons.append(f"genre {song['genre']} is not {favorite_genre} (+0.00)")

    # Mood (max +1.0)
    favorite_mood = user_prefs["favorite_mood"]
    if favorite_mood is not None:
        if song["mood"] == favorite_mood:
            score += 1.0
            reasons.append(f"mood matches {favorite_mood} (+1.00)")
        else:
            reasons.append(f"mood {song['mood']} is not {favorite_mood} (+0.00)")

    # Acousticness (max +1.0): likes_acoustic maps to a target of 0.8, otherwise 0.2
    likes_acoustic = user_prefs["likes_acoustic"]
    if likes_acoustic is not None:
        target_acousticness = 0.8 if likes_acoustic else 0.2
        points = 1.0 * closeness(song["acousticness"], target_acousticness)
        score += points
        reasons.append(
            f"acousticness {song['acousticness']:.2f} vs target {target_acousticness:.2f} (+{points:.2f} of 1.00)"
        )

    # Valence (max +1.0)
    target_valence = user_prefs["target_valence"]
    if target_valence is not None:
        points = 1.0 * closeness(song["valence"], target_valence)
        score += points
        reasons.append(f"valence {song['valence']:.2f} vs target {target_valence:.2f} (+{points:.2f} of 1.00)")

    # Danceability (max +0.5)
    target_danceability = user_prefs["target_danceability"]
    if target_danceability is not None:
        points = 0.5 * closeness(song["danceability"], target_danceability)
        score += points
        reasons.append(
            f"danceability {song['danceability']:.2f} vs target {target_danceability:.2f} (+{points:.2f} of 0.50)"
        )

    # Tempo (max +0.5): both sides normalized so BPM does not swamp the other terms
    target_bpm = user_prefs["target_bpm"]
    if target_bpm is not None:
        points = 0.5 * closeness(normalize_bpm(song["tempo_bpm"]), normalize_bpm(target_bpm))
        score += points
        reasons.append(f"tempo {song['tempo_bpm']:.0f} bpm vs target {target_bpm:.0f} bpm (+{points:.2f} of 0.50)")

    return score, reasons
