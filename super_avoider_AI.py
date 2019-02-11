import numpy as np
from keras.models import Model
from keras.layers import Input, Dense


class SuperAvoiderAI:
    def __init__(self, input_shape, neurons_layer, activations):
        """
        ## Units ##
        The amount of "neurons" or "cells" in a layer.
        ## Shapes ##
        Shapes are consequences of the model's configuration.
        Shapes are tuples representing how many elements an array or tensor has in each dimension.
        ## Input shape ##
        What flows between layers are tensors. Tensors can be seen as matrices, with shapes.
        In Keras, the input layer itself is not a layer, but a tensor.
        It's the starting tensor you send to the first hidden layer.
        This tensor must have the same shape as your training data.
        ## Weights ##
        Weights will be entirely automatically calculated based on the input and the output shapes.
        Again, each type of layer works in a certain way. But the weights will be a matrix capable of
        transforming the input shape into the output shape by some mathematical operation.
        In a dense layer, weights multiply all inputs. It's a matrix with one column per input and one row per unit,
        but this is often not important for basic works.
        ## Input dim ##
        If your input shape has only one dimension, you don't need to give it as a tuple,
        you give input_dim as a scalar number.
        :param input_shape: tuple([iterable]), immutable sequence type.
        :param neurons_layer: Number of neurons in each hidden layer.
        :param activations: List of activation functions
        :return: Object of class
        """
        if len(activations) != len(neurons_layer):
            print("Must have an activaiton function for each layer!")
            print("Number of activations and layers: (%i, %i)" % (len(activations), len(neurons_layer)))
            exit(1)
        self.use_bias = False
        self.input_layer = Input(shape=input_shape)
        for i in range(len(neurons_layer)):
            if i == 0:
                self.output_layers = Dense(units=neurons_layer[i], activation=activations[i])(self.input_layer)
            else:
                self.output_layers = Dense(units=neurons_layer[i], activation=activations[i])(self.output_layers)
        self.model = Model(self.input_layer, self.output_layers)

    def model_summary(self):
        """Print summary"""
        self.model.summary()

    def update_weights(self, new_weights, is_flat):
        if is_flat:
            new_weights = self.reshape_flatten_array(new_weights)
        self.set_weights(new_weights)

    def is_numpy(self, x):
        """
        Check if ind is a numpy array
        :param x: Array representing the individual
        :return: Boolean
        """
        if type(x) is np.ndarray:
            return True
        else:
            return False

    def get_shapes(self, use_bias=None):
        """
        Return layer shapes
        Default is without bias weights
        :param use_bias: Boolean
        :return: list of shape tuples
        """
        if use_bias is not None:
            self.use_bias = use_bias

        shapes = []
        # Return bias shapes as well
        if self.use_bias:
            for weight_array in self.get_weights():
                shapes.append(weight_array.shape)
        else:  # Use only weights
            for weight_array in self.get_weights()[0::2]:
                shapes.append(weight_array.shape)
        return shapes

    def get_weights(self):
        """
        :return: Numpy array(s) of shape (sum(neuron layers + biases),).
        If more than one layer the output will be a list of numpy arrays
        """
        return self.model.get_weights()

    def set_weights(self, weights):
        """
        sets the values of the weights of the model, from a list of Numpy arrays.
        The arrays in the list should have the same shape as those returned by get_weights()
        :param weights: Numpy array(s)
        :return:
        """
        if self.use_bias is False:
            biases = self.get_weights()[1::2]  # Pick only bias vectors
            for i, layer in enumerate(self.model.layers):
                # weights[0][0][0] = 1  # Test model weights are updated
                if i > 0:  # Skip input layer since it doesn't have weights associated with it
                    layer.set_weights([np.array(weights[i - 1]), biases[i - 1]])
                # print(self.get_weights())
        else:
            self.model.set_weights(weights)

    def print_weights_biases(self):
        """Print information"""
        print("Weights:\n%s\nBiases:\n%s" % (self.get_weights()[0::2], self.get_weights()[1::2]))

    def get_predict(self, input_sample, classify=False, verbose=0):
        """
        Calculate an output of the model.
        :param input_sample: Numpy array of same shape as 'input_shape'
        :param classify: Boolean
        :param verbose: 0 or 1
        :return:
        """
        try:
            output = self.model.predict(input_sample, verbose=verbose)
            if classify:
                if output.shape[-1] > 1:  # Return how many columns is in the output
                    return output.argmax(axis=-1)  # Return column index of maximum value for each row
                else:
                    return (output > 0.5).astype('int')
            else:
                return output
        except (ValueError, TypeError):
            print("Dimensions incorrect! Input expected %s got %s " % (input_sample.shape, self.model.input_shape))
            return

    def get_flatten_weights(self, use_bias):
        """
        Method takes weights from each layer and append them one-by-one to a list.
        List is then converted to a numpy array

        ""
        self.get_weights()[0::2] return every other array from list.
        Keras get_weights() is therefore [weights_1, bias_1, weights_2, bias_2, ...]
        ""

        :param use_bias: Include bias values in returned array
        :return: 1D numpy array
        """
        self.use_bias = use_bias
        one_dim_weights = []
        if use_bias:
            for weight_array in self.get_weights():
                for weight in weight_array.flatten():
                    one_dim_weights.append(weight)
        else:
            for weight_array in self.get_weights()[0::2]:
                for weight in weight_array.flatten():
                    one_dim_weights.append(weight)

        return one_dim_weights

    def reshape_flatten_array(self, flatten_array):
        """
        Reshape a 1D array returned from the get_flatten_weights() method to the shapes
        returned by this method.
        :param flatten_array: List or numpy array, converted to numpy array if it's not one
        :return: list of numpy arrays with shape equal to the provided shapes argument
        """
        if self.is_numpy(flatten_array) is False:
            flatten_array = np.array(flatten_array)
        shapes = self.get_shapes()
        # Create list of indexes to split flatten_array
        tmp_ind = []
        for i, shape_tuple in enumerate(shapes):
            tmp = 1
            for value in shape_tuple:
                tmp *= value
            if i == 0:
                tmp_ind.append(tmp)
            elif i < len(shapes) - 1:  # No need to save index flatten_array[end] in our list
                tmp_ind.append(tmp_ind[i-1] + tmp)
        #####################################################
        # Split at the indexes
        original_shape = np.split(flatten_array, tmp_ind)
        #####################################################
        # Reshape each numpy array according to shapes tuples
        for j, _tuple in enumerate(shapes):
            original_shape[j] = original_shape[j].reshape(_tuple)
        return original_shape

if __name__ == '__main__':
    SA = SuperAvoiderAI(input_shape=(50,), neurons_layer=[10, 10, 4], activations=["relu", "relu", "softmax"])
    X = SA.get_flatten_weights(use_bias=True)
    SA.update_weights(new_weights=X, is_flat=True)

    Y = SA.get_flatten_weights(use_bias=False)
    SA.update_weights(new_weights=Y, is_flat=True)
    print(SA.get_shapes())
