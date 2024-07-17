'''
A BaseModel class that all the other models (including user custom models) are built
on. This allows for more flexibility and customization in the package.
'''
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
import numpy as np

class _SyncfitModelMeta(type):
    '''
    This just gives all the subclasses for BaseModel the same docstrings
    for the inherited abstract methods
    '''
    def __new__(mcls, classname, bases, cls_dict):
        cls = super().__new__(mcls, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__'):
                member.__doc__ = getattr(bases[-1], name).__doc__
        return cls

class SyncfitModel(object, metaclass=_SyncfitModelMeta):
    '''
    An Abstract Base Class to define the basic methods that all syncfit
    models must contain. This will help maintain some level of standard for the models
    while also allowing users to customize their own.
    '''

    # Write some getters for things that are model specific
    # THESE WILL BE THE SAME ACROSS ALL MODELS!
    @staticmethod
    def get_pos(theta_init:list, nwalkers:int) -> list[float]:
        '''
        Gets the initial position of all of the walkers assuming a gaussian distribution
        centered at theta_init.

        Args:
            theta_init (list): Initial location of the walkers
            nwalkers (int): Number of walkers

        Returns:
            A 2D array of the positions of all of the walkers
        '''
        ndim = len(theta_init)
        if not isinstance(theta_init, np.ndarray):
            theta_init = np.array(theta_init)

        diff = 0.01 # The amount to offset by, so 1 will give random pos between -1 and 1
        pos_offset = np.random.rand(nwalkers, ndim)*diff*2 - diff # *2 - 1 to put between -1 and 1 instead of 0 and 1
        pos = theta_init + pos_offset # this will offset the initial positions by pos_offset
        
        return pos

    @staticmethod
    def get_kwargs(nu:list, F_mJy:list, F_error:list, lum_dist:float=None,
                       t:float=None, p:float=None, upperlimit:list=None) -> dict:
        '''
        Packages up the args to be passed into the model based on the user input.

        Args:
            nu (list): frequencies in GHz
            F_mJy (list): Fluxes in milli janskies
            F_error (list): Flux errors in milli janskies
            p (float): A p-value to pass to the model, only used if p-value is fixed

        Returns:
            Dictionary of values, converted for the modeling used in the mcmc
        '''
        nu = 1e9*nu
        F = np.array(F_mJy).astype(float)
        F_error = np.array(F_error)

        base_args = {'nu':nu, 'F':F, 'F_error':F_error, 'upperlimit':upperlimit} 
        
        if p is not None:
            base_args['p'] = p

        if lum_dist is not None:
            base_args['lum_dist'] = lum_dist

        if t is not None:
            base_args['t'] = t
            
        return base_args

    # package those up for easy getting in do_emcee
    @classmethod
    def unpack_util(cls, theta_init, nu, F_mJy, F_error, nwalkers, lum_dist=None,
                    t=None, p=None, upperlimit=None):
        '''
        A wrapper on the utility functions.

        Args:
            theta_init (list): List of initial theta locations
            nu (list): frequencies in GHz
            F_mJy (list): Fluxes in milli janskies
            F_error (list): Flux errors in milli janskies
            p (float): A p-value to pass to the model, only used if p-value is fixed
            nwalkers (int): THe number of walkers to use
        '''
        return (cls.get_pos(theta_init,nwalkers),
                cls.get_labels(p=p),
                cls.get_kwargs(nu, F_mJy, F_error, p, upperlimit))

    @classmethod
    def lnprob(cls, theta:list, **kwargs):
        '''Keep or throw away step likelihood and priors

        Args:
            theta (list): location of the walker
            **kwargs: Any other arguments to be past to lnprior or loglik

        Returns:
            The likelihood of the data at that location
        '''
        lp = cls.lnprior(theta, **kwargs)
        if not np.isfinite(lp):
            return -np.inf
        else:
            return lp + cls.loglik(theta, **kwargs)

    @classmethod
    def loglik(cls, theta, nu, F, F_error, p=None, **kwargs):
        '''Log Likelihood function

        Args:
            theta (list): position of the walker
            nu (list): frequencies in GHz
            F_muJy (list): Fluxes in micro janskies
            F_error (list): Flux errors in micro janskies
            p (float): A p-value to pass to the model, only used if p-value is fixed

        Returns:
            The logarithmic likelihood of that theta position
        '''
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            if p is not None:
                model_result = cls.SED(nu, p, *theta, **kwargs)
            else:
                model_result = cls.SED(nu, *theta, **kwargs)

        if not np.any(np.isfinite(model_result)):
            ll = -np.inf
        else:    
            sigma2 = F_error**2
        
            chi2 = np.sum((F - model_result)**2/sigma2)
            ll = -0.5*chi2
        
        return ll

    @staticmethod
    def _is_below_upperlimits(nu, F, upperlimits, theta, model, p=None):
        '''
        Checks that the location of theta is below any upperlimits
        '''

        if upperlimits is None:
            return True
        
        where_upperlimit = np.where(upperlimits)[0]
        F_upperlimits = F[where_upperlimit]

        if p is None:
            test_fluxes = model(nu, *theta)[where_upperlimit]
        else:
            test_fluxes = model(nu, p, *theta)[where_upperlimit]

        return np.all(F_upperlimits > test_fluxes)
    
    # Some *required* abstract methods
    @staticmethod
    @abstractmethod
    def get_labels(*args, **kwargs):
        '''
        Describes a list of labels used in the return values of the mcmc chain.
        This varies depending on the inputs to the MCMC.
        '''
        pass
        
    @staticmethod
    @abstractmethod
    def SED(*args, **kwargs):
        '''
        Describes the SED model for the model that subclasses this BaseModel
        '''
        pass
    
    @staticmethod
    @abstractmethod
    def lnprior(*args, **kwargs):
        '''
        Logarithmic prior function that can be changed based on the SED model.
        '''
        pass

    @staticmethod
    @abstractmethod
    def dynesty_transform(*args, **kwargs):
        '''
        Prior transformation function passed to dynesty
        '''
        pass
    
    # override __subclasshook__
    @classmethod
    def __subclasshook__(cls, C):
        reqs = ['SED', 'lnprior', 'get_labels']
        if cls is BaseModel:
            if all(any(arg in B.__dict__ for B in C.__mro__) for arg in reqs):
                return True
        return NotImplemented

    # add a register method so users don't have to create a new class
    @classmethod
    def override(cls,func):
        '''
        This method should be used as a decorator to override other methods 
        '''
        exec(f'cls.{func.__name__} = func')
