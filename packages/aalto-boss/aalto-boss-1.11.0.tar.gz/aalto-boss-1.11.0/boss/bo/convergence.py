from __future__ import annotations

import abc

import numpy as np
from numpy.typing import ArrayLike

from boss.bo.results import BOResults
from boss.settings import Settings


def select_conv_checker(settings: Settings) -> BaseConvChecker | None:
    """
    Selects and instantiates a convergence checker based on given settings.

    Currently takes into account:
        convtype: the desired convergence checker type
        conv_reltol: tolerance relative to a scale value
        conv_abstol: absolute tolerance
        conv_iters: number of iterations for which the tolerance criterion
            must be fulfilled to trigger convergence.

    Parameters
    ----------
    settings : Settings
        The settings object.

    Returns
    -------
    BaseConvChecker | None
        If either conv_abstol or conv_reltol were specified a convergence checker object
        is returned, else None.
    """
    convtype = settings["convtype"]
    rel_tol = settings["conv_reltol"]
    abs_tol = settings["conv_abstol"]
    if (convtype is None) or (rel_tol is abs_tol is None):
        return None

    if convtype == "glmin_val":
        checker = ConvCheckerVal(
            rel_tol=rel_tol,
            abs_tol=abs_tol,
            n_iters=settings["conv_iters"],
        )
    elif convtype == "glmin_loc":
        checker = ConvCheckerLoc(
            rel_tol=rel_tol,
            abs_tol=abs_tol,
            n_iters=settings["conv_iters"],
        )
    else:
        raise ValueError(f"Unknown convtype {convtype}")

    return checker


class BaseConvChecker(abc.ABC):
    """Abstract base class for convergence checkers."""

    @abc.abstractmethod
    def check(self, bo_results: BOResults) -> bool:
        """
        Checks if the implemented convergence check is satisfied.

        Parameters
        ----------
        bo_results : BOResults
            Current BO results object from which the checker obtains
            information to perform the check.

        Returns
        -------
        bool
            True if the check is satisfied, False otherwise.
        """
        pass

    def __call__(self, bo_results) -> bool:
        """Convenience method to run the convergence check."""
        return self.check(bo_results)


class ConvCheckerVal(BaseConvChecker):
    """Convergence checker based on the predicted global minimum value.

    Each iteration, the absolute difference between the previous and current predicted
    global minimum is computed and checked against an absolute and relative tolerance.
    If the tolerance remains satisfied for a given number of iterations,
    the convergence check is considered successful.

    For more info see: https://web.mit.edu/10.001/Web/Tips/Converge.htm
    """

    def __init__(
        self,
        rel_tol: float = 1e-3,
        abs_tol: float = 1e-7,
        n_iters: int = 5,
        f_ref: float | None = None,
        scale_type: str = "max",
    ) -> None:
        """
        Creates a new checker.

        Parameters
        ----------
        rel_tol : float
            Tolerance relative to scale value determined by the scale_type argument.
        abs_tol : float
            Absolute tolerance, should be a small value that ensures that the convergence
            check can be satisfied even if the true min is close to 0.
        n_iters : int
            Number of iterations for which the tolerance criterion must be satisfied
            to trigger succesful convergence.
        f_ref : float | None
            If given, the current global min prediction is compared against this reference
            value. If None is provided, the previous global min prediction is used.
            This argument is typically only explicitly specified for testing purposes
            when the true global min is known.
        scale_type : str
            A scale type for the relative tolerance. Can be one of:
                max: uses the maximum of the current global min prediction and the
                the f_ref value.
                yrange: uses the current range of observation values, i.e. acquistions.
        """
        self.abs_tol = abs_tol
        self.rel_tol = rel_tol
        self.n_iters = n_iters
        self.f_ref = f_ref
        self.scale_type = scale_type

    def check(self, bo_results: BOResults) -> bool:
        """
        Checks if the implemented convergence check is satisfied.

        Parameters
        ----------
        bo_results : BOResults
            Current BO results object from which the checker obtains
            information to perform the check.

        Returns
        -------
        bool
            True if the check is satisfied, False otherwise.
        """
        res = bo_results
        mu_glmin = res["mu_glmin"]
        if self.scale_type == "yrange":
            yrange = res.get_est_yrange()
            scale = yrange[1] - yrange[0]

        # If we don't have enough data for look two or one (if comparing to a ref value)
        # iteration backwards, we can't perform the check.
        if len(mu_glmin.data) < self.n_iters + int(self.f_ref is None):
            return False

        for i in range(self.n_iters):
            mu_glmin_i = mu_glmin.value(-i - 1)
            if not self.f_ref:
                f_ref = mu_glmin.value(-i - 2)
            else:
                f_ref = self.f_ref

            if self.scale_type == "max":
                scale = np.maximum(np.abs(mu_glmin_i), np.abs(f_ref))
            elif self.scale_type != "yrange":
                raise ValueError(f"Unknown scale type {self.scale_type}")

            df = abs(mu_glmin_i - f_ref)
            if df > scale * self.rel_tol + self.abs_tol:
                return False

        return True


class ConvCheckerLoc(BaseConvChecker):
    """Convergence checker based on the predicted global minimum location.

    Each iteration, the norm of the difference between the previous and current predicted
    global minimum location is computed and checked against an absolute and relative tolerance.
    If the tolerance remains satisfied for a given number of iterations,
    the convergence check is considered successful.

    For more info see: https://web.mit.edu/10.001/Web/Tips/Converge.htm
    """

    def __init__(
        self,
        rel_tol: float = 1e-3,
        abs_tol: float = 1e-7,
        n_iters: int = 5,
        x_ref: ArrayLike | None = None,
        scale_type="lengthscale",
    ) -> None:
        """
        Creates a new checker.

        Parameters
        ----------
        rel_tol : float
            Tolerance relative to scale value determined by the scale_type argument.
        abs_tol : float
            Absolute tolerance, should be a small value that ensures that the convergence
            check can be satisfied even if the true min locatoin is close to the origin.
        n_iters : int
            Number of iterations for which the tolerance criterion must be satisfied
            to trigger succesful convergence.
        x_ref : float | None
            If given, the current global min location prediction is compared against this reference
            value. If None is provided, the previously predicted global min location is used.
            This argument is typically only explicitly specified for testing purposes
            when the true global min location is known.
        scale_type : str
            A scale type for the relative tolerance. Can be one of:
                max: uses the maximum of the currently predicted global min location and the
                the x_ref value.
                lengthscale: uses the current range of observation values, i.e. acquistions.
        """
        self.abs_tol = abs_tol
        self.rel_tol = rel_tol
        self.n_iters = n_iters
        self.x_ref = x_ref
        self.scale_type = scale_type

    def check(self, bo_results: BOResults) -> bool:
        """
        Checks if the implemented convergence check is satisfied.

        Parameters
        ----------
        bo_results : BOResults
            Current BO results object from which the checker obtains
            information to perform the check.

        Returns
        -------
        bool
            True if the check is satisfied, False otherwise.
        """
        res = bo_results
        x_glmin = res["x_glmin"]
        n_iters = self.n_iters
        scale = None

        # If we don't have enough data for look two or one (if comparing to a ref value)
        # iteration backwards, we can't perform the check.
        if len(x_glmin.data) < n_iters + int(self.x_ref is None):
            return False

        for i in range(n_iters):
            x_glmin_i = x_glmin.value(-i - 1)

            if self.x_ref is not None:
                x_ref = self.x_ref
            else:
                x_ref = x_glmin.value(-i - 2)

            dx = np.linalg.norm(x_glmin_i - x_ref)

            if self.scale_type == "lengthscale":
                scale = res.select("model_params", -i - 1)[1:]
            elif self.scale_type == "max":
                scale = np.maximum(np.linalg.norm(x_glmin_i), np.linalg.norm(x_ref))
            else:
                raise ValueError(f"Unknown scale type {self.scale_type}")

            if dx > scale * self.rel_tol + self.abs_tol:
                return False

        return True
