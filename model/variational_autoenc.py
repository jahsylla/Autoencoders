# Some of codes referred to tensorflow 2.0 official tutorial for VAE
import tensorflow as tf
from tensorflow.keras.layers import InputLayer, Conv2D, Flatten, Dense, Conv2DTranspose, Reshape


class VAE(tf.keras.Model):
    def __init__(self, latent_dim: int, net_type: str='simple'):
        super(VAE, self).__init__()
        self.latent_dim = latent_dim
        assert net_type in ['simple', 'conv']
        if net_type == "simple":
            self.inference_net = tf.keras.Sequential([
                InputLayer(input_shape=[28, 28, 1]),
                Flatten(),
                Dense(128, activation='relu'),
                Dense(64, activation='relu'),
                Dense(self.latent_dim * 2),    # [means, stds]
            ])
            self.generative_net = tf.keras.Sequential([
                InputLayer(input_shape=[self.latent_dim]),
                Dense(64, activation='relu'),
                Dense(128, activation='relu'),
                Dense(28 * 28 * 1),
                Reshape(target_shape=[28, 28, 1]),
            ])
        if net_type == "conv":
            self.inference_net = tf.keras.Sequential([
                InputLayer(input_shape=[28, 28, 1]),
                Conv2D(filters=32, kernel_size=3, strides=(2, 2), activation='relu'),
                Conv2D(filters=64, kernel_size=3, strides=(2, 2), activation='relu'),
                Flatten(),
                Dense(256, activation='relu'),
                # No activation
                Dense(self.latent_dim * 2),  # [means, stds]
            ])
            self.generative_net = tf.keras.Sequential([
                InputLayer(input_shape=[self.latent_dim]),
                Dense(256, activation='relu'),
                Dense(7 * 7 * 32, activation='relu'),
                Reshape(target_shape=(7, 7, 32)),
                Conv2DTranspose(
                    filters=64,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="SAME",
                    activation='relu'),
                Conv2DTranspose(
                    filters=32,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="SAME",
                    activation='relu'),
                # No activation
                Conv2DTranspose(
                    filters=1, kernel_size=3, strides=(1, 1), padding="SAME"),
            ])

    def encode(self, x):
        mean_logvar = self.inference_net(x)
        N = mean_logvar.shape[0]
        mean = tf.slice(mean_logvar, [0, 0], [N, self.latent_dim])
        logvar = tf.slice(mean_logvar, [0, self.latent_dim], [N, self.latent_dim])
        return mean, logvar

    def decode(self, z, apply_sigmoid=False):
        logits = self.generative_net(z)
        if apply_sigmoid:
            probs = tf.sigmoid(logits)
            return probs
        return logits


class CVAE(tf.keras.Model):
    def __init__(self, latent_dim: int, net_type: str='simple'):
        super(CVAE, self).__init__()
        
        self.latent_dim = latent_dim
        self.num_classes = 10
        assert net_type in ['simple', 'conv']

        if net_type == "simple":
            self.inference_net = tf.keras.Sequential([
                InputLayer(input_shape=[28 * 28 * 1 + self.num_classes]),
                Flatten(),
                Dense(256, activation='relu'),
                Dense(128, activation='relu'),
                Dense(self.latent_dim * 2),    # [means, stds]
            ])
            self.generative_net = tf.keras.Sequential([
                InputLayer(input_shape=[self.latent_dim + self.num_classes]),
                Dense(128, activation='relu'),
                Dense(256, activation='relu'),
                Dense(28 * 28 * 1),
                Reshape(target_shape=[28, 28, 1]),
            ])

    def encode(self, x, y):
        conditional_x = tf.concat([Flatten()(x), tf.one_hot(y, self.num_classes)], 1)
        mean_logvar = self.inference_net(conditional_x)
        N = mean_logvar.shape[0]
        mean = tf.slice(mean_logvar, [0, 0], [N, self.latent_dim])
        logvar = tf.slice(mean_logvar, [0, self.latent_dim], [N, self.latent_dim])
        return mean, logvar

    def decode(self, z, y, apply_sigmoid=False):
        conditional_z = tf.concat([Flatten()(z), tf.one_hot(y, self.num_classes)], 1)
        logits = self.generative_net(conditional_z)
        if apply_sigmoid:
            probs = tf.sigmoid(logits)
            return probs
        return logits
