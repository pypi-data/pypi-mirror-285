from __future__ import annotations

from pathlib import Path
from typing import *

import numpy as np
import numpy.typing as npt


class Mesh:
    def __init__(
        self,
        bounds: npt.ArrayLike,
        free_dims: npt.ArrayLike | None = None,
        grid_pts: npt.ArrayLike = (50,),
    ) -> None:
        """
        Creates a mesh := coordinate grid over a hypercube given by bounds.

        The idea is to have 2 different representations of the grid:
            (1) As a coordinate array where each grid node is a single row,
               the shape of the array is thus (num_nodes x num_dim). This
               representation is referred to as `coords` in the code.
            (2) As a list of arrays identical to what would be returned by
               np.meshgrid. This representation is referred to as `grid` in the
               code.

        Representation (1) is used for evaluating vectorized functions on the grid
        while (2) is used for contour and surface plots.

        The class furthermore allows us to make grids for arbitrary slices along
        coordinate axes in our input space by specifying which dimensions
        (i.e. coordinates x, y, z...) are free to vary and which dimensions
        are fixed to create a slice in input space.

        Parameters
        ----------
        bounds : npt.ArrayLike[float, 2d]
            Bounds for the entire input space, one row for each dimension
            in the form of [lower, upper].
        free_dims : npt.ArrayLike[int, 1d] | None
            The free dimenensions of the input space. If none are given, all
            dimensions are assumed to be free.
        grid_pts : npt.ArrayLike[int, 1d]
            The number of grid points per dimension. If only a single value is
            given it will be extended to all dimensions.
        """
        self.bounds = np.atleast_2d(bounds)

        if free_dims is None:
            self.free_dims = np.arange(len(self.bounds))
        else:
            self.free_dims = np.atleast_1d(free_dims)

        # The grid points are the number of points in each dimension.
        grid_pts = np.atleast_1d(grid_pts)
        if len(grid_pts) == 1:
            self.grid_pts = np.repeat(grid_pts, len(self.free_dims))
        else:
            self.grid_pts = np.asarray(grid_pts)

        # The grid shape is similar to grid points, but
        # with the first and second elements swapped to be
        # consistent with the array shapes returned by np.meshgrid.
        self.grid_shape = np.copy(self.grid_pts)
        if len(self.grid_pts) >= 2:
            self.grid_shape[0], self.grid_shape[1] = (
                self.grid_shape[1],
                self.grid_shape[0],
            )

        # construct basis and coords
        self._coords, self._grid = self.build()

    @classmethod
    def from_grid_spec(
        cls, bounds: Sequence[float], grid_spec: Sequence[int]
    ) -> "Mesh":
        """
        Constructor that creates a Mesher instance from a grid specification.

        A grid specification is an array with 3 elements [x1, x2, npts] where x1, x2
        are the free dimensions and npts the number of grid points per dimension. This
        is the same format used by the BOSS keyword pp_models_slice, except that here the
        indexing of the dimensions start from 0.
        """
        slc = grid_spec
        if slc[0] == slc[1]:
            free_dims = [slc[0]]
            shape = (slc[2],)
        else:
            free_dims = [slc[0], slc[1]]
            shape = (slc[2], slc[2])
        self = cls(bounds, free_dims, shape)
        return self

    @property
    def size(self) -> int:
        return np.prod(self.grid_pts)

    @property
    def coords(self) -> npt.NDArray:
        """
        The grid represented as a coordinate array.

        Each node in the grid occupies a single row in the array
        so the resulting shape is (num_nodes, num_dim).
        """
        return self._coords

    @property
    def grid(self) -> list[npt.NDArray]:
        """
        The grid represented as meshgrid arrays.

        The values for each coordinate are given in separate arrays,
        see np.meshgrid for details.
        """
        return self._grid

    def build(self) -> tuple[npt.NDArray, list[npt.NDArray]]:
        """
        Builds two representations of the grid:
        """
        basis = [
            np.linspace(self.bounds[d, 0], self.bounds[d, 1], self.grid_pts[i])
            for i, d in enumerate(self.free_dims)
        ]
        coords = np.nan * np.ones((self.size, len(self.bounds)))
        grid = np.meshgrid(*basis)
        coords[:, self.free_dims] = np.stack([X.flatten() for X in grid], axis=1)
        return coords, grid

    @property
    def fixed_dims(self) -> np.ndarray:
        """The dimensions that have been fixed to a constant value."""
        return np.array([d for d in range(len(self.bounds)) if d not in self.free_dims])

    def get_grid_spec(self) -> List[int]:
        """Returns a grid specification for the current mesh, if one exists."""
        if len(self.free_dims) == 2 and self.grid_shape[0] != self.grid_shape[1]:
            raise RuntimeError("Grid points in x != y.")
        return [*self.free_dims, self.grid_shape[0]]

    def set_fixed_dims(
        self, val: float | Sequence[float], dim: int | Sequence[int] | None = None
    ):
        """
        Fixes the specified grid dimensions to the given values.

        Parameters
        ----------
        val : float
        A constant value for the fixed dimension(s).
        dim : int | None
        The dimensions(s) to fix. Defaults to all non-free dimensions.
        """
        val = np.atleast_1d(val)
        if dim is None:
            dim = self.fixed_dims
        else:
            dim = np.atleast_1d(dim).astype(int)

        if len(val) == 1:
            val = val[0] * np.ones(len(dim))

        intersct = np.intersect1d(self.free_dims, dim)
        if len(intersct) > 0:
            raise ValueError(f"Cannot fix free dimension: {intersct}")

        self._coords[:, dim] = val

    def calc_func(
        self, func: Callable, coord_shaped: bool = False, vectorized: bool = True
    ) -> np.ndarray:
        """
        Calculates a given function over the grid.

        Parameters
        ----------
        func : Callable
        The function which to calcuate over the grid. If vectorized, the function
        is assumed to accept a 2d array as argument where each
        row defines a separate argument to be evaluated.

        coord_shaped : bool
        Determines the shape of the array of returned function values.
        If false, values are returned with shape compatible with meshgrid,
        otherwise they are in coordinate format: shape (n_pts, dim).

        vectorized : bool
        If true, the function is assumed to be vectorized and will only be called
        once with the whole grid as input. Otherwise the function will be called once
        per node in the grid.

        Returns
        -------
        Y : np.ndarray
        The calcuated function values.
        """
        if vectorized:
            Y = func(self.coords)
        else:
            Y = np.reshape([func(x) for x in self.coords], (len(self.coords), 1))

        if not coord_shaped:
            return Y.reshape(self.grid_shape)
        else:
            return Y


def grid_calc(
    func: Callable,
    bounds: Sequence[float],
    free_dims: Sequence[int] = (0, 1),
    grid_pts: Sequence[int] = (50,),
    fixed_dim_vals: float | str = "midpoint",
    vectorized: bool = True,
) -> tuple[tuple[np.ndarray], np.ndarray]:
    """Evaluates function on a grid representing (a slice of) design space.

    Creates a grid from given design space bounds and a slice-specification,
    then calcuates a given function on the grid.

    Parameters
    ----------
    func : Callable
    The function which to calcuate over the grid. The function is assumed
    to accept be vectorized and accept 2d arrays where each
    row defines a separate argument to be calcuated.

    bounds: ArrayLike [2d, float | int]
    The design space bounds, given as a 2d array where each row contains
    the bounds for the corresponding dimension.

    free_dims: Sequence[int]

    grid_pts: Sequence[int]

    fixed_dim_vals: npt.ArrayLike | str
    Dimensions that are not included in the slice must be set to
    constant values, these can be provided here as an array. By default,
    the midpoint of the corresponding bounds are used.

    Returns
    -------
    tuple
    A tuple with two elements (grid, Y): grid is a tuple of arrays containing
    the grid coordinates in the same format as np.meshgrid, Y contains the
    corresponding function calcuations.
    """
    bounds = np.atleast_2d(bounds)
    mesher = Mesh(bounds, free_dims=free_dims, grid_pts=grid_pts)
    if len(mesher.fixed_dims) > 0:
        if fixed_dim_vals == "midpoint":
            mesher.set_fixed_dims(0.5 * np.sum(bounds[mesher.fixed_dims], axis=1))
        else:
            mesher.set_fixed_dims(fixed_dim_vals)

    Y = mesher.calc_func(func, vectorized=vectorized)
    return mesher.grid, Y
