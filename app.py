from flask import Flask, render_template, request, redirect, url_for, Response
import requests
import difflib

app = Flask(__name__)

# Your TMDB API Key
TMDB_API_KEY = "483a8d6b53d5bb68c110d2c17aa6d725"

def search_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    return response.json().get('results', [])

def get_movie_details(tmdb_id, media_type='movie'):
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json()

def get_trending_movies():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json().get('results', [])

def get_trending_series():
    url = f"https://api.themoviedb.org/3/trending/tv/week?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json().get('results', [])

def get_trending_anime():
    url = f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16"
    response = requests.get(url)
    return response.json().get('results', [])

@app.route('/')
def home():
    trending_movies = get_trending_movies()[:6]
    trending_series = get_trending_series()[:6]
    trending_anime = get_trending_anime()[:6]
    return render_template('home.html', movies=trending_movies, series=trending_series, anime=trending_anime)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    results = search_tmdb(query)
    if not results:
        all_titles = [r['title'] for r in search_tmdb(' ')]
        corrected = difflib.get_close_matches(query, all_titles, n=1, cutoff=0.6)
        if corrected:
            results = search_tmdb(corrected[0])
    return render_template('search.html', results=results)

@app.route('/watch/<media_type>/<int:tmdb_id>')
def watch(media_type, tmdb_id):
    details = get_movie_details(tmdb_id, media_type)
    return render_template('watch.html', details=details, media_type=media_type, tmdb_id=tmdb_id)

# 🛡️ Proxy route to load vidsrc.to iframe safely
@app.route('/proxy/embed/<media_type>/<int:tmdb_id>')
def proxy_embed(media_type, tmdb_id):
    vidsrc_url = f"https://vidsrc.to/embed/{media_type}/{tmdb_id}"
    response = requests.get(vidsrc_url)
    return Response(response.content, content_type=response.headers.get('Content-Type'))

if __name__ == '__main__':
    app.run(debug=True)
