import tensorflow as tf
import numpy as np

def download_images():
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

    train_images = train_images.reshape(train_images.shape[0], 28, 28, 1).astype('float32')
    test_images = test_images.reshape(test_images.shape[0], 28, 28, 1).astype('float32')
    return (train_images, train_labels), (test_images, test_labels)

def normalize(train_images, test_images):
    # Normalizing the images to the range of [0., 1.]
    train_images /= 255.
    test_images /= 255.
    return train_images, test_images

def add_gaussian_noise(X, mean=0, std=1):
    """Returns a copy of X with Gaussian noise."""
    return X.copy() + std * np.random.standard_normal(X.shape) + mean

def load_dataset(ae_type, batch_size=1000):
    (train_images, train_labels), (test_images, test_labels) = download_images()

    # If using Denoising AE, add noise to train data
    if ae_type == "DAE":
        train_images = add_gaussian_noise(train_images)
    train_images, test_images = normalize(train_images, test_images)

    TRAIN_BUF = 60000
    TEST_BUF = 10000

    BATCH_SIZE = batch_size

    train_dataset_image = tf.data.Dataset.from_tensor_slices(train_images).batch(BATCH_SIZE)
    train_dataset_label = tf.data.Dataset.from_tensor_slices(train_labels).batch(BATCH_SIZE)
    train_dataset = tf.data.Dataset.zip((train_dataset_image, train_dataset_label)).shuffle(TRAIN_BUF)

    test_dataset_image = tf.data.Dataset.from_tensor_slices(test_images).batch(BATCH_SIZE)
    test_dataset_label = tf.data.Dataset.from_tensor_slices(test_labels).batch(BATCH_SIZE)
    test_dataset = tf.data.Dataset.zip((test_dataset_image, test_dataset_label)).shuffle(TEST_BUF)

    return train_dataset, test_dataset
