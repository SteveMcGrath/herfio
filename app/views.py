from flask import Flask, render_template, request
from .extensions import db
from .models import Auction
from .forms import SearchForm


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def search():
    '''Search Page'''
    form = SearchForm()
    results = None
    stats = {}
    if form.validate_on_submit():
        if form.search.data == '':
            form.search.data = '[EMPTY]'
        else:
            q = Auction.query.order_by(Auction.name)
            for word in form.search.data.split():
                q = q.filter(Auction.name.like('%%%s%%' % word))
            results = q.all()
        if results:
            stats['high'] = max([i.price_per_stick for i in results if i.price_per_stick is not None])
            stats['low'] = min([i.price_per_stick for i in results if i.price_per_stick is not None])
            stats['avg'] = sum([i.price_per_stick for i in results if i.price_per_stick is not None])/len(results)
    return render_template('search.html',
        results=results, 
        form=form,
        stats=stats,
        search_string=form.search.data,
    )