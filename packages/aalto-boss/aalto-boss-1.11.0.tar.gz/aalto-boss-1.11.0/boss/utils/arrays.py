"""A collection of array-related functions.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def shape_consistent_X(X: ArrayLike, dim: int) -> NDArray[np.float64]:
    """Ensures that X-data is consistent with the user function dimension.

    The shape of X is checked for consistency with the user function dimension,
    and converted to 2D and/or transposed if needed.

    Parameters
    ----------
    X : ArrayLike of floats
        Locations for user function observations.
    dim : int
        Dimension of the user function domain.

    Returns
    ------
    NDArray[np.float64]
        X-data with consistent shape.
    """
    X = np.atleast_2d(X)
    if dim == 1:
        if X.shape[1] > dim:
            X = X.T
    else:
        if X.shape[1] != dim:
            raise ValueError(
                f"X-shape = {X.shape} inconsistent with dimension of bounds = {dim}"
            )
    return X


def shape_consistent_Y(
    Y: ArrayLike, dim: int, ygrad: bool = False
) -> NDArray[np.float64]:
    """Ensures that Y-data is consistent with the user function dimension.

    The shape of Y is checked for consistency with the user function dimension
    and whether gradient observations are included. If needed, Y is converted to
    2D and/or transposed.

    Parameters
    ----------
    Y : ArrayLike of floats
        User function observations, possibly with gradient data included.
    dim : int
        Dimension of the user function domain.

    Returns
    ------
    NDArray[np.float64]
        Y-data with consistent shape.
    """
    Y = np.atleast_2d(Y)
    if not ygrad:
        if Y.shape[1] > 1:
            Y = Y.T
    else:
        if Y.shape[1] != (dim + 1):
            if Y.shape[0] != (dim + 1):
                raise ValueError("Missing gradient data in Y.")
            Y = Y.T
    return Y


def shape_consistent_XY(
    X: ArrayLike,
    Y: ArrayLike | None,
    dim: int,
    nan_pad: bool = False,
    ygrad: bool = False,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Ensures that X and Y-data are shape consistent.

    The shape of X is checked for consistency with the user function dimension.
    The shape of Y is then checked for consistency with X and possibly padded with nan-values upon request.

    This function should be called by any user-facing method that accepts X, Y-data.

    Parameters
    ----------
    X : ArrayLike of floats
        Input data, scalars and 1d-arrays will be promoted to 2d.
    Y : ArrayLike of floats | None
        Output data, scalars and 1d-arrays will be promoted to 2d.
    dim : int
        Dimension of the user function domain, as specified by the bounds.
    nan_pad : bool = False
        Whether to allow Y with less rows than X to be nan-padded until
        the number of rows match.
    ygrad : bool = False
        Whether gradient observations are included or not.

    Returns
    ------
    tuple[NDArray[np.float64], NDArray[np.float64]]:
        X, Y-data with consistent shapes.
    """
    X = shape_consistent_X(X, dim)
    if Y is None:
        if nan_pad:
            Y = np.empty((X.shape[0], 1 + ygrad * dim)) * np.nan
        else:
            raise ValueError("Y=None not allowed for nan_pad=False")
    else:
        Y = shape_consistent_Y(Y, dim, ygrad)
        n_diff = X.shape[0] - Y.shape[0]
        if n_diff > 0:
            if nan_pad:
                Y_fill = np.empty((n_diff, 1 + ygrad * dim)) * np.nan
                Y = np.concatenate((Y, Y_fill), axis=0)
            else:
                raise ValueError("Number of rows in X and Y must match.")
        elif n_diff < 0:
            raise ValueError("Y cannot contain more rows than X.")
    return X, Y
