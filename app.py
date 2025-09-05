from flask import Flask, render_template, request
import pandas as pd
import requests
import pickle
import joblib

app = Flask(__name__)


# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = joblib.load('similarity_jj.pkl')

# TMDB API key
TMDB_API_KEY = 'c18fda7b54423b9c3388bb2ac51678ec'

def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}')
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "/static/default.jpg"

def recommend(movie_title):
    try:
        index = movies[movies['title'] == movie_title].index[0]
    except IndexError:
        return [], []

    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    movie_titles = movies['title'].values
    recommendations = []
    posters = []
    selected_movie = None

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        if selected_movie:
            recommendations, posters = recommend(selected_movie)

    return render_template('index.html',
                           movies=movie_titles,
                           selected_movie=selected_movie,
                           recommendations=zip(recommendations, posters))

if __name__ == '__main__':
    app.run(debug=True)
