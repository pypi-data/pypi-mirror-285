import itertools
import warnings

import numpy as np
from scipy.stats import qmc


class InitManager:
    def __init__(self, inittype, bounds, initpts, seed=None, scramble=False):
        """
        Creates initial points which can be queried with the get_x and get_all
        methods. Available types of initial points (parameter inittype) are:
            sobol
            random
            grid
        """
        self.dim = bounds.shape[0]
        self.rng = np.random.default_rng(seed)
        if inittype.lower() == "sobol":
            self.X_init = self._sobol(bounds, initpts, scramble=scramble)
        elif inittype.lower() == "random":
            self.X_init = self._random(bounds, initpts)
        elif inittype.lower() == "grid":
            n_side = np.power(initpts, 1.0 / self.dim)
            if np.all(np.isclose(n_side, n_side.astype(int))):
                n_side = n_side.astype(int)
            else:
                n_side = np.round(n_side).astype(int)
                initpts = n_side**self.dim
                warnings.warn(
                    "Grid based initial point creation modifies"
                    + " initpts so that nth root of it is an integer"
                    + " , where n in the number of dimensions."
                )
            self.X_init = self._grid(bounds, n_side)
        else:
            raise TypeError(f"Unknown initial point type: {inittype}")

    def get_x(self, i):
        """
        Returns the i:th initial point
        """
        return self.X_init[i, :]

    def get_all(self):
        """
        Returns all generated initial points
        """
        return self.X_init

    def _sobol(self, bounds, initpts, scramble=False):
        """
        Initial points with the quasi-random Sobol sequence
        """
        npts = np.max(initpts)
        sampler = qmc.Sobol(d=self.dim, scramble=scramble, seed=self.rng)
        sample = sampler.random(npts)
        pts = qmc.scale(sample, bounds[:, 0], bounds[:, 1])
        if not np.isscalar(initpts) and len(initpts) > 1:
            pts = self._extend(pts, initpts)
        return pts

    def _random(self, bounds, initpts):
        """
        Initial points randomly
        """
        npts = np.max(initpts)
        pts = self.rng.random((npts, self.dim))
        pts = pts * (bounds[:, 1] - bounds[:, 0]) + bounds[:, 0]
        if not np.isscalar(initpts) and len(initpts) > 1:
            pts = self._extend(pts, initpts)
        return pts

    def _grid(self, bounds, npts):
        """
        Initial points in a grid. Total number of points returned is npts^dim.
        """
        if not np.isscalar(npts) and len(npts) > 1:
            pts = []
            for task, task_npts in enumerate(npts):
                task_pts = self._make_grid(bounds, task_npts)
                pts.append(np.hstack((task_pts, np.full((len(task_pts), 1), task))))
            pts = np.vstack(pts)
        else:
            pts = self._make_grid(bounds, int(np.take(npts, 0)))
        return pts

    def _make_grid(self, bounds, npts):
        """
        Return grid with npts points across bounds in each dimension.
        """
        base = [np.linspace(*b, num=npts, endpoint=True) for b in bounds]
        return np.array(list(itertools.product(*base))).astype(float)

    def _extend(self, data, npts):
        """
        Extend initial points with task index.
        """
        data = np.atleast_2d(data)
        data_extended = []
        for task, task_npts in enumerate(npts):
            task_data = np.hstack((data[:task_npts], np.full((task_npts, 1), task)))
            data_extended.append(task_data)
        data_extended = np.vstack(data_extended)
        return data_extended
