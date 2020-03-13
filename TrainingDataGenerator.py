# AI名称：海龟一号

# 2种基础训练数据：对数k线 对数镜象k线 

#输入数据包括收盘价，最高价，最低价

# 训练数据不包括外汇（因为外汇的绝对波动和相对波动都较小），外汇只作为混合分母，但预测可以包含外汇

# 当RV>1时，生成基础训练数据

# 训练数据的混合次数 = RV^2（与外汇收盘价数据混合），外汇数据不够时可以少量重复，不会过度拟合

# 生成Tfrecord

import myconsole

myconsole.line("你好，海龟一号！")

marketcount = myconsole.readnum("请输入要训练的市场数量，0表示全部：")

mixcount = myconsole.readnum("请输入要混合的外汇市场数量，0表示全部：")

