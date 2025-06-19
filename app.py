
import streamlit as st
import pandas as pd
import pickle
import requests
import time

def fetch_poster(movie_id, retries=3):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": "42d55615dbb0926da45b002bb3cae6be", "language": "en-US"}
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                print(f"No poster found for movie_id {movie_id}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} - Error fetching poster for movie_id {movie_id}: {e}")
            time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s, 4s
    return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)

        poster = fetch_poster(movie_id)
        recommended_posters.append(poster)

        time.sleep(0.3)  # delay to avoid API rate limit

    return recommended_movies, recommended_posters

# Load data
movies_dict = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommendation System')

selected_movie = st.selectbox(
    "Select a movie:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    # Filter out recommendations without posters
    filtered = [(n, p) for n, p in zip(names, posters) if p is not None]

    if not filtered:
        st.write("No recommendations available with posters.")
    else:
        cols = st.columns(len(filtered))
        for col, (name, poster) in zip(cols, filtered):
            col.text(name)
            col.image(poster)


