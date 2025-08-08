## -----------------------------------------------------------------------------
## film_mood_board_enhanced.py
## -----------------------------------------------------------------------------
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# ---- PAGE CONFIG ----
# Set the page configuration. This should be the first Streamlit command.
st.set_page_config(
    page_title="🎬 Paige's Mood Board", # <-- Updated title
    page_icon="🎨", # <-- Updated icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- API & IMAGE CONFIG ----
# Central place for API configurations
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/original"

# ---- API KEY HANDLING ----
# Securely get API key from Streamlit secrets and handle missing key
try:
    API_KEY = st.secrets["API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("🚨 API_KEY not found! Please add it to your Streamlit secrets.")
    st.stop()

# ---- STATE MANAGEMENT ----
# Initialize session state for favorites and movie data to prevent re-fetching
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "current_movie" not in st.session_state:
    st.session_state.current_movie = None

# ---- HELPER FUNCTIONS ----

def search_movie(query):
    """Searches for a movie on TMDb and returns the first result."""
    search_url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": query, "language": "en-US"}
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[0] if results else None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to TMDb API: {e}")
        return None

def get_movie_details(movie_id):
    """Fetches detailed information for a specific movie, including credits."""
    details_url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY, "append_to_response": "videos,images,credits,similar"}
    try:
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch movie details: {e}")
        return None

def display_favorites():
    """Renders the list of favorite movies in the sidebar."""
    st.sidebar.title("❤️ Paige's Favorite Films") # <-- Updated title
    if not st.session_state.favorites:
        st.sidebar.info("Your favorite movies will appear here. Add some!")
    else:
        for fav_title in st.session_state.favorites:
            if st.sidebar.button(f"🗑️ {fav_title}", key=f"fav_{fav_title}"):
                st.session_state.favorites.remove(fav_title)
                st.experimental_rerun()

# ---- MAIN APP LAYOUT ----

# --- BANNER --- ## <-- NEW
# Make sure you have the banner image saved as 'banner.png' in the same folder
try:
    st.image("banner.png", use_container_width=True)
except FileNotFoundError:
    st.title("🎨 Paige's Mood Board") # Fallback to title if image not found

st.write("Discover everything about your favorite films. Search for a movie to get started.")

# --- SIDEBAR ---
display_favorites()

# --- SEARCH BAR ---
movie_query = st.text_input("Enter a movie title", placeholder="e.g., La La Land")

if movie_query:
    with st.spinner('Searching for your movie...'):
        movie_result = search_movie(movie_query)

    if movie_result:
        # Fetch all details in one go
        st.session_state.current_movie = get_movie_details(movie_result["id"])
    else:
        st.error("No results found. Try a different title!")

# --- DISPLAY MOVIE DETAILS ---
if st.session_state.current_movie:
    movie = st.session_state.current_movie
    movie_title = movie.get("title", "N/A")
    
    # --- HEADER SECTION ---
    col1, col2 = st.columns([1, 2])
    with col1:
        if movie.get("poster_path"):
            st.image(POSTER_BASE_URL + movie["poster_path"], use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x750.png?text=No+Poster", use_container_width=True)
            
    with col2:
        st.header(movie_title)
        
        # --- METADATA ---
        release_date = movie.get('release_date', 'N/A')
        rating = f"{movie.get('vote_average', 0):.1f}/10"
        genres = ", ".join([g['name'] for g in movie.get('genres', [])])
        runtime = f"{movie.get('runtime', 0)} min"
        
        st.markdown(f"**🗓️ Release Date:** {release_date} | **⭐ Rating:** {rating} | **⏳ Runtime:** {runtime}")
        st.markdown(f"**🎭 Genres:** {genres}")
        
        # --- TAGLINE & OVERVIEW ---
        if movie.get("tagline"):
            st.markdown(f"> *{movie.get('tagline')}*")
        st.write(movie.get("overview", "No overview available."))
        
        # --- FAVORITE BUTTON LOGIC ---
        is_favorited = movie_title in st.session_state.favorites
        button_text = "❤️ Remove from Favorites" if is_favorited else "🤍 Add to Favorites"
        if st.button(button_text, use_container_width=True):
            if is_favorited:
                st.session_state.favorites.remove(movie_title)
                st.success(f"Removed {movie_title} from favorites!")
            else:
                st.session_state.favorites.append(movie_title)
                st.success(f"Added {movie_title} to favorites!")
            st.experimental_rerun()

    st.markdown("---")

    # --- TABS FOR DETAILS ---
    tab1, tab2, tab3, tab4 = st.tabs(["🎥 Trailer", "👨‍👩‍👧‍👦 Cast & Crew", "📸 Stills", "🎯 Similar Movies"])

    with tab1:
        st.subheader("🎥 Watch Trailer")
        videos = movie.get("videos", {}).get("results", [])
        trailer = next((v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if trailer:
            st.video(f"https://www.youtube.com/watch?v={trailer['key']}")
        else:
            st.info("No trailer available for this movie.")

    with tab2:
        st.subheader("👨‍👩‍👧‍👦 Top Billed Cast")
        credits = movie.get("credits", {})
        cast = credits.get("cast", [])
        if cast:
            cols = st.columns(5)
            for idx, person in enumerate(cast[:10]):
                if person.get("profile_path"):
                    cols[idx % 5].image(IMAGE_BASE_URL + person["profile_path"])
                    cols[idx % 5].write(f"**{person['name']}**")
                    cols[idx % 5].caption(f"as {person['character']}")
        else:
            st.info("Cast information not available.")

    with tab3:
        st.subheader("📸 Movie Stills")
        backdrops = movie.get("images", {}).get("backdrops", [])
        if backdrops:
            st.image([IMAGE_BASE_URL + img["file_path"] for img in backdrops[:9]], width=250)
        else:
            st.info("No stills available for this movie.")
            
    with tab4:
        st.subheader("🎯 Similar Movies You Might Like")
        similar_movies = movie.get("similar", {}).get("results", [])
        if similar_movies:
            cols = st.columns(4)
            for idx, smovie in enumerate(similar_movies[:8]):
                if smovie.get("poster_path"):
                    with cols[idx % 4]:
                        st.image(IMAGE_BASE_URL + smovie["poster_path"], use_container_width=True, caption=smovie["title"])
        else:
            st.info("Couldn't find any similar movies.")
