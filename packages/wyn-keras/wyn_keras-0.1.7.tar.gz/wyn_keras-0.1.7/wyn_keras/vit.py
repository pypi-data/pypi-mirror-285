from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow import keras
from tensorflow.keras import layers


class Patches(layers.Layer):
    """
    Layer for extracting patches from images.
    """

    def __init__(self, patch_size: int):
        super().__init__()
        self.patch_size = patch_size

    def call(self, images: tf.Tensor) -> tf.Tensor:
        """
        Extracts patches from images.

        Args:
            images: Input images tensor.

        Returns:
            Tensor containing image patches.
        """
        batch_size = tf.shape(images)[0]
        patches = tf.image.extract_patches(
            images=images,
            sizes=[1, self.patch_size, self.patch_size, 1],
            strides=[1, self.patch_size, self.patch_size, 1],
            rates=[1, 1, 1, 1],
            padding="VALID",
        )
        patch_dims = patches.shape[-1]
        patches = tf.reshape(patches, [batch_size, -1, patch_dims])
        return patches


class PatchEncoder(layers.Layer):
    """
    Layer for encoding patches.
    """

    def __init__(self, num_patches: int, projection_dim: int):
        super().__init__()
        self.num_patches = num_patches
        self.projection = layers.Dense(units=projection_dim)
        self.position_embedding = layers.Embedding(
            input_dim=num_patches, output_dim=projection_dim
        )

    def call(self, patches: tf.Tensor) -> tf.Tensor:
        """
        Encodes patches by projecting them and adding position embeddings.

        Args:
            patches: Input patches tensor.

        Returns:
            Tensor containing encoded patches.
        """
        positions = tf.range(start=0, limit=self.num_patches, delta=1)
        encoded = self.projection(patches) + self.position_embedding(positions)
        return encoded


class ViT:
    """
    Vision Transformer (ViT) class for image classification.

    Attributes:
        num_classes: Number of output classes.
        input_shape: Shape of the input images.
        learning_rate: Learning rate for the optimizer.
        weight_decay: Weight decay for the optimizer.
        batch_size: Batch size for training.
        num_epochs: Number of training epochs.
        image_size: Size of the input images.
        patch_size: Size of each patch.
        projection_dim: Dimension of the patch projections.
        num_heads: Number of attention heads in the transformer.
        transformer_units: List of units in the transformer layers.
        transformer_layers: Number of transformer layers.
        mlp_head_units: List of units in the MLP head.
    """

    def __init__(
        self,
        num_classes: int = 2,
        input_shape: Tuple[int, int, int] = (299, 299, 3),
        learning_rate: float = 0.001,
        weight_decay: float = 0.0001,
        batch_size: int = 256,
        num_epochs: int = 800,
        image_size: int = 72,
        patch_size: int = 6,
        projection_dim: int = 64,
        num_heads: int = 4,
        transformer_units: List[int] = [128, 64],
        transformer_layers: int = 10,
        mlp_head_units: List[int] = [2048, 1024],
    ):
        self.num_classes = num_classes
        self.input_shape = input_shape
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.image_size = image_size
        self.patch_size = patch_size
        self.projection_dim = projection_dim
        self.num_heads = num_heads
        self.transformer_units = transformer_units
        self.transformer_layers = transformer_layers
        self.mlp_head_units = mlp_head_units
        self.num_patches = (image_size // patch_size) ** 2
        self.data_augmentation = keras.Sequential(
            [
                layers.Normalization(),
                layers.Resizing(image_size, image_size),
                layers.RandomFlip("horizontal"),
                layers.RandomRotation(factor=0.02),
                layers.RandomZoom(height_factor=0.2, width_factor=0.2),
            ],
            name="data_augmentation",
        )

    def mlp(
        self, x: tf.Tensor, hidden_units: List[int], dropout_rate: float
    ) -> tf.Tensor:
        """
        Creates a Multi-Layer Perceptron (MLP) block.

        Args:
            x: Input tensor.
            hidden_units: List of hidden units for the MLP.
            dropout_rate: Dropout rate for the MLP.

        Returns:
            Output tensor after applying the MLP.
        """
        for units in hidden_units:
            x = layers.Dense(units, activation=tf.nn.gelu)(x)
            x = layers.Dropout(dropout_rate)(x)
        return x

    def create_vit_classifier(self) -> keras.Model:
        """
        Creates the Vision Transformer (ViT) classifier model.

        Returns:
            A Keras Model instance.
        """
        inputs = layers.Input(shape=self.input_shape)
        augmented = self.data_augmentation(inputs)
        patches = Patches(self.patch_size)(augmented)
        encoded_patches = PatchEncoder(self.num_patches, self.projection_dim)(patches)

        for _ in range(self.transformer_layers):
            x1 = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
            attention_output = layers.MultiHeadAttention(
                num_heads=self.num_heads, key_dim=self.projection_dim, dropout=0.1
            )(x1, x1)
            x2 = layers.Add()([attention_output, encoded_patches])
            x3 = layers.LayerNormalization(epsilon=1e-6)(x2)
            x3 = self.mlp(x3, hidden_units=self.transformer_units, dropout_rate=0.1)
            encoded_patches = layers.Add()([x3, x2])

        representation = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
        representation = layers.Flatten()(representation)
        representation = layers.Dropout(0.5)(representation)
        features = self.mlp(
            representation, hidden_units=self.mlp_head_units, dropout_rate=0.5
        )
        logits = layers.Dense(self.num_classes)(features)
        model = keras.Model(inputs=inputs, outputs=logits)
        return model

    def run_experiment(
        self,
        model: keras.Model,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Runs the training and evaluation experiment.

        Args:
            model: The Keras model to be trained.
            x_train: Training images.
            y_train: Training labels.
            x_test: Testing images.
            y_test: Testing labels.

        Returns:
            A dictionary containing the training history.
        """
        optimizer = tfa.optimizers.AdamW(
            learning_rate=self.learning_rate, weight_decay=self.weight_decay
        )

        model.compile(
            optimizer=optimizer,
            loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=[
                keras.metrics.SparseCategoricalAccuracy(name="accuracy"),
                keras.metrics.SparseTopKCategoricalAccuracy(5, name="top-5-accuracy"),
            ],
        )

        checkpoint_filepath = "/tmp/checkpoint"
        checkpoint_callback = keras.callbacks.ModelCheckpoint(
            checkpoint_filepath,
            monitor="val_accuracy",
            save_best_only=True,
            save_weights_only=True,
        )

        history = model.fit(
            x=x_train,
            y=y_train,
            batch_size=self.batch_size,
            epochs=self.num_epochs,
            validation_split=0.1,
            callbacks=[checkpoint_callback],
        )

        model.load_weights(checkpoint_filepath)
        _, accuracy, top_5_accuracy = model.evaluate(x_test, y_test)
        print(f"Test accuracy: {accuracy * 100:.2f}%")
        print(f"Test top 5 accuracy: {top_5_accuracy * 100:.2f}%")

        return history

    def plot_patches(self, images: np.ndarray):
        """
        Plots the patches extracted from the first image in the batch.

        Args:
            images: Batch of images from which to extract and plot patches.
        """
        plt.figure(figsize=(4, 4))
        image = images[0]
        patches = Patches(self.patch_size)(tf.convert_to_tensor([image]))
        patches = patches.numpy().reshape(-1, self.patch_size, self.patch_size, image.shape[2])
        n = int(np.sqrt(patches.shape[0]))
        for i, patch in enumerate(patches):
            ax = plt.subplot(n, n, i + 1)
            plt.imshow(patch)
            plt.axis("off")
        plt.show()

