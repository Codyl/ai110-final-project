from typing import List, Optional
from dataclasses import asdict

try:
    from .song import Song, SONG_FIELDS, OPTIONAL_SONG_FIELDS
    from .user_profile import UserProfile, USER_PREF_KEYS
    from .song_loader import parse_bool, load_songs
    from .scoring import score_song
    from .ranking import MAX_REROLLS, recommend_songs
except ImportError:  # run as a script (python src/main.py), where src/ is the top level
    from song import Song, SONG_FIELDS, OPTIONAL_SONG_FIELDS
    from user_profile import UserProfile, USER_PREF_KEYS
    from song_loader import parse_bool, load_songs
    from scoring import score_song
    from ranking import MAX_REROLLS, recommend_songs

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, seed: Optional[int] = None) -> List[Song]:
        """Returns the top k songs for a user profile, best first."""
        # Shares recommend_songs() so the class and function versions never disagree.
        results = recommend_songs(asdict(user), [asdict(song) for song in self.songs], k=k, seed=seed)
        songs_by_id = {song.id: song for song in self.songs}
        return [songs_by_id[song["id"]] for song, _, _ in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a semicolon-separated explanation of how a song scored for a user."""
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons)
