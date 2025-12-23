import streamlit as st
import pickle
import pandas as pd
import requests

API_KEY = "YOUR_API_KEY"  # 🔑 put your TMDB key here

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=dd2464e1c3badc10aed6bb5c3e8a8f71&language=en-US"
    response = requests.get(url)
    data = response.json()

    poster_path = data.get("poster_path")
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    return None


# Load data
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open("similarity.pkl", "rb"))

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []
    posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id  # ✅ correct ID
        recommendations.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return recommendations, posters


# Streamlit UI
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie",
    movies["title"].values
)

if st.button("Recommend"):
    recommendations, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(recommendations[i])
            if posters[i]:
                st.image(posters[i])
