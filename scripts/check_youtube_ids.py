"""Checks every youtube_id in data/songs.csv against YouTube's oEmbed endpoint.

Run from the repo root:  python scripts/check_youtube_ids.py

For each song it prints the video's real title and channel so you can confirm it is the right song.
HTTP 401 means the video is not embeddable; 404 means it does not exist or is private.
"""

import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


def check(video_id: str) -> str:
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(
        f"https://www.youtube.com/watch?v={video_id}", safe=""
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            info = json.load(response)
        return f"OK   {info.get('title')!r} by {info.get('author_name')!r}"
    except urllib.error.HTTPError as error:
        reason = {401: "not embeddable", 404: "not found or private"}.get(error.code, "error")
        return f"FAIL HTTP {error.code} ({reason})"
    except urllib.error.URLError as error:
        return f"FAIL {error.reason}"


def main() -> int:
    failures = 0
    with open("data/songs.csv", newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            result = check(row["youtube_id"])
            failures += result.startswith("FAIL")
            print(f"{row['id']:>2} {row['title']} / {row['artist']}: {row['youtube_id']} -> {result}")
    print(f"\n{failures} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
