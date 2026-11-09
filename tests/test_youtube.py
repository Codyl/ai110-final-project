import pytest

from src.player import embed_html, is_valid_video_id, search_url, watch_url
from src.song_loader import load_songs

HEADER = "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness,youtube_id\n"


def write_csv(tmp_path, rows):
    path = tmp_path / "songs.csv"
    path.write_text(HEADER + rows, encoding="utf-8")
    return str(path)


def test_bundled_csv_has_a_valid_video_for_every_song():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 30
    assert all(is_valid_video_id(s["youtube_id"]) for s in songs)
    assert len({s["youtube_id"] for s in songs}) == len(songs)


def test_loader_reads_youtube_id(tmp_path):
    path = write_csv(tmp_path, "1,A,B,pop,happy,0.5,100,0.5,0.5,0.5,dQw4w9WgXcQ\n")
    assert load_songs(path)[0]["youtube_id"] == "dQw4w9WgXcQ"


def test_blank_youtube_id_is_allowed(tmp_path):
    path = write_csv(tmp_path, "1,A,B,pop,happy,0.5,100,0.5,0.5,0.5,\n")
    assert load_songs(path)[0]["youtube_id"] == ""


def test_missing_youtube_column_defaults_to_blank(tmp_path):
    path = tmp_path / "songs.csv"
    path.write_text(HEADER.replace(",youtube_id", "") + "1,A,B,pop,happy,0.5,100,0.5,0.5,0.5\n", encoding="utf-8")
    assert load_songs(str(path))[0]["youtube_id"] == ""


def test_invalid_youtube_id_is_rejected(tmp_path):
    path = write_csv(tmp_path, "1,A,B,pop,happy,0.5,100,0.5,0.5,0.5,not a video\n")
    with pytest.raises(ValueError, match="line 2: youtube_id"):
        load_songs(path)


@pytest.mark.parametrize("bad", ["", "short", "has spaces!!", "x" * 12, None, 123])
def test_embed_html_rejects_bad_ids(bad):
    with pytest.raises(ValueError):
        embed_html(bad)


def test_embed_html_and_links():
    assert "youtube.com/embed/dQw4w9WgXcQ" in embed_html("dQw4w9WgXcQ")
    assert watch_url("dQw4w9WgXcQ") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert search_url("Fix You", "Coldplay") == "https://www.youtube.com/results?search_query=Fix+You+Coldplay"
