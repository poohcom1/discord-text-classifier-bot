import os
import sys
import re
import string
import util.config_loader as cfg
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from tensorflow.keras import layers
from tensorflow.keras import losses

url = cfg.get('data_dir_name')
batch_size = cfg.get_int('batch_size')
seed = cfg.get_int('seed')
max_features = cfg.get_int('max_features')
sequence_length = cfg.get_int('sequence_length')
embedding_dim = cfg.get_int('embedding_dim')
epoches = cfg.get_int('epoches')


def load_model(model_name):
    print('Loading %s' % (model_name))

    model = tf.keras.models.load_model(os.path.join('models', model_name))

    def custom_standardization(input_data):
        lowercase = tf.strings.lower(input_data)
        return tf.strings.regex_replace(lowercase,
                                        '[%s]' % re.escape(string.punctuation),
                                        '')

    vectorize_layer = TextVectorization(
        standardize=custom_standardization,
        max_tokens=max_features,
        output_mode='int',
        output_sequence_length=sequence_length)

    vocab = []
    with open(os.path.join('models', model_name, 'vocabs.txt'), 'r') as file:
        for line in file.readlines():
            vocab.append(line.replace('\n', ''))

    class_names = []
    with open(os.path.join('models', model_name, 'class_names.txt'), 'r') as file:
        for line in file.readlines():
            class_names.append(int(line.replace('\n', '')))

    vectorize_layer.set_vocabulary(vocab)

    export_model = tf.keras.Sequential([
        vectorize_layer,
        model,
        layers.Activation('sigmoid')
    ])

    export_model.compile(
        loss=losses.SparseCategoricalCrossentropy(), optimizer="adam", metrics=['accuracy']
    )

    return export_model, class_names


def predict(text, model, class_names):
    percentages = model.predict([text])[0]

    # print(percentages)
    return class_names[np.argmax(percentages)]


if __name__ == '__main__':
    model, names = load_model(sys.argv[1])

    while True:
        print(predict(input("Text: "), model, names))
