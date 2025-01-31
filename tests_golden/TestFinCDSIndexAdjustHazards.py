###############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
###############################################################################

import sys
sys.path.append("..")

from FinTestCases import FinTestCases, globalTestCaseMode
from financepy.utils.global_types import SwapTypes
from financepy.utils.date import Date
from financepy.utils.day_count import DayCountTypes
from financepy.utils.frequency import FrequencyTypes
from financepy.products.credit.cds_curve import CDSCurve
from financepy.products.rates.ibor_single_curve import IborSingleCurve
from financepy.products.rates.ibor_swap import IborSwap
from financepy.products.credit.cds import CDS
from financepy.products.credit.cds_index_portfolio import CDSIndexPortfolio
from os.path import dirname, join

test_cases = FinTestCases(__file__, globalTestCaseMode)

##########################################################################
# TO DO
##########################################################################


def build_Ibor_Curve(tradeDate):

    value_dt = tradeDate.add_days(1)
    dcType = DayCountTypes.ACT_360

    depos = []
    fras = []
    swaps = []

    dcType = DayCountTypes.THIRTY_E_360_ISDA
    fixedFreq = FrequencyTypes.SEMI_ANNUAL
    settle_dt = value_dt

    maturity_dt = settle_dt.add_months(12)
    swap1 = IborSwap(
        settle_dt,
        maturity_dt,
        SwapTypes.PAY,
        0.0502,
        fixedFreq,
        dcType)
    swaps.append(swap1)

    maturity_dt = settle_dt.add_months(24)
    swap2 = IborSwap(
        settle_dt,
        maturity_dt,
        SwapTypes.PAY,
        0.0502,
        fixedFreq,
        dcType)
    swaps.append(swap2)

    maturity_dt = settle_dt.add_months(36)
    swap3 = IborSwap(
        settle_dt,
        maturity_dt,
        SwapTypes.PAY,
        0.0501,
        fixedFreq,
        dcType)
    swaps.append(swap3)

    maturity_dt = settle_dt.add_months(48)
    swap4 = IborSwap(
        settle_dt,
        maturity_dt,
        SwapTypes.PAY,
        0.0502,
        fixedFreq,
        dcType)
    swaps.append(swap4)

    maturity_dt = settle_dt.add_months(60)
    swap5 = IborSwap(
        settle_dt,
        maturity_dt,
        SwapTypes.PAY,
        0.0501,
        fixedFreq,
        dcType)
    swaps.append(swap5)

    libor_curve = IborSingleCurve(value_dt, depos, fras, swaps)

    return libor_curve

##########################################################################


def buildIssuerCurve(tradeDate, libor_curve):

    value_dt = tradeDate.add_days(1)

    cdsMarketContracts = []

    cds_coupon = 0.0048375
    maturity_dt = Date(29, 6, 2010)
    cds = CDS(value_dt, maturity_dt, cds_coupon)
    cdsMarketContracts.append(cds)

    recovery_rate = 0.40

    issuer_curve = CDSCurve(value_dt,
                            cdsMarketContracts,
                            libor_curve,
                            recovery_rate)

    return issuer_curve

##########################################################################


def test_performCDSIndexHazardRateAdjustment():

    tradeDate = Date(1, 8, 2007)
    step_in_dt = tradeDate.add_days(1)
    value_dt = step_in_dt

    libor_curve = build_Ibor_Curve(tradeDate)

    maturity3Y = tradeDate.next_cds_date(36)
    maturity5Y = tradeDate.next_cds_date(60)
    maturity7Y = tradeDate.next_cds_date(84)
    maturity10Y = tradeDate.next_cds_date(120)

    path = dirname(__file__)
    filename = "CDX_NA_IG_S7_SPREADS.csv"
    full_filename_path = join(path, "data", filename)
    f = open(full_filename_path, 'r')

    data = f.readlines()
    issuer_curves = []

    for row in data[1:]:

        splitRow = row.split(",")
        spd3Y = float(splitRow[1]) / 10000.0
        spd5Y = float(splitRow[2]) / 10000.0
        spd7Y = float(splitRow[3]) / 10000.0
        spd10Y = float(splitRow[4]) / 10000.0
        recovery_rate = float(splitRow[5])

        cds3Y = CDS(step_in_dt, maturity3Y, spd3Y)
        cds5Y = CDS(step_in_dt, maturity5Y, spd5Y)
        cds7Y = CDS(step_in_dt, maturity7Y, spd7Y)
        cds10Y = CDS(step_in_dt, maturity10Y, spd10Y)
        cds_contracts = [cds3Y, cds5Y, cds7Y, cds10Y]

        issuer_curve = CDSCurve(value_dt,
                                cds_contracts,
                                libor_curve,
                                recovery_rate)

        issuer_curves.append(issuer_curve)

    ##########################################################################
    # Now determine the average spread of the index
    ##########################################################################

    cdsIndex = CDSIndexPortfolio()

    averageSpd3Y = cdsIndex.average_spread(value_dt,
                                           step_in_dt,
                                           maturity3Y,
                                           issuer_curves) * 10000.0

    averageSpd5Y = cdsIndex.average_spread(value_dt,
                                           step_in_dt,
                                           maturity5Y,
                                           issuer_curves) * 10000.0

    averageSpd7Y = cdsIndex.average_spread(value_dt,
                                           step_in_dt,
                                           maturity7Y,
                                           issuer_curves) * 10000.0

    averageSpd10Y = cdsIndex.average_spread(value_dt,
                                            step_in_dt,
                                            maturity10Y,
                                            issuer_curves) * 10000.0

    test_cases.header("LABEL", "VALUE")
    test_cases.print("AVERAGE SPD 3Y", averageSpd3Y)
    test_cases.print("AVERAGE SPD 5Y", averageSpd5Y)
    test_cases.print("AVERAGE SPD 7Y", averageSpd7Y)
    test_cases.print("AVERAGE SPD 10Y", averageSpd10Y)
    test_cases.banner(
        "===================================================================")

    ##########################################################################
    # Now determine the intrinsic spread of the index to same maturity dates
    # As the single name CDS contracts
    ##########################################################################

    cdsIndex = CDSIndexPortfolio()

    intrinsicSpd3Y = cdsIndex.intrinsic_spread(value_dt,
                                               step_in_dt,
                                               maturity3Y,
                                               issuer_curves) * 10000.0

    intrinsicSpd5Y = cdsIndex.intrinsic_spread(value_dt,
                                               step_in_dt,
                                               maturity5Y,
                                               issuer_curves) * 10000.0

    intrinsicSpd7Y = cdsIndex.intrinsic_spread(value_dt,
                                               step_in_dt,
                                               maturity7Y,
                                               issuer_curves) * 10000.0

    intrinsicSpd10Y = cdsIndex.intrinsic_spread(value_dt,
                                                step_in_dt,
                                                maturity10Y,
                                                issuer_curves) * 10000.0

    ##########################################################################
    ##########################################################################

    test_cases.header("LABEL", "VALUE")
    test_cases.print("INTRINSIC SPD 3Y", intrinsicSpd3Y)
    test_cases.print("INTRINSIC SPD 5Y", intrinsicSpd5Y)
    test_cases.print("INTRINSIC SPD 7Y", intrinsicSpd7Y)
    test_cases.print("INTRINSIC SPD 10Y", intrinsicSpd10Y)
    test_cases.banner(
        "===================================================================")

    ##########################################################################
    ##########################################################################

    index_cpns = [0.002, 0.0037, 0.0050, 0.0063]
    index_upfronts = [0.0, 0.0, 0.0, 0.0]

    index_maturity_dts = [Date(20, 12, 2009),
                            Date(20, 12, 2011),
                            Date(20, 12, 2013),
                            Date(20, 12, 2016)]

    index_recoveryRate = 0.40

    tolerance = 1e-4  # should be smaller

    import time
    start = time.time()

    indexPortfolio = CDSIndexPortfolio()
    adjustedIssuerCurves = indexPortfolio.hazard_rate_adjust_intrinsic(
        value_dt,
        issuer_curves,
        index_cpns,
        index_upfronts,
        index_maturity_dts,
        index_recoveryRate,
        tolerance)

    end = time.time()
    test_cases.header("TIME")
    test_cases.print(end - start)

#    num_credits = len(issuer_curves)
#    test_cases.print("#","MATURITY","CDS_UNADJ","CDS_ADJ")
#    for m in range(0,num_credits):
#        for cds in cds_contracts:
#            unadjustedSpread = cds.par_spread(value_dt,issuer_curves[m])
#            adjustedSpread = cds.par_spread(value_dt,adjustedIssuerCurves[m])
#            test_cases.print(m,str(cds._maturity_dt),"%10.3f"%(unadjustedSpread*10000),"%10.3f" %(adjustedSpread*10000))

    cdsIndex = CDSIndexPortfolio()

    intrinsicSpd3Y = cdsIndex.intrinsic_spread(value_dt,
                                               step_in_dt,
                                               index_maturity_dts[0],
                                               adjustedIssuerCurves) * 10000.0

    intrinsicSpd5Y = cdsIndex.intrinsic_spread(value_dt,
                                               step_in_dt,
                                               index_maturity_dts[1],
                                               adjustedIssuerCurves) * 10000.0

    intrinsicSpd7Y = cdsIndex.intrinsic_spread(value_dt,
                                               step_in_dt,
                                               index_maturity_dts[2],
                                               adjustedIssuerCurves) * 10000.0

    intrinsicSpd10Y = cdsIndex.intrinsic_spread(value_dt,
                                                step_in_dt,
                                                index_maturity_dts[3],
                                                adjustedIssuerCurves) * 10000.0

    # If the adjustment works then this should equal the index spreads
    test_cases.header("LABEL", "VALUE")
    test_cases.print("ADJUSTED INTRINSIC SPD 3Y", intrinsicSpd3Y)
    test_cases.print("ADJUSTED INTRINSIC SPD 5Y", intrinsicSpd5Y)
    test_cases.print("ADJUSTED INTRINSIC SPD 7Y", intrinsicSpd7Y)
    test_cases.print("ADJUSTED INTRINSIC SPD 10Y", intrinsicSpd10Y)

###############################################################################


test_performCDSIndexHazardRateAdjustment()
test_cases.compareTestCases()
