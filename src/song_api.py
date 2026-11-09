"""Client for the Freqblog Music Metadata API (https://api.freqblog.com/docs).

The API key is read from the API_KEY variable in .env and is only ever sent from this server-side code.
"""
import csv
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

API_URL = "https://api.freqblog.com"
TIMEOUT_SECONDS = 60

load_dotenv()


class SongApiError(Exception):
    """Raised when the API cannot be reached or does not return usable data."""


def _get(path: str, params: Dict) -> Dict:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise SongApiError("API_KEY is not set. Add it to the .env file.")
    try:
        response = requests.get(
            f"{API_URL}{path}", params=params, headers={"x-api-key": api_key}, timeout=TIMEOUT_SECONDS
        )
    except requests.RequestException as error:
        raise SongApiError(f"Could not reach the song API: {error}") from None
    if response.status_code == 404:
        raise SongApiError("The song API has no data for that track.")
    if not response.ok:
        raise SongApiError(f"The song API returned an error ({response.status_code}).")
    return response.json()


def search_tracks(query: str, limit: int = 5) -> List[Dict]:
    """Searches the catalog by track title or artist name. Returns dicts with track_name and artist_name."""
    return _get("/search", {"q": query, "limit": limit}).get("results", [])


def fetch_song(title: str, artist: str) -> Dict:
    """Looks up audio features for one track and maps them to a songs.csv row (without an id)."""
    data = _get("/lookup", {"title": title, "artist": artist})
    numbers = {
        "energy": data.get("energy"),
        "tempo_bpm": data.get("bpm"),
        "valence": data.get("valence"),
        "danceability": data.get("danceability"),
        "acousticness": data.get("acousticness"),
    }
    missing = [name for name, value in numbers.items() if value is None]
    if missing:
        raise SongApiError(f"The song API has no {', '.join(missing)} for this track.")
    return {
        "title": data.get("track_name") or title,
        "artist": data.get("artist_name") or artist,
        "genre": (data.get("genre") or "unknown").title(),
        "mood": (data.get("mood") or "unknown").capitalize(),
        **{name: round(float(value), 2) for name, value in numbers.items()},
        "youtube_id": "",
    }


def add_song_to_csv(song: Dict, csv_path: str) -> bool:
    """Appends the song to the CSV with the next free id. Returns False if title and artist already exist."""
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    for row in rows:
        if row["title"].lower() == song["title"].lower() and row["artist"].lower() == song["artist"].lower():
            return False
    next_id = max((int(row["id"]) for row in rows), default=0) + 1
    with open(csv_path, "rb") as csv_file:
        content = csv_file.read()
    with open(csv_path, "a", newline="", encoding="utf-8") as csv_file:
        if content and not content.endswith(b"\n"):
            csv_file.write("\r\n")
        csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="ignore").writerow({"id": next_id, **song})
    return True
