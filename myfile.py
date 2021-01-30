import tensorflow.compat.v1 as tf
import random
import os
import math

validation_ratio = 0.02

def save(training_data, market_id, train_count, validation_count, max_rv):
    prefix="train-"
    train_count += len(training_data)
    return save_tfrecord(training_data, market_id, train_count, validation_count, max_rv, prefix)


def save_validation(training_data, market_id, train_count, validation_count, max_rv):
    prefix="validation-"
    validation_count += len(training_data)
    return save_tfrecord(training_data, market_id, train_count, validation_count, max_rv, prefix)


def save_tfrecord(training_data, market_id, train_count, validation_count, max_rv, prefix):
    path = "Output"
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
    file_name = "Output/" + prefix + str(math.floor(max_rv)) + "_" + market_id +".tfrecord"
    tfwriter = tf.python_io.TFRecordWriter(file_name,
                                           options=tf.python_io.TFRecordOptions(
                                               tf.python_io.TFRecordCompressionType.ZLIB))
    for training_sample in training_data:

        example = tf.train.Example(features=tf.train.Features(feature={
            "max_prices": tf.train.Feature(float_list=tf.train.FloatList(value=list(map(float,training_sample["max_prices"])))),
            "min_prices": tf.train.Feature(float_list=tf.train.FloatList(value=list(map(float,training_sample["min_prices"])))),
            "c_prices": tf.train.Feature(float_list=tf.train.FloatList(value=list(map(float,training_sample["c_prices"])))),
            #"label": tf.train.Feature(float_list=tf.train.FloatList(value=list(map(float,training_sample["label"])))),
            "label": tf.train.Feature(int64_list=tf.train.Int64List(value=training_sample["label"])),
        }))

        tfwriter.write(example.SerializeToString())

    tfwriter.close()
    return train_count, validation_count
