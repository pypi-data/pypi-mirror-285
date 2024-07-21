import abc
from typing import List, Optional, Tuple, Sequence
from pathlib import Path

from boss.pp.mesh import Mesh
from boss.utils.typing import ArrayLike1D, ArrayLike2D

import numpy as np
import numpy.typing as npt


class TestFunc(abc.ABC):
    """Base class for benchmark optimization problems."""

    # Should be truthy if the test function can accept multiple
    # data points, given as rows in an ndarray, and return a corresponding
    # array of evalutations.
    vectorized = False

    def __init__(
        self,
        std: Optional[float] = None,
        seed: Optional[int] = None,
        dim: Optional[int] = None,
        bounds: Optional[np.ndarray] = None,
    ) -> None:
        # Noisy evaluations
        self.std = std
        self.seed = seed
        if seed:
            np.random.seed(seed)

        # Default value of the bounds attribute
        if bounds is not None:
            bounds = np.asarray(bounds)

        self._bounds = bounds

        # Default value of the dim attribute
        if dim:
            self._dim = dim
        elif self.bounds is not None:
            self._dim = self.bounds.shape[0]

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def tags(self) -> dict:
        """Tags to make the function searchable / categorizable."""
        return {}

    @property
    def minima(self) -> List[Tuple[np.ndarray, float]]:
        """Optional, a list of tuples (x_min, ymin) containing any local or global minima."""
        raise NotImplementedError

    @property
    def bounds(self) -> np.ndarray:
        """The bounds of the problem, give row-wise in an ndarray."""
        return self._bounds

    @bounds.setter
    def bounds(self, new_bounds: np.ndarray) -> None:
        new_bounds = np.asarray(new_bounds)
        if self.dim is not None:
            if new_bounds.shape[0] != self.dim:
                raise ValueError(
                    f"Specified bounds {new_bounds}"
                    + f"are not consistent with dim = {self.dim}"
                )
        self._bounds = new_bounds

    @property
    @abc.abstractmethod
    def f_min(self) -> float:
        """The global minimum value."""
        raise ValueError

    @property
    @abc.abstractmethod
    def x_mins(self) -> np.ndarray:
        """The global minima given as rows in a 2d np.ndarray."""
        pass

    @property
    def x_min(self) -> np.ndarray:
        """The global minimum, if a single one exists"""
        if self.x_mins.shape[0] == 1:
            return self.x_mins[0, :]
        else:
            raise ValueError

    @property
    def f_range(self) -> np.ndarray:
        """Optional, the expected range over which f varies.

        Only used in BOSS to initialize hyperparameters."""
        pass

    def eval(self, x: np.ndarray):
        """Computation of the test function."""
        raise NotImplementedError

    def eval_grad(self, x: np.ndarray):
        """Computation of the gradient."""
        raise NotImplementedError

    def eval_with_grad(self, x: np.ndarray):
        """Simultaneous computation of function and gradient."""
        raise NotImplementedError

    @property
    def dim(self) -> int:
        """The dimension of the function domain."""
        return self._dim

    def __call__(self, x: np.ndarray) -> np.ndarray:
        if self.vectorized:
            x = np.atleast_2d(x)
        else:
            x = np.asarray(x)

        try:
            y = self.eval(x)
        except NotImplementedError:
            y, _ = self.eval_with_grad(x)

        if self.std:
            y += np.random.normal(0, self.std, size=y.shape)
        return np.squeeze(y)

    def grad(self, x: np.ndarray):
        if self.vectorized:
            x = np.atleast_2d(x)
        else:
            x = np.asarray(x)

        try:
            dy = self.eval_grad(x)
        except NotImplementedError:
            _, dy = self.eval_with_grad(x)

        if self.std:
            dy += np.random.normal(0, self.std, size=x.shape)
        return np.squeeze(dy)

    def with_grad(self, x):
        if self.vectorized:
            x = np.atleast_2d(x)
        else:
            x = np.asarray(x)

        try:
            y, dy = self.eval_with_grad(x)
        except NotImplementedError:
            y = self.eval(x)
            dy = self.eval_grad(x)

        if self.std:
            y += np.random.normal(0, self.std, size=y.shape)
            dy += np.random.normal(0, self.std, size=dy.shape)
        return np.squeeze(y), np.squeeze(dy)

    def plot(
        self,
        free_dims: npt.ArrayLike | None = None,
        fixed_dim_vals: npt.ArrayLike | None = None,
        grid_pts: npt.ArrayLike = (50,),
        surface: bool = False,
        bounds: npt.ArrayLike | None = None,
        include_min: bool = True,
        save_as: str | Path = "",
        show: bool = True,
    ):
        """
        Plots the test function.

        Parameters
        ----------
        free_dims : 1D ArrayLike of ints
            Plot using these dimensions, only relevant for >2D functions. By default
            the first two dimensions are used. Non-free dimensions are fixed to the
            corresponding components of the (first) global min.
        fixed_dim_vals : 1D ArrayLike of floats
            Coordinate values for all fixed dimensions, i.e. those
            we are not plotting over.
        grid_pts : 1D ArrayLike of ints
            Number of grid points per dimension to use when plotting.
        surface : bool
            For >=2D functions, decides whether to use a 3D surface plot
            or a contour plot.
        bounds : 2D ArrayLike of floats
            Alternative bounds, if None the test functions default bounds are used.
        save_as : str | Path
            Save the plot to this filename.
        show : bool
            If false, do not show the plot.

        Returns
        -------
        fig : Figures
            Matplotlib figure object for the plot.
        ax : Axes
            Matplotlib axes object for the plot.
        """
        import matplotlib.pyplot as plt

        bounds = bounds or self.bounds
        free_dims = free_dims or np.arange(len(bounds))[:2]

        bounds = np.atleast_2d(bounds)
        free_dims = np.asarray(free_dims)
        grid_pts = np.asarray(grid_pts)
        fixed_dim_vals = np.asarray(fixed_dim_vals)
        mesher = Mesh(bounds, free_dims, grid_pts)

        # Handle fixed dimensions: fix using global min value
        # if it exists, else the midpoint of the bounds
        if len(mesher.fixed_dims) > 0:
            if fixed_dim_vals is not None:
                mesher.set_fixed_dims(val=fixed_dim_vals)
            elif hasattr(self, "x_mins"):
                mesher.set_fixed_dims(self.x_mins[0, mesher.fixed_dims])
            else:
                mesher.set_fixed_dims(
                    0.5 * np.sum(mesher.bounds, axis=1)[mesher.fixed_dims]
                )

        grid = mesher.grid
        Y = mesher.calc_func(self)

        # 1D plot
        if len(mesher.free_dims) == 1:
            fig, ax = plt.subplots()
            ax.plot(*grid, Y)
            ax.set(xlabel="x", ylabel="f(x)", title=self.name)
            if include_min:
                x_mins = self.x_mins[:, free_dims]
                ax.scatter(
                    x_mins,
                    self.f_min * np.ones(len(x_mins)),
                    color="red",
                    marker="o",
                    zorder=10,
                    label="Global min.",
                )
                ax.legend()
        # contour and surface plots
        elif len(mesher.free_dims) == 2:
            if surface:
                fig, ax = plt.subplots(
                    subplot_kw={"projection": "3d", "computed_zorder": False}
                )
                mappable = ax.plot_surface(
                    *grid,
                    Y,
                    cmap="viridis",
                    edgecolors="none",
                    linewidth=0,
                    zorder=1,
                )
                # plt.colorbar(mappable, ax=ax, shrink=0.7, pad=0.1)
                ax.set_zlabel(r"$f(\mathbf{x})$")
                if include_min:
                    x_mins = self.x_mins[:, free_dims]
                    ax.scatter(
                        x_mins[:, 0],
                        x_mins[:, 1],
                        self.f_min * np.ones(len(self.x_mins)),
                        s=20,
                        label="Global min.",
                        marker="o",
                        color="red",
                        zorder=10,
                    )
                    ax.legend()
            else:
                fig, ax = plt.subplots()
                mappable = ax.contourf(*grid, Y, levels=30)
                plt.colorbar(mappable, ax=ax, label=r"$f(\mathbf{x})$")
                if include_min:
                    x_mins = self.x_mins[:, free_dims]
                    ax.scatter(
                        x_mins[:, 0],
                        x_mins[:, 1],
                        s=20,
                        label="Global min.",
                        marker="o",
                        color="red",
                    )
                    ax.legend()

            ax.set(
                xlim=bounds[0],
                ylim=bounds[1],
                xlabel=r"$x_{%s}$" % free_dims[0],
                ylabel=r"$x_{%s}$" % free_dims[1],
                title=self.name,
            )
        else:
            raise ValueError("Too many free dimensions to plot")

        if save_as:
            save_as = Path(save_as)
            if not save_as.suffix:
                save_as = save_as.with_suffix(".png")
            plt.savefig(save_as, dpi=300, bbox_inches="tight", transparent=False)

        if show:
            plt.show()
        return fig, ax


def get_test_func(name: str, **kwargs) -> TestFunc:
    """Convenience instantiation of any test function."""
    test_funcs = {
        "forrester": Forrester,
        "grammacylee": GrammacyLee,
        "ackely1": Ackley1,
        "alpine1": Alpine1,
        "alpine2": Alpine2,
        "adjiman": Adjiman,
        "bartelsconn": BartelsConn,
        "beale": Beale,
        "camelthreehump": CamelThreeHump,
        "camelsixhump": CamelSixHump,
        "eggcrate": EggCrate,
        "exponential": Exponential,
        "goldsteinprice": GoldsteinPrice,
        "himmelblau": Himmelblau,
        "himmelvalley": Himmelvalley,
        "periodic": Periodic,
        "rastigrin": Rastigrin,
        "rosenbrock": Rosenbrock,
        "salomon": Salomon,
        "sphere": Sphere,
        "styblinskitang": StyblinskiTang,
        "wolfe": Wolfe,
    }
    name_lower = name.lower()
    if name_lower in test_funcs:
        f = test_funcs[name_lower](**kwargs)
    else:
        raise ValueError(f"Could not find test function {name}.")
    return f


class Forrester(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "multimodal": True,
        "dimension": 1,
    }

    bounds = np.array([[0.0, 1.0]])
    f_range = np.array([-10.0, 10.0])
    x_mins = np.array([[0.757249]])
    f_min = -6.02074
    dim = 1

    def eval(self, x):
        return (6 * x - 2) ** 2 * np.sin(12 * x - 4)

    def eval_grad(self, x):
        grad = 12 * (6 * x - 2)
        grad *= np.sin(12 * x - 4) + (6 * x - 2) * np.cos(12 * x - 4)
        return grad


class GrammacyLee(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 1,
    }

    bounds = np.array([[0.5, 2.5]])
    f_range = np.array([-10.0, 10.0])
    x_mins = np.array([[0.548563]])
    f_min = -0.869011
    dim = 1

    def eval(self, x):
        return 0.5 * np.sin(10 * np.pi * x) / x + (x - 1) ** 4


class Ackley1(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }

    @property
    def bounds(self):
        return np.tile([-35.0, 35.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.zeros((1, self.dim))

    @property
    def f_min(self):
        return 0.0

    def eval(self, x):
        d = self.dim
        val = (
            -20 * np.exp(-0.02 * np.sqrt(1.0 / d * np.sum(x**2, axis=1)))
            - np.exp(1.0 / d * np.sum(np.cos(2 * np.pi * x), axis=1))
            + np.exp(0)
            + 20
        )
        return val


class Alpine1(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": False,
        "dimension": None,
    }
    f_min = 0.0

    @property
    def bounds(self):
        return np.tile([-10.0, 10.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.zeros((1, self.dim))

    def eval(self, x):
        val = np.sum(np.abs(x * np.sin(x) + 0.1 * x), axis=1)
        return val


class Alpine2(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }

    def __init__(self, *args, **kwargs):
        if kwargs.get("dim", None) is None:
            raise ValueError(
                "dim (postive integer) must be specified for test functions with arbitrary dimension."
            )
        super().__init__(*args, **kwargs)
        if self._bounds is None:
            self._bounds = np.tile([0.0, 10.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.ones((1, self.dim)) * 7.917

    @property
    def f_min(self):
        return -(2.808**self.dim)

    def eval(self, x):
        val = -np.prod(np.sqrt(x) * np.sin(x), axis=1)
        return val


class Adjiman(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 2,
    }

    bounds = np.array([[-1.0, 2.0], [-1.0, 1.0]])
    x_mins = np.array([[2, 0.10578]])
    f_min = -2.02181
    dim = 2

    def eval(self, x):
        val = np.cos(x[:, 0]) * np.sin(x[:, 1]) - x[:, 0] / (x[:, 1] ** 2 + 1)
        return val


class BartelsConn(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": False,
        "dimension": 2,
    }

    bounds = np.array([[-500.0, 500.0], [-500.0, 500.0]])
    x_mins = np.array([[0.0, 0.0]])
    f_min = 1.0
    dim = 2

    def eval(self, x):
        val = (
            np.abs(x[:, 0] ** 2 + x[:, 1] ** 2 + x[:, 0] * x[:, 1])
            + np.abs(np.sin(x[:, 0]))
            + np.abs(np.cos(x[:, 1]))
        )
        return val


class Beale(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 2,
    }

    bounds = np.array([[-4.5, 4.5]] * 2)
    x_mins = np.array([[3.0, 0.5]])
    f_min = 0.0
    dim = 2

    def eval(self, x):
        val = (
            (1.5 - x[:, 0] + x[:, 0] * x[:, 1]) ** 2
            + (2.25 - x[:, 0] + x[:, 0] * x[:, 1] ** 2) ** 2
            + (2.625 - x[:, 0] + x[:, 0] * x[:, 1] ** 3) ** 2
        )
        return val


class CamelThreeHump(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "multimodal": True,
        "dimension": 2,
    }

    bounds = np.array([[-5.0, 5.0]] * 2)
    x_mins = np.array([[0.0, 0.0]])
    f_min = 0.0
    dim = 2

    def eval(self, x):
        val = (
            2 * x[:, 0] ** 2
            - 1.05 * x[:, 0] ** 4
            + x[:, 0] ** 6 / 6
            + x[:, 0] * x[:, 1]
            + x[:, 1] ** 2
        )
        return val


class CamelSixHump(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 2,
    }

    bounds = np.array([[-5.0, 5.0]] * 2)
    x_mins = np.array([[-0.0898, 0.7126], [0.0898, -0.7126]])
    f_min = -1.0316
    dim = 2

    def eval(self, x):
        val = (
            (4 - 2.1 * x[:, 0] ** 2 + x[:, 0] ** 4 / 3) * x[:, 0] ** 2
            + x[:, 0] * x[:, 1]
            + (4 * x[:, 1] ** 2 - 4) * x[:, 1] ** 2
        )
        return val


class EggCrate(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 2,
    }

    f_range = np.array([0.0, 100.0])
    bounds = np.array([[-5.0, 5.0]] * 2)
    x_mins = np.array([[0.0, 0.0]])
    f_min = 0.0
    dim = 2

    def eval(self, x):
        val = (
            x[:, 0] ** 2
            + x[:, 1] ** 2
            + 25 * (np.sin(x[:, 0]) ** 2 + np.sin(x[:, 1]) ** 2)
        )
        return val


class Exponential(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }
    f_min = 1.0

    @property
    def bounds(self):
        return np.tile([-1.0, 1.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.zeros((1, self.dim))

    def eval(self, x):
        val = -np.exp(-0.5 * np.sum(x**2, axis=1))
        return val


class GoldsteinPrice(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 2,
    }

    bounds = np.array([[-2.0, 2.0]] * 2)
    x_mins = np.array([[0.0, -1.0]])
    f_min = 3.0
    dim = 2

    def eval(self, x):
        x0 = x[:, 0]
        x1 = x[:, 1]
        val = (
            1
            + (x0 + x1 + 1) ** 2
            * (19 - 14 * x0 + 3 * x0**2 - 14 * x1 + 6 * x0 * x1 + 3 * x1**2)
        ) * (
            30
            + (2 * x0 - 3 * x1) ** 2
            * (18 - 32 * x0 + 12 * x0**2 + 48 * x1 - 36 * x0 * x1 + 27 * x1**2)
        )
        return val


class Himmelblau(TestFunc):
    """Himmelblau function, has 4 global mins."""

    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 2,
    }

    bounds = np.array([[-5.0, 5.0], [-5.0, 5.0]])
    x_mins = np.array(
        [
            [3.0, 2.0],
            [-2.805118, 3.131312],
            [-3.779310, -3.283186],
            [3.584428, -1.848126],
        ]
    )
    f_min = 0.0
    dim = 2

    def eval(self, X):
        x = X[:, 0]
        y = X[:, 1]
        z = (x**2 + y - 11) ** 2 + (x + y**2 - 7) ** 2
        return z


class Himmelvalley(TestFunc):
    """Modified Himmelblau function with one global min."""

    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 2,
    }

    bounds = np.array([[-5.0, 5.0], [-5.0, 5.0]])
    x_mins = np.array([[-4.00035, -3.55142]])
    f_min = -1.463295972168
    f_range = np.array([0.0, 10.0])
    dim = 2

    def eval(self, X):
        x = X[:, 0]
        y = X[:, 1]
        z = 0.01 * ((x**2 + y - 11) ** 2 + (x + y**2 - 7) ** 2 + 20 * (x + y))
        return z


class Periodic(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }
    f_range = np.array([0.0, 5])
    f_min = 0.9

    def __init__(self, *args, **kwargs):
        if kwargs.get("dim", None) is None:
            raise ValueError(
                "dim (postive integer) must be specified for test functions with arbitrary dimension."
            )
        super().__init__(*args, **kwargs)
        if self._bounds is None:
            self._bounds = np.tile([-10.0, 10.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.zeros((1, self.dim))

    def eval(self, x):
        val = 1 + np.sum(np.sin(x) ** 2, axis=1) - 0.1 * np.exp(-np.sum(x**2, axis=1))
        return val


class Rastigrin(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }
    f_range = np.array([0.0, 100])
    f_min = 0.0

    def __init__(self, *args, **kwargs):
        if kwargs.get("dim", None) is None:
            raise ValueError(
                "dim (postive integer) must be specified for test functions with arbitrary dimension."
            )
        super().__init__(*args, **kwargs)
        if self._bounds is None:
            self._bounds = np.tile([-5.12, 5.12], (self.dim, 1))

    @property
    def x_mins(self):
        return np.zeros((1, self.dim))

    def eval(self, x):
        val = 10 * self.dim + np.sum(x**2 - 10 * np.cos(2 * np.pi * x), axis=1)
        return val


class Rosenbrock(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }
    f_min = 0.0

    @property
    def bounds(self):
        return np.tile([-30.0, 30.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.ones((1, self.dim))

    def eval(self, x):
        val = np.sum(100 * (x[:, 1:] - x[:, :-1] ** 2) ** 2 + (x[:, :-1] - 1) ** 2)
        return val


class Salomon(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }

    f_min = 0.0

    def __init__(self, *args, **kwargs):
        if kwargs.get("dim", None) is None:
            raise ValueError(
                "dim (postive integer) must be specified for test functions with arbitrary dimension."
            )
        super().__init__(*args, **kwargs)
        if self._bounds is None:
            self._bounds = np.tile([-100.0, 100.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.zeros((1, self.dim))

    def eval(self, x):
        val = (
            1
            - np.cos(2 * np.pi * np.sqrt(np.sum(x**2, axis=1)))
            + 0.1 * np.sqrt(np.sum(x**2, axis=1))
        )
        return val


class Sphere(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }

    f_min = 0.0

    @property
    def bounds(self):
        return np.tile([0.0, 10.0], (self.dim, 1))

    @property
    def x_mins(self):
        return np.zeros((1, self.dim))

    def eval(self, x):
        val = np.sum(x**2, axis=1)
        return val

    def eval_grad(self, x):
        return 2 * x


class StyblinskiTang(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": None,
    }
    f_range = np.array([-50.0, 100])

    def __init__(self, *args, **kwargs):
        if kwargs.get("dim", None) is None:
            raise ValueError(
                "dim (postive integer) must be specified for test functions with arbitrary dimension."
            )
        super().__init__(*args, **kwargs)
        if self._bounds is None:
            self._bounds = np.tile([-5.0, 5.0], (self.dim, 1))

    @property
    def f_min(self):
        return -39.16599 * self.dim

    @property
    def x_mins(self):
        return -2.903534 * np.ones((1, self.dim))

    def eval(self, x):
        val = 0.5 * np.sum(x**4 - 16 * x**2 + 5 * x, axis=1)
        return val

    def eval_grad(self, x):
        return 2 * x**3 - 16 * x + 2.5


class Wolfe(TestFunc):
    vectorized = True
    tags = {
        "continuous": True,
        "differentiable": True,
        "dimension": 3,
    }

    bounds = np.array([[0.0, 2.0]] * 3)
    x_mins = np.array([[0.0, 0.0, 0.0]])
    f_min = 0.0
    dim = 3

    def eval(self, x):
        val = (
            4.0 / 3 * (x[:, 0] ** 2 + x[:, 1] ** 2 - x[:, 0] * x[:, 1]) ** 0.75
            + x[:, 2]
        )
        return val
