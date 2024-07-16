# wyn-keras 🎉

A Python package for building and experimenting with Vision Transformer (ViT) models using TensorFlow and Keras.

## Directory Structure 📁

```
wyn-keras/
├── pyproject.toml
├── README.md
├── wyn_keras
│   ├── __init__.py
│   └── vit.py
├── tests
│   └── __init__.py
└── .gitignore
```

## Installation Instructions 📦

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

### Additional Functions (Coming Soon...) 🚧

Stay tuned for more functionalities to be added in the future!

## Example Usage 📚

### MNIST Example

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

# Plot attention
vit_model.plot_attention(model, x_test[0])
```

### CIFAR-10 Example

```python
import tensorflow as tf
from wyn_keras.vit import ViT

# Load and preprocess the CIFAR-10 dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

# Number of classes in CIFAR-10 dataset
num_classes = 10

# Create an instance of the ViT class
vit_model = ViT(num_classes=num_classes, input_shape=(32, 32, 3), image_size=32, num_epochs=2)

# Create the ViT model
model = vit_model.create_vit_classifier()

# Train the model
history = vit_model.run_experiment(model, x_train, y_train, x_test, y_test)

# Plot attention
vit_model.plot_attention(model, x_test[0])
```

## Author ✍️

**Yiqiao Yin**  
Email: [eagle0504@gmail.com](mailto:eagle0504@gmail.com)  
Personal Site: [https://www.y-yin.io/](https://www.y-yin.io/)
