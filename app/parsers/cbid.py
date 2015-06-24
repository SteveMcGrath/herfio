from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from app.models import Auction, Brand
from app.extensions import db
import requests, re


class Parser(object):
    url = 'http://www.cigarbid.com/Auction/ClosingToday/?IsCatPage=False&PageSize=10000&ViewType=List&SpecialSearch=True&SpecialSearchDisplay=Lots+Closing+Today&keyword=CLOSINGTODAY&SortOrder=endingsoon&CategoryFilters=&AuctionFilters=CLASSIC,QUICKBUY&BonusBuyOnly=False'

    def get_page(self, url):
        '''returns with a BeautifulSoup object of the URL specified.'''
        resp = requests.get(url)
        return BeautifulSoup(resp.content)

    def timestamp_gen(self, text):
        '''Generates a datetime object off of the "time left" component'''
        try:
            t = re.findall(r'(\d{1,3})h (\d{1,2})m', text)
            return datetime.now() + timedelta(hours=int(t[0][0]), minutes=int(t[0][1]))
        except IndexError:
            t = re.findall(r'(\d{1,2})m (\d{1,2})s', text)
            return datetime.now() + timedelta(minutes=int(t[0][0]), seconds=int(t[0][1]))

    def parse_item(self, item):
        '''
        Parses an individual entry from the main listing.  This is how the majority
        of the updates will be occuring.  We will mostly be using these updates for
        awareness of auctions that have been added.  While we are here we will
        continue to track the price of the auction even though it is not closed, as
        this may become relevent in some searches.
        '''
        regexes = [
            re.compile(r'\w+ of (\d{1,3})'),
            re.compile(r'^(\d{1,3})[ -]'),
        ]
        aid = item.findChild('td', {'class': 'cb_wcb cb_colsm'}).findNext('span').get('data-id')
        auction = Auction.query.filter_by(aid=aid, site='cbid').first()
        
        if not auction:
            # as we haven't seen this action before, we will need to get all of
            # the usual information and store that into a new Auction database
            # object.
            link = 'http://www.cigarbid.com%s' % item.findNext('a').get('href')
            title = item.findNext('a').text
            category = item.findNext('a').findNext('span').text
            auction = Auction()

            try:
                auction.name, auction.quantity = re.findall(r'^([\W\w]+) \((\d{1,3})\)', title)[0]
                auction.type = 'box'
            except IndexError:
                data = title.split(' - ')
                auction.name = data[0]
                for regex in regexes:
                    if not auction.quantity:
                        i = regex.findall(data[0])
                        if len(i) > 0:
                            auction.quantity = int(i[0])
            auction.site = 'cbid'
            auction.link = link
            auction.aid = item.find('span', {'class': 'add'}).get('data-id')
            auction.close = self.timestamp_gen(item.find('td', {'class': 'cb_product_timeleft'}).text)
            #brand.auctions.append(auction)
            db.session.add(auction)

        # now we need to get the current price and update the timestamp.
        cprice = item.find('td', {'class': 'cb_product_current_price'}).findNext('span').text.strip('$')
        if cprice is not u'':
            auction.price = float(cprice)
        auction.timestamp = datetime.now()

        # Now we need to commit the changes to the database ;)
        db.session.commit()

    def get_final_price(self, page):
        '''Attempts to get the final price of the cigars.'''
        bids = page.findAll('td', {'class': 'lot_winning_bid'})
        high = 0.0
        for bid in bids:
            nbid = float(re.findall(r'\$(\d{1,4}\.\d{2})', bid.text)[0])
            if nbid > high: 
                high = nbid
        return high

    def run(self):
        '''Primary loop'''
        # Here we will be interating through the different URLs defined in
        # the objects and will be handing the individual entries off to the
        # parse_item function for handling.
        page = self.get_page(self.url)
        items = page.find('div', attrs={'class': 'cb_product_listing'}).findChildren('tr')[2:]
        for item in items:
            self.parse_item(item)

        # Commit all of the updates and new items
        #db.session.commit()

        for auction in Auction.query.filter(Auction.close <= datetime.now())\
                                    .filter(Auction.finished == False)\
                                    .filter(Auction.site == 'cbid').all():
            # Now we will need to work our way through all of the closed auctions
            # that haven't been finalized yet.  Finalization is effectively getting
            # the closed price for the auction, tagging the auction as finished
            # (so that we know not to finalize again), and update the timestamp
            # one last time.
            print 'Closing %s:%s' % (auction.aid, auction.name)
            page = self.get_page(auction.link)
            auction.price = self.get_final_price(page)
            auction.finished = True
            auction.timestamp = datetime.now()

        # Commit all of the final changes!!!!
        db.session.commit()
