# inception.py

import tensorflow as tf
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Lambda, Input, Dense, GlobalAveragePooling2D
from typing import Tuple

class InceptionV3Model:
    """
    InceptionV3 model class for creating a pre-trained InceptionV3 model with custom input shape and output classes.

    Attributes:
        input_shape (Tuple[int, int, int]): The shape of the input images (height, width, channels).
        num_classes (int): The number of output classes.
        resize_shape (Tuple[int, int]): The shape to resize input images to.
    """

    def __init__(self, 
                 input_shape: Tuple[int, int, int] = (32, 32, 3), 
                 num_classes: int = 10, 
                 resize_shape: Tuple[int, int] = (75, 75)):
        """
        Initialize the InceptionV3 model with input shape, number of output classes, and resize shape.

        Args:
            input_shape (Tuple[int, int, int]): The shape of the input images (height, width, channels).
            num_classes (int): The number of output classes.
            resize_shape (Tuple[int, int]): The shape to resize input images to.
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.resize_shape = resize_shape

    def build_model(self) -> Model:
        """
        Build the InceptionV3 model.

        Returns:
            Model: The built InceptionV3 model.
        """
        # Define model (pre-trained)
        base_model = InceptionV3(include_top=False, input_shape=(self.resize_shape[0], self.resize_shape[1], 3), weights='imagenet')

        # Resize Input images to resize_shape
        new_input = Input(shape=self.input_shape)
        resized_img = Lambda(lambda image: tf.compat.v1.image.resize_images(image, self.resize_shape))(new_input)
        new_outputs = base_model(resized_img)
        model = Model(new_input, new_outputs)

        # Freeze all the layers
        for layer in model.layers:
            layer.trainable = False

        # Add Dense layer to classify on CIFAR10
        output = model.output
        output = GlobalAveragePooling2D()(output)
        output = Dense(units=self.num_classes, activation='softmax')(output)
        model = Model(model.input, output)

        return model
