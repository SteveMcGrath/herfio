print 'Starting script...'
import urllib,urllib2,re,MySQLdb,time,datetime
from datetime import date
def open_db_mysql():
    print 'Opening DB connection...'
    db = MySQLdb.connect(host="**domain**.org", user="**domain**org_cb", passwd="*******",db="**domain**org_cb")
    return db

def main():
    db = open_db_mysql()
    print 'Getting URL...'
    req = urllib2.Request('http://www.cigarbid.com/Auction/ClosingToday/?BonusBuyOnly=False&IsCatPage=False&AuctionFilters=&CategoryFilters=&SortOrder=relevance&ViewType=&SpecialSearchDisplay=Lots%20Closing%20Today&SpecialSearch=True&keyword=CLOSINGTODAY&PageSize=10000')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    print 'Compiling result...'
    match=re.compile('<tr(.+?)/">(.+?)</a><br /><span>(.+?)</span></td><td class="cb_product_qty">(.+?)<(.+?)cb_lot_price_(.+?)">(.+?)<(.+?)timeleft(.+?)Recently Closed(.+?)">(.+?)<(.+?)').findall(link)
    print 'Looping results...'
    i = 0
    x = 0
    maxrecordsadded = 2000
    maxrecordsprocessed = 5000
    for fill1,auitem,autype,auquant,fill2,aulotid,aubid,fill3,timeleft,fill4,closedatetime,fill5 in match:
        aulotid = aulotid.replace("'","").replace('"','')
        if (scrapeauction(aulotid,db) == 1):
            i = i + 1
            x = x + 1
        else:
            i = i + 1
        if ((i > maxrecordsprocessed) or (x > maxrecordsadded)):
            print 'max hit...'
            break
    print "Processed " + str(i) + " records."
    print "Added " + str(x) + " records."
    db.close()
    f = open('cbid_clsau_new_log.txt','a')
    f.write(str(datetime.datetime.now()) + ' : ' + str(i) + ' Processed, ' + str(x) + ' Added\n')
    f.close()
    print "Success."

def scrapeauction(lotid,db):
        i = lotid
        cursor = db.cursor()
        cursor.execute("SELECT aulotid from compauction where aulotid=" + str(lotid))
        if (cursor.rowcount > 0):
            print 'Lot #' + str(i) + ' bypassed, already in db.'
            return 0
        print 'Getting URL for ' + str(i) + '...'
        req = urllib2.Request('http://www.cigarbid.com/Auction/Lot/' + str(i))
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        db_type = 'mysql'
        z = 0
        #if (link.find("Auction Closed") > 0) and (link.find("Free Fall:") < 1) and (link.find("Bought out with QuickBuy") < 1) and (link.find("No Bids Yet") < 1):
        if (link.find("Auction Closed") > 0) and (link.find("Free Fall:") < 1) and (link.find("No Bids Yet") < 1):
            print 'Valid closed auction found : ' + str(i) + '...'
            
            link = link.replace('"','').replace("'","").replace('\n','')
            if (link.find("Bought out with QuickBuy") < 1):
                match=re.compile('lot_title_line_one>(.+?): (.+?)<(.+?)Closing Bid to Win:(.+?)<(.+?)Qty Available:</td><td>(.+?)<(.+?)Closes on (.+?)<(.+?)lot_winning_bids_box(.+?)lot_winners_toolbox').findall(link)
            else:
                match=re.compile('lot_title_line_one>(.+?): (.+?)<(.+?)Bought out with QuickBuy(.+?)<(.+?)Qty Available:</td><td>(.+?)<(.+?)Closes on (.+?)<(.+?)lot_winning_bids_box(.+?)lot_winners_toolbox').findall(link)
            for autype,auitem,fill1,aubid,fill2,auquant,fill3,closedatetime,fill4,winners in match:
                #f= open('cbid_clsau_new_exlog.txt','a')
                #f.write(str(i) + ' winners:' + winners + '\n')
                #f.close()
                tdatetime = time.strptime(closedatetime, '%b %d, %Y %I:%M %p')
                auclosetime = time.strftime('%H:%M',tdatetime)
                auclosedate = time.strftime('%Y-%m-%d',tdatetime)
                auclosedatetime = closedatetime.replace("'","").replace('"','')
                aulotid = str(i)
                auitem = auitem.replace("'","").replace('"','').strip()
                autype = autype.replace("'","").replace('"','')
                auquant = int(auquant.replace("'","").replace('"',''))
                if (link.find("Bought out with QuickBuy") < 1):
                    aubid = float(aubid.replace("'","").replace('"','').replace('$',''))
                else:
                    aubid = ''
                winners = winners.replace('"','').replace("'","").replace('\n','')
                wmatch=re.compile('lot_units>(.+?)unit(.+?)lot_winning_bid>(.+?)ea').findall(winners) #bids
                n = len(link) - link.rfind('QuickBuys')
                qbwin = link[-n:]
                wmatch2=re.compile('lot_winning_bid>\$(.+?)ea(.+?)lot_units>(.+?)unit').findall(qbwin) #quickbuys
                for numunits,fill1,bid in wmatch: #bids
                    if ((numunits.find('>') > 0) or (bid.find('>') > 0)): #quickbuys
                        print 'quickbuy bypassed in bid area'
                    else: #bids
                        numunits = numunits.replace(' ','')
                        bid = bid.replace('/','').replace('$','')
                        aubuytype = 'bid'
                        if db_type == 'mysql':
                            z = 0
                            while int(numunits) > z:
                                #curRes = cursor.execute("INSERT INTO compauction(auitem,autype,auquant,aubid,aubuytype,auclosedate,auclosetime,auclosedatetime,aulotid,updatedatetime) values ('" + auitem + "','" + autype + "'," + str(numunits) + "," + str(bid) + ",'" + aubuytype + "','" + auclosedate + "','" + auclosetime + "','" + auclosedatetime + "','" + aulotid + "',now())")
                                curRes = cursor.execute("INSERT INTO compauction(auitem,autype,auquant,aubid,aubuytype,auclosedate,auclosetime,auclosedatetime,aulotid,updatedatetime) values ('" + auitem + "','" + autype + "'," + str(1) + "," + str(bid) + ",'" + aubuytype + "','" + auclosedate + "','" + auclosetime + "','" + auclosedatetime + "','" + aulotid + "',now())")
                                z = z + 1
                        else:
                            curRes = cursor.execute("INSERT INTO compauction(auitem,autype,auquant,aubid,aubuytype,auclosedate,auclosetime,auclosedatetime,aulotid,updatedatetime) values ('" + auitem + "','" + autype + "'," + str(numunits) + "," + str(bid) + ",'" + aubuytype + "','" + auclosedate + "','" + auclosetime + "','" + auclosedatetime + "','" + aulotid + "','now')")
                            curRes = curRes.rowcount
                        if curRes == 1:
                            print 'added item: ' + auitem + ' - ' + str(auquant) + ' - ' + aubuytype
                            db.commit()
                        elif curRes == 0:
                            print 'error adding item: ' + auitem + ' - ' + str(auquant)
                for qbid,fill1,numunits in wmatch2: #quickbuys
                    if ((numunits.find('>') > 0) or (qbid.find('>') > 0) or (link.find('QuickBuys') < 1)): #bid
                        print 'bid bypassed in quickbuy area'
                        #print 'numunits: '
                        #print numunits 
                        #print 'qbid: '
                        #print qbid
                    else: #quickbuy
                        numunits = numunits.replace(' ','')
                        qbid = qbid.replace('/','').replace('$','')
                        aubuytype = 'quickbuy'
                        if db_type == 'mysql':
                            z = 0
                            while int(numunits) > z:
                                #curRes = cursor.execute("INSERT INTO compauction(auitem,autype,auquant,aubid,aubuytype,auclosedate,auclosetime,auclosedatetime,aulotid,updatedatetime) values ('" + auitem + "','" + autype + "'," + str(numunits) + "," + str(qbid) + ",'" + aubuytype + "','" + auclosedate + "','" + auclosetime + "','" + auclosedatetime + "','" + aulotid + "',now())")
                                curRes = cursor.execute("INSERT INTO compauction(auitem,autype,auquant,aubid,aubuytype,auclosedate,auclosetime,auclosedatetime,aulotid,updatedatetime) values ('" + auitem + "','" + autype + "'," + str(1) + "," + str(qbid) + ",'" + aubuytype + "','" + auclosedate + "','" + auclosetime + "','" + auclosedatetime + "','" + aulotid + "',now())")
                                z = z + 1
                        else:
                            curRes = cursor.execute("INSERT INTO compauction(auitem,autype,auquant,aubid,aubuytype,auclosedate,auclosetime,auclosedatetime,aulotid,updatedatetime) values ('" + auitem + "','" + autype + "'," + str(numunits) + "," + str(qbid) + ",'" + aubuytype + "','" + auclosedate + "','" + auclosetime + "','" + auclosedatetime + "','" + aulotid + "','now')")
                            curRes = curRes.rowcount
                        if curRes == 1:
                            print 'added item: ' + auitem + ' - ' + str(auquant) + ' - ' + aubuytype
                            db.commit()
                        elif curRes == 0:
                            print 'error adding item: ' + auitem + ' - ' + str(auquant)

        else:
            print 'Invalid closed auction found : ' + str(i) + '...'
            return 0
        cursor.close()
        if (z > 0):
            return 1
        else:
            return 0
    
if __name__ == '__main__':
    main()
