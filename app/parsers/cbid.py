from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from app.models import Auction, Brand
from app.extensions import db
from . import logging
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
        keywords = [
            'toro', 'robusto', 'belicoso', 'connecticut', 'maduro', 'churchill',
            'torpedo', 'corona', 'single', 'lonsdale', 'corojo', 'sumatra',
            'magnum', 'maestro', 'brillantes', 'series \'a\'', 'imperial',
            'box-press', 'gigante', 'shorty', 
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
                # Not all Boxes are in the boxes part of the auction.  We will
                # will instead leverage the commonality of the title formatting
                # to pull all of these.
                auction.name, auction.quantity = re.findall(r'^([\W\w]+) \((\d{1,3})\)', title)[0]
                auction.type = 'box'
            except IndexError:
                auction.name = title
                if category == 'Boxes':
                    try:
                        auction.name, auction.quantity = re.findall(r'^([\W\w]+) \((\d{1,3})\)', title)[0]
                        auction.type = 'box'
                    except IndexError:
                        pass
                elif category == '5-Packs':
                    # The next way we can handle this is to look for all of the
                    # 5-Packs in the response and set the quantity to 5.
                    auction.quantity = 5
                    auction.type = '5-pack'
                elif category == 'Singles':
                    # Singles should always be a quantity of 1.
                    auction.quantity = 1
                    auction.type = 'single'
                elif category == 'Sampler':
                    auction.quantity = 1
                    auction.type = 'sampler'
                
                if not auction.quantity:
                    # These 3 categories are some genetal catch-all categories
                    # and we need to handle the information in a more generic
                    # way.

                    # First lets run through some of the more common paths that
                    # peopl take...
                    if '5 cigars' in title.lower():
                        auction.type = '5-pack'
                        auction.quantity = 5
                    elif '10 cigars' in title.lower():
                        auction.type = '10-pack'
                        auction.quantity = 10
                    if '-pack' in title.lower():
                        matches = re.findall(r'(\d{1,3})-pack', title.lower())
                        if len(matches) > 0:
                            auction.type = '%s-pack' % matches[0]
                            auction.quantity = int(matches[0])
                    elif 'sampler' in title.lower():
                        auction.type = 'sampler'
                        auction.quantity = 1
                    elif '5 cigars' in title.lower():
                        auction.type = '5-pack'
                        auction.quantity = 5
                    elif '10 cigars' in title.lower():
                        auction.type = '10-pack'
                        auction.quantity = 10
                    elif 'pack of 5' in title.lower():
                        auction.type = '5-pack'
                        auction.quantity = 5
                    elif 'pack of 10' in title.lower():
                        auction.type = '10-pack'
                        auction.quantity = 10                    
                    elif ' cigars' in title.lower(): 
                        matches = re.findall(r'(\d{1,3})[ -]cigars', title.lower())
                        if len(matches) > 0:
                            auction.type = 'bundle'
                            auction.quantity = int(matches[0])
                    elif 'single' in title.lower():
                        auction.type = 'single'
                        auction.quantity = 1
                    else:
                        matches = re.findall(r'(\w+) of (\d{1,3})', title.lower())
                        if len(matches) > 0:
                            auction.type = matches[0][0]
                            auction.quantity = int(matches[0][1])
                            if auction.type in ['brick',]:
                                auction.type = 'bundle'

                    if not auction.quantity:
                        for keyword in keywords:
                            # If all else has failed, we have a list of keywords
                            # that would let us know of the title is referring to
                            # cigars or some other merch.  If any of these match,
                            # then we will consider it a single.
                            if keyword in title.lower():
                                auction.quantity = 1
                if not auction.quantity:
                    # Well none of the above options matched, so this doesn't
                    # appear to be a Cigar listing.  Lets abort, throw a pretty
                    # message, and get on with it.
                    logging.debug('ABORTING %s:%s:%s' % (aid, category, title))
                    return
                else:
                    logging.debug('CREATED %s:%s:%s:%s' % (aid, category, auction.quantity, title))
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
            try:
                nbid = float(re.findall(r'\$(\d{1,4}\.\d{2})', bid.text)[0])
                if nbid > high: 
                    high = nbid
            except IndexError:
                pass
        return high

    def run(self, finish_state=False, get_new_listings=True):
        '''Primary loop'''
        # Here we will be interating through the different URLs defined in
        # the objects and will be handing the individual entries off to the
        # parse_item function for handling.
        if get_new_listings:
            page = self.get_page(self.url)
            items = page.find('div', attrs={'class': 'cb_product_listing'}).findChildren('tr')[2:]
            for item in items:
                self.parse_item(item)

        # Commit all of the updates and new items
        #db.session.commit()

        for auction in Auction.query.filter(Auction.close <= datetime.now())\
                                    .filter(Auction.finished == finish_state)\
                                    .filter(Auction.site == 'cbid').all():
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
