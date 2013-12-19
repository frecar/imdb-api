# -*- coding: utf-8 -*-
from time import time
import re
import requests
import httplib

from app import cache

HEADERS = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain",
    "Accept-Language": 'en'
}


class Movie:
    def __init__(self, data):
        self.imdb_id = data['imdb_id']
        self.title = data['title']
        self.release_date = data['release_date']
        self.url = data['url']
        self.rating = data['rating']
        self.year = data['year']

    def __unicode__(self):
        return self.title

    @staticmethod
    @cache.memoize(60 * 60 * 24 * 7)
    def get_movie_by_imdb_id(id):
        url = 'http://www.imdb.com/title/%s/' % id

        imdb_data = requests.get(url, headers=HEADERS)

        print url

        regex = '<h1 class="header">.*<span class="itemprop" itemprop="name">(.*)<\/span>[\s\S]*' \
                '<span class="nobr">\(<a href="\/year\/([\d+]*)[\s\S]*' \
                '<meta itemprop="datePublished" content="(.*)"[\s\S]*' \
                '<span itemprop="ratingValue">([\d+.?]*)'

        data = re.findall(regex, imdb_data.text)

        if data:
            title, year, release_date, rating = data[0]
            return Movie({'imdb_id': id,
                          'url': url,
                          'title': title if title else "",
                          'release_date': release_date,
                          'rating': rating,
                          'year': year})

        return None

    @staticmethod
    @cache.memoize(60 * 60 * 24 * 7)
    def most_popular_feature_films():
        movies = []

        r = requests.get('http://www.imdb.com/search/title?&title_type=feature&sort=moviemeter,asc',
                         headers=HEADERS)

        ids = sorted(list(set(re.findall("""<a href=\"/title/([a-z][a-z]\d+)/""", r.text))),
                     key=lambda m: m[0])

        for id in ids:
            t1 = time()
            movie = Movie.get_movie_by_imdb_id(id)
            print time()-t1

            if movie:
                movies.append(movie)

        return movies


class User:
    def __init__(self, imdb_user_id):
        self.imdb_user_id = imdb_user_id

    def watchlist(self):

        movies = []

        rows = []
        url = 'www.imdb.com'
        path = '/list/export?list_id=watchlist&author_id=%s' % self.imdb_user_id
        connection = httplib.HTTPConnection(url)
        connection.request("POST", path, '', HEADERS)
        response = connection.getresponse()
        if response.status == 200:
            input = response.read()
            rows.extend(input.split("\n")[1:])

        for row in rows:
            # Remove " in beginning and end, since it is splitted on ","
            row = row[1:len(row) - 1]
            data = row.split("\",\"")
            if len(data) > 4 and not re.search('TV', data[6]):
                data_decoded = [d.decode('utf-8') for d in data]
                movies.append(Movie({'imdb_id': data_decoded[1],
                                     'title': data_decoded[5],
                                     'release_date': data_decoded[14],
                                     'url': data_decoded[15],
                                     'rating': data_decoded[9],
                                     'year': data_decoded[11]}))

        return movies

