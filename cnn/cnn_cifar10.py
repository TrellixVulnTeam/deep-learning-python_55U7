"""
Tute: https://cambridgespark.com/content/tutorials/convolutional-neural-networks-with-keras/index.html
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from keras.datasets import cifar10 # subroutines for fetching the CIFAR-10 dataset
from keras.models import Model # basic class for specifying and training a neural network
from keras.layers import Input, Convolution2D, MaxPooling2D, Dense, Dropout, Flatten
from keras.utils import np_utils # utilities for one-hot encoding of ground truth values
from keras.models import model_from_json
import numpy as np

"""
The hyperparameters are:

The batch size, representing the number of training examples being used simultaneously during a single iteration of the gradient descent algorithm;
The number of epochs, representing the number of times the training algorithm will iterate over the entire training set before terminating1;
The kernel sizes in the convolutional layers;
The pooling size in the pooling layers;
The number of kernels in the convolutional layers;
The dropout probability (we will apply dropout after each pooling, and after the fully connected layer);
The number of neurons in the fully connected layer of the MLP.
"""

batch_size = 32  # in each iteration, we consider 32 training examples at once
num_epochs = 200  # we iterate 200 times over the entire training set
kernel_size = 3  # we will use 3x3 kernels throughout
pool_size = 2  # we will use 2x2 pooling throughout
conv_depth_1 = 32  # we will initially have 32 kernels per conv. layer...
conv_depth_2 = 64  # ...switching to 64 after the first pooling layer
drop_prob_1 = 0.25  # dropout after pooling with probability 0.25
drop_prob_2 = 0.5  # dropout in the FC layer with probability 0.5
hidden_size = 512  # the FC layer will have 512 neurons

(X_train, y_train), (X_test, y_test) = cifar10.load_data()  # fetch CIFAR-10 data

num_train, height, width, depth = X_train.shape  # there are 50000 training examples in CIFAR-10
num_test = X_test.shape[0]  # there are 10000 test examples in CIFAR-10
num_classes = np.unique(y_train).shape[0]  # there are 10 image classes

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= np.max(X_train)  # Normalise data to [0, 1] range
X_test /= np.max(X_test)  # Normalise data to [0, 1] range

Y_train = np_utils.to_categorical(y_train, num_classes)  # One-hot encode the labels
Y_test = np_utils.to_categorical(y_test, num_classes)  # One-hot encode the labels

"""
Architecture
"""

inp = Input(shape=(height, width, depth))  # depth goes last in TensorFlow back-end (first in Theano)

# Conv [32] -> Conv [32] -> Pool (with dropout on the pooling layer)
conv_1 = Convolution2D(conv_depth_1, (kernel_size, kernel_size), padding='same', activation='relu')(inp)
conv_2 = Convolution2D(conv_depth_1, (kernel_size, kernel_size), padding='same', activation='relu')(conv_1)
pool_1 = MaxPooling2D(pool_size=(pool_size, pool_size))(conv_2)
drop_1 = Dropout(drop_prob_1)(pool_1)

# Conv [64] -> Conv [64] -> Pool (with dropout on the pooling layer)
conv_3 = Convolution2D(conv_depth_2, (kernel_size, kernel_size), padding='same', activation='relu')(drop_1)
conv_4 = Convolution2D(conv_depth_2, (kernel_size, kernel_size), padding='same', activation='relu')(conv_3)
pool_2 = MaxPooling2D(pool_size=(pool_size, pool_size))(conv_4)
drop_2 = Dropout(drop_prob_1)(pool_2)

# Now flatten to 1D, apply FC -> ReLU (with dropout) -> softmax
flat = Flatten()(drop_2)
hidden = Dense(hidden_size, activation='relu')(flat)
drop_3 = Dropout(drop_prob_2)(hidden)
out = Dense(num_classes, activation='softmax')(drop_3)

model = Model(inputs=inp, outputs=out)  # To define a model, just specify its input and output layers

model.compile(loss='categorical_crossentropy',  # using the cross-entropy loss function
              optimizer='adam',  # using the Adam optimiser
              metrics=['accuracy'])  # reporting the accuracy

model.fit(X_train, Y_train,                # Train the model using the training set...
          batch_size=batch_size, epochs=num_epochs,
          verbose=1, validation_split=0.1)  # ...holding out 10% of the data for validation
model.evaluate(X_test, Y_test, verbose=1)   # Evaluate the trained model on the test set!

# serialize model to JSON
model_json = model.to_json()
with open("cnn_cifar10_model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("cnn_cifar10_model.h5")
print("Saved model to disk")

# later...

# load json and create model
json_file = open('cnn_cifar10_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("cnn_cifar10_model.h5")
print("Loaded model from disk")

# evaluate loaded model on test data
loaded_model.compile(loss='categorical_crossentropy',  # using the cross-entropy loss function
              optimizer='adam',  # using the Adam optimiser
              metrics=['accuracy'])  # reporting the accuracy
score = loaded_model.evaluate(X_test, Y_test, verbose=1)

print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1] * 100))