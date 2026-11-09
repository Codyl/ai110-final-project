import csv
import re
from typing import List, Dict

try:
    from .song import SONG_FIELDS, OPTIONAL_SONG_FIELDS, OPTIONAL_TEXT_FIELDS
except ImportError:  # run as a script (python src/main.py), where src/ is the top level
    from song import SONG_FIELDS, OPTIONAL_SONG_FIELDS, OPTIONAL_TEXT_FIELDS

YOUTUBE_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{11}")

def parse_bool(text: str) -> bool:
    """Reads a yes/no cell from the CSV. Blank means False."""
    value = text.strip().lower()
    if value in ("", "false", "0", "no"):
        return False
    if value in ("true", "1", "yes"):
        return True
    raise ValueError(f"expected true/false, got {text!r}")

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames or []
        missing_headers = [name for name in SONG_FIELDS if name not in headers]
        if missing_headers:
            raise ValueError(f"{csv_path} is missing columns: {', '.join(missing_headers)}")

        songs = []
        for line_number, row in enumerate(reader, start=2):
            blanks = [name for name in SONG_FIELDS if row.get(name) is None or not row[name].strip()]
            if blanks:
                raise ValueError(f"{csv_path} line {line_number}: empty value for {', '.join(blanks)}")
            song = {name: kind(row[name].strip()) for name, kind in SONG_FIELDS.items()}
            for name in OPTIONAL_SONG_FIELDS:
                try:
                    song[name] = parse_bool(row.get(name) or "")
                except ValueError as error:
                    raise ValueError(f"{csv_path} line {line_number}: {name}: {error}") from None
            for name in OPTIONAL_TEXT_FIELDS:
                song[name] = (row.get(name) or "").strip()
            if song.get("youtube_id") and not YOUTUBE_ID_PATTERN.fullmatch(song["youtube_id"]):
                raise ValueError(f"{csv_path} line {line_number}: youtube_id: invalid video id {song['youtube_id']!r}")
            songs.append(song)
    return songs
