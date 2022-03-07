
import numpy as np

def sigmoid(x):
    sig = 1 / (1 + np.exp(-x))     # Define sigmoid function
    return sig
