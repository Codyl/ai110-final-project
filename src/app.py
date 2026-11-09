import os

import streamlit as st
import streamlit.components.v1 as components
from recommender import load_songs, recommend_songs
from song_api import SongApiError, add_song_to_csv, fetch_song, search_tracks
from player import embed_html, is_valid_video_id, search_url, watch_url, PLAYER_HEIGHT

st.set_page_config(page_title="Music Recommender", page_icon="🎵")
st.title("🎵 Music Recommender")


SONGS_CSV = "data/songs.csv"


@st.cache_data
def get_songs(csv_modified_time: float):
    # The modified time is part of the cache key, so editing the CSV reloads the songs.
    return load_songs(SONGS_CSV)


songs = get_songs(os.path.getmtime(SONGS_CSV))


def show_player(song):
    """Embedded YouTube player for a song, with plain links as a fallback."""
    video_id = song.get("youtube_id", "")
    if is_valid_video_id(video_id):
        components.html(embed_html(video_id), height=PLAYER_HEIGHT + 10)
        # st.markdown(f"[Open on YouTube]({watch_url(video_id)})")
    else:
        st.caption("No video saved for this song.")
        # st.markdown(f"[Search on YouTube]({search_url(song['title'], song['artist'])})")

# Build dropdown options from the data itself (your genres/moods are free-form)
genres = sorted({s["genre"] for s in songs})
moods = sorted({s["mood"] for s in songs})

with st.sidebar:
    # Enter the song title or artist name to filter the songs
    search_query = st.text_input("Search", value="", placeholder="Type a song title or artist name")
    st.header("Your preferences")
    favorite_genre = st.selectbox("Favorite genre", genres)
    favorite_mood = st.selectbox("Favorite mood", moods)
    target_energy = st.slider("Energy", 0.0, 1.0, 0.8, 0.05)
    target_valence = st.slider("Valence (positivity)", 0.0, 1.0, 0.8, 0.05)
    target_danceability = st.slider("Danceability", 0.0, 1.0, 0.8, 0.05)
    target_bpm = st.slider("Tempo (BPM)", 40, 200, 120)
    likes_acoustic = st.checkbox("Likes acoustic", value=False)
    k = st.slider("Number of results", 1, 10, 5)

user_prefs = {
    "favorite_genre": favorite_genre,
    "favorite_mood": favorite_mood,
    "target_energy": target_energy,
    "likes_acoustic": likes_acoustic,
    "target_valence": target_valence,
    "target_danceability": target_danceability,
    "target_bpm": float(target_bpm),
}
if search_query not in ["", None]:
    st.subheader("Search results")
    found_songs = False
    for song in songs:
        if search_query.lower() in song["title"].lower() or search_query.lower() in song["artist"].lower():
            with st.container(border=True):
                st.markdown(f"**{song['title']}** by {song['artist']}")
                st.caption(f"Genre: {song['genre']}, Mood: {song['mood']}, Energy: {song['energy']:.2f}, Valence: {song['valence']:.2f}, Danceability: {song['danceability']:.2f}, BPM: {song['tempo_bpm']:.1f}")
                show_player(song)
            found_songs = True
    if not found_songs:
        st.caption("No songs found.")
        if st.button("Add this song"):
            try:
                st.session_state["candidates"] = (search_query, search_tracks(search_query))
            except SongApiError as error:
                st.error(str(error))
        query_searched, candidates = st.session_state.get("candidates", (None, []))
        if query_searched == search_query:
            if not candidates:
                st.caption("No matching songs found online.")
            for index, candidate in enumerate(candidates):
                with st.container(border=True):
                    st.markdown(f"**{candidate['track_name']}** by {candidate['artist_name']}")
                    st.caption(f"Album: {candidate.get('album_name', '')}")
                    if st.button("Add", key=f"add_{index}"):
                        try:
                            new_song = fetch_song(candidate["track_name"], candidate["artist_name"])
                            if add_song_to_csv(new_song, SONGS_CSV):
                                st.session_state.pop("candidates", None)
                                st.success(f"Added {new_song['title']}. Search again to see it.")
                            else:
                                st.info("That song is already in your list.")
                        except SongApiError as error:
                            st.error(str(error))


if not search_query:
    st.subheader("Top recommendations")
    for song, score, explanation in recommend_songs(user_prefs, songs, k=k):
        with st.container(border=True):
            st.markdown(f"**{song['title']}** by {song['artist']}")
            st.caption(f"Genre: {song['genre']}")
            st.caption(f"Mood: {song['mood']}")
            st.caption(f"Energy: {song['energy']:.2f}")
            st.caption(f"Valence: {song['valence']:.2f}")
            st.caption(f"Danceability: {song['danceability']:.2f}")
            st.caption(f"BPM: {song['tempo_bpm']:.1f}")

            show_player(song)

            with st.expander("Why this recommendation?", expanded=False):
                st.caption(f"Score: {score:.2f} Because: {explanation}")
