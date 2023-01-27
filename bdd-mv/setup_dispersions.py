'''Setup: dispersion functions.'''

## External modules.
import numpy as np

## Internal modules.


###############################################################################


## Dispersion function definitions.

def dispersion_huber(x):
    '''
    This is the pseudo-Huber function.
    '''
    return np.sqrt(x**2+1.0)-1.0


def d1_huber(x):
    '''
    Returns the first derivative of dispersion_huber.
    '''
    return x / np.sqrt(x**2+1)


def d2_huber(x):
    '''
    Returns the second derivative of dispersion_huber.
    '''
    return 1.0 / (x**2+1.0)**(1.5)


###############################################################################
