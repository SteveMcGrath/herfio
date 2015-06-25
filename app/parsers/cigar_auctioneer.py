from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from app.models import Auction, Brand
from app.extensions import db
from . import logging
import requests, re


class Parser(object):
    urls = {
        'box': 'http://www.cigarauctioneer.com/search.cfm/st/box',
        'bundle': 'http://www.cigarauctioneer.com/search.cfm/st/bun',
        '5-pack': 'http://www.cigarauctioneer.com/search.cfm/st/5pak',
        '10-pack': 'http://www.cigarauctioneer.com/search.cfm/st/10pak',
        'sampler': 'http://www.cigarauctioneer.com/search.cfm/st/samp',
        'single': 'http://www.cigarauctioneer.com/search.cfm/st/sing',
    }

    def get_page(self, url):
        '''returns with a BeautifulSoup object of the URL specified.'''
        resp = requests.post(url, data={'NumPerPage': 'ALL', 'sort': '3'})
        return BeautifulSoup(resp.content)

    def timestamp_gen(self, text):
        '''Generates a datetime object off of the "time left" component'''
        time = {
            'days': re.findall(r'(\d{1,3})d', text),
            'hours': re.findall(r'(\d{1,3})hr', text),
            'minutes': re.findall(r'(\d{1,2})m', text),
            'seconds': re.findall(r'(\d{1,2})s', text),
        }

        for item in time:
            if len(time[item]) > 0:
                time[item] = int(time[item][0])
            else:
                time[item] = 0

        return datetime.now() + timedelta(
            days=time['days'],
            hours=time['hours'],
            minutes=time['minutes'],
            seconds=time['seconds']
        )

    def parse_item(self, item, index, package_type):
        '''
        Parses an individual entry from the main listing.  This is how the majority
        of the updates will be occuring.  We will mostly be using these updates for
        awareness of auctions that have been added.  While we are here we will
        continue to track the price of the auction even though it is not closed, as
        this may become relevent in some searches.
        '''
        aid = item.findChild('input', {'name': 'frmAuctionID%s' % index}).get('value')
        bid = item.findChild('input', {'name': 'frmBrandCode%s' % index}).get('value')
        auction = Auction.query.filter_by(aid=aid, site='cigarauctioneer').first()
        brand = Brand.query.filter_by(ca_id=bid).first()

        if not brand:
            brand = Brand()
            brand.name = item.findChild('input', {'name': 'frmBrandDesc%s' % index}).get('value')
            brand.ca_id = bid
            db.session.add(brand)

        if not auction:
            # as we haven't seen this action before, we will need to get all of
            # the usual information and store that into a new Auction database
            # object.
            auction = Auction()
            auction.type = package_type
            auction.name = item.findChild('input', {'name': 'frmItemDesc%s' % index}).get('value')
            auction.aid = aid
            auction.site = 'cigarauctioneer'
            auction.close = self.timestamp_gen(item.findChild('div', text='Time Left:').findNext('div').text)
            auction.link = item.findChild('a', {'itemprop': 'url'}).get('href')
            if package_type is not 'singles':
                auction.quantity = int(item.findChild('input', {'name': 'frmItemsPerPack%s' % index}).get('value'))
            else:
                auction.quantity = 1
            brand.auctions.append(auction)
            db.session.add(auction)

        # now we need to get the current price and update the timestamp.
        auction.price = float(item.findChild('div', {'itemprop': 'price'}).text.strip('$'))
        auction.timestamp = datetime.now()

        # Now we need to commit the changes to the database ;)
        db.session.commit()

    def get_final_price(self, page):
        '''Attempts to get the final price of the cigars.'''
        a_type = page.find('div', text='Auction Type:').findNext('img').get('class').split()
        if 'spicon_english' in a_type:
            # In a regular auction, the high bidder wins.  In this case its
            # simply a matter of pulling the high bid and converting it into a
            # float.
            try:
                return float(page.find(attrs={'id': 'highbid'}).text.strip('$'))
            except:
                return None
        if 'spicon_yankee' in a_type:
            # In this case we are dealing with a yankee auction.  As there are
            # multiple winners for this auction, we only want the high price.
            try:
                return float(page.find(attrs={'id': 'highbidder'}).findNext('span').text.strip('$'))
            except:
                return None

    def run(self):
        '''Primary loop'''
        for url in self.urls:
            # Here we will be interating through the different URLs defined in
            # the objects and will be handing the individual entries off to the
            # parse_item function for handling.
            page = self.get_page(self.urls[url])
            items = page.findAll('div', attrs={'itemtype': 'http://schema.org/Product'})
            for item in items:
                self.parse_item(item, items.index(item) + 1, url)

        # Commit all of the updates and new items
        #db.session.commit()

        for auction in Auction.query.filter(Auction.close <= datetime.now())\
                                    .filter(Auction.finished == False)\
                                    .filter(Auction.site == 'cigarauctioneer').all():
            # Now we will need to work our way through all of the closed auctions
            # that haven't been finalized yet.  Finalization is effectively getting
            # the closed price for the auction, tagging the auction as finished
            # (so that we know not to finalize again), and update the timestamp
            # one last time.
            logging.debug('CLOSING %s:%s' % (auction.aid, auction.name))
            page = self.get_page(auction.link)
            auction.price = self.get_final_price(page)
            auction.finished = True
            auction.timestamp = datetime.now()
            db.session.commit()
