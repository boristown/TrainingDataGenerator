import random
import math
import numpy as np
import datetime

price_input_len = 120

def generate_training_sample_single(max_list, min_list, c_list, rv):
    training_sample = {}
    max_log_list = [math.log(max_value) for max_value in max_list]
    min_log_list = [math.log(min_value) for min_value in min_list]
    c_log_list = [math.log(c_value) for c_value in c_list]
    max_price = max(max_log_list)
    min_price = min(min_log_list)
    price_range = max_price - min_price
    center_price = ( max_price + min_price ) / 2.0
    training_sample["max_prices"] = [(max_log_value-center_price)/price_range+0.5 for max_log_value in max_log_list][-1::-1]
    training_sample["min_prices"] = [(min_log_value-center_price)/price_range+0.5 for min_log_value in min_log_list][-1::-1]
    training_sample["c_prices"] = [(c_log_value-center_price)/price_range+0.5 for c_log_value in c_log_list][:-1][-1::-1]
    training_sample["label"] = [0.5 + math.atan(rv) / math.pi] if c_list[price_input_len] >  c_list[price_input_len - 1] else [0.5 - math.atan(rv) / math.pi]
    return training_sample

def generate_training_sample(max_list, min_list, c_list, rv):
    training_sample = generate_training_sample_single(max_list, min_list, c_list, rv)
    training_sample_mirror = generate_training_sample_single(
        [1.0 / min_value for min_value in min_list],
        [1.0 / max_value for max_value in max_list], 
        [1.0 / c_value for c_value in c_list], 
        rv
        )
    return [training_sample, training_sample_mirror]

def generate_training_mix_sample(date_list, max_list, min_list, c_list, rv, currency_market):
    currency_index = 0
    max_list_mix = [0.0] * price_input_len
    min_list_mix = [0.0] * price_input_len
    c_list_mix = [0.0] * (price_input_len + 1)
    for price_index in range(price_input_len):
        while currency_index < len(currency_market) - 1 and currency_market[currency_index]["date"] < date_list[price_index]:
            currency_index += 1
        max_list_mix[price_index] = max_list[price_index] / currency_market[currency_index]["c"]
        min_list_mix[price_index] = min_list[price_index] / currency_market[currency_index]["c"]
        c_list_mix[price_index] = c_list[price_index] / currency_market[currency_index]["c"]
    c_list_mix[price_input_len] = c_list[price_input_len] / currency_market[currency_index]["c"]
    if min(min_list) > 0:
        tr_list_mix = [max_list_mix[input_index] / min_list_mix[input_index] - 1 for input_index in range(price_input_len)]
        atr_mix = sum(tr_list_mix) / price_input_len
        volatility_mix = max(c_list_mix[price_input_len], c_list_mix[price_input_len - 1]) / min(c_list_mix[price_input_len], c_list_mix[price_input_len - 1]) - 1
        if atr_mix > 0 and volatility_mix > 0:
            rv = math.log(1 + volatility_mix, 1 + atr_mix)
    return generate_training_sample(max_list_mix, min_list_mix, c_list_mix, rv)

def generate_training_samples(sample_prices, currency_markets, max_rv):
    training_samples = []
    date_list = [sample_price["date"] for sample_price in sample_prices]
    o_list = [sample_price["o"] for sample_price in sample_prices]
    h_list = [sample_price["h"] for sample_price in sample_prices]
    l_list = [sample_price["l"] for sample_price in sample_prices]
    c_list = [sample_price["c"] for sample_price in sample_prices]

    max_time = 0   # 已知最大连续出现次数初始为0
    cur_time = 1   # 记录当前元素是第几次连续出现
    pre_element = None   # 记录上一个元素是什么
    for i in c_list:
        if i == pre_element:   # 如果当前元素和上一个元素相同,连续出现次数+1,并更新最大值
            cur_time += 1
            max_time = max((cur_time, max_time))
        else:   # 不同则刷新计数器
            pre_element = i
            cur_time = 1
            
    max_span = datetime.timedelta(days=0)   # 已知最大连续出现次数初始为0
    cur_span = 1   # 记录当前元素是第几次连续出现
    for input_index in range(price_input_len):
        cur_span = date_list[input_index+1] - date_list[input_index]
        max_span = max((cur_span, max_span))

    close_open_max = 1
    close_open_cur = 1
    for input_index in range(price_input_len):
        close_open_cur = max(c_list[input_index], o_list[input_index + 1]) / min(c_list[input_index], o_list[input_index + 1])
        close_open_max = max(close_open_cur, close_open_max)

    if max_time < 5 and max_span < datetime.timedelta(days=10) and close_open_max < 2 : #收盘价格不能连续5天相同,日期相隔不能超过10天
        last_c_list = [o_list[input_index] if input_index == 0 else c_list[input_index - 1] for input_index in range(price_input_len)]
        max_list = [max(h_list[input_index], l_list[input_index], o_list[input_index], c_list[input_index], last_c_list[input_index]) for input_index in range(price_input_len)]
        min_list = [min(h_list[input_index], l_list[input_index], o_list[input_index], c_list[input_index], last_c_list[input_index]) for input_index in range(price_input_len)]
        if min(min_list) > 0 and min(max_list) > 0:
            tr_list = [max_list[input_index] / min_list[input_index] - 1 for input_index in range(price_input_len)]
            atr = sum(tr_list) / price_input_len
            volatility = max(c_list[price_input_len], c_list[price_input_len - 1]) / min(c_list[price_input_len], c_list[price_input_len - 1]) - 1
            if atr > 0 and volatility > 0:
                rv = math.log(1 + volatility, 1 + atr)
                max_rv = max(rv, max_rv)
                if rv >= 1:
                    training_samples.extend(generate_training_sample(max_list, min_list, c_list, rv))
                    mix_count = (math.floor( rv ) ** 2) * 3 - 1
                    mix_index_list = np.random.choice(len(currency_markets), mix_count)
                    mix_key_list = list(currency_markets.keys())
                    for mix_index in mix_index_list:
                        training_samples.extend(generate_training_mix_sample(date_list, max_list, min_list, c_list, rv, currency_markets[mix_key_list[mix_index]]))
    return training_samples, max_rv

def generate_taining_data(training_market, currency_markets):
    training_data = []
    max_rv = 0
    training_total_len = len(training_market) - price_input_len
    for training_data_index in range(training_total_len):
        training_samples, max_rv = generate_training_samples(training_market[training_data_index:training_data_index+price_input_len+1], currency_markets, max_rv)
        training_data.extend(training_samples)
    random.shuffle(training_data)
    return training_data, max_rv