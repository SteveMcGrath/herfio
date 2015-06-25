import logging, os

logging.basicConfig(
    filename=os.path.join(os.path.abspath(os.path.dirname(__file__)),'bidparser.log'), 
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)

import cigar_auctioneer
import cbid

parsers = {
#    'cigarauctioneer': cigar_auctioneer.Parser(),
    'cbid': cbid.Parser(),
}