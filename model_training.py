import os
from typing import Tuple
import re
import string
import numpy as np
import util.config_loader as cfg
import tensorflow as tf
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from tensorflow.keras import layers
from tensorflow.keras import losses


batch_size = cfg.get_int('batch_size')
seed = cfg.get_int('seed')
max_features = cfg.get_int('max_features')
sequence_length = cfg.get_int('sequence_length')
embedding_dim = cfg.get_int('embedding_dim')
epoches = cfg.get_int('epoches')


def get_raw_dataset(url: str) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
    if 'train' not in os.listdir(url) or 'test' not in os.listdir(url):
        raise Exception('Dataset not found!')

    raw_train_ds = tf.keras.preprocessing.text_dataset_from_directory(os.path.join(url, 'train'),
                                                                      batch_size=batch_size,
                                                                      validation_split=0.2,
                                                                      subset='training',
                                                                      seed=seed)

    raw_val_ds = tf.keras.preprocessing.text_dataset_from_directory(os.path.join(url, 'train'),
                                                                    batch_size=batch_size,
                                                                    validation_split=0.2,
                                                                    subset='validation',
                                                                    seed=seed)

    raw_test_ds = tf.keras.preprocessing.text_dataset_from_directory(os.path.join(url, 'test'),
                                                                     batch_size=batch_size,
                                                                     seed=seed)

    return raw_train_ds, raw_val_ds, raw_test_ds


def custom_standardization(input_data):
    lowercase = tf.strings.lower(input_data)
    return tf.strings.regex_replace(lowercase,
                                    '[%s]' % re.escape(string.punctuation),
                                    '')


def prepare_data(raw_train_ds, raw_val_ds, raw_test_ds):
    vectorize_layer = TextVectorization(
        standardize=custom_standardization,
        max_tokens=max_features,
        output_mode='int',
        output_sequence_length=sequence_length)

    train_text = raw_train_ds.map(lambda x, y: x)
    vectorize_layer.adapt(train_text)

    def vectorize_text(text, label):
        text = tf.expand_dims(text, -1)
        return vectorize_layer(text), label

    train_ds = raw_train_ds.map(vectorize_text)
    val_ds = raw_val_ds.map(vectorize_text)
    test_ds = raw_test_ds.map(vectorize_text)

    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, test_ds, vectorize_layer


def prepare_model(class_count):
    model = tf.keras.Sequential([
        layers.Embedding(max_features + 1, embedding_dim),
        layers.Dropout(0.2),
        layers.GlobalAveragePooling1D(),
        layers.Dropout(0.2),
        layers.Dense(class_count, activation='softmax')
    ])

    model.compile(loss=losses.SparseCategoricalCrossentropy(),
                  optimizer='adam',
                  metrics=['accuracy'])

    return model


def train_model(model, train_ds, val_ds, epochs=10):
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs)

    return model


def generate_export_model(model, vectorize_layer):
    export_model = tf.keras.Sequential([
        vectorize_layer,
        model,
        layers.Activation('sigmoid')
    ])

    export_model.compile(
        loss=losses.SparseCategoricalCrossentropy(), optimizer="adam", metrics=['accuracy']
    )

    return export_model


def predict_text(model, text, raw_data):
    percentages = model.predict([text])[0]
    return raw_data.class_names[np.argmax(percentages)]


def train_and_save_model(name='model', epoches=epoches):
    raw_train_ds, raw_val_ds, raw_test_ds = get_raw_dataset(
        cfg.get('data_dir_name'))

    train_ds, val_ds, test_ds, vector_layer = prepare_data(
        raw_train_ds, raw_val_ds, raw_test_ds)

    model = prepare_model(len(raw_train_ds.class_names))

    model = train_model(model, train_ds, val_ds, epoches)

    i = 1
    while os.path.exists(os.path.join('models', "%s%d" % (name, i))):
        i += 1

    save_dir = os.path.join('models', "%s%d" % (name, i))

    model.save(save_dir)

    with open(os.path.join(save_dir, 'vocabs.txt'), 'w') as file:
        for line in vector_layer.get_vocabulary():
            file.write(line + '\n')

    with open(os.path.join(save_dir, 'class_names.txt'), 'w') as file:
        for line in raw_train_ds.class_names:
            file.write(line + '\n')

    loss, accuracy = model.evaluate(test_ds)

    print("Loss: ", loss)
    print("Accuracy: ", accuracy)

    export_model = generate_export_model(model, vector_layer)

    while True:
        text = input("Text: ")
        if text == 'q':
            exit()
        print(predict_text(export_model, text, raw_train_ds))


if __name__ == '__main__':
    train_and_save_model()
