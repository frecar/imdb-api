# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.cache import Cache


app = Flask(__name__)
app.config.update({
    'DEBUG': True,
    'CACHE_TYPE': 'simple',
})

cache = Cache(app)