import os
from typing import Tuple
import util.config_loader as cfg
import tensorflow as tf
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from tensorflow.keras import layers
from tensorflow.keras import losses


batch_size = 32
seed = 42
max_features = 10000
sequence_length = 250
embedding_dim = 64


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
                                                                    subset='training',
                                                                    seed=seed)

    raw_test_ds = tf.keras.preprocessing.text_dataset_from_directory(os.path.join(url, 'test'),
                                                                     batch_size=batch_size,
                                                                     seed=seed)

    return raw_train_ds, raw_val_ds, raw_test_ds


def custom_standardization(input):
    return input


def prepare_data(raw_train_ds, raw_val_ds, raw_test_ds):
    vectorize_layer = TextVectorization(
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
        layers.Dense(class_count)
    ])

    model.compile(loss=losses.SparseCategoricalCrossentropy(from_logits=True),
                  optimizer='adam',
                  metrics=['accuracy'])

    return model


def train_model(model, train_ds, val_ds, epochs=10):
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs)

    return model


if __name__ == '__main__':
    raw_train_ds, raw_val_ds, raw_test_ds = get_raw_dataset(
        cfg.get('data_dir_name'))

    train_ds, val_ds, test_ds, vector_layer = prepare_data(
        raw_train_ds, raw_val_ds, raw_test_ds)

    model = prepare_model(len(raw_train_ds.class_names))

    model = train_model(model, train_ds, val_ds)

    loss, accuracy = model.evaluate(test_ds)

    print("Loss: ", loss)
    print("Accuracy: ", accuracy)
