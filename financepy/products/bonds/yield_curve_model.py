##############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
##############################################################################


import numpy as np
from scipy.interpolate import splev
from ...utils.helpers import label_to_string

###############################################################################


class FinCurveFitMethod():
    pass

###############################################################################


class CurveFitPolynomial():

    def __init__(self, power=3):
        self._parentType = FinCurveFitMethod
        self._power = power
        self._coeffs = []

    def _interpolated_yield(self, t):
        yld = np.polyval(self._coeffs, t)
        return yld

    def __repr__(self):
        s = label_to_string("OBJECT TYPE", type(self).__name__)
        s += label_to_string("Power", self._power)

        for c in self._coeffs:
            s += label_to_string("Coefficient", c)

        return s

    def _print(self):
        """ Simple print function for backward compatibility. """
        print(self)

###############################################################################


class CurveFitNelsonSiegel():

    def __init__(self, tau=None, bounds=[(-1, -1, -1, 0.5), (1, 1, 1, 100)]):
        self._parentType = FinCurveFitMethod
        self._beta_1 = None
        self._beta_2 = None
        self._beta_3 = None
        self._tau = tau
        """ Fairly permissive bounds. Only tau_1 is 1-100 """
        self._bounds = bounds

    def _interpolated_yield(self, t, beta_1=None, beta_2=None,
                            beta_3=None, tau=None):

        t = np.maximum(t, 1e-10)

        if beta_1 is None:
            beta_1 = self._beta_1

        if beta_2 is None:
            beta_2 = self._beta_2

        if beta_3 is None:
            beta_3 = self._beta_3

        if tau is None:
            tau = self._tau

        theta = t / tau
        expTerm = np.exp(-theta)
        yld = beta_1
        yld += beta_2 * (1.0 - expTerm) / theta
        yld += beta_3 * ((1.0 - expTerm) / theta - expTerm)
        return yld

    def __repr__(self):
        s = label_to_string("OBJECT TYPE", type(self).__name__)
        s += label_to_string("beta_1", self._beta_1)
        s += label_to_string("beta_2", self._beta_2)
        s += label_to_string("beta_3", self._beta_3)
        s += label_to_string("Tau", self._tau)
        return s

    def _print(self):
        """ Simple print function for backward compatibility. """
        print(self)

###############################################################################


class CurveFitNelsonSiegelSvensson():

    def __init__(self, tau_1=None, tau_2=None,
                 bounds=[(0, -1, -1, -1, 0, 1), (1, 1, 1, 1, 10, 100)]):
        """ Create object to store calibration and functional form of NSS
        parametric fit. """

        self._parentType = FinCurveFitMethod
        self._beta_1 = None
        self._beta_2 = None
        self._beta_3 = None
        self._beta_4 = None
        self._tau_1 = tau_1
        self._tau_2 = tau_2

        """ I impose some bounds to help ensure a sensible result if
        the user does not provide any bounds. Especially for tau_2. """
        self._bounds = bounds

    def _interpolated_yield(self, t, beta_1=None, beta_2=None, beta_3=None,
                            beta_4=None, tau_1=None, tau_2=None):

        # Careful if we get a time zero point
        t = np.maximum(t, 1e-10)

        if beta_1 is None:
            beta_1 = self._beta_1

        if beta_2 is None:
            beta_2 = self._beta_2

        if beta_3 is None:
            beta_3 = self._beta_3

        if beta_4 is None:
            beta_4 = self._beta_4

        if tau_1 is None:
            tau_1 = self._tau_1

        if tau_2 is None:
            tau_2 = self._tau_2

        theta1 = t / tau_1
        theta2 = t / tau_2
        expTerm1 = np.exp(-theta1)
        expTerm2 = np.exp(-theta2)
        yld = beta_1
        yld += beta_2 * (1.0 - expTerm1) / theta1
        yld += beta_3 * ((1.0 - expTerm1) / theta1 - expTerm1)
        yld += beta_4 * ((1.0 - expTerm2) / theta2 - expTerm2)
        return yld

    def __repr__(self):
        s = label_to_string("OBJECT TYPE", type(self).__name__)
        s += label_to_string("beta_1", self._beta_1)
        s += label_to_string("beta_2", self._beta_2)
        s += label_to_string("beta_3", self._beta_3)
        s += label_to_string("beta_4", self._beta_3)
        s += label_to_string("tau_1", self._tau_1)
        s += label_to_string("tau_2", self._tau_2)
        return s

    def _print(self):
        """ Simple print function for backward compatibility. """
        print(self)

###############################################################################


class CurveFitBSpline():

    def __init__(self, power=3, knots=[1, 3, 5, 10]):
        self._parentType = FinCurveFitMethod
        self._power = power
        self._knots = knots
        self._spline = None

    def _interpolated_yield(self, t):
        t = np.maximum(t, 1e-10)
        yld = splev(t, self._spline)
        return yld

    def __repr__(self):
        s = label_to_string("OBJECT TYPE", type(self).__name__)
        s += label_to_string("Power", self._power)
        s += label_to_string("Knots", self._knots)
        s += label_to_string("Spline", self._spline)
        return s

    def _print(self):
        """ Simple print function for backward compatibility. """
        print(self)

###############################################################################
