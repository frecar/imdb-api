# -*- coding: utf-8 -*-

from app import app
from models import User, Movie
from utils import json_response


@app.route('/watchlist/<imdb_user_id>/')
def watchlist(imdb_user_id):

    movies = User(imdb_user_id).watchlist()
    return json_response(movies)


@app.route('/mostpopular/')
def most_popular_feature_films():
    """<a href="\/title\/([a-z][a-z]\d+)\/"""

    movies = Movie.most_popular_feature_films()
    return json_response(movies)