# -*- coding: utf-8 -*-
import re
import requests
import httplib

from app import cache

HEADERS = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain",
    "Accept-Language": 'en-us'
}


class IMDBObject:
    def __init__(self, data):
        self.imdb_id = data['imdb_id']
        self.title = data['title']
        self.url = data['url']
        self.rating = data['rating']
        self.img = data['img']

    def __unicode__(self):
        return self.title

    @staticmethod
    @cache.memoize(12 * 4 * 60 * 60 * 24 * 7)
    def get_by_imdb_id(id):
        url = 'http://akas.imdb.com/title/%s/' % id

        imdb_data = requests.get(url, headers=HEADERS)

        regex = 'id="img_primary"[\s\S]*src="(.*)"[\s\S]*' \
                '<h1 class="header">.*<span class="itemprop" itemprop="name">(.*)<\/span>[\s\S]*' \
                '<span itemprop="ratingValue">([\d+.?]*)'

        data = re.findall(regex, imdb_data.text)

        if data:
            img, title, rating = data[0]
            return IMDBObject({'imdb_id': id,
                               'url': url,
                               'img': img,
                               'title': title if title else "",
                               'rating': rating,
            })

        return None

    @staticmethod
    @cache.memoize(60 * 60 * 24 * 7)
    def top_moviemeter(url, max_elements=50):

        elements = []
        start = 0

        while start < max_elements:
            request = requests.get(url + "&start=%s" % start, headers=HEADERS)

            ids = set(re.findall("""<a href=\"/title/([a-z][a-z]\d+)/""", request.text)[0:50])

            for id in ids:
                imdb_element = IMDBObject.get_by_imdb_id(id)

                if imdb_element:
                    elements.append(imdb_element)

            start += 50

        return sorted(elements, key=lambda m: m.rating, reverse=True)

    @staticmethod
    def most_popular():
        raise NotImplementedError


class Movie(IMDBObject):

    @staticmethod
    @cache.memoize(60 * 60 * 24 * 7)
    def most_popular():
        return IMDBObject.top_moviemeter(
            'http://www.imdb.com/search/title?sort=moviemeter,asc&title_type=feature',
            max_elements=50)


class TV(IMDBObject):

    @staticmethod
    def guess_epguide_name(show):
        title = show.title.lower().strip()

        if title.startswith("the"):
            title = title[3:]

        return title.replace(".", "").replace(" ", "")

    @staticmethod
    @cache.memoize(60 * 60 * 24 * 7)
    def most_popular():
        shows = IMDBObject.top_moviemeter(
            'http://www.imdb.com/search/title?sort=moviemeter,asc&title_type=tv_series',
            max_elements=50)

        for show in shows:
            show.epguide = TV.guess_epguide_name(show)

        return shows


class User:
    def __init__(self, imdb_user_id):
        self.imdb_user_id = imdb_user_id

    @cache.memoize(60 * 60 * 24 * 7)
    def watchlist(self):

        movies = []

        rows = []
        url = 'akas.imdb.com'
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

