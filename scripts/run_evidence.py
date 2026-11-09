"""Reproduces the evidence in assets/evidence.txt. Run from the repo root: python scripts/run_evidence.py"""
import sys

sys.path.insert(0, "src")
from recommender import load_songs, recommend_songs  # noqa: E402

PROFILES = {
    "A. Pop / happy (starter, lowercase labels)": {
        "favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False,
        "target_valence": 0.8, "target_danceability": 0.8, "target_bpm": 120.0},
    "B. Pop / sad (exact catalog labels)": {
        "favorite_genre": "Pop", "favorite_mood": "Sad, emotional", "target_energy": 0.5},
    "C. Calm classical": {
        "favorite_genre": "Classical", "favorite_mood": "Melancholic, contemplative",
        "target_energy": 0.2, "likes_acoustic": True},
    "D. Loud metal": {
        "favorite_genre": "Heavy metal", "favorite_mood": "Aggressive, energetic", "target_energy": 0.95},
    "E. Energy only": {"target_energy": 0.9},
    "F. Contradiction (classical + sad but loud, not acoustic)": {
        "favorite_genre": "Classical", "favorite_mood": "Sad, emotional", "target_energy": 0.95,
        "likes_acoustic": False},
    "G. No preferences": {},
}

songs = load_songs("data/songs.csv")
print(f"Catalog: {len(songs)} songs. Settings: seed=0, jitter=0 (no random bonus), k=5\n")
for name, prefs in PROFILES.items():
    print(f"=== {name}")
    print(f"prefs: {prefs}")
    for i, (song, score, why) in enumerate(recommend_songs(prefs, songs, k=5, seed=0, jitter=0.0), 1):
        print(f"{i}. {song['title']} - {song['artist']} [{song['genre']}] score {score:.2f}")
        if i == 1:
            print(f"   because: {why}")
    print()

# ---- Guardrail experiments ----
from collections import Counter  # noqa: E402
from scoring import score_song  # noqa: E402

print("=== Guardrail 1: bad input is rejected, not silently scored")
for label, args in [("None prefs", (None, songs[0])), ("non-dict prefs", ("pop", songs[0])),
                    ("song missing 'energy'", ({}, {**songs[0], "energy": ""}))]:
    try:
        score_song(*args)
        print(f"{label}: accepted (unexpected)")
    except (ValueError, TypeError) as error:
        print(f"{label}: {type(error).__name__}: {error}")

print("\n=== Guardrail 2: scores stay inside 0..8 even for impossible targets")
extreme = {"favorite_genre": "x", "favorite_mood": "x", "target_energy": 50, "likes_acoustic": True,
           "target_valence": -9, "target_danceability": 99, "target_bpm": 5000.0}
scores = [score_song(extreme, s)[0] for s in songs]
print(f"min {min(scores):.2f}, max {max(scores):.2f}")

print("\n=== Guardrail 3: one artist cannot fill the list (k=10, max_per_artist=1)")
top = recommend_songs(PROFILES["A. Pop / happy (starter, lowercase labels)"], songs, k=10, seed=0, jitter=0.0)
counts = Counter(s["artist"] for s, _, _ in top)
print(f"{len(top)} songs, most songs by one artist: {max(counts.values())}")

print("\n=== Guardrail 4: same seed gives the same list; previous_ids forces a different list")
prefs = PROFILES["C. Calm classical"]
first = recommend_songs(prefs, songs, k=5, seed=7)
again = recommend_songs(prefs, songs, k=5, seed=7)
fresh = recommend_songs(prefs, songs, k=5, seed=7, previous_ids=[s["id"] for s, _, _ in first])
print("repeatable with seed:", [s["id"] for s, _, _ in first] == [s["id"] for s, _, _ in again])
print("differs from previous list:", [s["id"] for s, _, _ in first] != [s["id"] for s, _, _ in fresh])

print("\n=== Known weakness: exact-text matching")
for g in ("Classical", "classical", " Classical "):
    s, why = score_song({"favorite_genre": g}, next(x for x in songs if x["genre"] == "Classical"))
    print(f"favorite_genre={g!r} vs a Classical song -> {s:.2f}")

# ---- Vibe search (RAG) with a STUB client: no AWS call is made ----
from vibe_search import VibeIndex, build_vibe_playlist, validate_request  # noqa: E402

KEYWORDS = ["calm", "intense", "sad", "happy", "slow", "fast", "acoustic", "electric", "danceable", "bright"]


class StubClient:
    """Stands in for Bedrock: keyword-count embeddings and a canned chat reply."""
    embed_model_id = "stub-embed"

    def __init__(self, reply):
        self.reply = reply

    def embed(self, text):
        lowered = text.lower()
        return [lowered.count(word) + 0.001 for word in KEYWORDS]

    def complete(self, system, user):
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


print("\n=== Vibe search (STUB client, not real Bedrock): retrieve -> model preferences -> validate -> rank")
reply = '{"target_energy": 0.2, "target_valence": 0.3, "likes_acoustic": true, "favorite_genre": "Rock", "summary": "Quiet, sad, acoustic."}'
client = StubClient(reply)
index = VibeIndex(songs, client)
result = build_vibe_playlist("calm sad slow acoustic music for studying", index, client, k=5, seed=0)
print(f"summary: {result.summary}")
print(f"preferences kept: { {k: v for k, v in result.preferences.items() if v is not None} }")
print("(favorite_genre 'Rock' was not an exact genre in the retrieved songs, so the guardrail dropped it)")
for i, (s, score, _) in enumerate(result.recommendations, 1):
    print(f"{i}. {s['title']} - {s['artist']} score {score:.2f}")

print("\n=== Vibe guardrail: unusable model reply -> fallback to closest matches")
bad = StubClient("Sure! Here are some songs you might like.")
result = build_vibe_playlist("calm sad slow acoustic music", index, bad, k=3)
print(f"used_fallback={result.used_fallback}")
print(f"note: {result.note}")
for s, score, why in result.recommendations:
    print(f"- {s['title']} ({why})")

print("\n=== Vibe guardrail: bad requests are rejected before any model call")
for text in ("", "   ", "x" * 301):
    try:
        validate_request(text)
    except ValueError as error:
        print(f"{text[:10]!r}...: {error}")
