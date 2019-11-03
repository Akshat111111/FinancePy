# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 16:51:05 2016

@author: Dominic O'Kane
"""

from finutils.FinError import FinError
from products.bonds.FinBond import FinBond
from finutils.FinGlobalVariables import gDaysInYear
from enum import Enum
from math import sqrt, exp, log
from finutils.FinMath import N

###############################################################################


class FinBondOptionModel(Enum):
    HO_LEE = 2
    HULL_WHITE = 3


class FinBondOptionTypes(Enum):
    EUROPEAN_CALL = 1
    EUROPEAN_PUT = 2

###############################################################################
###############################################################################


class FinBondOption():
    ''' Class for options on fixed coupon bonds. '''

    def __init__(self,
                 maturityDate,
                 coupon,
                 frequencyType,
                 accrualType,
                 expiryDate,
                 strikePrice):

        self._expiryDate = expiryDate
        self._strikePrice = strikePrice
        self._bond = FinBond(maturityDate,
                             coupon,
                             frequencyType,
                             accrualType)

###############################################################################

    def value(self,
              valueDate,
              discountCurve,
              modelType,
              modelParams,
              optionType):
        ''' Value the bond option using the specified model. '''

        t1 = (self._expiryDate - valueDate) / gDaysInYear
        t2 = (self._bond._maturityDate - valueDate) / gDaysInYear
        K = self._strike

        if self._bond._coupon == 0.0:
            # A zero coupon bond can be priced using either Ho-Lee or
            # Hull-White

            if modelType == FinShortRateModel.HO_LEE:
                sigma = modelParams[0]
                sigmaP = sigma * (t2 - t1) * sqrt(t1)
            elif modelType == FinShortRateModel.HULL_WHITE:
                a = modelParams[0]
                term1 = (1.0 - exp(-a * (t2 - t1)))
                term2 = (1.0 - exp(-2.0 * a * t1)) / 2.0 / a
                sigmaP = sigma * term1 * sqrt(term2) / a
            else:
                raise FinError("Unknown Model Type " + str(modelType))

            L = 1.0
            pt2 = discountCurve.df(t2)
            pt1 = discountCurve.df(t1)
            h = log(L * pt2 / pt1 / self._strikePrice) / sigmaP + sigmaP / 2.0

            if optionType == FinBondOptionTypes.EUROPEAN_CALL:
                v = L * pt2 * N(h) - K * pt1 * N(h - sigmaP)
            else:
                v = K * pt1 * N(-h + sigmaP) - L * pt2 * N(-h)

            return v

        else:
            # JAMSHIDIAN MODEL
            v = 0.0

        return v
