from __future__ import annotations

import abc

import numpy as np
from numpy.typing import ArrayLike, NDArray
from boss.utils.typing import ArrayLike1D, ArrayLike2D

from boss.bo.acq.base import BaseAcquisition
from boss.bo.acq.cost import AdditiveCost, DivisiveCost, CostAwareAcquisition
from boss.bo.acq.explore import Explore
from boss.bo.acq.multi import MTHeuristic


def _is_explore(acqfn: BaseAcquisition) -> bool:
    """Checks if acquisition function is (based on) pure Exploration."""
    if isinstance(acqfn, Explore):
        return True
    elif isinstance(acqfn, CostAwareAcquisition) and hasattr(acqfn, "acqfn"):
        return isinstance(acqfn.acqfn, Explore)
    else:
        return False


class BaseAcquisitionManager(abc.ABC):
    """Abstract base class for acquisition managers.

    An acquisition manager handles the process of obtaining the next acquisition
    point(s). To be a valid acquisition manager, children only need to implement
    the acquire method. Acquisition managers are used, e.g., to implement batch acquisition
    schemes.
    """

    def __init__(self) -> None:
        # A message that, if set, is printed to the main output every iteration.
        # Mainly intended to be set internally in the acquisition manager.
        self.message = ""

    @abc.abstractmethod
    def acquire(self) -> NDArray[np.float64]:
        """Returns the next acquisition(s).

        Returns
        -------
        X: np.ndarray
            2D array where the next acquisitions are stored row-wise.
        """
        pass


class Sequential(BaseAcquisitionManager):
    """A basic sequential acquisition manager.

    This manager performs acquisitions sequentially, i.e., only one acquisition
    per iteration, as opposed to batch acquisitions. It is the default acquisition
    manager used in BOSS and has the ability to perform so-called pure exploration
    when the model is overconfident about the next acquisition. Pure exploration
    refers to maximizing only the model variance during the acquisition.
    """

    def __init__(
        self,
        acqfn: BaseAcquisition,
        bounds: ArrayLike2D | ArrayLike1D,
        optimtype: str = "score",
        acqtol: float | None = None,
    ) -> None:
        """Constructs a new sequential acquisition manager.

        Parameters
        ----------
        acqfn : BaseAcquisition
            The acquisition function to use.
        bounds : ArrayLike2D | ArrayLike1D
            Bounds over which is acquisition function is minimized.
        optimtype : str
            The name of the acquisition function optimizer to use.
        acqtol : float | None
            The threshold used to determine if the model is overconfident
            about the next acquisition and pure exploration should be triggered.
        """
        super().__init__()
        self.acqfn = acqfn
        self.bounds = np.atleast_2d(bounds)
        self.acqtol = acqtol
        self.optimtype = optimtype

        # If the acq func is not already (based on) pure exploration, we create
        #  a pure exploration acq func that will be used if the is_loc_overconfident
        # check is triggered. Cost functions and multi-task heuristics are applied
        # if required.
        self.explorefn = None
        if not _is_explore(self.acqfn):
            self.explorefn = Explore(self.acqfn.model)
            if isinstance(self.acqfn, (AdditiveCost, DivisiveCost)):
                cost_class = type(self.acqfn)
                self.explorefn = cost_class(self.explorefn, self.acqfn.costfn)
            elif isinstance(self.acqfn, MTHeuristic):
                self.explorefn = MTHeuristic(self.explorefn, self.acqfn.cost_arr)

    def acquire(self) -> NDArray[np.float64]:
        """Determines the next acquisition by minimizing the acquisition function.

        Returns
        -------
        np.ndarray
            The next acquisition, returned as a 2D array for consistency with
            batch acquisition managers.
        """
        x_next = self.acqfn.minimize(self.bounds, optimtype=self.optimtype)
        if self.explorefn is not None and self.is_loc_overconfident(x_next):
            self.explorefn.model = self.acqfn.model
            x_next = self.explorefn.minimize(self.bounds, optimtype=self.optimtype)

        return np.atleast_2d(x_next)

    def is_loc_overconfident(self, x_next: ArrayLike) -> bool:
        """Determines if the model is overconfident about the next acquisition.

        We define the model to be overconfident at a given input point if the predicted
        standard deviation is lower than the threshold set by acqtol keyword.
        This information is then used to trigger pure exploration.

        Parameters
        ----------
        x_next : np.ndarray
            The input point at which to check for model overconfidence.

        Returns
        -------
        bool:
            Whether the model is overconfident at x_next or not.
        """
        if self.acqtol is None:
            return False
        else:
            var_next = self.acqfn.model.predict(x_next)[1]
            if var_next < self.acqtol**2:
                self.message = (
                    "Acquisition location too confident, doing pure exploration"
                )
                return True
            else:
                self.message = ""
                return False
