'''Setup: algorithms.'''

## External modules.
import numpy as np

## Internal modules.
from mml.algos import Algorithm
from mml.algos.gd import GD_ERM
from setup_losses import parse_dro


###############################################################################


class Weighted_Average(Algorithm):
    '''
    An Algorithm for sequentially computing
    the simplest possible sequential weighted
    average of parameter candidates.
    '''
    
    def __init__(self, model_main=None, model_ancillary=None):
        super().__init__(model=model_main, loss=None, name=None)
        self.model_ancillary = model_ancillary
        self.weight_sum = 1.0
        return None
    
    
    def update(self, X=None, y=None):
        for pn, p in self.paras.items():
            p *= self.weight_sum
            p += self.model_ancillary.paras[pn]
            p /= self.weight_sum + 1.0
        self.weight_sum += 1.0
        return None


class GD_ERM_DRO_CR(GD_ERM):
    '''
    A simple modification to ensure that
    for Cressie-Read type DRO implement using
    gradient descent, we compute the gradients
    correctly.
    
    Assumes that 'loss' is of the class DRO_CR().
    '''
    
    def __init__(self, bound, shape, step_coef=None,
                 model=None, loss=None, name=None):
        super().__init__(step_coef=step_coef, model=model,
                         loss=loss, name=name)
        self.bound = bound
        self.shape = shape
        return None
    
    
    def newdir(self, X=None, y=None):
        
        ## Preparatory calculations.
        theta = self.model.paras["theta"].item()
        crecip = 1.0 / self.shape
        cstar = self.shape / (self.shape-1.0)
        scale = 1.0 / np.mean(
            np.clip(
                a=self.loss.base(model=self.model, X=X, y=y)-theta,
                a_min=0.0, a_max=None
            )**cstar
        )**crecip # valid since (1/cstar)-1 = -1/c.
        scale *= (1.0+self.shape*(self.shape-1.0)*self.bound)**crecip / cstar
        
        ## Gradients of the modified losses.
        loss_grads = self.loss.grad(model=self.model, X=X, y=y)
        
        ## Update direction based on gradients of the desired loss.
        newdirs = {}
        for pn, g in loss_grads.items():
            if pn == "theta":
                newdirs[pn] = -(scale*(g.mean(axis=0, keepdims=False)-1.0)+1.0)
            else:
                newdirs[pn] = -scale*g.mean(axis=0, keepdims=False)
        return newdirs


## Simple parser for algorithm objects.

def get_algo(name, model, loss, name_main=None, model_main=None, **kwargs):

    ## Setup of the ancillary algorithm (always done).
    if name == "SGD":
        if kwargs["risk_name"] == "entropic":
            algo = GD_ERM_Tilted(tilt=kwargs["gamma"],
                                 step_coef=kwargs["step_size"],
                                 model=model,
                                 loss=loss)
        elif kwargs["risk_name"] == "dro":
            bound, shape = parse_dro(atilde=kwargs["atilde"])
            algo = GD_ERM_DRO_CR(bound=bound,
                                 shape=shape,
                                 step_coef=kwargs["step_size"],
                                 model=model,
                                 loss=loss)
        else:
            algo = GD_ERM(step_coef=kwargs["step_size"],
                          model=model,
                          loss=loss)
    else:
        raise ValueError("Please pass a valid algorithm name.")

    ## Setup of the main algorithm (done only when specified).
    if name_main is None or name_main == "":
        algo_main = None
    else:
        if name_main == "Ave":
            algo_main = Weighted_Average(model_main=model_main,
                                         model_ancillary=model)
        else:
            raise ValueError("Please pass a valid main algorithm name.")
    
    return (algo, algo_main)

                      

###############################################################################
