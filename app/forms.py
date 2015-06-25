from flask.ext.wtf import Form
from wtforms.fields import TextField
from flask.ext.wtf.html5 import *


class SearchForm(Form):
    search = TextField('search')