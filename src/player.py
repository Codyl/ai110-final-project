"""Helpers for playing a song's YouTube video inside the app (YouTube's embedded player only)."""

import re
from urllib.parse import quote_plus

YOUTUBE_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{11}")

# YouTube's embed policy asks for a visible player of at least 200x200.
PLAYER_HEIGHT = 220


def is_valid_video_id(video_id) -> bool:
    return isinstance(video_id, str) and YOUTUBE_ID_PATTERN.fullmatch(video_id) is not None


def watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def search_url(title: str, artist: str) -> str:
    """Fallback link when a song has no video id or the embed is blocked."""
    return f"https://www.youtube.com/results?search_query={quote_plus(f'{title} {artist}')}"


def embed_html(video_id: str, height: int = PLAYER_HEIGHT) -> str:
    """HTML for an embedded player. Raises ValueError for anything that is not an 11-character video id."""
    if not is_valid_video_id(video_id):
        raise ValueError(f"invalid YouTube video id: {video_id!r}")
    return (
        f'<iframe width="100%" height="{height}" '
        f'src="https://www.youtube.com/embed/{video_id}?rel=0" '
        'title="YouTube video player" frameborder="0" '
        'allow="accelerometer; encrypted-media; picture-in-picture" '
        'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
    )
