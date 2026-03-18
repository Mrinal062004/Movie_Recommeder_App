import streamlit as st
import pickle
import pandas as pd
import requests

# TMDB API KEY
API_KEY = "dd2464e1c3badc10aed6bb5c3e8a8f71"


# fetch Poster


def fetch_poster(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

    except:
        pass

    return "https://via.placeholder.com/500x750?text=No+Poster"


# fetch Movie Detail


def fetch_details(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        rating = data.get("vote_average", "Not available")
        release = data.get("release_date", "Not available")
        overview = data.get("overview", "No overview available")

        return rating, release, overview

    except:
        return "N/A", "N/A", "No overview available"


# Fetch Trailer

@st.cache_data
def fetch_trailer(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if "results" in data:
            for video in data["results"]:
                if video["type"] == "Trailer" and video["site"] == "YouTube":
                    return "https://www.youtube.com/watch?v=" + video["key"]

    except:
        pass

    return None


# Fetch Data

movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open("similarity.pkl", "rb"))


# Total Movie Recommended

def recommend(movie):

    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    posters = []
    ids = []

    for i in movie_list:

        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        ids.append(movie_id)

    return recommended_movies, posters, ids


# Interface

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 AI Movie Recommender System")


selected_movie_name = st.selectbox(
    "Select a movie",
    movies["title"].values
)


# Button

if st.button("Recommend Movies"):

    recommendations, posters, ids = recommend(selected_movie_name)

    cols = st.columns(5)

    for i in range(5):

        with cols[i]:

            st.subheader(recommendations[i])

            st.image(posters[i])

            rating, release, overview = fetch_details(ids[i])

            with st.expander("📄 Movie Info"):

                st.write("⭐ Rating:", rating)
                st.write("📅 Release Date:", release)

                st.write("📖 Overview:")
                st.write(overview)

                trailer = fetch_trailer(ids[i])

                if trailer:
                    st.markdown(f"▶ [Watch Trailer]({trailer})")
                else:
                    st.write("Trailer not available")