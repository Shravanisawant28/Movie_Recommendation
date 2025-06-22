"""
Movie Recommendation System using Streamlit, Pandas, Pickle, and OMDb API.

🔹 Select a movie from the dropdown
🔹 Get 5 similar movie recommendations
🔹 Posters are fetched using OMDb API
"""
import streamlit as st
import pandas as pd
import pickle
import requests
from concurrent.futures import ThreadPoolExecutor

# fetch posters using OMDb API
def fetch_poster_omdb(title):
    url = "http://www.omdbapi.com/"
    params = {"apikey": "d093b256", "t": title}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_url = data.get('Poster')
        if poster_url and poster_url != "N/A":
            return poster_url
        else:
            print(f"No poster found for title: {title}")    
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for title '{title}': {e}")
        return None

# recommend movie
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = [movies.iloc[i[0]].title for i in movies_list]

    with ThreadPoolExecutor(max_workers=5) as executor:
        recommended_posters = list(executor.map(fetch_poster_omdb, recommended_movies))

    return recommended_movies, recommended_posters

# load data
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

    cols = st.columns(5)

    for i in range(5):
        if i < len(names):
            name = names[i]
            poster = posters[i]
        else:
            name = "N/A"
            poster = None

        with cols[i]:
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.markdown(
                    "<div style='width:100%; height:300px; border:1px solid #ccc; display:flex; align-items:center; justify-content:center;'>No Poster</div>",
                    unsafe_allow_html=True
                )
            st.markdown(
                f"<div style='text-align: center; font-weight: bold;'>{name}</div>",
                unsafe_allow_html=True
            )


