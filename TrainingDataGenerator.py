# AI名称：海龟一号

# 2种基础训练数据：对数k线 对数镜象k线 

#输入数据包括收盘价，最高价，最低价

# 训练数据不包括外汇（因为外汇的绝对波动和相对波动都较小），外汇只作为混合分母，但预测可以包含外汇

# 当相对波动RV>1时，生成基础训练数据

# 训练数据的混合次数 = RV^2（与外汇收盘价数据混合），外汇数据不够时可以少量重复，不会过度拟合
# 生成Tfrecord

import myconsole #这是控制台IO的相关代码
import mydb #这是数据库处理的相关代码
import myfile #这是tfrecord文件保存的相关代码

myconsole.out("你好，我是海龟一号！现在就开始生成全世界最好的训练数据吧！")
myconsole.out("正在统计全球市场信息……")
market_total, currency_total = mydb.get_market_count()
training_market_count = myconsole.read_num("请输入要训练的市场数量，总计" + str(market_total) + "个市场：")
training_currency_count = myconsole.read_num("请输入要混合的外汇市场数量，总计" + str(currency_total) + "个外汇市场：")
myconsole.out("正在载入训练市场清单……")
market_list = mydb.load_market_list(training_market_count)
myconsole.out("正在载入外汇市场数据……")
currency_markets = mydb.load_currency_markets(training_currency_count)

for market in market_list:
    myconsole.out("正在载入市场" + market["name"] + "的数据……")
    training_market = mydb.load_market(market["id"])
    myconsole.out("正在生成市场" + market["name"] + "的训练数据……")
    training_data = mygenerator.generate_taining_data(training_market, currency_markets)
    myconsole.out("正在保存市场" + market["name"] + "的训练数据……")
    myfile.save(training_data)
