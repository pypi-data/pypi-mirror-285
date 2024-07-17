"""
This module creates the external funcions used in the MATER class.
"""

from functools import wraps

import numpy as np
import pandas as pd

from pandas.core.frame import DataFrame

# Functions definition


def _log_normal(time: DataFrame, life_time: DataFrame, standard_deviation: DataFrame, k: int) -> DataFrame:
    r"""
    Compute the log-normal probability density function.

    This function calculates the log-normal distribution given the lifetime mean value, standard deviation, and a set of time points. It is typically used to model time until failure or time until an event occurs, where the event times are assumed to follow a log-normal distribution.

    :param time: :math:`t` a DataFrame containing time points at which the log-normal distribution is evaluated.
    :param life_time: :math:`\mu_{l,o,t}` a DataFrame containing the lifetime mean values.
    :param standard_deviation: :math:`\sigma_{l,o,t}` a DataFrame containing the standard deviations of the lifetime values.
    :param k: A `time` integer.
    :type time: pd.DataFrame
    :type life_time: pd.DataFrame
    :type standard_deviation: pd.DataFrame
    :type k: int
    :return: :math:`d^{log}_{l,o,t}` a DataFrame containing the computed log-normal probability densities at each time point.
    :rtype: pd.DataFrame

    Calculation
    -----------
    The probability density function for a log-normal distribution is calculated as follows:

    .. math::
        d^{log}_{l,o,t}[t,\mu_{l,o,t},\sigma_{l,o,t},k] = \frac{1}{(t - k) \sigma_{l,o,t} \sqrt{2\pi}} \exp\left(-\frac{(\log(t - k) - \mu_{l,o,t})^2}{2\sigma_{l,o,t}^2}\right)
        :label: probability_density_function

    Notes
    -----
    Indices are the :ref:`variables dimensions <dimensions>`.
    """
    return np.exp(
        -1
        / 2
        * ((np.log(time.loc[:, k + 1 :] - k).subtract(life_time[k], axis=0)).div(standard_deviation[k], axis=0)) ** 2
    ) / ((time.loc[:, k + 1 :] - k).mul(standard_deviation[k], axis=0) * np.sqrt(2 * np.pi))


def _exponential_decay(time: DataFrame, life_time: DataFrame, k: int):
    r"""
    Calculate the exponential decay for given time points and decay lifetimes.

    :param time: :math:`t` is a `Time` DataFrame fot `time` :math:`t \ge k+1`.
    :type time: pd.DataFrame
    :param life_time: :math:`L^m_{l,o}(k)` is a `lifetime_mean_value` DataFrame at `time` :math:`k`.
    :type life_time: pd.DataFrame
    :param k: a `time` integer.
    :type k: int

    :return: :math:`d^e_{l,o,t}` a DataFrame resulting of the exponential decay function.
    :rtype: pd.DataFrame

    calculation
    -----------
    .. math::
        d^e_{l,o,t}[t,L^m_{l,o,t},k] = \frac{{e^{-\frac{{(t - k)}}{{L^m_{l,o}(k)}}}}}{{L^m_{l,o}(k)}}
        :label: exponential_decay

    Notes
    -----
    Indices are the :ref:`variables dimensions <dimensions>`.
    """
    return (
        np.exp(-(time.loc[:, k + 1 :] - k).div(life_time[k], axis=0))
        .div(life_time[k], axis=0)
        .dropna(axis=0, how="all")
    )


def profile(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.profiler.enable()
        retval = func(self, *args, **kwargs)
        self.profiler.disable()
        return retval

    return wrapper


def _compute_pseudoinverse(matrix):
    """Compute the Moore-Penrose pseudoinverse of a given matrix.

    This function calculates the pseudoinverse of a matrix using the NumPy linear algebra library. The Moore-Penrose pseudoinverse is a generalization of the matrix inverse for square matrices and is applicable to non-square matrices as well.

    :param matrix: A pandas DataFrame representing the matrix for which the pseudoinverse is to be computed.
    :type matrix: pd.DataFrame
    :return: The pseudoinverse of the matrix as a NumPy array. This array has the same dimensions as the input matrix transposed, and it satisfies the four Moore-Penrose conditions.
    :rtype: np.ndarray

    Notes
    -----
    The pseudoinverse :math:`A^+` of a matrix :math:`A` is defined such that it satisfies the following conditions:

    .. math::
        AA^+A &= A,

        A^+AA^+ &= A^+,

        (AA^+)^T &= AA^+,

        (A^+A)^T &= A^+A.

    The computation is performed using the NumPy library's `linalg.pinv` method, which is based on Singular Value Decomposition (SVD).

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame([[1, 2], [3, 4]])
    >>> compute_pseudoinverse(df)
    array([[-2. ,  1. ],
           [ 1.5, -0.5]])

    See Also
    --------
    `np.linalg.pinv <https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html>`_ : NumPy's method to compute the pseudoinverse of a matrix.

    References
    ----------
    - Penrose, R. (1955). A generalized inverse for matrices. Proceedings of the Cambridge Philosophical Society, 51, 406-413.
    - Ben-Israel, A., & Greville, T. N. E. (2003). Generalized inverses: Theory and applications. Springer Science & Business Media.

    """
    return np.linalg.pinv(matrix.values)
