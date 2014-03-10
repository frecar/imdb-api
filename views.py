# -*- coding: utf-8 -*-

from app import app, cache
from models import User, Movie, IMDBObject, TV
from utils import json_response

@app.route('/watchlist/<imdb_user_id>/')
@cache.memoize(60 * 60 * 24 * 7)
def watchlist(imdb_user_id):

    movies = User(imdb_user_id).watchlist()
    return json_response(movies)

@app.route('/<imdb_id>/')
@cache.memoize(60 * 60 * 24 * 7)
def view_movie(imdb_id):

    movie = IMDBObject.get_by_imdb_id(imdb_id)
    return json_response(movie)

@app.route('/mostpopular/films/')
def most_popular_feature_films():
    """<a href="\/title\/([a-z][a-z]\d+)\/"""

    movies = Movie.most_popular()
    return json_response(movies)

@app.route('/mostpopular/tv/')
def most_popular_feature_tv():
    """<a href="\/title\/([a-z][a-z]\d+)\/"""

    movies = TV.most_popular()
    return json_response(movies)