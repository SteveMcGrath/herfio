# BidHistory

BidHistory is a cigar auction site scraper and analytics site designed
to aide people in making smart decisions in buying cigars from these
sites.

# Supported Sites

* [CigarBid](http://cigarbid.com)
* [CigarAuctioneer](http://cigarauctioneer.com)
* [CigarMonster](http://cigarmonster.com)

# API

As was requested, support has been added to return the information
as a JSON dictionary instead of as the HTML file that is default.
In order to force the site to return JSON, it's simply a matter of
setting the HTTP Header: "Content-Type: application/json" to get
JSON data returned.  The following fields are available for backend
parsing:

* ***full_search*** - This overrides the default search behavior of
					  searching for each word and will instead search
					  for the entire string defined in this query
					  parameter instead of the default URL path.
* ***site*** - The site query parameter allows the caller to limit
			   the results of the response to a specific auction site's
			   information.