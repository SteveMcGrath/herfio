import logging

logging.basicConfig(
    filename='bidparser.log', 
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)

import cigar_auctioneer
import cbid

parsers = {
#    'cigarauctioneer': cigar_auctioneer.Parser(),
    'cbid': cbid.Parser(),
}