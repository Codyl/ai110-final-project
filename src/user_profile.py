from dataclasses import dataclass

USER_PREF_KEYS = [
    "favorite_genre",
    "favorite_mood",
    "target_energy",
    "likes_acoustic",
    "target_valence",
    "target_danceability",
    "target_bpm",
]

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
