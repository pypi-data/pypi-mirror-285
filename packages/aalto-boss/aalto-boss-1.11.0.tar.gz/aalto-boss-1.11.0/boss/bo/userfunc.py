from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

from boss.utils.arrays import shape_consistent_XY, shape_consistent_Y


@dataclass
class UserFuncOutput:
    """Stores the output from the user function(s)."""

    X: NDArray[np.float64]
    Y: NDArray[np.float64]


class BaseUserFunc(abc.ABC):
    """Abstract base class for BOSS user function wrapper classes."""

    def __init__(self, func: Callable, dim: int) -> None:
        """
        Initializes a new wrapped user function.

        Parameters
        ----------
        func : Callable
            The user function to wrap.
        dim : int
            The dimension of the input space.
        """
        self.func = func
        self.dim = dim

    @abc.abstractmethod
    def evaluate(self, X_in: ArrayLike) -> UserFuncOutput:
        """Evaluates the user function at the given inputs."""

    def __call__(self, X_in: ArrayLike) -> UserFuncOutput:
        """
        Alias for UserFunc.evaluate.
        """
        return self.evaluate(X_in)


class STUserFunc(BaseUserFunc):
    """Wrapper class for BOSS user functions.

    Checks for extra user-defined data (e.g, in the case of symmetry points).
    """

    def evaluate(self, X_in: ArrayLike) -> UserFuncOutput:
        """
        Evaluates the user function (possibly with gradients) at the given inputs.

        Note that more inputs maybe be added by the user function, e.g.,
        in the case of symmetry points.

        Parameters
        ----------
        X_in : np.ndarray with shape (n_inputs, dim)
            The inputs for which to evaluate the user function.

        Returns
        -------
        UserFuncOutput
            Dataclass with attributes:
                X : np.ndarray with shape (n_inputs, dim)
                    The inputs used to evaluate the user function.
                Y : np.ndarray with shape (n_inputs, 1) or (n_inputs, 1 + dim)
                    Corresponding array of user function values, if there are
                    gradients they are stored in the last columns.
        """
        X_in = np.atleast_2d(X_in)
        Y = []
        X_out = []
        # Loop over batch points
        for x_in in X_in:
            out = self.func(np.atleast_2d(x_in))  # 2d input for backwards compat.
            # check if userfn returns extra data (e.g., symmetry points)
            if isinstance(out, tuple):
                x_out, y = shape_consistent_XY(*out, dim=self.dim)
                X_out.append(x_out)
                Y.append(y)
            else:
                y = shape_consistent_Y(out, dim=self.dim)
                Y.append(y)

        if len(X_out) == 0:
            X_out = X_in
        else:
            X_out = np.concatenate(X_out)

        Y = np.concatenate(Y)
        return UserFuncOutput(X_out, Y)


class GradientUserFunc(BaseUserFunc):
    """Wrapper class for BOSS user functions with gradient observations.

    Automatically  extra user-defined data (e.g, in the case of symmetry points).
    """

    def evaluate(self, X_in: ArrayLike) -> UserFuncOutput:
        """
        Evaluates the user function (possibly with gradients) at the given inputs.

        Note that more inputs maybe be added by the user function, e.g.,
        in the case of symmetry points.

        Parameters
        ----------
        X_in : np.ndarray with shape (n_inputs, dim)
            The inputs for which to evaluate the user function.

        Returns
        -------
        UserFuncOutput
            Dataclass with attributes:
                X : np.ndarray with shape (n_inputs, dim)
                    The inputs used to evaluate the user function.
                Y : np.ndarray with shape (n_inputs, 1) or (n_inputs, 1 + dim)
                    Corresponding array of user function values, if there are
                    gradients they are stored in the last columns.
        """
        X_in = np.atleast_2d(X_in)
        Y = []
        X_out = []
        # Loop over batch points
        for x_in in X_in:
            out = self.func(x_in)
            # check if userfn returns extra data (e.g., symmetry points)
            if len(out) == 3:
                x_out, y, dy = out
                x_out, y = shape_consistent_XY(x_out, y, dim=self.dim)
                dy, y = shape_consistent_XY(dy, y, dim=self.dim)
                X_out.append(x_out)
            elif len(out) == 2:
                y, dy = out
                dy, y = shape_consistent_XY(dy, y, dim=self.dim)
            else:
                raise ValueError("Incorrect number of ouputs from user function.")

            Y.append(np.concatenate((y, dy), axis=1))

        if len(X_out) == 0:
            X_out = X_in
        else:
            X_out = np.concatenate(X_out)

        Y = np.concatenate(Y)
        return UserFuncOutput(X_out, Y)


class MTUserFunc(BaseUserFunc):
    """Wrapper class for multiple BOSS user functions."""

    def __init__(self, func_list: list[Callable], dim: int) -> None:
        self.func_list = func_list
        self.dim = dim

    def __len__(self) -> int:
        """Returns the length of the user function list."""
        return len(self.func_list)

    def evaluate(self, X_in: ArrayLike) -> UserFuncOutput:
        """
        Evaluates the user function at the given inputs.

        Parameters
        ----------
        X_in : np.ndarray with shape (n_inputs, dim + 1)
            Input data and corresponding task indices for the user functions
            to be evaluated.

        Returns
        -------
        UserFuncOutput
            Dataclass with attributes:
                X : np.ndarray with shape (n_inputs, dim)
                    The inputs used to evaluate the user function.
                Y : np.ndarray with shape (n_inputs, 1) or (n_inputs, 1 + dim)
                    Corresponding array of user function values, if there are
                    gradients they are stored in the last columns.
        """
        # Separate x-data and indices
        X_in = np.atleast_2d(X_in)
        X_in, indices = X_in[:, :-1], X_in[:, -1]
        indices = indices.astype(int)

        Y = []
        X_out = []
        indices_out = []
        # Loop over batch points
        for x_in, index in zip(X_in, indices):
            out = self.func_list[index](np.atleast_2d(x_in))
            # check if userfn returns extra data (e.g., symmetry points)
            if isinstance(out, tuple):
                x_out, y = out
                x_out, y = shape_consistent_XY(x_out, y, dim=self.dim)
                index_out = index * np.ones(x_out.shape[0], dtype=float)
                indices_out.append(index_out)
                X_out.append(x_out)
                Y.append(y)
            else:
                y = shape_consistent_Y(out, dim=self.dim)
                Y.append(y)

        if len(X_out) == 0:
            X_out = X_in
            indices_out = indices[:, None]
        else:
            indices_out = np.concatenate(indices_out)[:, None]

        # put X data and indices back together
        X_out = np.concatenate((X_out, indices_out), axis=1)
        Y = np.concatenate(Y)
        return UserFuncOutput(X_out, Y)
