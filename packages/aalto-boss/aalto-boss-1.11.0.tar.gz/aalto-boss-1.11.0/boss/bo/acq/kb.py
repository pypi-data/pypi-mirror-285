from __future__ import annotations

import copy
from numpy.typing import ArrayLike, NDArray
from boss.utils.typing import ArrayLike1D, ArrayLike2D

import numpy as np

from boss.bo.acq.base import BaseAcquisition
from boss.bo.acq.manager import BaseAcquisitionManager
from boss.settings import select_acq_func


class KrigingBeliever(BaseAcquisitionManager):
    """
    Implements a Kriging-Believer strategy for batch acquisitions. A batch is
    constructed sequentially by approximating objective function observations
    using surrogate model predictions, also referred to as hallucinated observations.
    During each iteration, a temporary surrogate model is updated with the hallucinated
    data. Once a batch of the desired size has been constructed the temporary model
    is discarded.
    """

    def __init__(
        self,
        acqfn: BaseAcquisition,
        bounds: ArrayLike2D | ArrayLike1D,
        batchpts: int,
        optimtype: str = "score",
    ) -> None:
        """
        Initializes a new KB acquisition manager.

        Parameters
        ----------
        acqfn : BaseAcquisition
            Acquisition function to use.
        bounds : ArrayLike2D | ArrayLike1D
            Bounds of the user objective function.
        batchpts : int
            Size of the batch, i.e., the number of x-data points to acquire.
        optimtype : str
            The type of algorithm to use when optimizing the acquisition function.
            Defaults to 'score'.
        """
        super().__init__()
        self.acqfn = acqfn
        self.bounds = np.atleast_2d(bounds)
        self.batchpts = batchpts
        self.optimtype = optimtype

    def acquire(self, X_inject: ArrayLike | None = None) -> NDArray[np.float64]:
        """
        Calculates a new batch of acquisitions.

        Parameters
        ----------
        X_inject : ArrayLike | None
            Additional input data that is temporarily injected into the existing model data
            for the purpose of constructing the batch. Can be used, e.g., to push acquisitions
            away from selected locations.

        Returns
        -------
        NDArray[np.float64]
            A 2d array containing the new batch, with acquisitions stored row-wise.
        """
        acqfn_tmp = copy.deepcopy(self.acqfn)
        model_tmp = acqfn_tmp.model

        if X_inject is None:
            X_batch = np.empty((0, len(self.bounds)), dtype=np.float64)
        else:
            X_batch = np.atleast_2d(X_inject)

        for _ in range(self.batchpts):
            X_next = np.atleast_2d(
                acqfn_tmp.minimize(self.bounds, optimtype=self.optimtype)
            )
            # Approximate a new observation using intermediate model.
            Y_next = model_tmp.predict(X_next)[0]
            # Update and optimize the intermediate model using the approx. observation.
            model_tmp.add_data(X_next, Y_next)
            model_tmp.optimize(2)
            X_batch = np.vstack((X_batch, X_next))

        return X_batch


class MultiKrigingBeliever:
    """
    Experimental implementation of Kriging-Believer batches for multiple surrogate
    models and acquisition functions.
    """

    def __init__(
        self,
        bo_main_list: list,
        batchspec: dict[str, int],
    ) -> None:
        """
        Initializes a new multi-Kriging-Believer manager.

        Parameters
        ----------
        bo_main_list : list
        List of BOMain objects to make acquisitions for, typically one for each
        objective.
        batchspec : dict
           A dictionary mapping acq. func. names to batch points. E.g. if batchspec
           is given as {'elcb:' 1, 'explore': 2}, one ELCB acquisition and two
           pure-exploration acquisitions will be made for each objective.
        """
        self.bo_main_list = bo_main_list
        self.acq_history = {}
        self.batchspec = batchspec

    def acquire(
        self, X_inject: ArrayLike | None = None, history: bool = False
    ) -> NDArray[np.float64]:
        """
        Calculates a new batch of acquisitions.

        Parameters
        ----------
        X_inject : ArrayLike | None
            Additional input data that is temporarily injected into the existing model
            data for the purpose of constructing the batch. Can be used, e.g., to push
            acquisitions away from selected locations.
        history : bool
            Used for debugging. If truthy, the intermediate acquisition functions will
            be stored in an attribute called 'acq_history' that maps tuples
            (BOMain index, acqfn name, batch point index) to the corresponding
            acquisition functions.

        Returns
        -------
        NDArray[np.float64]
            A 2d array containing the new batch, with acquisitions stored row-wise.
        """
        bo_mains = self.bo_main_list
        bounds = bo_mains[0].settings["bounds"]

        # set up acqfns and batsizes from batchspecs
        acq_funcs = []
        batchpts_list = []
        for _ in bo_mains:
            acq_funcs.append(
                [
                    select_acq_func({"acqfn_name": name})
                    for name in self.batchspec.keys()
                ]
            )
            batchpts_list.append(list(self.batchspec.values()))

        n_inject = 0
        if X_inject is None:
            X_batch = np.empty((0, len(bounds)), dtype=np.float64)
        else:
            X_batch = np.atleast_2d(X_inject)
            n_inject = len(X_batch)

        for i_bo, bo in enumerate(bo_mains):
            model = copy.deepcopy(bo.model)

            if X_batch.shape[0] > 0:
                Y_batch = model.predict(X_batch)[0]
                model.add_data(X_batch, Y_batch)
                model.optimize(2)

            for acqfn, batchpts in zip(acq_funcs[i_bo], batchpts_list[i_bo]):
                acqfn.model = model

                for i_bat in range(batchpts):
                    X_next = np.atleast_2d(acqfn.minimize(bounds))

                    if history:
                        self.acq_history[(i_bo, acqfn.name, i_bat)] = copy.deepcopy(
                            acqfn
                        )

                    Y_next = model.predict(X_next)[0]
                    model.add_data(X_next, Y_next)
                    model.optimize(2)
                    X_batch = np.vstack((X_batch, X_next))

        return X_batch[n_inject:, :]
