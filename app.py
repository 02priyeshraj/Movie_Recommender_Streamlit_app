import pickle
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


# Function to fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:  # Only return if poster exists
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except Exception:
        return None
    return None  # ❌ Skip movies without posters


# Function to get movie recommendations
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:30]:  # Fetch more to ensure valid posters
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)

        if poster_url:  # ✅ Only include if poster exists
            recommended_movie_posters.append(poster_url)
            recommended_movie_names.append(movies.iloc[i[0]].title)

        if len(recommended_movie_names) >= 9:  # Limit to 9 recommendations
            break

    return recommended_movie_names, recommended_movie_posters


# Streamlit UI
st.set_page_config(page_title="Movie Recommender 🎬", layout="wide")

# 🎨 Custom CSS styling
st.markdown(
    """
    <style>
    body {
        background-color: #0d0d0d;
        color: #ffffff;
    }
    .main {
        background-color: #111111;
        padding: 20px;
        border-radius: 12px;
    }
    h1 {
        text-align: center;
        color: #ffcc00;
        font-family: 'Trebuchet MS', sans-serif;
    }
    .stSelectbox label {
        font-size: 18px;
        font-weight: bold;
        color: #ffcc00;
    }
    .movie-title {
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown("<h1>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)

# Load movie data and similarity matrix
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Dropdown for selecting a movie
movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Select a Movie:", movie_list)

# Show recommendations when button is clicked
if st.button('🔍 Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    st.markdown("## 🍿 Recommended Movies for You")
    st.write("---")

    # Display movies in rows of 3
    for i in range(0, len(recommended_movie_names), 3):
        cols = st.columns(3, gap="large")

        for j in range(3):
            if i + j < len(recommended_movie_names):
                with cols[j]:
                    st.image(
                        recommended_movie_posters[i + j],
                        use_container_width=True,
                        caption=f"⭐ {recommended_movie_names[i + j]}"
                    )
