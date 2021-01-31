import mypsw
import myconsole
import datetime
import time
import re
import requests
import mysql.connector
import math

split_date_min_str = '2019-11-16'
split_date_max_str = '2020-6-28'

def connector():
    try:
        myconnector = mysql.connector.connect(host=mypsw.host, 
            user=mypsw.user, 
            passwd=mypsw.passwd, 
            database=mypsw.database, 
            auth_plugin='mysql_native_password'
            )
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
    symbol_list = [
       #'"1057391"', #BTC
       #'"1061445"', #LTC
       #'"1057392"', #XRP
       '"1068308"', #XRP/BTC
       ]
    myconnector, mycursor = connector()
    if myconnector:
        statement = 'select SYMBOL, max(SYMBOL_ALIAS) from symbol_alias ' \
        'where symbol in ( ' + ','.join(symbol_list) + ' ) and ' \
        'market_type <> "外汇" group by symbol order by rand() ' \
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
                            ' and date < "' + split_date_max_str +  '" order by date'
        mycursor.execute(statement)
        try:
            dbresults = mycursor.fetchall()
        except Exception as e:
            print("数据库连接失败！" + str(e))
            return None
        for dbresult in dbresults:
            market.append({"date":dbresult[0], "o":dbresult[1], "h":dbresult[2], "l":dbresult[3], "c":dbresult[4]})
    marketlen = len(market)
    print("len = " + str(marketlen))
    price_index1 = 0
    price_index2 = 1
    price_index3 = 2
    for price_index1 in range(marketlen-2):
        price_index2 = price_index1 + 1
        price_index3 = price_index2 + 1
        if price_index3 >= marketlen:
            break
        close1 = market[price_index1]["c"]
        close2 = market[price_index2]["c"]
        close3 = market[price_index3]["c"]
        open2 = market[price_index2]["o"]
        open3 = market[price_index3]["o"]
        gap12 = max(close1,open2) / min(close1,open2) - 1
        gap23 = max(close2,open3) / min(close2,open3) - 1
        gap13 = max(close1,open3) / min(close1,open3) - 1
        ratio12 = max(close1,close2) / min(close1,close2) - 1
        ratio13 = max(close1,close3) / min(close1,close3) - 1
        if (gap12 > gap13 and gap23 > gap13) or ratio12 > (ratio13 * 10):
            market.remove(market[price_index2])
            marketlen -= 1
    return market

def load_varlidation_market(market_id):
    market = []
    myconnector, mycursor = connector()
    if myconnector:
        statement = 'SELECT date, o, h, l, c FROM pricehistory WHERE c > 0.0 and l > 0.0 and h > 0.0 and o > 0.0 and SYMBOL = "' + market_id + '" ' \
                            ' and date > "' + split_date_min_str +  '" order by date'
        mycursor.execute(statement)
        try:
            dbresults = mycursor.fetchall()
        except Exception as e:
            print("数据库连接失败！" + str(e))
            return None
        for dbresult in dbresults:
            market.append({"date":dbresult[0], "o":dbresult[1], "h":dbresult[2], "l":dbresult[3], "c":dbresult[4]})
    marketlen = len(market)
    print("len = " + str(marketlen))
    price_index1 = 0
    price_index2 = 1
    price_index3 = 2
    for price_index1 in range(marketlen-2):
        price_index2 = price_index1 + 1
        price_index3 = price_index2 + 1
        if price_index3 >= marketlen:
            break
        close1 = market[price_index1]["c"]
        close2 = market[price_index2]["c"]
        close3 = market[price_index3]["c"]
        open2 = market[price_index2]["o"]
        open3 = market[price_index3]["o"]
        gap12 = max(close1,open2) / min(close1,open2) - 1
        gap23 = max(close2,open3) / min(close2,open3) - 1
        gap13 = max(close1,open3) / min(close1,open3) - 1
        ratio12 = max(close1,close2) / min(close1,close2) - 1
        ratio13 = max(close1,close3) / min(close1,close3) - 1
        if (gap12 > gap13 and gap23 > gap13) or ratio12 > (ratio13 * 10):
            market.remove(market[price_index2])
            marketlen -= 1
    return market

def get_training_price_live(pairId):
    is_currency = False
    startdate = datetime.datetime.strptime('2010-1-1', '%Y-%m-%d')
    enddate = datetime.datetime.strptime(split_date_max_str, '%Y-%m-%d')
    return get_history_price(pairId, is_currency, startdate, enddate)

def get_validation_price_live(pairId):
    is_currency = False
    startdate = datetime.datetime.strptime(split_date_min_str, '%Y-%m-%d')
    enddate = datetime.datetime.strptime('2021-12-31', '%Y-%m-%d')
    return get_history_price(pairId, is_currency, startdate, enddate)

def get_history_price(pairId, is_currency, startdate, enddate):
    marketList = []
    priceList = []
    if is_currency:
        smlID_str = '1072600'
    else:
        smlID_str = '25609849'

    url = "https://cn.investing.com/instruments/HistoricalDataAjax"

    headers = {
        'accept': "text/plain, */*; q=0.01",
        'origin': "https://cn.investing.com",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'postman-token': "17db1643-3ef6-fa9e-157b-9d5058f391e4"
        }
    #st_date_str = (datetime.datetime.utcnow() + datetime.timedelta(days = -startdays)).strftime(dateformat).replace("-","%2F")
    #end_date_str = (datetime.datetime.utcnow()).strftime(dateformat).replace("-","%2F")
    st_date_str = startdate.strftime("%Y-%m-%d").replace("-","%2F")
    end_date_str = enddate.strftime("%Y-%m-%d").replace("-","%2F")
    payload = "action=historical_data&curr_id="+ pairId +"&end_date=" + end_date_str + "&header=null&interval_sec=Daily&smlID=" + smlID_str + "&sort_col=date&sort_ord=DESC&st_date=" + st_date_str
    try:
        response = requests.request("POST", url, data=payload, headers=headers, verify=False, timeout=40)
    except Exception as e:
        time.sleep(7)
    if response == None:
        pass
    table_pattern = r'<tr>.+?<td.+?data-real-value="([^><"]+?)".+?</td>' \
            '.+?data-real-value="([^><"]+?)".+?</td>.+?data-real-value="([^><"]+?)".+?</td>'  \
            '.+?data-real-value="([^><"]+?)".+?</td>.+?data-real-value="([^><"]+?)".+?</td>'  \
            '.+?</tr>'
    row_matchs = re.finditer(table_pattern,response.text,re.S)
    timestamp_list = []
    price_list = []
    openprice_list = []
    highprice_list = []
    lowprice_list = []
    price_count = 0
    insert_val = []
    #print(str(response.text))
    lastclose = -1
    for cell_matchs in row_matchs:
        price_count += 1
        #print(str(cell_matchs.group(0)))
        timestamp = int(str(cell_matchs.group(1)))
        price = float(str(cell_matchs.group(2)).replace(",",""))
        openprice = float(str(cell_matchs.group(3)).replace(",",""))
        highprice = float(str(cell_matchs.group(4)).replace(",",""))
        lowprice = float(str(cell_matchs.group(5)).replace(",",""))
        #if price_count == 1 or price != price_list[price_count-2]:
        if price > 0 and openprice > 0 and highprice > 0 and lowprice > 0 and (highprice != lastclose or lowprice != lastclose):
            timestamp_list.append(timestamp)
            price_list.append(price)
            openprice_list.append(openprice)
            highprice_list.append(highprice)
            lowprice_list.append(lowprice)
        lastclose = price
    marketList = [ {"date":datetime.datetime.fromtimestamp(timestamp_list[i]), "o":openprice_list[i], "h":highprice_list[i], "l":lowprice_list[i], "c":price_list[i]} for i in range(len(timestamp_list)-1,-1,-1) ]
    #return timestamp_list, price_list, openprice_list, highprice_list, lowprice_list
    return marketList
