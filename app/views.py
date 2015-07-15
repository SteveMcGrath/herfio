from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import not_
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
    full_search = request.args.get('full_search')
    site = request.args.get('site')
    category = request.args.get('category')
    auctions = None
    stats = {'display': False}
    
    if form.validate_on_submit():
        return redirect('/search/%s' % form.search.data.replace(' ', '_'))

    if search_string == '':
        search_string = None

    if search_string or full_search:
        if full_search:
            a = Auction.query.filter(Auction.name.contains(full_search))
        else:
            search_string = unquote(search_string).decode('utf8').replace('_', ' ')
            a = Auction.query
            for word in search_string.split():
                # lets go ahead and allow for some parameterization...
                if '=' in word:
                    name, value = word.split('=')
                    if name.lower() == 'category':
                        category = value
                    if name.lower() == 'site':
                        site = value
                else:
                    # is this a negative filter?
                    if word[0] == '-':
                        inverse = True
                    else:
                        inverse = False

                    # Is the word a single character?  if it is, when we will need to
                    # add spaces around it.
                    if len(word) == 1:
                        word = ' %s ' % word

                    if inverse:
                        a = a.filter(not_(Auction.name.contains(word[1:])))
                    else:
                        a = a.filter(Auction.name.contains(word))

        # now we have a unified way of handling parameters.
        if site:
            a = a.filter(Auction.site.in_(site.split(',')))
        if category:
            a = a.filter(Auction.type.in_(category.split(',')))              
        auctions = a.order_by(Auction.close).all()

        if auctions:
            # First we are going to pull out the subset of the data that we will
            # be using.  We don't want to have any Null values (which would
            # indicate that the auction never sold for anything) and we don't
            # want to have samplers in our dataset either (as they are a variety
            # if sticks and the prices won't jive with the data).
            pa = []
            trend = []
            prices = []
            heat = {}
            for auction in auctions:
                if ((auction.price_per_stick is not None 
                     and auction.finished 
                     and auction.type != 'sampler')
                     or 'sampler' in category.split(',')):
                    pa.append(auction)
                    trend.append([mktime(auction.close.timetuple()) * 1000, float(auction.price_per_stick)])
                    prices.append(auction.price_per_stick)

            # Now for all the fun math stuff.  We will be sorting the prices so
            # that they are in order from low to high.  Once we have that we
            # can start to use that to build a profile of what this price range
            # really looks like.
            prices = sorted(prices)
            heat = {}
            for price in prices:
                iprice = int(price * 100)
                if iprice not in heat:
                    heat[iprice] = 0
                heat[iprice] += 1
            if len(prices) > 0:
                stats['heatmap'] = [[float(i) / 100, heat[i]] for i in heat]
                stats['trend'] = trend
                stats['display'] = True
                stats['avg'] = float(sum(prices)/len(prices))
                stats['std_deviation'] = float(std(prices))
                stats['best'] = float(prices[0])
                stats['great'] = stats['avg'] - (stats['std_deviation'] * 2)
                stats['good'] = stats['avg'] - stats['std_deviation']
                stats['poor'] = stats['avg'] + stats['std_deviation']
                stats['bad'] = stats['avg'] + (stats['std_deviation'] * 2)
                stats['worst'] = float(prices[-1])
    if request.mimetype == 'application/json':
        return jsonify(
            auctions=[a.serialize() for a in auctions],
            stats=stats,
            search_string=search_string
        )
    else:        
        return render_template('search.html',
            auctions=auctions,
            form=form,
            stats=stats,
            search_string=search_string,
        )