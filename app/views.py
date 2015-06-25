from flask import Flask, render_template, request, redirect, url_for
from .extensions import db
from .models import Auction
from .forms import SearchForm
from urllib2 import unquote
from numpy import median, std, floor, average


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/search/<search_string>')
def search(search_string=None):
    '''Search Page'''
    form = SearchForm()
    results = None
    stats = {}
    
    if form.validate_on_submit():
        return redirect('/search/%s' % form.search.data)

    if search_string:
        search_string = unquote(search_string).decode('utf8')
        if search_string == '':
            search_string = '[EMPTY]'
        else:
            o = Auction.query.order_by(Auction.name).filter_by(finished=False)
            c = Auction.query.order_by(Auction.close).filter_by(finished=True)
            for word in search_string.split():
                o = o.filter(Auction.name.like('%%%s%%' % word))
                c = c.filter(Auction.name.like('%%%s%%' % word))
            closed_auctions = c.all()
            open_auctions = o.all()

        if closed_auctions:
            prices = sorted([i.price_per_stick for i in closed_auctions if i.price_per_stick is not None])
            if len(prices) > 0:
                stats['avg_price'] = average(prices)
                stats['median_price'] = median(prices)
                stats['std_deviation'] = std(prices)
                stats['worst_price'] = min(prices)
                stats['bad_price'] = prices[floor(len(prices)*5/6)]
                stats['poor_price'] = prices[floor(len(prices)*4/6)]
                stats['good_price'] = prices[floor(len(prices)*2/6)]
                stats['great_price'] = prices[floor(len(prices)*1/6)]
                stats['best_price'] = max(prices)
            stats['trend'] = [[mktime(i.close.timetuple()), i.price_per_stick] for i in closed_auctions if i.price_per_stick is not None]            

    return render_template('search.html',
        open_auctions=open_auctions,
        closed_auctions=cloased_auctions, 
        form=form,
        stats=stats,
        search_string=search_string,
    )