import numpy as np


def wtdquantile(y: np.array, SW: np.array, g: float):
    """
    The function `wtdquantile` calculates a weighted quantile of an array based on a given weight array
    and quantile level.

    :param y: The `y` parameter is expected to be a NumPy array containing the data values for which you
    want to calculate the weighted quantile
    :type y: np.array
    :param SW: np.array
    :type SW: np.array
    :param g: The parameter `g` in the `wtdquantile` function represents the quantile level you want to
    calculate.
    :type g: float
    :return: The function `wtdquantile` returns the weighted quantile of the input array `y` based on
    the weights in the array `SW` and the quantile level `g`.
    """
    Y = y.copy()
    sw = SW.copy()
    if g >= 1:
        return np.max(Y)
    o = np.argsort(Y)
    cum_w = np.cumsum(sw[o])
    cum_w = np.array(cum_w)
    threshold = np.sum(sw) * g
    idx = np.array(o[cum_w >= threshold])[0]
    return Y[idx]


def goldsectmax(f, a, b, tol=0.001, m=100):
    """
    The `goldsectmax` function implements the golden section search algorithm to find the maximum of a
    function within a specified interval.

    :param f: The `f` parameter in the `goldsectmax` function is a function that you want to optimize
    using the golden section search algorithm. This function should take a single input argument and
    return a numerical value. You can pass any function that meets this criteria to the `goldsectmax`
    function for
    :param a: The parameter `a` represents the lower bound of the interval within which the maximum of
    the function `f` is to be found
    :param b: The parameter `b` in the `goldsectmax` function represents the upper bound of the interval
    within which the maximum of the function `f` is to be found
    :param tol: The `tol` parameter in the `goldsectmax` function stands for the tolerance level. It
    determines the precision of the optimization algorithm. The algorithm will stop iterating once the
    difference between the upper and lower bounds (`b` and `a`) falls below this tolerance level
    :param m: The parameter `m` in the `goldsectmax` function represents the maximum number of
    iterations allowed for the algorithm to converge to a solution. If the number of iterations exceeds
    this limit without reaching the desired tolerance level `tol`, a warning message is printed
    indicating that the maximum iterations have been exceeded, defaults to 100 (optional)
    :return: The function `goldsectmax` returns the approximate maximum value of a given function `f`
    within the interval `[a, b]` using the golden section search method.
    """
    iter = 0
    phi = (np.sqrt(5) - 1) / 2
    a_star = b - phi * abs(b - a)
    b_star = a + phi * abs(b - a)

    while abs(b - a) > tol:
        iter += 1
        if iter > m:
            print("Warning: iterations maximum exceeded")
            break
        if f(a_star) > f(b_star):
            b = b_star
            b_star = a_star
            a_star = b - phi * abs(b - a)
        else:
            a = a_star
            a_star = b_star
            b_star = a + phi * abs(b - a)

    return (a + b) / 2


def rearrange_cvar(cvar):
    """
    The function rearranges a given array `cvar` in ascending order using NumPy's `np.sort` method.

    :param cvar: It looks like the function `rearrange_cvar` takes a variable `cvar` as input and
    returns a sorted version of it. The function creates a copy of the input `cvar`, sorts the copy, and
    then returns the sorted copy
    :return: The function `rearrange_cvar` is returning a sorted copy of the input `cvar` array.
    """
    cvar_permuted = cvar.copy()

    return np.sort(cvar_permuted)


np.random.seed(0)


def make_cvgroup(n, K, right=True):
    """
    The function `make_cvgroup` generates cross-validation group assignments based on random splits.

    :param n: The parameter `n` represents the number of samples or data points that will be split into
    different groups
    :param K: The parameter `K` represents the number of groups you want to split the data into. It is
    used in the function `make_cvgroup` to determine the number of groups to create based on the input
    data
    :param right: The `right` parameter in the `np.digitize` function determines how the bins are
    closed. If `right=True`, the intervals include the right edge but not the left edge. If
    `right=False`, the intervals include the left edge but not the right edge, defaults to True
    (optional)
    :return: The function `make_cvgroup` returns an array of integers representing the group assignments
    for each data point. The data points are split into `K` groups based on random values generated
    using `np.random.rand(n)`. The `np.digitize` function is used to assign each data point to a group
    based on the quantiles of the random values. The `right` parameter determines whether the
    """
    split = np.random.rand(n)
    return np.digitize(split, np.quantile(split, np.linspace(0, 1, K + 1)), right=right)


def make_cvgroup_balanced(data, K, form_t):
    """
    The function `make_cvgroup_balanced` assigns cross-validation group numbers to data based on a
    specified form_t column to balance the groups.

    :param data: It seems like you were about to provide more information about the 'data' parameter but
    it got cut off. Could you please provide more details or context about the 'data' parameter so that
    I can assist you better with the 'make_cvgroup_balanced' function?
    :param K: The parameter `K` in the `make_cvgroup_balanced` function represents the number of groups
    you want to create for cross-validation. It is used to determine how the data will be split into
    different groups for cross-validation purposes
    :param form_t: The `form_t` parameter seems to be used as an index or key to access a specific
    column or feature in the `data` array. It is used to filter the data based on whether the value in
    that column is equal to 1 or 0
    :return: The function `make_cvgroup_balanced` returns an array `cvgroup` containing the
    cross-validation group assignments for each data point in the input data. The cross-validation group
    assignments are determined based on the input data, the number of folds `K`, and the form_t
    parameter.
    """
    cvgroup = np.zeros(len(data), dtype=int)
    cvgroup[data[form_t] == 1] = make_cvgroup((data[form_t] == 1).sum(), K, right=True)
    cvgroup[data[form_t] == 0] = make_cvgroup((data[form_t] == 0).sum(), K, right=False)
    return cvgroup
