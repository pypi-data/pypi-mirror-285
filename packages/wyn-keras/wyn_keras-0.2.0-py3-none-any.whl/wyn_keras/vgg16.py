# vgg16.py

from tensorflow.keras import layers, models
from tensorflow.keras.models import Sequential

class VGG16:
    """
    VGG16 model class for creating a VGG16-like convolutional neural network.

    Attributes:
        input_shape (tuple): The shape of the input images (height, width, channels).
        num_classes (int): The number of output classes.
    """

    def __init__(self, input_shape: tuple, num_classes: int):
        """
        Initialize the VGG16 model with input shape and number of output classes.

        Args:
            input_shape (tuple): The shape of the input images (height, width, channels).
            num_classes (int): The number of output classes.
        """
        self.input_shape = input_shape
        self.num_classes = num_classes

    def build_model(self) -> models.Sequential:
        """
        Build the VGG16 model.

        Returns:
            models.Sequential: The built VGG16 model.
        """
        model = Sequential()

        # First convolutional block
        model.add(layers.Conv2D(64, (3, 3), padding='same', activation='relu', input_shape=self.input_shape))
        model.add(layers.Conv2D(64, (3, 3), padding='same', activation='relu'))
        model.add(layers.MaxPooling2D((2, 2), strides=(2, 2)))

        # Second convolutional block
        model.add(layers.Conv2D(128, (3, 3), padding='same', activation='relu'))
        model.add(layers.Conv2D(128, (3, 3), padding='same', activation='relu'))
        model.add(layers.MaxPooling2D((2, 2), strides=(2, 2)))

        # Third convolutional block
        model.add(layers.Conv2D(256, (3, 3), padding='same', activation='relu'))
        model.add(layers.Conv2D(256, (3, 3), padding='same', activation='relu'))
        model.add(layers.Conv2D(256, (3, 3), padding='same', activation='relu'))
        model.add(layers.MaxPooling2D((2, 2), strides=(2, 2)))

        # Fourth convolutional block
        model.add(layers.Conv2D(512, (3, 3), padding='same', activation='relu'))
        model.add(layers.Conv2D(512, (3, 3), padding='same', activation='relu'))
        model.add(layers.Conv2D(512, (3, 3), padding='same', activation='relu'))
        model.add(layers.MaxPooling2D((2, 2), strides=(2, 2)))

        # Fifth convolutional block
        model.add(layers.Conv2D(512, (3, 3), padding='same', activation='relu'))
        model.add(layers.Conv2D(512, (3, 3), padding='same', activation='relu'))
        model.add(layers.Conv2D(512, (3, 3), padding='same', activation='relu'))
        model.add(layers.MaxPooling2D((2, 2), strides=(2, 2)))

        # Flattening and Fully Connected Layers
        model.add(layers.Flatten())
        model.add(layers.Dense(4096, activation='relu'))
        # model.add(layers.Dense(4096, activation='relu'))
        model.add(layers.Dense(self.num_classes, activation='softmax'))

        return model
