mport streamlit as st
import requests
from PIL import Image
from io import BytesIO

# ---- READ API KEY FROM STREAMLIT SECRETS ----
API_KEY = st.secrets["API_KEY"]  # Set this in Streamlit Cloud secrets

# ---- TMDb CONFIG ----
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# ---- PAGE SETTINGS ----
st.set_page_config(page_title="🎬 Film Mood Board", page_icon="🎥", layout="wide")
st.title("🎬 Film Mood Board")
st.write("Search for any movie to see its poster, stills, trailer, and recommendations.")

# ---- FAVORITES STORAGE ----
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---- INPUT ----
movie_query = st.text_input("Enter movie title")

if movie_query:
    # Search movie
    search_url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": movie_query}
    search_res = requests.get(search_url, params=params).json()

    if search_res["results"]:
        movie = search_res["results"][0]
        movie_id = movie["id"]

        st.header(movie["title"])
        st.write(f"**Release Date:** {movie.get('release_date', 'N/A')}")
        st.write(f"**Rating:** {movie.get('vote_average', 'N/A')}/10")
        st.write(movie.get("overview", ""))

        # Poster
        if movie.get("poster_path"):
            poster_url = IMAGE_BASE + movie["poster_path"]
            st.image(poster_url, width=300)

        # Favorite Button
        if st.button("❤️ Add to Favorites"):
            if movie["title"] not in st.session_state.favorites:
                st.session_state.favorites.append(movie["title"])
                st.success(f"Added {movie['title']} to favorites!")
            else:
                st.warning("Already in favorites!")

        # Fetch images
        images_url = f"{BASE_URL}/movie/{movie_id}/images"
        images_res = requests.get(images_url, params={"api_key": API_KEY}).json()

        backdrops = images_res.get("backdrops", [])
        if backdrops:
            st.subheader("📸 Movie Stills")
            cols = st.columns(3)
            for idx, img in enumerate(backdrops[:9]):
                img_url = IMAGE_BASE + img["file_path"]
                img_data = requests.get(img_url).content
                cols[idx % 3].image(Image.open(BytesIO(img_data)), use_container_width=True)

        # Fetch trailer
        video_url = f"{BASE_URL}/movie/{movie_id}/videos"
        video_res = requests.get(video_url, params={"api_key": API_KEY}).json()
        videos = video_res.get("results", [])
        trailer = next((v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"), None)

        if trailer:
            st.subheader("🎥 Watch Trailer")
            youtube_url = f"https://www.youtube.com/watch?v={trailer['key']}"
            st.video(youtube_url)

        # Similar movies
        similar_url = f"{BASE_URL}/movie/{movie_id}/similar"
        similar_res = requests.get(similar_url, params={"api_key": API_KEY}).json()
        similar_movies = similar_res.get("results", [])

        if similar_movies:
            st.subheader("🎯 Similar Movies You Might Like")
            sim_cols = st.columns(4)
            for idx, smovie in enumerate(similar_movies[:8]):
                if smovie.get("poster_path"):
                    sim_cols[idx % 4].image(IMAGE_BASE + smovie["poster_path"], use_container_width=True)
                    sim_cols[idx % 4].write(smovie["title"])

    else:
        st.error("No results found.")

# ---- SHOW FAVORITES ----
if st.session_state.favorites:
    st.sidebar.header("❤️ Favorite Films")
    for fav in st.session_state.favorites:
        st.sidebar.write(f"🎬 {fav}")
