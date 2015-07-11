from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from app.models import Auction, Brand
from app.extensions import db
from . import logging
import requests, re


class Parser(object):
    def get_page(self, url, **kwargs):
        '''returns with a BeautifulSoup object of the URL specified.'''
        resp = requests.get(url, **kwargs)
        return BeautifulSoup(resp.content)

    def item_parse(self, item_id, price, page=None):
        '''
        Parses the CigarMonster AJAX API output
        '''
        # As time is gong to be mostly computed for CigarMonster items, we need
        # to get a some pre-determined times computed out first.
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        hrtime = datetime(today.year, today.month, today.day, today.hour, 00)
        mtime = datetime(today.year, today.month, today.day, 11, 00)
        ntime = datetime(today.year, today.month, today.day, 23, 00)

        # Now lets check to see if this item has already been worked on...
        auction = Auction.query.filter(Auction.aid == item_id)\
                               .filter(Auction.site == 'cigarmonster')\
                               .filter(Auction.close >= today).first()
        if not auction:
            # As there is nothing in the database, we will check to see if we 
            # need to create a new entry for this deal.  CigarMonster uses an
            # AJAX popin to display the details.  We will be using that to get
            # a consistant point of information.
            url = 'http://www.cigarmonster.com/include/ajax_getPopin.cfm'
            if not page:
                page = self.get_page(url, params={'num': item_id})

            # Lets populate the attributes dictionary with the information we
            # are pulling from the popin.
            attrs = {}
            for a in page.findAll('div', {'class': 'detail-l'}):
                name = a.text.lower().strip(':')
                value = a.findNext('div', {'class': 'detail-r'}).text.lower()
                attrs[name] = value

            # If there is no quantity in the popin, then this isn't specifically
            # a cigar item and we will want to ignore it.
            if 'quantity' in attrs:
                auction = Auction()
                auction.aid = item_id
                auction.timestamp = datetime.now()
                auction.link = 'http://www.cigarmonster.com'
                auction.site = 'cigarmonster'
                auction.quantity = int(attrs['quantity'].split()[0])

                # If the quantity is greater than 1, then we will want to set the
                # type a N-pack where N is the number of cigars that we pulled.
                # if the quantity is really 1, then sey the type to single.
                if auction.quantity > 1:
                    auction.type = '%s-pack' % auction.quantity
                elif auction.quantity == 1:
                    auction.type = 'single'

                # Next we will need to get the price.
                auction.price = price
                
                # As not all of the CigarMonster auctions have a shape in the 
                # name of the auction, we will want to add this for searching
                # purposes.  We will append (SHAPE) to the end of the deal name.
                if page.find('div', {'class': 'mashupitempopdes'}):
                    name = page.find('div', {'class': 'mashupitempopdes'}).text
                else:
                    name = page.find('h2', {'class': 'monsteritemdes'}).text
                auction.name = name + ' (%s)' % attrs['shape']
                
                # So if we see any indications that this is a sampler, then we
                # should re-type it to be as such.
                if ('sampler' in auction.name or 
                    attrs['size'] == 'varies' or 
                    attrs['shape'] == 'assorted'):
                    auction.type = 'sampler'

                if today > mtime and today < ntime:
                    auction.close = hrtime + timedelta(hours=12)
                else:
                    auction.close = hrtime + timedelta(hours=1)
                logging.info('CigarMonster - ADDING %s' % auction.name)
                db.session.add(auction)
                db.session.commit()

    def run(self):
        raid = re.compile(r'\d+')
        page = self.get_page('http://www.cigarmonster.com')

        # If this is a Mashup, then we will need to parse through each item...
        for item in page.findAll('a', {'class': 'mashupItem'}):
            price = float(item.findNext('span', {'class': 'mashupitemprice'}).contents[0].strip('$'))
            self.item_parse(item.get('name'), price=price, itype='mashup')

        # if this is an individual deal, then we will have to handle the page
        # a little different;y, as there is only one item, and as such, the
        # format is different.
        if page.find('div', {'class': 'monsterdealcurrent'}):
            price = float(page.find('span', {'itemprop': 'price'}).text.strip('$'))
            aid = raid.findall(page.find('img', {'id': 'skupic'}).get('onclick'))[0]
            self.item_parse(aid, price=price, page=page, itype='individual')

        # a little cleanup action here to make sure that all of the deals that
        # have expired are actually closed.
        stmt = db.update(Auction)\
                      .where(Auction.site == 'cigarmonster')\
                      .where(Auction.close < datetime.now())\
                      .where(Auction.finished == False)\
                      .values(finished=True)
        db.engine.execute(stmt)

