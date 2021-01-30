# AI名称：海龟Ⅹ

# 2种基础训练数据：对数k线 对数镜象k线 

#输入数据包括收盘价，最高价，最低价

# 训练数据不包括外汇（因为外汇的绝对波动和相对波动都较小），外汇只作为混合分母，但预测可以包含外汇

# 当相对波动RV>0.5时，生成基础训练数据

# 训练数据的混合次数 = RV^2（与外汇收盘价数据混合），外汇数据不够时可以少量重复，不会过度拟合
# 生成Tfrecord

#海龟8号AI升级计划

#算命猫  AI纪元 
#过去和未来并不存在一条清晰的界线，未来也是完整历史的一部分，而历史总是在不断重复。
#从理论上讲：只要AI学习了过去全部的历史数据，它就能够在某种程度上具备预测未来的能力。

#目前已经采集了全球近万个市场的数据（包括个股、加密货币、外汇、全球股指、商品期货），但还不够，数据还需要更加完善。特别是需要更新加密货币的市场清单，所有已知币种的K线信息都需要采集。
#从海龟7号的经验来看，无论是增加神经网络的层级（从海龟6号的169层增加到海龟号的201层）还是延长训练时间（从海龟6号的2小时延长到海龟7号的25小时）都已经无法提高准确率了——必须增加输入的信息量。
#具体来讲，需要将神经网络的历史价格输入由120天的收盘价、最高价、最低价（12*10*3），提升为225天（15*15*3），正方形的输入可以方便卷积运算，更多的信息量为更高的准确率提供了可能性。
#训练数据的加权算法也需要修改：
#按ATR/2的止损点，计算每种K线形态的止损收益；数据权重=int((收益*2/ATR)^2)。
#最后，使用0与1的标签标记训练数据集，(0,1)表示做多，(1,0)表示做空。
#准备开始训练。

import myconsole #这是控制台IO的相关代码
import mydb #这是数据库处理的相关代码
import myfile #这是tfrecord文件保存的相关代码
import mygenerator #这是训练数据生成器的相关代码

myconsole.out("您好，即将生成海龟X的训练数据。采用渐进式的训练方案，首次训练使用BTC一个市场，通过N轮扩展，增加到2^N个市场，使用最后两个月的数据为验证级。")
myconsole.out("正在统计全球市场信息……")
market_total, currency_total = mydb.get_market_count()
training_market_count = myconsole.in_num("请输入要训练的市场数量，总计" + str(market_total) + "个市场：")
training_currency_count = myconsole.in_num("请输入要混合的外汇市场数量，总计" + str(currency_total) + "个外汇市场：") 
myconsole.out("正在载入训练市场清单……")
market_list = mydb.load_market_list(training_market_count)
myconsole.out("正在载入外汇市场数据……")
currency_markets = mydb.load_currency_markets(training_currency_count)

train_count = 0
validation_count = 0

market_index = 0

for (market_id,market_name) in market_list.items():
    market_index += 1
    myconsole.out("正在载入市场" + market_name + "的数据……" + str(market_index) + "/" + str(training_market_count))
    training_market = None
    while training_market is None:
        training_market = mydb.load_market(market_id)
        validation_market = mydb.load_varlidation_market(market_id)
    myconsole.out("正在生成市场" + market_name + "的训练数据……")
    training_data, max_rv = mygenerator.generate_taining_data(training_market, currency_markets)
    #if max_rv < 1:
    #    continue
    myconsole.out("正在保存市场" + market_name + "的训练数据……")
    train_count, validation_count = myfile.save(training_data, market_id, train_count, validation_count, max_rv)
    myconsole.out("正在生成市场" + market_name + "的验证数据……")
    validation_data, max_rv = mygenerator.generate_taining_data(validation_market, currency_markets)
    myconsole.out("正在保存市场" + market_name + "的验证数据……")
    train_count, validation_count = myfile.save_validation(training_data, market_id, train_count, validation_count, max_rv)
    myconsole.out("训练集：" + str(train_count) + "/验证集：" + str(validation_count))
