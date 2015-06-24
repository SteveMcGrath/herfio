def open_db_mysql():
    import MySQLdb
    print 'Opening DB connection...'
    db = MySQLdb.connect(host="**domain**.org", user="**domain**org_cb", passwd="******",db="**domain**org_cb")
    return db

def main():
    print 'Starting script...'
    db = open_db_mysql()
    cursor = db.cursor()
    cursor2 = db.cursor()
    print 'Updating compitemlist...'
    cursor.execute('TRUNCATE TABLE compitemlist')
    cursor.execute("insert into compitemlist(compitemname,compitemnum) SELECT auitem, COUNT(auitem) AS cauitem FROM compauction GROUP BY auitem ORDER BY auitem")
    print 'Updating computemtype...'
    cursor.execute('TRUNCATE TABLE compitemtype')
    cursor.execute('insert into compitemtype(compitem) SELECT autype FROM compauction GROUP BY autype ORDER BY autype')
    print 'Success'

if __name__ == '__main__':
    main()

