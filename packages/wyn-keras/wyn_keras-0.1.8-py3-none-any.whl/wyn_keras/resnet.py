# resnet.py

import tensorflow as tf
from tensorflow.keras import layers, models, Input
from tensorflow.keras.models import Model
from typing import Tuple, List

class ResNet:
    """
    ResNet50 model class for creating a ResNet50-like convolutional neural network.

    Attributes:
        input_shape (Tuple[int, int, int]): The shape of the input images (height, width, channels).
        num_classes (int): The number of output classes.
        kernel_size (int): The size of the kernel for convolutional layers.
        filters (List[int]): The number of filters for each convolutional block.
        strides (Tuple[int, int]): The strides for the convolutional layers.
    """

    def __init__(self, 
                 input_shape: Tuple[int, int, int] = (224, 224, 3), 
                 num_classes: int = 1000, 
                 kernel_size: int = 3, 
                 filters: List[int] = [64, 64, 256], 
                 strides: Tuple[int, int] = (2, 2)):
        """
        Initialize the ResNet50 model with input shape, number of output classes, kernel size, filters, and strides.

        Args:
            input_shape (Tuple[int, int, int]): The shape of the input images (height, width, channels).
            num_classes (int): The number of output classes.
            kernel_size (int): The size of the kernel for convolutional layers.
            filters (List[int]): The number of filters for each convolutional block.
            strides (Tuple[int, int]): The strides for the convolutional layers.
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.kernel_size = kernel_size
        self.filters = filters
        self.strides = strides

    def identity_block(self, input_tensor, kernel_size, filters) -> tf.Tensor:
        """
        Build an identity block.

        Args:
            input_tensor (tf.Tensor): The input tensor to the block.
            kernel_size (int): The size of the kernel for convolutional layers.
            filters (List[int]): The number of filters for each convolutional block.

        Returns:
            tf.Tensor: The output tensor of the identity block.
        """
        filters1, filters2, filters3 = filters

        x = layers.Conv2D(filters1, (1, 1))(input_tensor)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)

        x = layers.Conv2D(filters2, kernel_size, padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)

        x = layers.Conv2D(filters3, (1, 1))(x)
        x = layers.BatchNormalization()(x)

        x = layers.add([x, input_tensor])
        x = layers.Activation('relu')(x)
        return x

    def conv_block(self, input_tensor, kernel_size, filters, strides=(2, 2)) -> tf.Tensor:
        """
        Build a convolutional block.

        Args:
            input_tensor (tf.Tensor): The input tensor to the block.
            kernel_size (int): The size of the kernel for convolutional layers.
            filters (List[int]): The number of filters for each convolutional block.
            strides (Tuple[int, int]): The strides for the convolutional layers.

        Returns:
            tf.Tensor: The output tensor of the convolutional block.
        """
        filters1, filters2, filters3 = filters

        x = layers.Conv2D(filters1, (1, 1), strides=strides)(input_tensor)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)

        x = layers.Conv2D(filters2, kernel_size, padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)

        x = layers.Conv2D(filters3, (1, 1))(x)
        x = layers.BatchNormalization()(x)

        shortcut = layers.Conv2D(filters3, (1, 1), strides=strides)(input_tensor)
        shortcut = layers.BatchNormalization()(shortcut)

        x = layers.add([x, shortcut])
        x = layers.Activation('relu')(x)
        return x

    def build_model(self) -> models.Model:
        """
        Build the ResNet50 model.

        Returns:
            models.Model: The built ResNet50 model.
        """
        input_tensor = Input(shape=self.input_shape)

        # Initial convolution layer
        x = layers.ZeroPadding2D(padding=(3, 3))(input_tensor)
        x = layers.Conv2D(64, (7, 7), strides=(2, 2))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.ZeroPadding2D(padding=(1, 1))(x)
        x = layers.MaxPooling2D((3, 3), strides=(2, 2))(x)

        # Residual blocks
        x = self.conv_block(x, 3, [64, 64, 256], strides=(1, 1))
        x = self.identity_block(x, 3, [64, 64, 256])
        x = self.identity_block(x, 3, [64, 64, 256])

        x = self.conv_block(x, 3, [128, 128, 512])
        x = self.identity_block(x, 3, [128, 128, 512])
        x = self.identity_block(x, 3, [128, 128, 512])
        x = self.identity_block(x, 3, [128, 128, 512])

        x = self.conv_block(x, 3, [256, 256, 1024])
        x = self.identity_block(x, 3, [256, 256, 1024])
        x = self.identity_block(x, 3, [256, 256, 1024])
        x = self.identity_block(x, 3, [256, 256, 1024])
        x = self.identity_block(x, 3, [256, 256, 1024])
        x = self.identity_block(x, 3, [256, 256, 1024])

        x = self.conv_block(x, 3, [512, 512, 2048])
        x = self.identity_block(x, 3, [512, 512, 2048])
        x = self.identity_block(x, 3, [512, 512, 2048])

        # Final part
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(self.num_classes, activation='softmax')(x)

        # Create model
        model = Model(input_tensor, x)

        return model
