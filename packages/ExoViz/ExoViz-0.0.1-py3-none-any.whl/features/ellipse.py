import numpy as np 

#A function defining an ellipse
def ellipse(phi,a,b):
    return np.array([a*np.cos(phi), b*np.sin(phi)])

