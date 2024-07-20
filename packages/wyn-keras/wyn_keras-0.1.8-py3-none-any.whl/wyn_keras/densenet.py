# densenet.py

import tensorflow as tf
from tensorflow.keras import layers, models, Input
from typing import Tuple

class DenseNet121:
    """
    DenseNet121 model class for creating a DenseNet121-like convolutional neural network.

    Attributes:
        input_shape (Tuple[int, int, int]): The shape of the input images (height, width, channels).
        num_classes (int): The number of output classes.
        growth_rate (int): The growth rate for the dense blocks.
        compression_factor (float): The compression factor for the transition layers.
    """

    def __init__(self, 
                 input_shape: Tuple[int, int, int] = (224, 224, 3), 
                 num_classes: int = 1000, 
                 growth_rate: int = 32, 
                 compression_factor: float = 0.5):
        """
        Initialize the DenseNet121 model with input shape, number of output classes, growth rate, and compression factor.

        Args:
            input_shape (Tuple[int, int, int]): The shape of the input images (height, width, channels).
            num_classes (int): The number of output classes.
            growth_rate (int): The growth rate for the dense blocks.
            compression_factor (float): The compression factor for the transition layers.
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.growth_rate = growth_rate
        self.compression_factor = compression_factor

    def dense_block(self, x: tf.Tensor, num_layers: int, growth_rate: int) -> tf.Tensor:
        """
        Build a dense block.

        Args:
            x (tf.Tensor): The input tensor to the block.
            num_layers (int): The number of layers in the dense block.
            growth_rate (int): The growth rate for the dense blocks.

        Returns:
            tf.Tensor: The output tensor of the dense block.
        """
        for _ in range(num_layers):
            output = layers.BatchNormalization()(x)
            output = layers.Activation('relu')(output)
            output = layers.Conv2D(4 * growth_rate, (1, 1), padding='same', kernel_initializer='he_normal')(output)
            output = layers.BatchNormalization()(output)
            output = layers.Activation('relu')(output)
            output = layers.Conv2D(growth_rate, (3, 3), padding='same', kernel_initializer='he_normal')(output)
            x = layers.Concatenate()([x, output])
        return x

    def transition_layer(self, x: tf.Tensor, compression_factor: float) -> tf.Tensor:
        """
        Build a transition layer.

        Args:
            x (tf.Tensor): The input tensor to the layer.
            compression_factor (float): The compression factor for the transition layers.

        Returns:
            tf.Tensor: The output tensor of the transition layer.
        """
        num_filters = int(x.shape[-1] * compression_factor)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.Conv2D(num_filters, (1, 1), padding='same', kernel_initializer='he_normal')(x)
        x = layers.AveragePooling2D((2, 2), strides=(2, 2))(x)
        return x

    def build_model(self) -> models.Model:
        """
        Build the DenseNet121 model.

        Returns:
            models.Model: The built DenseNet121 model.
        """
        input_tensor = Input(shape=self.input_shape)

        # Initial convolution layer
        x = layers.Conv2D(2 * self.growth_rate, (7, 7), strides=(2, 2), padding='same', kernel_initializer='he_normal')(input_tensor)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)

        # Dense blocks and transition layers
        x = self.dense_block(x, 6, self.growth_rate)
        x = self.transition_layer(x, self.compression_factor)

        x = self.dense_block(x, 12, self.growth_rate)
        x = self.transition_layer(x, self.compression_factor)

        x = self.dense_block(x, 24, self.growth_rate)
        x = self.transition_layer(x, self.compression_factor)

        x = self.dense_block(x, 16, self.growth_rate)

        # Global average pooling and output layer
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(self.num_classes, activation='softmax')(x)

        model = models.Model(input_tensor, x, name='densenet121')
        return model
