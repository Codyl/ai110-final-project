import random
from typing import List, Dict, Tuple, Optional

try:
    from .scoring import score_song
except ImportError:  # run as a script (python src/main.py), where src/ is the top level
    from scoring import score_song

# How many times recommend_songs() re-rolls its randomness to avoid repeating the previous list.
MAX_REROLLS = 20

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    seed: Optional[int] = None,
    jitter: float = 0.3,
    max_per_artist: int = 1,
    previous_ids: Optional[List[int]] = None,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns up to k (song_dict, score, explanation) tuples, best first.
      - Liked and disliked songs are never recommended.
      - Randomness: each song gets a random bonus between 0 and `jitter` points, used only
        for ordering, so near-ties can swap between calls. The returned score is the real one.
        Pass a `seed` to make a run repeatable; leave it None for a different mix each time.
      - Diversity: at most `max_per_artist` songs per artist. If that leaves fewer than k songs,
        the best remaining songs fill the gap rather than returning a short list.
      - No exact repeats: pass the song ids of the list you showed last as `previous_ids` and the
        new list will differ from it. It re-rolls the randomness, then swaps the last pick for
        the next best song. Only a catalog with no spare eligible song can return the same list.
    """
    if k < 0 or jitter < 0 or max_per_artist < 1:
        raise ValueError("k and jitter must not be negative, and max_per_artist must be at least 1")

    rng = random.Random(seed)
    scored = []
    for song in songs:
        if song.get("is_liked") or song.get("is_disliked"):
            continue
        score, reasons = score_song(user_prefs, song)
        scored.append((score, song, "; ".join(reasons)))

    def pick() -> Tuple[List[tuple], List[tuple]]:
        """Ranks the scored songs with fresh jitter and returns (picked, leftover) lists."""
        ranked = sorted(
            ((score + rng.uniform(0, jitter), score, song, explanation) for score, song, explanation in scored),
            key=lambda item: (-item[0], item[2]["title"]),
        )
        picked, rest, artist_counts = [], [], {}
        for item in ranked:
            artist = item[2]["artist"]
            if len(picked) < k and artist_counts.get(artist, 0) < max_per_artist:
                picked.append(item)
                artist_counts[artist] = artist_counts.get(artist, 0) + 1
            else:
                rest.append(item)
        missing = k - len(picked)
        picked.extend(rest[:missing])
        return picked, rest[missing:]

    def ids(items: List[tuple]) -> List[int]:
        """Returns the song ids of ranked items, in order."""
        return [item[2]["id"] for item in items]

    picked, rest = pick()
    if previous_ids is not None:
        previous = list(previous_ids)
        for _ in range(MAX_REROLLS):
            if ids(picked) != previous:
                break
            picked, rest = pick()
        if ids(picked) == previous and picked and rest:
            kept = picked[:-1]
            counts = {}
            for item in kept:
                counts[item[2]["artist"]] = counts.get(item[2]["artist"], 0) + 1
            replacement = next((item for item in rest if counts.get(item[2]["artist"], 0) < max_per_artist), rest[0])
            picked = sorted(kept + [replacement], key=lambda item: -item[0])

    return [(song, score, explanation) for _, score, song, explanation in picked]
