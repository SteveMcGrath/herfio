import logging, os

try:
    logging.basicConfig(
        filename='/var/log/bidparser.log', 
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s]: %(message)s'
    )
except IOError:
    logging.basicConfig(
        filename='bidparser.log', 
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s]: %(message)s'
    ) 

import cigar_auctioneer
import cigarmonster
import cbid

parsers = {
    'cigarauctioneer': cigar_auctioneer.Parser(),
    'cbid': cbid.Parser(),
    'cigarmonster': cigarmonster.Parser(),
}