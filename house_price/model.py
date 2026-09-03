"""Estimator wrappers shared by the notebook and the API.

These live in the package rather than in notebook cells because the exported
pickle references them by import path: ``joblib.load`` in ``backend/`` has to be
able to find the same classes that ``joblib.dump`` saw.
"""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, clone


class ClippedRegressor(BaseEstimator, RegressorMixin):
    """Wraps a regressor and clips its predictions to the training price range.

    Training on ``log1p(price)`` and inverting with ``expm1`` makes a small
    log-space error enormous in rupees at the top of the range. On this dataset
    exactly one test prediction came back at 300 Cr against an actual of 16 Cr,
    and that single row moved R2 from 0.744 to **-3.638** - one row in 12,530
    deciding the headline metric.

    Clipping to the range actually observed while fitting is the honest fix: a
    model has no basis for predicting a price eight times higher than anything it
    was ever shown. It leaves the median error untouched and stops one
    exponentiated outlier from speaking for the whole model.
    """

    def __init__(self, estimator=None, lower_quantile: float = 0.0, upper_quantile: float = 1.0):
        self.estimator = estimator
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    def fit(self, X, y):
        """Fit the wrapped estimator and record the clip bounds from ``y``."""
        self.estimator_ = clone(self.estimator)
        self.estimator_.fit(X, y)
        values = np.asarray(y, dtype=float)
        self.low_ = float(np.quantile(values, self.lower_quantile))
        self.high_ = float(np.quantile(values, self.upper_quantile))
        return self

    def predict(self, X):
        """Predict, clipped to the range seen during fitting."""
        return np.clip(self.estimator_.predict(X), self.low_, self.high_)

    def __sklearn_tags__(self):
        # Defer to the wrapped estimator so cross_val_score and friends treat
        # this as the regressor it wraps.
        return self.estimator.__sklearn_tags__()


class SmearedRegressor(BaseEstimator, RegressorMixin):
    """Corrects the bias you get from training on log price and using expm1.

    The project brief suggests fitting on ``log1p(y)`` and inverting with
    ``expm1``, which is good advice as far as it goes. What it doesn't mention is
    that the two steps don't cancel.

    Least squares in log space fits ``E[log y | x]``, the *mean of the log*.
    Exponentiating that gives you back the **median** of y, not the mean, because
    ``exp`` is convex and Jensen's inequality says ``exp(E[log y]) <= E[y]``. So
    every prediction comes out systematically low. On this dataset the naive
    back-transform predicts a total 4.7% under the actual total, and no amount of
    extra training fixes it, because the model is doing exactly what it was asked.

    Duan's smearing estimator (1983) is the standard non-parametric correction.
    Take the training residuals in log space, average ``exp`` of them, and scale
    every prediction by that factor:

    ```text
    S = mean(exp(log y_i - f(x_i)))
    prediction = expm1(f(x) + log S)
    ```

    Which one you actually want depends on the loss you care about, and they pull
    in opposite directions:

    - uncorrected gives the conditional median, which is what minimises absolute
      and percentage error, so it wins on MAE and MdAPE
    - smeared gives the conditional mean, which is what minimises squared error
      and is the only one that adds up correctly over a set of properties, so it
      wins on RMSE, R2, and any total

    Pricing one flat, the median is the better answer. Valuing a portfolio, the
    uncorrected version is short by 4.7% and the smeared one is not.
    """

    def __init__(self, estimator=None):
        self.estimator = estimator

    def fit(self, X, y):
        """Fit on log price, then measure the smearing factor from the residuals."""
        self.estimator_ = clone(self.estimator)
        log_y = np.log1p(np.asarray(y, dtype=float))
        self.estimator_.fit(X, log_y)
        residuals = log_y - self.estimator_.predict(X)
        self.smearing_ = float(np.mean(np.exp(residuals)))
        return self

    def predict(self, X):
        """Predict in rupees, scaled by the smearing factor."""
        return np.expm1(self.estimator_.predict(X) + np.log(self.smearing_))

    def __sklearn_tags__(self):
        return self.estimator.__sklearn_tags__()
