import mypsw
import myconsole
import mysql.connector

def connector():
    try:
        myconnector = mysql.connector.connect(host=mypsw.host, 
            user=mypsw.user, 
            passwd=mypsw.passwd, 
            database=mypsw.database, 
            auth_plugin='mysql_native_password')
        mycursor = myconnector.cursor()
    except Exception as e:
        myconsole.out(str(e))
        return None,None
    return myconnector, mycursor

def get_market_count():
    myconnector, mycursor = connector()
    if myconnector:
        statement =    'SELECT count(DISTINCT symbol) as market_count FROM symbol_alias where MARKET_TYPE <> "外汇" ' \
                                'union ' \
                                'SELECT count(DISTINCT symbol) as market_count FROM symbol_alias where MARKET_TYPE = "外汇"'
        mycursor.execute(statement)
        dbresults = mycursor.fetchall()
        if len(dbresults) == 2:
            return int(dbresults[0][0]), int(dbresults[1][0])
    return 0, 0

def load_market_list(training_market_count):
    market_list = {}
    myconnector, mycursor = connector()
    if myconnector:
        statement = 'select SYMBOL, max(SYMBOL_ALIAS) from symbol_alias ' \
        'where market_type <> "外汇" group by symbol order by rand() ' \
        'limit ' + str(training_market_count)
        mycursor.execute(statement)
        dbresults = mycursor.fetchall()
        for dbresult in dbresults:
            market_list[dbresult[0]] = dbresult[1]
    return market_list

def load_currency_markets(training_currency_count):
    currency_markets = {}
    myconnector, mycursor = connector()
    if myconnector:
        statement = 'SELECT symbol, date, c FROM pricehistory WHERE  c > 0.0 and SYMBOL IN (SELECT t.symbol FROM ( ' \
                            'select DISTINCT symbol from symbol_alias where MARKET_TYPE = "外汇" limit ' + str(training_currency_count) + ' ' \
                            ') as t) order by symbol, date'
        mycursor.execute(statement)
        dbresults = mycursor.fetchall()
        for dbresult in dbresults:
            if dbresult[0] not in currency_markets:
                currency_markets[dbresult[0]] = []
            currency_markets[dbresult[0]].append({"date":dbresult[1], "c":dbresult[2]})
    return currency_markets

def load_market(market_id):
    market = []
    myconnector, mycursor = connector()
    if myconnector:
        statement = 'SELECT date, o, h, l, c FROM pricehistory WHERE c > 0.0 and l > 0.0 and h > 0.0 and o > 0.0 and SYMBOL = "' + market_id + '" ' \
                            'order by date'
        mycursor.execute(statement)
        dbresults = mycursor.fetchall()
        for dbresult in dbresults:
            market.append({"date":dbresult[0], "o":dbresult[1], "h":dbresult[2], "l":dbresult[3], "c":dbresult[4]})
    return market