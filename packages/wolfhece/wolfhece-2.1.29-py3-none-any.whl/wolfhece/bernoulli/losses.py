import numpy as np
from math import pi
from scipy.optimize import fsolve, newton, root, root_scalar
import matplotlib.pyplot as plt
from jax import grad, jit, numpy as jnp
import timeit

@jit
def _colebrook_white(f, k, diameter, reynolds):
    """
    Colebrook-White equation for friction factor

    @param f: float, friction factor [-]
    @param k: float, roughness of the pipe [m]
    @param diameter: float, diameter of the pipe [m]
    @param reynolds: float, Reynolds number [-]
    """
    return 1. / jnp.sqrt(f) + 2. * jnp.log10(k / (3.7 * diameter) + 2.51 / (reynolds * jnp.sqrt(f)))

""" Gradient of the Colebrook-White equation """
grad_colebrook_white = jit(grad(_colebrook_white))
""" Second derivative of the Colebrook-White equation """
grad2_colebrook_white = jit(grad(grad(_colebrook_white)))

def f_colebrook_white(f, k, diameter, reynolds):
    """
    Solve the Colebrook-White equation using Newton's method

    @param f: float, initial guess for the friction factor  [-]
    @param k: float, roughness of the pipe [m]
    @param diameter: float, diameter of the pipe [m]
    @param reynolds: float, Reynolds number [-]
    """
    f_sol = newton(_colebrook_white, f, grad_colebrook_white, args=(k, diameter, reynolds), rtol=1e-6)
    return f_sol.item()


# Test multiple solvers
def test_colebrook_fsolve():
    """ Test the Colebrook-White equation using Scipy fsolve """

    k= 1.e-4
    diam = .5
    viscosity = 1.e-6
    area = pi * (diam/2.)**2.
    discharge = 1.
    velocity = discharge / area
    reynolds = velocity * diam / viscosity

    f_guess = 0.02  # Initial guess for the friction factor
    f_sol = fsolve(_colebrook_white, f_guess, args=(k, diam, reynolds), xtol=1e-14)
    return f_sol[0]

def test_colebrook_root_scalar():
    """ Test the Colebrook-White equation using Scipy root_scalar """

    k= 1.e-4
    diam = .5
    viscosity = 1.e-6
    area = pi * (diam/2.)**2.
    discharge = 1.
    velocity = discharge / area
    reynolds = velocity * diam / viscosity

    f_guess = 0.02  # Initial guess for the friction factor
    f_sol = root_scalar(_colebrook_white, method='brentq', bracket=[0.,10.], x0 = f_guess, args=(k, diam, reynolds)) #, fprime = grad_colebrook_white, fprime2 = grad2_colebrook_white, xtol=1e-6)
    return f_sol.root

def test_colebrook_newton():
    """ Test the Colebrook-White equation using Scipy newton """

    k= 1.e-4
    diam = .5
    viscosity = 1.e-6
    area = pi * (diam/2.)**2.
    discharge = 1.
    velocity = discharge / area
    reynolds = velocity * diam / viscosity

    f_guess = 0.02  # Initial guess for the friction factor

    f_sol = newton(_colebrook_white, f_guess, grad_colebrook_white, args=(k, diam, reynolds), rtol=1e-6)
    return f_sol.item()


if __name__ == '__main__':

    trootscalar = timeit.timeit(test_colebrook_root_scalar, number = 1000)
    tfsolve     = timeit.timeit(test_colebrook_fsolve, number = 1000)
    tnewton     = timeit.timeit(test_colebrook_newton, number = 1000)

    trootscalar = test_colebrook_root_scalar()
    tfsolve     = test_colebrook_fsolve()
    tnewton     = test_colebrook_newton()

    sol_newton = f_colebrook_white(.02, 1.e-4, .5, 1/(pi*(.5/2.)**2.)*.5/1.e-6)

    assert sol_newton == tnewton

    pass
