'''
Various models to use in MCMC fitting 
'''
import numpy as np
from .syncfit_model import SyncfitModel

class B1B2(SyncfitModel):
    '''
    Two-break model for the self-absorption break (nu_a) and the minimal energy break
    (nu_m). This model uses nu_m > nu_a, the opposite of the B4B5 model.
    '''

    def get_labels(p=None):
        if p is None:
            return ['p','log F_v', 'log nu_a','log nu_m']
        else:
            return ['log F_v', 'log nu_a','log nu_m']

    # the model, must be named SED!!!
    def SED(nu, p, log_F_nu, log_nu_a, log_nu_m, **kwargs):
        b1 = 2
        b2 = 1/3
        b3 = (1-p)/2

        s1 = 1.06
        s2 = 1.76-0.38*p

        F_nu = 10**log_F_nu
        nu_m = 10**log_nu_m
        nu_a = 10**log_nu_a

        term1 = ( (nu/nu_a)**(-s1*b1) + (nu/nu_a)**(-s1*b2) )**(-1/s1)
        term2 = ( 1 + (nu/nu_m)**(s2*(b2-b3)) )**(-1/s2)

        return F_nu * term1 * term2

    def lnprior(theta, nu, F, upperlimit, p=None, **kwargs):
        ''' Priors: '''
        uppertest = SyncfitModel._is_below_upperlimits(
            nu, F, upperlimit, theta, B1B2.SED, p=p
        )
        
        if p is None:
            p, log_F_nu, log_nu_a, log_nu_m = theta
        else:
            log_F_nu, log_nu_a, log_nu_m = theta

        if 2< p < 4 and -4 < log_F_nu < 2 and 6 < log_nu_a < 12 and log_nu_m > log_nu_a and uppertest:
            return 0.0

        else:
            return -np.inf


        def dynesty_transform(theta, nu, F, upperlimit, p=None, **kwargs):
            '''
            Prior transform for dynesty
            '''

            if p is None:
                p, log_F_nu, log_nu_a, log_nu_m = theta
                fixed_p = False,
            else:
                fixed_p = True
                log_F_nu, log_nu_a, log_nu_m = theta


            # log_F_nu between -4 and 2
            log_F_nu = log_F_nu*6 - 4

            # log_nu_a between 6 and 11
            log_nu_a = log_nu_a*5 + 6

            # same transform to log_nu_m
            log_nu_m = log_nu_m*5 + 6
            
            if not fixed_p:
                # p should be between 2 and 4
                p = 2*p + 2

                return p,log_F_nu,log_nu_a,log_nu_m
            return log_F_nu,log_nu_a,log_nu_m
