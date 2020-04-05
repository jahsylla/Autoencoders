# parser_args code referred the hwalseoklee's code:
# https://github.com/hwalsuklee/tensorflow-data-VAE/blob/master/run_main.py

import tensorflow as tf
from utils import data, plot
from model.autoencoder import AE, VAE, CVAE
#from train_utils.autoencoder import AETrain, VAETrain, CVAETrain
from loss import compute_loss
import time
import argparse


def parse_args():
    desc = "Tensorflow 2.0 implementation of 'AutoEncoder Families (AE, VAE, CVAE(Conditional VAE))'"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--ae_type', type=str, default=False,
                        help='Type of autoencoder: [AE, VAE, CVAE]')
    parser.add_argument('--latent_dim', type=int, default=2,
                        help='Degree of latent dimension(a.k.a. "z")')
    parser.add_argument('--num_epochs', type=int, default=15,
                        help='The number of training epochs')
    parser.add_argument('--learn_rate', type=float, default=1e-4,
                        help='Learning rate during training')
    parser.add_argument('--batch_size', type=int, default=1000,
                        help='Batch size')
    return parser.parse_args()


def train(ae_type, net_type,latent_dim=2, epochs=100, lr=1e-4, batch_size=1000):

    if ae_type == "AE":
        model = AE(latent_dim, net_type=net_type)
    elif ae_type == "VAE":
        model = VAE(latent_dim, net_type=net_type)
    elif ae_type == "CVAE":
        model = CVAE(latent_dim, net_type=net_type)
    else:
        raise ValueError

    # load train and test data
    train_dataset, test_dataset = data.load_dataset(batch_size=batch_size)
    # initialize Adam optimizer
    optimizer = tf.keras.optimizers.Adam(lr)

    for epoch in range(1, epochs + 1):
        t = time.time()
        last_loss = 0
        for train_x, _ in train_dataset:
            gradients, loss = compute_gradients(model, train_x, ae_type)
            apply_gradients(optimizer, gradients, model.trainable_variables)
            last_loss = loss
        if epoch % 10 == 0:
            print('Epoch {}, Loss: {}, Remaining Time at This Epoch: {:.2f}'.format(
                epoch, last_loss, time.time() - t
            ))

    if ae_type == "AE":
        plot.plot_AE(model, test_dataset)
    elif ae_type == "VAE":
        plot.plot_VAE(model, test_dataset)
    elif ae_type == "CVAE":
        plot.plot_CVAE(model, test_dataset)
    else:
        raise ValueError

    return model


def compute_gradients(model, x, ae_type):
    with tf.GradientTape() as tape:
        loss = compute_loss(model, x, ae_type)
    return tape.gradient(loss, model.trainable_variables), loss

def apply_gradients(optimizer, gradients, variables):
    optimizer.apply_gradients(zip(gradients, variables))

def main(args):

    train(latent_dim=args.latent_dim,
            epochs=args.num_epochs,
            lr=args.learn_rate,
            batch_size=args.batch_size,
            ae_type = args.ae_type,
            net_type = "simple",)

if __name__ == "__main__":
    args = parse_args()
    if args is None:
        exit()
    main(args)