import streamlit as st
import requests
import os

INGEST_URL = os.getenv("INGEST_URL", "http://ingestion:8000")
SEARCH_URL = os.getenv("SEARCH_URL", "http://search:8001")

st.title("Music Search Engine Admin")

# Insertion Form
with st.form("Insert Song"):
    singer = st.text_input("Singer")
    song_name = st.text_input("Song Name")
    genre = st.text_input("Genre")
    lyrics = st.text_area("Lyrics")
    submit = st.form_submit_button("Insert")
    if submit:
        try:
            response = requests.post(f"{INGEST_URL}/insert", json={"singer": singer, "song_name": song_name, "genre": genre, "lyrics": lyrics})
            response.raise_for_status()  # Raise an exception for bad status codes
            st.success(f"Inserted: {response.json()}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error adding song: {str(e)}")

# Search
query = st.text_input("Search Query")
if query:
    try:
        response = requests.get(f"{SEARCH_URL}/search", params={"query": query})
        response.raise_for_status()
        results = response.json()
        for result in results:
            st.write(f"{result['singer']} - {result['song_name']} ({result['genre']})")
            st.write(result['lyrics'][:100] + "...")
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching: {str(e)}")
