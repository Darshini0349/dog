"""
Project 3 (CV): Dog vs Cat Classifier
Trains a REAL convolutional neural network (Keras) for binary image
classification — this actually trains and reports real accuracy.

NOTE ON DATA: the classic Kaggle Dogs-vs-Cats images can't be downloaded in
every environment, so this script GENERATES a synthetic two-class image
dataset with a learnable visual difference ("cats" = images with circular
blob patterns, "dogs" = images with elongated/vertical patterns) plus noise.
Stated plainly. The CNN architecture and training loop are exactly what
you'd use on the real photos — to switch, point image_dataset_from_directory
at a folder of real cat/dog images instead of make_dataset().

Run: pip install tensorflow-cpu numpy
     python 03_dog_vs_cat_classifier.py

Concepts practiced: building a CNN (Conv2D/MaxPool/Dense), training with a
validation split, reading a real training curve, why CNNs suit images
(local patterns) over flat dense nets.
"""

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

IMG_SIZE = 32


def make_dataset(n_per_class=800, seed=42):
    """
    Synthetic 2-class images:
      class 0 ("cat"): a bright circular blob (round shapes)
      class 1 ("dog"): a bright vertical bar (elongated shapes)
    Plus noise, so the CNN has to actually learn the shape difference.
    """
    rng = np.random.default_rng(seed)
    images, labels = [], []

    for _ in range(n_per_class):
        # "cat": circular blob
        img = rng.normal(0.3, 0.1, (IMG_SIZE, IMG_SIZE)).clip(0, 1)
        cx, cy = rng.integers(10, 22, 2)
        yy, xx = np.ogrid[:IMG_SIZE, :IMG_SIZE]
        blob = (xx - cx) ** 2 + (yy - cy) ** 2 <= rng.integers(16, 36)
        img[blob] = 0.9
        images.append(img)
        labels.append(0)

        # "dog": vertical bar
        img = rng.normal(0.3, 0.1, (IMG_SIZE, IMG_SIZE)).clip(0, 1)
        col = rng.integers(8, 24)
        width = rng.integers(2, 5)
        img[:, col:col + width] = 0.9
        images.append(img)
        labels.append(1)

    X = np.array(images).reshape(-1, IMG_SIZE, IMG_SIZE, 1).astype("float32")
    y = np.array(labels)
    idx = rng.permutation(len(y))
    return X[idx], y[idx]


def build_cnn():
    model = models.Sequential([
        layers.Input((IMG_SIZE, IMG_SIZE, 1)),
        layers.Conv2D(16, 3, activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, activation="relu"),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(32, activation="relu"),
        layers.Dense(1, activation="sigmoid"),  # binary
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def main():
    print("=== Dog vs Cat Classifier (real CNN, synthetic images) ===")
    X, y = make_dataset()
    print(f"Dataset: {len(X)} images, {IMG_SIZE}x{IMG_SIZE} grayscale, 2 classes")

    split = int(0.8 * len(X))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    model = build_cnn()
    print(f"\nModel parameters: {model.count_params():,}")
    print("Training...")
    history = model.fit(
        X_train, y_train, validation_data=(X_val, y_val),
        epochs=5, batch_size=32, verbose=2,
    )

    val_acc = history.history["val_accuracy"][-1]
    print(f"\nFinal validation accuracy: {val_acc:.4f}")
    print("(High here because synthetic shapes are cleanly separable — on real")
    print(" cat/dog photos expect ~80-90% with this small a network.)")


if __name__ == "__main__":
    main()