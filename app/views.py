from flask import Flask, render_template, request, redirect, url_for
from .extensions import db
from .models import Auction
from .forms import SearchForm
from urllib2 import unquote
from time import mktime
from math import floor
from numpy import median, std


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/search/<search_string>')
@app.route('/search/')
def search(search_string=None):
    '''Search Page'''
    form = SearchForm()
    auctions = None
    stats = {'display': False}
    
    if form.validate_on_submit():
        return redirect('/search/%s' % form.search.data)

    if search_string:
        print search_string
        search_string = unquote(search_string).decode('utf8')
        #if search_string == '':
        #    search_string = '[EMPTY]'
        #else:
        a = Auction.query.order_by(Auction.name)
        for word in search_string.split():
            a = a.filter(Auction.name.like('%%%s%%' % word))
        auctions = a.all()
        print len(auctions)

        if auctions:
            prices = sorted([i.price_per_stick for i in auctions if i.price_per_stick is not None and i.finished])
            if len(prices) > 0:
                stats['display'] = True
                stats['avg'] = sum(prices)/len(prices)
                stats['std_deviation'] = float(std(prices))
                stats['worst'] = prices[-1]
                stats['bad'] = stats['avg_price'] - (stats['std_deviation'] * 2)
                stats['poor'] = stats['avg_price'] - stats['std_deviation']
                stats['good'] = stats['avg_price'] + stats['std_deviation']
                stats['great'] = stats['avg_price'] + (stats['std_deviation'] * 2)
                stats['best'] = prices[0]
            stats['trend'] = [[mktime(i.close.timetuple()), float(i.price_per_stick)] for i in auctions if i.price_per_stick is not None and i.finished]            

    return render_template('search.html',
        auctions=auctions,
        form=form,
        stats=stats,
        search_string=search_string,
    )