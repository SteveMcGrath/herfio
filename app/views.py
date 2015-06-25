from flask import Flask, render_template, request, redirect, url_for
from .extensions import db
from .models import Auction
from .forms import SearchForm
from urllib2 import unquote


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
            q = Auction.query.order_by(Auction.name)
            for word in search_string.split():
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
        search_string=search_string,
    )