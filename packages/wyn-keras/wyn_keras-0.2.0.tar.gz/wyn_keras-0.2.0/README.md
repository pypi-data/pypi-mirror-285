# wyn-keras 🎉

A Python package for building and experimenting with Popular Convolutional Neural Networks (CNN) and Vision Transformer (ViT) models using TensorFlow and Keras.

## Directory Structure 📁

```
wyn-keras/
├── pyproject.toml
├── README.md
├── wyn_keras
│   ├── __init__.py
│   ├── vgg16.py
│   ├── resnet.py
│   ├── densenet.py
│   ├── inception.py
│   └── vit.py
├── tests
│   └── __init__.py
└── .gitignore
```

## Installation Instructions (From `PIP`) 📦

To install the package from PyPI, use the following command:

```sh
pip install wyn-keras
```

For more information, visit the [PyPI page](https://pypi.org/project/wyn-keras/).

## Installation Instructions (Local) 📦

To install the package and its dependencies, use [Poetry](https://python-poetry.org/):

```sh
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install the package
poetry install
```

## Usage 🚀

### Vision Transformer

The `ViT` class allows you to create and train Vision Transformer models.

### VGG16

The `VGG16` class allows you to create and train VGG16 models.

### ResNet

The `ResNet50` class allows you to create and train ResNet50 models.

### DenseNet

The `DenseNet121` class allows you to create and train DenseNet121 models.

### InceptionV3

The `InceptionV3Model` class allows you to create and train InceptionV3 models.

### Additional Functions (Coming Soon...) 🚧

Stay tuned for more functionalities to be added in the future!

## Example Usage 📚

### Vision Transformer

```python
import tensorflow as tf
from wyn_keras.vit import ViT

# Load and preprocess the MNIST dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train[..., tf.newaxis].astype("float32") / 255.0
x_test = x_test[..., tf.newaxis].astype("float32") / 255.0

# Number of classes in MNIST dataset
num_classes = 10

# Create an instance of the ViT class
vit_model = ViT(num_classes=num_classes, input_shape=(28, 28, 1), image_size=28, num_epochs=2)

# Create the ViT model
model = vit_model.create_vit_classifier()

# Train the model
history = vit_model.run_experiment(model, x_train, y_train, x_test, y_test)

# Plot patches
vit_model.plot_patches(x_test)
```

### VGG16

```python
from wyn_keras.vgg16 import VGG16

# Define the input shape and number of classes
input_shape = (32, 32, 3)
num_classes = 10

# Create an instance of the VGG16 class
vgg16_instance = VGG16(input_shape=input_shape, num_classes=num_classes)

# Build the model
model_vgg16 = vgg16_instance.build_model()

# Print the model summary
model_vgg16.summary()
```

### ResNet

```python
from wyn_keras.resnet import ResNet50

# Define the input shape, number of classes, kernel size, filters, and strides
input_shape = (224, 224, 3)
num_classes = 1000
kernel_size = 3
filters = [64, 64, 256]
strides = (2, 2)

# Create an instance of the ResNet50 class
resnet_instance = ResNet50(input_shape=input_shape, num_classes=num_classes, kernel_size=kernel_size, filters=filters, strides=strides)

# Build the model
model_resnet = resnet_instance.build_model()

# Print the model summary
model_resnet.summary()
```

### DenseNet

```python
from wyn_keras.densenet import DenseNet121

# Define the input shape, number of classes, growth rate, and compression factor
input_shape = (224, 224, 3)
num_classes = 1000
growth_rate = 32
compression_factor = 0.5

# Create an instance of the DenseNet121 class
densenet_instance = DenseNet121(input_shape=input_shape, num_classes=num_classes, growth_rate=growth_rate, compression_factor=compression_factor)

# Build the model
model_densenet = densenet_instance.build_model()

# Print the model summary
model_densenet.summary()
```

### InceptionV3

```python
from wyn_keras.inception import InceptionV3Model

# Define the input shape, number of classes, and resize shape
input_shape = (32, 32, 3)
num_classes = 10
resize_shape = (75, 75)

# Create an instance of the InceptionV3Model class
inception_instance = InceptionV3Model(input_shape=input_shape, num_classes=num_classes, resize_shape=resize_shape)

# Build the model
model_inception = inception_instance.build_model()

# Print the model summary
model_inception.summary()
```

## Author ✍️

**Yiqiao Yin**  
Email: [eagle0504@gmail.com](mailto:eagle0504@gmail.com)  
Personal Site: [https://www.y-yin.io/](https://www.y-yin.io/)

