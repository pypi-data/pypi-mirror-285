from __future__ import annotations

import copy
import warnings
from abc import ABC, abstractmethod

import GPy
import numpy as np
import numpy.typing as npt
from GPy.kern import Kern

try:
    import torch
    import gpytorch
except:
    pass

from boss.utils.arrays import shape_consistent_X, shape_consistent_XY
from boss.utils.typing import ArrayLike1D, ArrayLike2D


class BaseModel(ABC):
    """
    Base class for surrogate models used in Bayesian optimization.
    """

    @property
    @abstractmethod
    def dim(self) -> int:
        pass

    @dim.setter
    def dim(self, _) -> None:
        raise AttributeError("Cannot set read-only attribute dim")

    @property
    @abstractmethod
    def X(self) -> npt.NDArray:
        pass

    @property
    @abstractmethod
    def Y(self) -> npt.NDArray:
        pass

    @Y.setter
    def Y(self, _) -> None:
        raise AttributeError("Cannot set read-only attribute Y")

    @X.setter
    def X(self, _) -> None:
        raise AttributeError("Cannot set read-only attribute X")

    @abstractmethod
    def add_data(self, X_new: npt.ArrayLike, Y_new: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        pass

    @abstractmethod
    def redefine_data(self, X: npt.ArrayLike, Y: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        pass

    @abstractmethod
    def get_best_xy(self) -> tuple[npt.NDArray, float]:
        """
        Returns the lowest energy acquisition (x, y).
        """
        pass

    @abstractmethod
    def predict(
        self, x: npt.ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise) and normalisation (norm).
        """
        pass

    @abstractmethod
    def predict_grads(
        self, x: npt.ArrayLike, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns prediction mean and variance gradients with respect to input
        at point x, with or without normalisation (norm).
        """
        pass

    @abstractmethod
    def predict_mean_sd_grads(
        self, x: npt.ArrayLike, noise: bool = True, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray, npt.NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise) and
        normalisation (norm).
        """
        pass

    @abstractmethod
    def predict_mean_grad(
        self, x: npt.ArrayLike, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model mean and its gradient at point x, with or without
        normalisation (norm).
        """
        pass

    @abstractmethod
    def estimate_num_local_minima(self, search_bounds: ArrayLike2D) -> int:
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        pass

    @abstractmethod
    def get_all_params(self) -> dict[str, float | npt.ArrayLike]:
        """
        Returns model parameters as a dictionary.
        """
        pass

    @abstractmethod
    def get_unfixed_params(self) -> npt.NDArray:
        """
        Returns the unfixed parameters of the model in an array.
        """
        pass

    @abstractmethod
    def sample_unfixed_params(self, num_samples: int):
        """
        Sample unfixed model parameters.
        """
        pass

    @abstractmethod
    def set_unfixed_params(self, params: npt.NDArray) -> None:
        """
        Sets the unfixed parameters of the model to given values.
        """
        pass

    @abstractmethod
    def optimize(self) -> None:
        """
        Updates unfixed model parameters.
        """
        pass


class STModel(BaseModel):
    """
    Functionality for creating, refitting and optimizing a GP model
    """

    def __init__(
        self,
        kernel: Kern,
        X: npt.ArrayLike,
        Y: npt.ArrayLike,
        noise: float = 1e-12,
        ynorm: bool = False,
    ) -> None:
        """
        Initializes the STModel class.
        """
        # normalise observation mean:
        self.normmean = np.mean(Y)
        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        # previous boss code used normsd to normalise observation variance:
        # if self.ynorm: self.normsd = np.std(Y)
        # current version normalises observation range:
        self.normsd = np.ptp(Y) if self.use_norm else 1
        # note that the choice betweeen variance or range normalisation needs
        # to be taken into account when we set kernel parameter priors
        # normalised data:
        Y_norm = (Y - self.normmean) / self.normsd
        # initialise model
        self.model = GPy.models.GPRegression(X, Y_norm, kernel=kernel, noise_var=noise)
        self.model.likelihood.fix()

    @property
    def dim(self) -> int:
        return self.model.kern.input_dim

    @property
    def kernel(self) -> Kern:
        return self.model.kern

    @property
    def X(self) -> npt.NDArray:
        return self.model.X

    @property
    def Y(self) -> npt.NDArray:
        return self.model.Y * self.normsd + self.normmean

    def __deepcopy__(self, memo: dict) -> STModel:
        cls = self.__class__
        model_copy = cls.__new__(cls)
        memo[id(self)] = model_copy
        for key, val in self.__dict__.items():
            # A GPy kernel object attached to a model can't be deepcopied in the
            # usual way due to a bug so we have to use the kernel's custom copy method.
            if key == "_kernel":
                setattr(model_copy, key, val.copy())
            else:
                setattr(model_copy, key, copy.deepcopy(val, memo))
        return model_copy

    def add_data(self, X_new: npt.ArrayLike, Y_new: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        X_new, Y_new = shape_consistent_XY(X_new, Y_new, self.dim)
        X = np.vstack([self.X, X_new])
        Y = np.vstack([self.Y, Y_new])
        self.redefine_data(X, Y)

    def redefine_data(self, X: npt.ArrayLike, Y: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        X, Y = shape_consistent_XY(X, Y, self.dim)
        # update normalisation
        self.normmean = np.mean(Y)
        if self.use_norm:
            self.normsd = np.ptp(Y)
        # update model
        Y_norm = (Y - self.normmean) / self.normsd
        self.model.set_XY(np.atleast_2d(X), np.atleast_2d(Y_norm))

    def get_best_xy(self) -> tuple[npt.NDArray, float]:
        """
        Returns the lowest energy acquisition (x, y).
        """
        x_best = np.array(self.X[np.argmin(self.Y)])
        y_best = np.min(self.Y)
        return x_best, y_best

    def predict(
        self, X: npt.ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        X = shape_consistent_X(X, self.dim)
        m, v = self.model.predict(X, include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(
        self, X: npt.ArrayLike, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        X = shape_consistent_X(X, self.dim)
        dmdx, dvdx = self.model.predictive_gradients(X)
        if norm:
            return dmdx, dvdx
        return dmdx * self.normsd, dvdx * (self.normsd**2)

    def predict_mean_sd_grads(
        self, X: npt.ArrayLike, noise: bool = True, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray, npt.NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).

        This method is a wrapper used primarily during calculations
        of acquisition functions and their derivatives.
        """
        m, v = self.predict(X, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(X, norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, X: npt.ArrayLike, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """Returns model mean and its gradient at point x.

        This method is a wrapper used primarily when the mean function
        is minimized in order to obtain a global minimum prediction.
        """
        m, _ = self.predict(X, norm=norm)
        dmdx, _ = self.predict_grads(X, norm=norm)
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds: ArrayLike2D) -> int:
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period"):
                bound_distance = (bounds[1] - bounds[0]) / kern.period[0]
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2
            numpts *= max(1, bound_distance / kern.lengthscale[0])
        return int(numpts)

    # model parameters:

    def get_all_params(self) -> dict[str, float | list]:
        """
        Returns model parameters as a dictionary with entries:
        noise, variance, lengthscales, periods
        where the last two are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        noise = self.model.likelihood.variance[0]
        sigma = self.model.kern.param_array[0]
        lss = []
        pers = []
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for kern in ks:
            lss.append(kern.lengthscale[0])
            if hasattr(kern, "period"):
                pers.append(kern.period[0])

        # the variables are returned in a dict:
        params = {}
        params["noise"] = noise
        params["variance"] = sigma
        params["lengthscales"] = lss
        params["periods"] = pers

        return params

    def get_unfixed_params(self) -> npt.NDArray:
        """
        Returns the unfixed parameters of the model in an array.
        """
        return np.array(self.model.unfixed_param_array.copy()).astype(float)

    def sample_unfixed_params(self, num_samples: int) -> npt.NDArray:
        """
        Sample unfixed model parameters.
        """
        hmc = GPy.inference.mcmc.HMC(self.model)
        burnin = hmc.sample(int(num_samples * 0.33))
        return hmc.sample(num_samples)

    def set_unfixed_params(self, params: npt.NDArray) -> None:
        """
        Sets the unfixed parameters of the model to given values.
        """
        self.model[self.model._fixes_] = params
        self.model.parameters_changed()

    def optimize(self, restarts: int = 1) -> None:
        """
        Updates the model hyperparameters by maximizing marginal likelihood.
        """
        self.model.optimization_runs = []
        if restarts == 1:
            self.model.optimize()
        else:
            self.model.optimize_restarts(
                num_restarts=restarts, verbose=False, messages=False
            )


class GradientModel(STModel):
    """
    Functionality for creating, refitting and optimizing a GP model with
    gradient observations.

    The GradientModel utilizes the GPy MultioutputGP model class, which allows
    for multiple input and output channels. We can include observed gradient
    data in GPR by defining separate channels for partial derivatives, in
    addition to the main function value channel.

    The DiffKern kernel computes cross-covariances between channels.
    """

    def __init__(
        self,
        kernel: Kern,
        X: npt.ArrayLike,
        Y_dY: npt.ArrayLike,
        noise: float = 1e-12,
        ynorm: bool = False,
    ) -> None:
        """
        Initializes the GradientModel class.
        """
        self._dim = kernel.input_dim

        # input channels
        X_list = [X] * (self.dim + 1)

        # observations
        Y, dY = Y_dY[:, :1], Y_dY[:, 1:]
        # normalization
        self.use_norm = ynorm
        self.normmean = np.mean(Y)
        self.normsd = np.ptp(Y) if self.use_norm else 1
        Y_norm = (Y - self.normmean) / self.normsd
        # output channels
        Y_list = [Y_norm] + [dY[:, d, None] for d in range(self.dim)]

        # the kernel is accompanied with a DiffKern for each partial derivative.
        kernel_list = [kernel]
        kernel_list += [GPy.kern.DiffKern(kernel, d) for d in range(self.dim)]

        # noise is given to the likelihood.
        likelihood = GPy.likelihoods.Gaussian(variance=noise)
        likelihood_list = [likelihood] * (self.dim + 1)

        # initialize model
        self.model = GPy.models.MultioutputGP(
            X_list=X_list,
            Y_list=Y_list,
            kernel_list=kernel_list,
            likelihood_list=likelihood_list,
        )
        self.model.likelihood.fix()

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def kernel(self) -> Kern:
        return self.model.kern

    @property
    def X(self):
        X_multioutput = self.model.X[:, :-1]
        output_index = self.model.X[:, -1]

        return X_multioutput[np.where(output_index == 0)[0]]

    @property
    def Y(self):
        Y_multioutput = self.model.Y
        output_index = self.model.X[:, -1]

        Y_norm = Y_multioutput[np.where(output_index == 0)[0]]
        Y = Y_norm * self.normsd + self.normmean

        dY = np.empty((len(Y), self.dim), dtype=float)
        for d in range(self.dim):
            dY[:, d, None] = Y_multioutput[np.where(output_index == d + 1)[0]]

        return np.concatenate((Y, dY), axis=1)

    def add_data(self, X_new: npt.ArrayLike, Y_dY_new: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        # construct new unnormalized dataset
        X_new, Y_dY_new = shape_consistent_XY(X_new, Y_dY_new, self.dim, ygrad=True)
        X = np.vstack([self.X, X_new])
        Y_dY = np.vstack([self.Y, Y_dY_new])
        # update model
        self.redefine_data(X, Y_dY)

    def redefine_data(self, X: npt.ArrayLike, Y_dY: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        Y, dY = Y_dY[:, :1], Y_dY[:, 1:]
        # update normalization
        self.normmean = np.mean(Y)
        if self.use_norm:
            self.normsd = np.ptp(Y)
        # update model
        Y_norm = (Y - self.normmean) / self.normsd
        X_list = [X] * (self.dim + 1)
        Y_list = [Y_norm] + [dY[:, d, None] for d in range(self.dim)]
        self.model.set_XY(X_list, Y_list)

    def get_best_xy(self) -> tuple[npt.NDArray, float]:
        """
        Returns the lowest energy acquisition (x, y).
        """
        x_best = np.array(self.X[np.argmin(self.Y[:, 0])])
        y_best = np.min(self.Y[:, 0])
        return x_best, y_best

    def predict(
        self, X: npt.ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise) and normalisation (norm).
        """
        m, v = self.model.predict([np.atleast_2d(X)], include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(
        self, X: npt.ArrayLike, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x, with or without normalisation (norm).
        """
        dmdx, dvdx = self.model.predictive_gradients([np.atleast_2d(X)])
        if norm:
            return dmdx[:, :, None], dvdx
        return (dmdx * self.normsd)[:, :, None], dvdx * (self.normsd**2)

    def estimate_num_local_minima(self, search_bounds: ArrayLike2D) -> int:
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1

        # For the GradientModel, the self.model.kern is the
        # MultioutputDerivativeKern. If self.dim > 1, the Prod kernel which
        # contains the individual kernels is located by
        # self.model.kern.parts[0]. If self.dim == 1, the individual kernel is
        # located by self.model.kern.parts.
        if self.dim > 1:
            ks = self.model.kern.parts[0].parts
        else:
            ks = self.model.kern.parts
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period"):
                bound_distance = (bounds[1] - bounds[0]) / kern.period[0]
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2
            numpts *= max(1, bound_distance / kern.lengthscale[0])
        return int(numpts)

    def get_all_params(self) -> dict[str, float | list]:
        """
        Returns model parameters as a dictionary with entries::
        noise, variance, lengthscales, periods
        where the last two are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        # The MultioutputGP model can contain multiple likelihoods
        # We only use one, and access the noise through model.likelihood[0]
        noise = self.model.likelihood[0]
        sigma = self.model.kern.param_array[0]
        lss = []
        pers = []
        # For the GradientModel, the self.model.kern is the
        # MultioutputDerivativeKern. If self.dim > 1, the Prod kernel which
        # contains the individual kernels is located by
        # self.model.kern.parts[0]. If self.dim == 1, the individual kernel is
        # located by self.model.kern.parts.
        if self.dim > 1:
            ks = self.model.kern.parts[0].parts
        else:
            ks = self.model.kern.parts
        for kern in ks:
            lss.append(kern.lengthscale[0])
            if hasattr(kern, "period"):
                pers.append(kern.period[0])

        # the variables are returned in a dict:
        params = {}
        params["noise"] = noise
        params["variance"] = sigma
        params["lengthscales"] = lss
        params["periods"] = pers

        return params


class MTModel(STModel):
    """
    Functionality for creating, refitting and optimizing a multi-task GP model.
    """

    def __init__(
        self,
        kernel: Kern,
        X: npt.ArrayLike,
        Y: npt.ArrayLike,
        noise: float = 1e-12,
        ynorm: bool = False,
    ) -> None:
        """
        Initializes the multi-task model class.
        """
        self._dim = kernel.input_dim
        self.num_tasks = kernel.parameters[-1].output_dim

        X, Y = shape_consistent_XY(X, Y, self.dim)
        inds = np.squeeze(X[:, -1]).astype(int)
        self.check_task_indices(inds)
        XX = [X[inds == index, :-1] for index in range(self.num_tasks)]
        YY = [Y[inds == index] for index in range(self.num_tasks)]

        # normalise observation mean and scale:
        self.normmean = [np.mean(Y) for Y in YY]
        self.normsd = [1] * self.num_tasks

        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        self.normsd = [np.ptp(Y) for Y in YY] if self.use_norm else 1

        # normalised observation list:
        YY_norm = [(Y - m) / s for Y, m, s in zip(YY, self.normmean, self.normsd)]
        self.model = GPy.models.GPCoregionalizedRegression(XX, YY_norm, kernel=kernel)
        self.model.mixed_noise.constrain_fixed(noise)

    @property
    def dim(self) -> int:
        return self._dim

    def get_X(self, index: int | None = None) -> npt.NDArray:
        """
        Returns observed X.
        """
        if index is None:
            return self.model.X
        else:
            return self.model.X[self.inds == index, :-1]

    def get_Y(self, index: int | None = None) -> npt.NDArray:
        """
        Returns observed Y.
        """
        if index is None:
            Y = self.model.Y.copy()
            for index in range(self.num_tasks):
                Y[self.inds == index] *= self.normsd[index]
                Y[self.inds == index] += self.normmean[index]
            return Y
        else:
            Y_norm = self.model.Y[self.inds == index]
            return Y_norm * self.normsd[index] + self.normmean[index]

    @property
    def X(self) -> npt.NDArray:
        return self.get_X()

    @property
    def Y(self) -> npt.NDArray:
        return self.get_Y()

    @property
    def inds(self) -> npt.NDArray:
        return self.model.X[:, -1].astype(int)

    def add_data(self, X_new: npt.ArrayLike, Y_new: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        X_new, Y_new = shape_consistent_XY(X_new, Y_new, self.dim)
        inds_new = X_new[:, -1].astype(int)

        # construct new datasets
        X = np.vstack([self.X, X_new])
        Y = np.vstack([self.Y, Y_new])
        inds = X[:, -1].astype(int)

        # update normalisation
        Y_norm = np.vstack([self.model.Y, np.zeros_like(Y_new)])
        for i in np.unique(inds_new):
            self.normmean[i] = np.mean(Y[inds == i])
            if self.use_norm:
                self.normsd[i] = np.ptp(Y[inds == i])
            Y_norm[inds == i] = (Y[inds == i] - self.normmean[i]) / self.normsd[i]

        # update model
        self.model.Y_metadata = {"output_index": inds}
        self.model.set_XY(X, Y_norm)

    def redefine_data(self, X: npt.ArrayLike, Y: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        X, Y = shape_consistent_XY(X, Y, self.dim)
        inds = X[:, -1].astype(int)
        self.check_task_indices(inds)

        # update normalisation
        Y_norm = np.zeros_like(Y)
        for i in range(self.num_tasks):
            self.normmean[i] = np.mean(Y[inds == i])
            if self.use_norm:
                self.normsd[i] = np.ptp(Y[inds == i])
            Y_norm[inds == i] = (Y[inds == i] - self.normmean[i]) / self.normsd[i]

        # update model
        self.model.Y_metadata = {"output_index": inds}
        self.model.set_XY(X, Y_norm)

    def get_best_xy(self, index: int | None = None) -> tuple[npt.NDArray, float]:
        """
        Returns the lowest energy acquisitions (x, y).
        """
        if index is None:
            x_best = []
            y_best = []
            for index in range(self.num_tasks):
                Y_i = self.get_Y(index)
                x_best.append(np.append(self.get_X(index)[np.argmin(Y_i)], index))
                y_best.append(np.min(Y_i))
        else:
            Y_i = self.get_Y(index)
            x_best = np.array(self.get_X(index)[np.argmin(Y_i)])
            y_best = np.min(Y_i)
        return x_best, y_best

    def check_task_indices(self, inds: npt.NDArray) -> None:
        """
        Raises an error if all tasks are not included in the index list or if
        the list includes more tasks than expected.
        """
        counts = np.bincount(inds, minlength=self.num_tasks)
        if not np.all(counts > 0):
            raise ValueError("All tasks must be represented in the dataset.")

        num_tasks = max(inds) + 1
        if num_tasks > self.num_tasks:
            raise ValueError(
                f"Received a dataset with {num_tasks} tasks. "
                f"Expected {self.num_tasks} tasks."
            )

    def extend_input(self, x: npt.ArrayLike, index: ArrayLike1D) -> npt.NDArray:
        """
        Returns x extended with task index.
        """
        x = np.atleast_2d(x)
        inds = np.full((len(x), 1), np.array(index).reshape(-1, 1))
        x = np.hstack((x, inds))
        return x

    def predict(
        self,
        X: npt.ArrayLike,
        index: npt.ArrayLike | None = None,
        noise: bool = True,
        norm: bool = False,
    ):
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise) and normalisation (norm).

        Task index can be included in the input X or provided with index.
        """
        # extend x with task index if needed
        X = shape_consistent_X(X, self.dim - (index is not None))
        if index is not None:
            X = self.extend_input(X, index)
        # build metadata
        inds = X[:, -1].astype(int)
        meta = {"output_index": inds}
        # predict output
        m, v = self.model.predict(X, Y_metadata=meta, include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        # remove normalisation
        for i in np.unique(inds):
            m[inds == i] = m[inds == i] * self.normsd[i] + self.normmean[i]
            v[inds == i] = v[inds == i] * self.normsd[i] ** 2
        return m, v

    def predict_grads(
        self, X: npt.ArrayLike, index: ArrayLike1D | None = None, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x, with or without normalisation (norm).

        Task index can be included in the input x or provided with index.
        """
        # extend x with task index if needed
        X = shape_consistent_X(X, self.dim - (index is not None))
        if index is not None:
            X = self.extend_input(X, index)
        # predictive gradients
        dmdx, dvdx = self.model.predictive_gradients(np.atleast_2d(X))
        if norm:
            return dmdx, dvdx
        # remove normalisation
        inds = X[:, -1].astype(int)
        for i in np.unique(inds):
            dmdx[inds == i] *= self.normsd[i]
            dvdx[inds == i] *= self.normsd[i] ** 2
        return dmdx, dvdx

    def predict_mean_sd_grads(
        self,
        X: npt.ArrayLike,
        index: ArrayLike1D | None = None,
        noise: bool = True,
        norm: bool = True,
    ) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray, npt.NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise) and
        normalisation (norm).

        Task index can be included in the input x or provided with index.
        """
        m, v = self.predict(X, index=index, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(X, index=index, norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, X: npt.ArrayLike, index: ArrayLike1D | None = None, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model mean and its gradient at point x, with or without
        normalisation (norm).

        Task index can be included in the input x or provided with index.
        """
        m, _ = self.predict(X, index=index, norm=norm)
        dmdx, _ = self.predict_grads(X, index=index, norm=norm)
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds: ArrayLike2D) -> int:
        """
        Returns estimated number of local minima calculated based on model
        properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1

        # get baseline kernel parameters (exclude coregionalisation kernel)
        ks = self.model.kern.parameters[:-1]
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period"):
                bound_distance = (bounds[1] - bounds[0]) / kern.period[0]
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2
            numpts *= max(1, bound_distance / kern.lengthscale[0])
        return int(numpts)

    def predict_task_covariance(self, x: npt.ArrayLike) -> npt.NDArray:
        """
        Return predictive covariance between tasks at point x.
        """
        inds = np.arange(self.num_tasks)
        x = np.squeeze(x)[:-1]
        x_list = np.vstack([self.extend_input(x, i) for i in inds])
        meta = {"output_index": inds.astype(int)}
        _, cov = self.model.predict(x_list, Y_metadata=meta, full_cov=True)
        return np.outer(self.normsd, self.normsd) * cov

    def get_all_params(self) -> dict[str, float | list]:
        """
        Returns model parameters as a dictionary with entries:
        noise, lengthscales, periods, kappa, W
        There exists a period only for those dimensions which are using a
        periodic kernel.
        """
        # likelihood params
        ll = self.model.likelihood.likelihoods_list
        noise = [likelihood.variance[0] for likelihood in ll]
        # kernel params
        lss = []
        pers = []
        # get baseline kernel parameters (exclude coregionalisation kernel)
        ks = self.model.kern.parameters[:-1]
        for kern in ks:
            lss.append(kern.lengthscale[0])
            if hasattr(kern, "period"):
                pers.append(kern.period[0])
        # coregionalisation params
        kappa = np.array(self.model.kern.parameters[-1].kappa).reshape(1, -1)
        W = np.array(self.model.kern.parameters[-1].W).reshape(1, -1)

        # the variables are returned in a dict:
        params = {}
        params["noise"] = noise
        params["lengthscales"] = lss
        params["periods"] = pers
        params["kappa"] = kappa
        params["W"] = W

        return params

    def get_task_covariance(self) -> npt.NDArray:
        """
        Returns estimated task covariance matrix.
        """
        kappa = np.array(self.model.kern.parameters[-1].kappa)
        W = np.array(self.model.kern.parameters[-1].W)
        cov = np.outer(W, W) + np.diag(kappa)
        return np.outer(self.normsd, self.normsd) * cov


class STModelTorch(BaseModel):
    """
    Functionality for creating, refitting and optimizing a GP model with Torch backend
    """

    def __init__(
        self,
        kernel: gpytorch.kernels | None = None,
        X: npt.ArrayLike | None = None,
        Y: npt.ArrayLike | None = None,
        noise: float = 1e-12,
        ynorm=False,
    ):
        """
        Initializes the STModelTorch class.
        """
        if not torch.cuda.is_available():
            print(
                "STModelTorch: No GPU backend supported cuda device, defaulted to CPU"
            )
        self.which_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.datatype = torch.float64  # Manual control over datatype
        torch.set_default_dtype(
            self.datatype
        )  # sets common torch dtype 32 faster but 64 to support scipy>=1.8

        self.ynorm = ynorm
        self.noise = noise

        self.reset(kernel, X, Y, self.noise, self.ynorm)

    def reset(self, kernel, X, Y, noise, ynorm):
        class GPyTorchRegression(
            gpytorch.models.ExactGP
        ):  # Inherit base model used for wrapping
            def __init__(self, train_x, train_y, likelihood, kernel):
                super().__init__(train_x, train_y, likelihood)
                self.mean = gpytorch.means.ConstantMean()
                self.covar_module = kernel

            def forward(self, x):  # Provide custom forward
                mean = self.mean(x)
                covar = self.covar_module(x)
                return gpytorch.distributions.MultivariateNormal(
                    mean, covar, validate_args=True
                )

        if X is not None and Y is not None:
            self.normmean = torch.mean(
                torch.tensor(Y), dtype=self.datatype
            )  # manually set dtype, inherits wrong dtype from numpy otherwise
            self.normsd = torch.tensor(np.ptp(Y)) if ynorm else 1.0
            X = torch.Tensor(X)
            Y = (torch.Tensor(Y).reshape(-1) - self.normmean) / self.normsd

        self.likelihood = gpytorch.likelihoods.GaussianLikelihood(
            noise_constraint=gpytorch.constraints.GreaterThan(1e-13)
        )
        self.model = GPyTorchRegression(
            X, Y, self.likelihood, kernel
        )  # wrapper for model class
        self.likelihood.noise = noise
        self.X_torch = X
        self.Y_torch = Y
        if self.X_torch is not None:
            self.X_torch = self.X_torch.to(self.which_device)
        if self.Y_torch is not None:
            self.Y_torch = self.Y_torch.to(self.which_device)
        self.likelihood.to(self.which_device)
        self.model.to(self.which_device)

        # set false for get_unifxed params as it goes by whether objects have grad

        self.likelihood.noise_covar.raw_noise.requires_grad = (
            False  # can in the future set kwd for optimizing noise
        )
        self.model.mean.raw_constant.requires_grad = False

    @property
    def kernel(self) -> gpytorch.kernels:
        return self.model.covar_module

    @property
    def dim(self) -> int:
        return len(self._get_kernel_parts())

    @property
    def X(self) -> npt.NDArray:
        if self.X_torch is not None:
            return np.atleast_2d(self.X_torch.cpu().numpy())
        else:
            return np.empty((0, self.dim), dtype=self.datatype)

    @property
    def Y(self) -> npt.NDArray:
        if self.Y_torch is not None:
            Y = self.Y_torch * self.normsd + self.normmean
            return np.atleast_2d(Y.cpu().numpy().reshape(-1, 1))
        else:
            return np.empty((0, self.dim), dtype=self.datatype)

    def _get_kernel_parts(self) -> list(gpytorch.kernels):
        """
        Returns kernel(s) from the product kernel
        """
        if isinstance(self.kernel.base_kernel, gpytorch.kernels.ProductKernel):
            kernel_parts = list(self.kernel.base_kernel.kernels)
        else:
            kernel_parts = list(self.kernel.sub_kernels())
        return kernel_parts

    def predict(
        self, x: npt.ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance at point x, with model variance (noise) as we return likelihood instead of model posterior.
        """
        x = np.atleast_2d(x)
        self.model.eval()
        self.likelihood.eval()
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            x_torch = torch.tensor(
                x, dtype=self.datatype, device=self.which_device
            )  # manually set dtype, otherwise inherits wrong type from numpy
            if noise:
                y_preds = self.likelihood(
                    self.model(x_torch)
                )  # equivalent to GPy inc likelihood = True, takes into acc epistemic uncertainty
            else:
                y_preds = self.model(
                    x_torch
                )  # only alleatoric uncertainty equivalent to GPy inc likelihood = False

            if norm:
                m = y_preds.mean
                v = y_preds.variance
            else:
                m = y_preds.mean * self.normsd + self.normmean
                v = y_preds.variance * (self.normsd**2)

        return m.cpu().numpy().reshape(-1, 1), v.cpu().numpy().reshape(-1, 1)

    def predict_grads(
        self, x: npt.ArrayLike, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        x = np.atleast_2d(x)
        x_torch = torch.tensor(
            x, dtype=self.datatype, requires_grad=True, device=self.which_device
        )
        self.model.eval()
        self.likelihood.eval()

        with gpytorch.settings.fast_pred_var():
            post = self.likelihood(self.model(x_torch))
            dmdx = torch.autograd.grad(post.mean.sum(), x_torch, retain_graph=True)[0]
            dvdx = torch.autograd.grad(post.variance.sum(), x_torch)[0]

        # Ensure shapes match Gpy return for EI acquisition function
        N, Q = x_torch.shape
        D = 1  # for single objective tasks
        dmdx = dmdx.view(N, Q, D)

        if norm:
            pass
        else:
            dmdx = dmdx * self.normsd
            dvdx = dvdx * (self.normsd**2)

        return (
            dmdx.cpu().numpy(),
            dvdx.cpu().numpy(),
        )

    def predict_mean_sd_grads(
        self, x: npt.ArrayLike, noise: bool = True, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray, npt.NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise) and
        normalisation (norm).
        """
        m, v = self.predict(x, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(x, norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, x: npt.ArrayLike, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model mean and its gradient at point x, with or without
        normalisation (norm).
        """
        m, _ = self.predict(x, norm=norm)
        dmdx, _ = self.predict_grads(x, norm=norm)
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds: ArrayLike2D) -> int:
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        numpts = 1
        ks = self._get_kernel_parts()

        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period_length"):
                bound_distance = (bounds[1] - bounds[0]) / float(kern.period_length)
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2

            numpts *= max(1, bound_distance / float(kern.lengthscale))

        return int(numpts)

    def get_all_params(self) -> dict[str, float | list]:
        """
        Returns model parameters as a dictionary with entries::
        noise, variance, lengthscales, periods
        where the last two are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        noise = self.likelihood.noise[0].item()  # homoscedastic so all noise equal
        sigma = (
            self.kernel.outputscale.item()
        )  # only one scale, since only wrapper kernel only contains scale
        lss = []
        pers = []

        kernel_parts = self._get_kernel_parts()

        for kern in kernel_parts:
            lss.append(kern.lengthscale.item())
            if hasattr(kern, "period_length"):
                pers.append(kern.period_length.item())

        # the variables are returned in a dict:
        params = {}
        params["noise"] = noise
        params["variance"] = sigma
        params["lengthscales"] = lss
        params["periods"] = pers

        return params

    def get_unfixed_params(self) -> npt.NDArray:
        """
        Returns the unfixed parameters of the model in an array.
        """
        unfixed = self._resolve_unfixed_params()  # unfixed parameter names
        params = np.zeros(len(unfixed))
        for ind, param_name in enumerate(unfixed):
            current_attr = self.model
            for attr in param_name.split("."):
                current_attr = getattr(current_attr, attr)
            params[ind] = float(current_attr)
        return params

    def sample_unfixed_params(self, num_samples):
        """
        Sample unfixed model parameters.
        """
        raise NotImplementedError(
            "This method is not available in the current torch backend model."
        )

    def _resolve_unfixed_params(self) -> list[str]:
        """
        Resolves whether parameter is fixed on unfixed based on gradient
        """
        unfixed = []
        for param_name, param in self.model.named_parameters():
            if param.requires_grad:
                unfixed.append(param_name.replace("raw_", ""))
        return unfixed

    def set_unfixed_params(
        self, params: npt.NDArray
    ) -> None:  # setting hypers by object names!
        """
        Sets the unfixed parameters of the model to given values.
        """
        hypers = dict(zip(self._resolve_unfixed_params(), torch.tensor(params)))
        self.model.initialize(**hypers)

    def optimize(self, restarts: int = 0) -> None:
        """
        Updates the model hyperparameters by maximizing marginal likelihood.
        """

        # Yuhaos heuristic efficient optimiser routine based on input dimension
        if self.X_torch.shape[1] > 3:
            lr = 0.002
            max_iter = 1000

        elif self.X_torch.shape[1] > 2:
            lr = 0.002
            max_iter = 300

        elif self.X_torch.shape[1] > 1:
            lr = 0.01
            max_iter = 200

        else:
            lr = 0.1
            max_iter = 200

        self.model.train()
        self.likelihood.train()
        optimizer = torch.optim.LBFGS(
            params=self.model.parameters(),
            tolerance_grad=1e-9,
            lr=lr,
            max_iter=max_iter,
            tolerance_change=1e-9,
            history_size=5,
            line_search_fn="strong_wolfe",
        )

        mll = gpytorch.mlls.ExactMarginalLogLikelihood(self.likelihood, self.model)

        def closure():
            optimizer.zero_grad()
            # Output from model
            output = self.model(self.X_torch)
            # Calc loss and backprop gradients
            loss = -mll(output, self.Y_torch)
            loss.backward()
            return loss

        optimizer.step(closure)

    def add_data(self, x_new, y_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        Y_unnorm = ((self.Y_torch * self.normsd) + self.normmean).cpu().numpy()
        added_X = np.vstack((self.X_torch.cpu().numpy(), x_new))
        added_Y = np.vstack((Y_unnorm.reshape(-1, 1), y_new))

        self.redefine_data(added_X, added_Y)

    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        self.reset(self.kernel, X, Y, self.noise, self.ynorm)

    def get_best_xy(self):
        """
        Returns the lowest energy acquisitions (x, y).
        """
        x_best = self.X_torch[torch.argmin(self.Y_torch.reshape(-1, 1))]
        y_best = np.min(self.Y.reshape(-1, 1))
        return x_best.cpu().numpy(), y_best


class HeteroscedasticModel(STModel):
    """
    Functionality for creating, refitting and optimizing a Heteroscedastic GP model
    """

    def __init__(
        self,
        kernel,
        hsc_noise,
        X: npt.ArrayLike,
        Y: npt.ArrayLike,
        hsc_args: dict | None = None,
        noise_init: ArrayLike1D = 1e-12,
        ynorm: bool = False,
    ) -> None:
        """
        Initializes the HeteroscedasticModel class.
        """
        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        self.hsc_noise = hsc_noise
        self.hsc_args = hsc_args
        self.noise_init = np.atleast_1d(noise_init)

        X, Y = shape_consistent_XY(X, Y, kernel.input_dim)
        self.normmean = np.mean(Y)
        # previous boss code used normsd to normalise observation variance:
        # if self.ynorm: self.normsd = np.std(Y)
        # current version normalises observation range:
        self.normsd = np.ptp(Y) if self.use_norm else 1.0
        # note that the choice betweeen variance or range normalisation needs
        # to be taken into account when we set kernel parameter priors
        # normalised data:
        Y_norm = (Y - self.normmean) / self.normsd

        # set Y_metadata
        Ny = Y.shape[0]
        Y_metadata = {"output_index": np.arange(Ny)[:, None]}
        # initalise model
        self.model = GPy.models.GPHeteroscedasticRegression(
            X, Y_norm, kernel=kernel, Y_metadata=Y_metadata
        )
        # for the first hyperparameter optimization the noise
        # is given pointwise by the noise_init keyword
        # if only one noise value is given, use constant noise
        if len(self.noise_init) == 1:
            noise_array = np.reshape(
                self.noise_init[0] * np.ones(X.shape[0]), (X.shape[0], -1)
            )
        else:
            noise_array = np.reshape(self.noise_init, (X.shape[0], -1))
        # set the noise parameters to the error in Y
        self.model[".*het_Gauss.variance"] = noise_array
        # fix the noise term
        self.model.het_Gauss.variance.fix()
        self.model.optimize()
        # lengthscales can be used for noise estimation
        # check that kernel lengthscales can be accessed
        lengthscale = None
        if hasattr(self.model.kern, "lengthscale"):
            lengthscale = [self.model.kern.lengthscale]
        elif hasattr(self.model.kern, "parts"):
            lengthscale = []
            for part in self.model.kern.parts:
                if hasattr(part, "lengthscale"):
                    lengthscale.append(part.lengthscale)
                else:
                    lengthscale.append(None)
                    warnings.warn(
                        "Kernel doesn't contain lengthscales in kern or kern.parts."
                    )
        else:
            warnings.warn("Kernel doesn't contain lengthscales in kern or kern.parts.")
        # estimate noise using the user-defined function
        noise_array = self.compute_hsc_noise(X, Y, Y_norm, lengthscale)
        self.model[".*het_Gauss.variance"] = noise_array
        self.model.het_Gauss.variance.fix()

    @property
    def kernel(self) -> Kern:
        return self.model.kern

    @property
    def dim(self) -> int:
        return self.model.kern.input_dim

    def compute_hsc_noise(
        self,
        X: npt.NDArray,
        Y: npt.NDArray,
        Y_norm: npt.NDArray,
        lengthscale: npt.NDArray,
    ) -> npt.NDArray:
        """
        Returns the noise estimate for each point X using the user-defined noise function.
        """
        # if using normalization estimate errors based on normalized data
        if self.use_norm:
            noise_array = self.hsc_noise(
                self.hsc_args, Y=Y_norm, X=X, lengthscale=lengthscale, model=self
            )
        else:
            noise_array = self.hsc_noise(
                self.hsc_args, Y=Y, X=X, lengthscale=lengthscale, model=self
            )
        return noise_array

    def add_data(self, X_new: npt.ArrayLike, Y_new: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        X_new, Y_new = shape_consistent_XY(X_new, Y_new, self.dim)
        X = np.vstack([self.X, X_new])
        Y = np.vstack([self.Y, Y_new])
        self.redefine_data(X, Y)

    def redefine_data(self, X: npt.ArrayLike, Y: npt.ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        # update normalisation
        X, Y = shape_consistent_XY(X, Y, self.dim)
        self.normmean = np.mean(Y)
        self.normsd = np.ptp(Y) if self.use_norm else 1
        Y_norm = (Y - self.normmean) / self.normsd
        # set Y_metadata
        Ny = Y.shape[0]
        Y_metadata = {"output_index": np.arange(Ny)[:, None]}
        # lengthscales can be used for noise estimation
        # check that kernel lengthscales can be accessed
        lengthscale_prev = None
        if hasattr(self.model.kern, "lengthscale"):
            lengthscale_prev = [self.model.kern.lengthscale]
        elif hasattr(self.model.kern, "parts"):
            lengthscale_prev = []
            for part in self.model.kern.parts:
                if hasattr(part, "lengthscale"):
                    lengthscale_prev.append(part.lengthscale)
                else:
                    lengthscale_prev.append(None)
                    warnings.warn(
                        "Kernel doesn't contain lengthscales in kern or kern.parts."
                    )
        else:
            warnings.warn("Kernel doesn't contain lengthscales in kern or kern.parts.")
        # estimate noise using the user-defined function
        noise_array = self.compute_hsc_noise(X, Y, Y_norm, lengthscale_prev)
        # update model by reinstantiating it
        self.model = self._reinit(X, Y_norm, self.kernel, Y_metadata)
        # set the noise parameters to the error in Y
        self.model[".*het_Gauss.variance"] = noise_array
        # we can fix the noise term
        self.model.het_Gauss.variance.fix()

    def _reinit(
        self, X: npt.ArrayLike, Y_norm: npt.ArrayLike, kernel: Kern, Y_metadata: dict
    ) -> GPy.models.GPHeteroscedasticRegression:
        """
        Returns the reinstantiated model with new X and Y data.
        This is done by reinstantiating the model because the 'set_XY'
        method is incorrectly implemented for heterocedastic GPs in GPy.
        """
        model = GPy.models.GPHeteroscedasticRegression(
            X, Y_norm, kernel=kernel, Y_metadata=Y_metadata
        )
        return model

    def predict(
        self, X: npt.ArrayLike, noise: bool = False, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        X = shape_consistent_X(X, self.dim)
        m, v = self.model.predict(
            X,
            include_likelihood=noise,
            Y_metadata=self.model.Y_metadata,
        )
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        else:
            return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(
        self, X: npt.ArrayLike, norm: bool = False
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at points X.
        """
        X = shape_consistent_X(X, self.dim)
        dmdx, dvdx = self.model.predictive_gradients(X)
        if norm:
            return dmdx, dvdx
        else:
            return dmdx * self.normsd, dvdx * (self.normsd**2)

    def predict_mean_sd_grads(
        self, X: npt.ArrayLike, noise: bool = False, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray, npt.NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).

        This method is a wrapper used primarily during calculations
        of acquisition functions and their derivatives.
        """
        m, v = self.predict(X, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(np.atleast_2d(X), norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, X: npt.ArrayLike, norm: bool = True
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """Returns model mean and its gradient at point x.

        This method is a wrapper used primarily when the
        mean function is minimized in order to obtain a
        global minimum prediction.
        """
        m, _ = self.predict(X, norm=norm)
        dmdx, _ = self.predict_grads(X, norm=norm)
        return m, dmdx

    # model parameters:

    def get_all_params(self) -> dict[str, float | list]:
        """
        Returns model parameters as a dictionary with entries:
        variance, noise, lengthscales, periods
        where the last three are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        noise_array = []
        for i in range(self.model.likelihood.variance.size):
            noise_array.append(self.model.likelihood.variance[i][0])

        sigma = self.model.kern.param_array[0]
        lss = []
        pers = []
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for kern in ks:
            lss.append(kern.lengthscale[0])
            if hasattr(kern, "period"):
                pers.append(kern.period[0])

        # the variables are returned in a dict:
        params = {}
        params["noise"] = noise_array
        params["variance"] = sigma
        params["lengthscales"] = lss
        params["periods"] = pers

        return params
