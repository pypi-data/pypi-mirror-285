from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import numpy as np


def tau_predict(X, y, weights):
    """
    Predicts tau values using weighted linear regression.

    Parameters:
    -----------
    X : array-like or DataFrame
        The input features for the regression model.
    y : array-like or Series
        The target values.
    weights : array-like
        The sample weights.

    Returns:
    --------
    tau_pred : array
        The predicted tau values.

    Example:
    --------
    >>> X = np.array([[1, 2], [3, 4], [5, 6]])
    >>> y = np.array([1, 2, 3])
    >>> weights = np.array([0.5, 0.2, 0.3])
    >>> tau_pred = tau_predict(X, y, weights)
    """
    model = LinearRegression()

    # Fit the model with weights
    model.fit(X, y, sample_weight=weights)

    # Make predictions
    tau_pred = model.predict(X)
    return tau_pred


def mu_calculate(data, cvgroup, y_ref, X_ref, A_col="A", sw_col="sw", K=5):
    """
    Calculates the predicted probabilities (mu0 and mu1) using cross-validated gradient boosting classifiers.

    Parameters:
    -----------
    data : DataFrame
        The DataFrame containing the input data.
    cvgroup : array-like
        An array indicating the cross-validation group for each sample.
    y_ref : array-like or Series
        The target values for the regression model.
    X_ref : array-like or DataFrame
        The input features for the regression model.
    A_col : str, optional
        The name of the column in the DataFrame that contains the treatment indicator (default is "A").
    sw_col : str, optional
        The name of the column in the DataFrame that contains sample weights (default is "sw").
    K : int, optional
        The number of cross-validation folds (default is 5).

    Returns:
    --------
    mu0_pred : array
        The predicted probabilities for the control group (A == 0).
    mu1_pred : array
        The predicted probabilities for the treatment group (A == 1).
    """
    mu0_pred = np.zeros(len(data))
    mu1_pred = np.zeros(len(data))

    for k in range(1, K + 1):
        train_indices = cvgroup != k
        test_indices = cvgroup == k

        clf0 = GradientBoostingClassifier(tol=0.1)
        clf1 = GradientBoostingClassifier(tol=0.1)

        train_A0 = train_indices & (data[A_col] == 0)
        train_A1 = train_indices & (data[A_col] == 1)

        clf0.fit(X_ref[train_A0], y_ref[train_A0], sample_weight=data[sw_col][train_A0])
        clf1.fit(X_ref[train_A1], y_ref[train_A1], sample_weight=data[sw_col][train_A1])

        mu0_pred[test_indices] = clf0.predict_proba(X_ref[test_indices])[:, 1]
        mu1_pred[test_indices] = clf1.predict_proba(X_ref[test_indices])[:, 1]

    return mu0_pred, mu1_pred


def var_calculate(
    data,
    X_ref,
    cvgroup,
    K=5,
    y_col="Y",
    mu0_col="mu0",
    sw_col="sw",
    A_col="A",
    rearrangement=False,
):
    """
    Calculates the variance predictions (var0 and var1) using cross-validated gradient boosting regressors.

    Parameters:
    -----------
    data : DataFrame
        The DataFrame containing the input data.
    X_ref : DataFrame
        The input features for the regression model.
    cvgroup : array-like
        An array indicating the cross-validation group for each sample.
    K : int, optional
        The number of cross-validation folds (default is 5).
    y_col : str, optional
        The name of the column in the DataFrame that contains the outcome values (default is "Y").
    mu0_col : str, optional
        The name of the column in the DataFrame that contains the predicted values for the control group (default is "mu0").
    sw_col : str, optional
        The name of the column in the DataFrame that contains sample weights (default is "sw").
    A_col : str, optional
        The name of the column in the DataFrame that contains the treatment indicator (default is "A").
    rearrangement : bool, optional
        If True, sets negative variance predictions to zero (default is False).

    Returns:
    --------
    var0_pred : array
        The predicted variances for the control group (A == 0).
    var1_pred : array
        The predicted variances for the treatment group (A == 1).
    """
    if X_ref is None:
        raise ValueError("X_ref must be provided as a pandas DataFrame.")

    var0_pred = np.zeros(len(data))
    var1_pred = np.zeros(len(data))
    X_ref[A_col] = data[A_col]

    for k in range(1, K + 1):
        train_indices = cvgroup != k
        test_indices = cvgroup == k

        fvar = GradientBoostingRegressor()

        y_ref0 = (data[y_col] - data[mu0_col]) ** 2
        sw = data[sw_col]

        # Ajustar el modelo para var0
        fvar.fit(
            X_ref[train_indices], y_ref0[train_indices], sample_weight=sw[train_indices]
        )

        # Predecir var0 y var1
        X_test0 = X_ref[test_indices].copy()
        X_test1 = X_ref[test_indices].copy()

        X_test0[A_col] = 0
        X_test1[A_col] = 1

        var0_pred[test_indices] = fvar.predict(X_test0)
        var1_pred[test_indices] = fvar.predict(X_test1)
    if rearrangement:
        var0_pred = var0_pred * (var0_pred > 0)
        var1_pred = var1_pred * (var1_pred > 0)
    return var0_pred, var1_pred
