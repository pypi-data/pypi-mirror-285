import numpy as np, pandas as pd
from .utils import wtdquantile, rearrange_cvar, goldsectmax
from .IF_calculate import IF

import pandas as pd


def cvar_if(
    data,
    p,
    q,
    mu1_col="mu1",
    mu0_col="mu0",
    A_col="A",
    ipw_col="ipw",
    Y_col="Y",
    tau="tau",
):
    """
    Calculate the conditional value at risk and inverse propensity weighting for a given dataset
    Args:
       data: pandas DataFrame containing the dataset.
       p: float, the confidence level for the conditional value at risk.
       q: float, The confidence level for the inverse propensity weighting.
       mu1_col: str, The column name for the treatment group mean.
       mu0_col: str, The column name for the control group mean.
       A_col: str, The column name for the treatment indicator.
       ipw_col: str, The column name for the inverse propensity weighting.
       Y_col: str, The column name for the outcome variable.
       tau: str, The column name for the treatment effect.

    """

    difference = data[mu1_col] - data[mu0_col]
    weighted_difference = (
        (2 * data[A_col] - 1)
        * data[ipw_col]
        * (
            data[Y_col]
            - data[A_col] * data[mu1_col]
            - (1 - data[A_col]) * data[mu0_col]
        )
    )
    condition = data[tau] <= q

    # Calculation
    result = q + (difference + weighted_difference - q) * (condition) / p

    return result


def cvar_if_plugin(data, p, q, tau="tau"):
    """
    Calculate the conditional value at risk for a given tau using plugin estimation
    Args:
      data: DataFrame containing the data.
      p: Probability of the event.
      q: Quantile value.
      tau: Column name for the quantile values.
    Returns:
     Conditional value at risk for the given tau using plugin estimation.
    """
    # Intermediate calculations
    tau_values = data[tau]
    condition = tau_values <= q

    # Calculation
    result = q + (tau_values - q) * condition / p

    return result


def cvar_if_tauate(
    data, p, q, mu1="mu1", mu0="mu0", A="A", ipw="ipw", Y="Y", tau="tau"
):
    """
    Calculate the conditional value at risk for a given tau using inverse propensity weighting
    Args:
        data: DataFrame containing the necessary columns.
        p: The quantile value for which to calculate the CVa.
        q: The quantile value for which to calculate the CVAR.
        mu1: The column name for the treatment group mean.
        mu0: The column name for the control group mean.
        A: The column name for the treatment indicator.
        Y: The column name for the outcome variable.
        tau: The column name for the treatment effect
    Returns:
        The conditional value at risk for the given tau using inverse propensity weighting.
    """
    # Extract columns from DataFrame
    mu1_values = data[mu1]
    mu0_values = data[mu0]
    A_values = data[A]
    ipw_values = data[ipw]
    Y_values = data[Y]
    tau_values = data[tau]

    # Intermediate calculations
    difference = mu1_values - mu0_values
    weighted_difference = (
        (2 * A_values - 1)
        * ipw_values
        * (Y_values - A_values * mu1_values - (1 - A_values) * mu0_values)
    )
    condition = tau_values <= q

    # Calculation
    result = (
        q
        + (difference + weighted_difference) * (condition / p - 1)
        - q * (condition / p)
    )

    return result


def cvar_if_bbouns_ate1(
    data,
    p,
    q,
    mu1="mu1",
    mu0="mu0",
    A="A",
    ipw="ipw",
    Y="Y",
    tau="tau",
    varsum01="varsum01",
    rho="rho",
    sdprod01="sdprod01",
):
    """
    Calculate the conditional value at risk (CVa) for a given dataset when bounds are applied and ate.
    Args:
        data (pd.DataFrame): The input dataset containing the relevant columns.
        p (float): The probability parameter.
        q (float): The quantile parameter.
        mu1 (str, optional): The column name for the treatment effect parameter mu1. Defaults to "mu1".
        mu0 (str, optional): The column name for the treatment effect parameter mu0. Defaults to "mu0".
        A (str, optional): The column name for the treatment indicator. Defaults to "A".
        ipw (str, optional): The column name for the inverse propensity weight. Defaults to "ipw".
        Y (str, optional): The column name for the outcome variable. Defaults to "Y".
        tau (str, optional): The column name for the treatment effect parameter. Defaults to "tau".
        varsum01(str, optional): The column name for the sum of treatment effects. Defaults to "varsum01".
        rho (str, optional): The column name for the treatment effect parameter. Defaults to "rho".
        sd (str, optional): The column name for the standard deviation of treatment effects. Defaults to "sd".
    Return:
        np.array: An array containing the treatment effects for each observation.
    """
    # Extract columns from DataFrame
    mu1_values = data[mu1]
    mu0_values = data[mu0]
    A_values = data[A]
    ipw_values = data[ipw]
    Y_values = data[Y]
    tau_values = data[tau]
    varsum01_values = data[varsum01]
    rho_values = data[rho]
    sdprod01_values = data[sdprod01]

    # Intermediate calculations

    weighted_difference = (
        (2 * A_values - 1)
        * ipw_values
        * (Y_values - A_values * mu1_values - (1 - A_values) * mu0_values)
    )

    sqrt_term = np.sqrt(
        (tau_values - q) ** 2 + varsum01_values - 2 * rho_values * sdprod01_values
    )

    # Calculation
    term1 = -weighted_difference
    term2 = (tau_values - q - sqrt_term) / (2 * p)
    term3 = (1 - (tau_values - q) / sqrt_term) * weighted_difference / (2 * p)

    result = term1 + q + term2 + term3

    return result


def cvar_bbound_mate(
    data, p, q, b, mu1="mu1", mu0="mu0", A="A", ipw="ipw", Y="Y", tau="tau"
):
    """
    Calculate the conditional value at risk for bounded treatment effects using a matrix-based approach
    Args:
        data (pd.DataFrame): Data containing the necessary columns for calculation
        p (float): Probability parameter for the bounded treatment effect model
        q (float): Quantile parameter for the bounded treatment effect model
        b (float): Bound parameter for the bounded treatment effect model
        mu1 (str, optional): Column name for the treatment effect parameter mu1. Defaults to "mu1".
        mu0 (str, optional): Column name for the treatment effect parameter mu0. Defaults to "mu0".
        A (str, optional): Column name for the treatment indicator variable. Defaults to "A".
        ipw (str, optional): Column name for the inverse propensity score. Defaults to "ipw".
        Y (str, optional): Column name for the outcome variable. Defaults to "Y".
        tau (str, optional): Column name for the treatment effect parameter. Defaults to "tau".
    Returns:
       np.array: Estimated treatment effect using the bounded treatment effect model
    """
    # Extract columns from DataFrame
    mu1_values = data[mu1]
    mu0_values = data[mu0]
    A_values = data[A]
    ipw_values = data[ipw]
    Y_values = data[Y]
    tau_values = data[tau]

    # Intermediate calculations
    weighted_difference = (
        (2 * A_values - 1)
        * ipw_values
        * (Y_values - A_values * mu1_values - (1 - A_values) * mu0_values)
    )
    mu = mu1_values - mu0_values
    condition = tau_values - b <= q

    # Calculation
    result = (
        -(mu + weighted_difference)
        + q
        + (mu + weighted_difference - q - b) * condition / (2 * p)
        + (mu + weighted_difference - q + b) * condition / (2 * p)
    )

    return result


def cvar_calculate(data, p, tau="tau", sw="sw", method_if=cvar_if, b=None):
    """
    Calculates the Conditional Value at Risk (CVaR) and its standard error (CVaR_se) for a given dataset.

    Parameters:
    -----------
    data : DataFrame
        The DataFrame containing the input data.
    p : float
        The desired percentile for the CVaR calculation.
    tau : str, optional
        The name of the column in the DataFrame that contains the tau values (default is "tau").
    sw : str, optional
        The name of the column in the DataFrame that contains the weights (default is "sw").
    method_if : function, optional
        The function to use for calculating the IF (Influence Function). The default is `cvar_if`.
    b : float, optional
        An optional value for the parameter b. If provided, `cvar_bbound_mate` is used instead of `method_if`.

    Returns:
    --------
    result : DataFrame
        A DataFrame with the following columns:
        - CVaR : The calculated Conditional Value at Risk.
        - CVaR_se : The standard error of the CVaR.
        - p : The percentile used for the CVaR calculation
    """
    # Extract columns from DataFrame
    tau_ref = data[tau]
    sw_ref = data[sw]

    # Calculate q using weighted quantile
    q = wtdquantile(tau_ref, sw_ref, p)

    # Calculate IF using the specified method_if function
    if b is not None:
        IF = cvar_bbound_mate(data, p, q, b, tau=tau)
    else:
        IF = method_if(data, p, q, tau=tau)

    # Calculate cvar and CVaR
    cvar = IF * sw_ref
    CVaR = np.nanmean(cvar)
    CVaR_se = np.nanstd(cvar) / np.sqrt(data.shape[0])

    # Return results as a DataFrame (assuming you want to return results in a structured format)
    result = pd.DataFrame({"CVaR": [CVaR], "CVaR_se": [CVaR_se], "p": [p]})

    if b is not None:
        result["b"] = [b]

    return result


def IF_bbound_mate(
    q,
    p,
    b,
    data,
    mu1_col="mu1",
    mu0_col="mu0",
    A_col="A",
    ipw_col="ipw",
    Y_col="Y",
    tau_col="tau",
):
    """
    Calculates the Influence Function (IF) with bounded bias for a given dataset.

    Parameters:
    -----------
    q : float
        The quantile value.
    p : float
        The desired percentile.
    b : float
        The bound for the bias.
    data : DataFrame
        The DataFrame containing the input data.
    mu1_col : str, optional
        The name of the column in the DataFrame that contains mu1 values (default is "mu1").
    mu0_col : str, optional
        The name of the column in the DataFrame that contains mu0 values (default is "mu0").
    A_col : str, optional
        The name of the column in the DataFrame that contains A values (default is "A").
    ipw_col : str, optional
        The name of the column in the DataFrame that contains inverse probability weights (default is "ipw").
    Y_col : str, optional
        The name of the column in the DataFrame that contains outcome values (default is "Y").
    tau_col : str, optional
        The name of the column in the DataFrame that contains tau values (default is "tau").

    Returns:
    --------
    result : Series
        A Series containing the calculated Influence Function values for each row in the DataFrame.
    """

    mu1 = data[mu1_col]
    mu0 = data[mu0_col]
    A = data[A_col]
    ipw = data[ipw_col]
    Y = data[Y_col]
    tau = data[tau_col]

    weighted_difference = (2 * A - 1) * ipw * (Y - A * mu1 - (1 - A) * mu0)
    mu = mu1 - mu0
    condition = tau - b <= q

    result = (
        -(mu + weighted_difference)
        + q
        + (mu + weighted_difference - q - b) * condition / (2 * p)
        + (mu + weighted_difference - q + b) * condition / (2 * p)
    )

    return result


def cvar_bbound_mate(
    data, ps: np.array, bs: np.array, tau_col="tau", sw_col="sw", sort_cvar=True
):
    """
    Calculates the Conditional Value at Risk (CVaR) with bounded bias for given datasets and parameters.

    Parameters:
    -----------
    data : DataFrame
        The DataFrame containing the input data.
    ps : np.array
        An array of percentiles for which to calculate the CVaR.
    bs : np.array
        An array of bias bounds.
    tau_col : str, optional
        The name of the column in the DataFrame that contains tau values (default is "tau").
    sw_col : str, optional
        The name of the column in the DataFrame that contains weight values (default is "sw").
    sort_cvar : bool, optional
        If True, sorts the CVaR values within each bias bound (default is True).

    Returns:
    --------
    results : DataFrame
        A DataFrame with the following columns:
        - CVaR : The calculated Conditional Value at Risk.
        - CVaR_se : The standard error of the CVaR.
        - p : The percentile used for the CVaR calculation.
        - b : The bias bound.

    """
    tau = data[tau_col]
    sw = data[sw_col]

    sw1 = np.concatenate((sw, sw))
    results = pd.DataFrame()

    for b in bs:
        tau1 = np.concatenate((tau + b, tau - b))
        for p in ps:
            q = wtdquantile(tau1, sw1, p)
            IF = IF_bbound_mate(q, p, b, data)
            cvar = IF * sw
            CVaR = np.nanmean(cvar)
            CVaR_se = np.nanstd(cvar) / np.sqrt(len(sw))
            result = pd.DataFrame({"CVaR": [CVaR], "CVaR_se": [CVaR_se], "p": [p]})

            if b is not None:
                result["b"] = [b]

            results = pd.concat((results, result))
    # results = results.round(2)
    if sort_cvar:
        n_results = results.copy()
        n_results["CVaR"] = n_results.groupby("b")["CVaR"].transform(rearrange_cvar)
        return n_results
    return results


def IF_cvar_bbouns_ate(
    data: pd.DataFrame,
    p: float,
    q: float,
    rho: float,
    mu1_col="mu1",
    mu0_col="mu0",
    A_col="A",
    ipw_col="ipw",
    Y_col="Y",
    tau_col="tau",
    varsum01_col="varsum01",
    sdprod01_col="sdprod01",
):
    """
    Calculates the Influence Function (IF) for CVaR with bounded bias and average treatment effect (ATE) for a given dataset.

    Parameters:
    -----------
    data : DataFrame
        The DataFrame containing the input data.
    p : float
        The desired percentile.
    q : float
        The quantile value.
    rho : float
        The correlation coefficient.
    mu1_col : str, optional
        The name of the column in the DataFrame that contains mu1 values (default is "mu1").
    mu0_col : str, optional
        The name of the column in the DataFrame that contains mu0 values (default is "mu0").
    A_col : str, optional
        The name of the column in the DataFrame that contains A values (default is "A").
    ipw_col : str, optional
        The name of the column in the DataFrame that contains inverse probability weights (default is "ipw").
    Y_col : str, optional
        The name of the column in the DataFrame that contains outcome values (default is "Y").
    tau_col : str, optional
        The name of the column in the DataFrame that contains tau values (default is "tau").
    varsum01_col : str, optional
        The name of the column in the DataFrame that contains the sum of variances (default is "varsum01").
    sdprod01_col : str, optional
        The name of the column in the DataFrame that contains the product of standard deviations (default is "sdprod01").

    Returns:
    --------
    result : Series
        A Series containing the calculated Influence Function values for each row in the DataFrame.

    """

    mu1 = data[mu1_col]
    mu0 = data[mu0_col]
    A = data[A_col]
    ipw = data[ipw_col]
    Y = data[Y_col]
    tau = data[tau_col]
    varsum01 = data[varsum01_col]
    sdprod01 = data[sdprod01_col]

    weighted_difference = (2 * A - 1) * ipw * (Y - A * mu1 - (1 - A) * mu0)
    sqrt_term = np.sqrt((tau - q) ** 2 + varsum01 - 2 * rho * sdprod01)

    term1 = -weighted_difference
    term2 = (tau - q - sqrt_term) / (2 * p)
    term3 = (1 - (tau - q) / sqrt_term) * weighted_difference / (2 * p)

    result = term1 + q + term2 + term3
    # if
    return result
