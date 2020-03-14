import random
import math
import numpy as np

training_input_len = 120

def generate_training_sample(max_list, min_list, c_list, rv):
    training_sample = None

    return training_sample

def generate_training_mix_sample(max_list, min_list, c_list, rv, currency_market):
    training_sample = None

    return training_sample

def generate_training_samples(sample_prices, currency_markets):
    training_samples = []
    o_list = [sample_price["o"] for sample_price in sample_prices]
    h_list = [sample_price["h"] for sample_price in sample_prices]
    l_list = [sample_price["l"] for sample_price in sample_prices]
    c_list = [sample_price["c"] for sample_price in sample_prices]
    last_c_list = [o_list[input_index] if input_index == 0 else c_list[input_index - 1] for input_index in range(training_input_len)]
    max_list = [max(h_list[input_index], last_c_list[input_index]) for input_index in range(training_input_len)]
    min_list = [min(l_list[input_index], last_c_list[input_index]) for input_index in range(training_input_len)]
    if min(min_list) > 0:
        tr_list = [max_list[input_index] / min_list[input_index] - 1 for input_index in range(training_input_len)]
        atr = sum(tr_list) / training_input_len
        volatility = max(c_list[training_input_len], c_list[training_input_len - 1]) / min(c_list[training_input_len], c_list[training_input_len - 1]) - 1
        if atr > 0 and volatility > 0:
            rv = math.log(1 + volatility, 1 + atr)
            if rv >= 1:
                training_samples.append(generate_training_sample(max_list, min_list, c_list, rv))
            if rv >= 2:
                mix_count = math.floor( rv ) ** 2 - 1
                mix_index_list = np.random.choice(len(currency_markets), mix_count)
                mix_key_list = currency_markets.keys()
                for mix_index in mix_index_list:
                    training_samples.append(generate_training_mix_sample(max_list, min_list, c_list, rv, currency_markets[mix_key_list[mix_index]]))
    return training_samples

def generate_taining_data(training_market, currency_markets):
    training_data = []
    training_total_len = len(training_market) - training_input_len
    for training_data_index in range(training_total_len):
        training_samples = generate_training_samples(training_market[training_data_index:training_data_index+training_input_len+1], currency_markets)
        training_data.extend(training_samples)
    random.shuffle(training_data)
    return training_data