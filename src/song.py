from dataclasses import MISSING, dataclass, fields

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Optional flags: a liked or disliked song is never recommended.
    is_liked: bool = False
    is_disliked: bool = False

# Required column name -> converter, taken from Song so it always matches the songs.csv headers.
SONG_FIELDS = {f.name: f.type for f in fields(Song) if f.default is MISSING}

# Columns that may be absent from songs.csv or left blank; they default to False.
OPTIONAL_SONG_FIELDS = [f.name for f in fields(Song) if f.default is not MISSING]

