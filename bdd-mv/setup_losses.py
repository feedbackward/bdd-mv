'''Setup: loss functions used for training and evaluation.'''

## External modules.
from copy import deepcopy
import numpy as np

## Internal modules.
from mml.losses import Loss
from mml.losses.absolute import Absolute
from mml.losses.classification import Zero_One
from mml.losses.cvar import CVaR
from mml.losses.dro import DRO_CR
from mml.losses.logistic import Logistic
from mml.losses.quadratic import Quadratic
from mml.utils.mest import est_loc_fixedpt


###############################################################################


## Special loss class definitions.


class MV_Huber(Loss):
    '''
    The modified loss underlying mean-variance minimization
    using simultaneous settings of location and scale, using a
    pseudo-Huber type of dispersion function for robustness.
    Takes an arbitrary base loss and transforms it.
    '''
    def __init__(self, loss_base,
                 alpha=None, beta=None, lam=None,
                 name=None):
        loss_name = "MV_Huber x {}".format(str(loss_base))
        super().__init__(name=loss_name)
        self.loss = loss_base
        self.alpha = alpha
        self.beta = beta
        self.lam = lam
        return None
    
    
    def func(self, model, X, y):
        '''
        '''
        losses = self.loss(model=model, X=X, y=y) # compute losses.
        location = model.paras["location"].item() # extract scalar.
        scale = model.paras["scale"].item() # extract scalar.
        val = np.sqrt((losses-location)**2+scale**2) - scale
        return self.alpha*location + self.beta*scale + self.lam*val

    
    def grad(self, model, X, y):
        '''
        '''
        
        ## Initial computations.
        losses = self.loss(model=model, X=X, y=y) # compute losses.
        location = model.paras["location"].item() # extract scalar.
        scale = model.paras["scale"].item() # extract scalar.
        loss_grads = self.loss.grad(model=model, X=X, y=y) # loss gradients.
        diffs = losses-location
        denom = np.sqrt(diffs**2 + scale**2)
        dispersion_grads = self.lam * diffs / denom
        location_grads = self.alpha - self.lam * diffs / denom
        scale_grads = self.lam * scale / denom + self.beta - self.lam * 1.0
        ddim = dispersion_grads.ndim
        ldim = model.paras["location"].ndim
        sdim = model.paras["scale"].ndim
        
        ## Gradient computations (WRT primary parameter).
        for pn, g in loss_grads.items():
            gdim = g.ndim
            if ddim > gdim:
                raise ValueError("Axis dimensions are wrong; ddim > gdim.")
            elif ddim < gdim:
                dispersion_grads_exp = np.expand_dims(
                    a=dispersion_grads,
                    axis=tuple(range(ddim,gdim))
                )
                g *= dispersion_grads_exp
            else:
                g *= dispersion_grads
        
        ## Gradient computations (WRT location).
        loss_grads["location"] = np.expand_dims(
            a=location_grads,
            axis=tuple(range(ddim,1+ldim))
        )
        
        ## Gradient computations (WRT scale).
        loss_grads["scale"] = np.expand_dims(
            a=scale_grads,
            axis=tuple(range(ddim,1+sdim))
        )
        
        ## Return gradients for all parameters being optimized.
        return loss_grads





class ConvexPolynomial(Loss):
    '''
    '''
    
    def __init__(self, exponent, name=None):
        super().__init__(name=name)
        self.exponent = exponent
        if self.exponent < 1.0:
            raise ValueError("This class only takes exponent >= 1.0.")
        return None

    
    def func(self, model, X, y):
        '''
        '''
        abdiffs = np.absolute(model(X=X)-y)
        if self.exponent == 1.0:
            return abdiffs
        else:
            return abdiffs**self.exponent / self.exponent
    
    
    def grad(self, model, X, y):
        '''
        '''
        
        loss_grads = deepcopy(model.grad(X=X)) # start with model grads.
        diffs = model(X=X)-y
        
        if self.exponent == 1.0:
            factors = np.sign(diffs)
        else:
            factors = np.absolute(diffs)**(self.exponent-1.0) * np.sign(diffs)
        
        ## Shape check to be safe.
        if factors.ndim != 2:
            raise ValueError("Require model(X)-y to have shape (n,1).")
        elif factors.shape[1] != 1:
            raise ValueError("Only implemented for single-output models.")
        else:
            for pn, g in loss_grads.items():
                g *= np.expand_dims(a=factors,
                                    axis=tuple(range(2,g.ndim)))
        return loss_grads


## Parser function for setting the DRO_CR parameters.
def parse_dro(atilde):
    shape = 2.0
    bound = ((1.0/(1.0-atilde))-1.0)**2.0 / 2.0
    return (bound, shape)


## Parser function for threshold setters.
def parse_threshold_setter(name, dispersion_d1=None, sigma=None):
    if name == "mean":
        return lambda x: np.mean(x)
    elif name == "median":
        return lambda x: np.median(x)
    elif name == "mest":
        if dispersion_d1 is None or sigma is None:
            s_error = "Missing dispersion_d1 or sigma for M-estimation."
            raise ValueError(s_error)
        else:
            inf_fn = lambda x: dispersion_d1(x=x, sigma=1.0)
            return lambda x: est_loc_fixedpt(X=x, s=sigma,
                                             inf_fn=inf_fn)
    else:
        s_error = "Did not recognize threshold setter {}".format(name)
        raise ValueError(s_error)


## Grab the desired loss object.

dict_losses = {
    "absolute": Absolute(name="absolute"),
    "logistic": Logistic(name="logistic"),
    "quadratic": Quadratic(name="quadratic"),
    "zeroone": Zero_One(name="zeroone")
}

def get_loss(name, **kwargs):
    '''
    A simple parser that takes a base loss and risk name,
    and returns the loss object that amounts to an unbiased
    estimator of the specified risk.
    '''

    ## First grab the loss and risk name, with a check.
    try:
        loss_base = dict_losses[name]
        risk_name = kwargs["risk_name"]
    except KeyError:
        print("Error: either loss is invalid or risk is missing.")
    
    ## Prepare and return the modified loss object as requested.
    if risk_name == "erm":
        loss = loss_base

    elif risk_name == "mvHuber":
        loss = MV_Huber(loss_base=loss_base,
                        alpha=kwargs["alpha"],
                        beta=kwargs["beta"],
                        lam=kwargs["lam"])
    
    elif risk_name == "cvar":
        loss = CVaR(loss_base=loss_base,
                    alpha=1.0-kwargs["prob"])
    
    elif risk_name == "dro":
        bound, shape = parse_dro(atilde=kwargs["atilde"])
        loss = DRO_CR(loss_base=loss_base, bound=bound, shape=shape)
    
    else:
        raise ValueError("Invalid risk name.")

    ## Finally, return both the base loss and the modified loss.
    return (loss_base, loss)


###############################################################################
