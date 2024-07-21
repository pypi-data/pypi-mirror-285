from __future__ import annotations

import abc
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from types import FunctionType
from typing import Any, Callable, Iterable, NamedTuple, Type, Protocol

import numpy as np
import numpy.typing as npt
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Session, relationship, selectinload

import boss.keywords as bkw
from boss.bo.results import BOResults
from boss.settings import Settings


@dataclass
class ResultArrays:
    """
    Holds BOSS result arrays. This is the return type for Result records
    that are converted to numpy or aggregated.
    """

    X: npt.NDArray | None = None
    Y: npt.NDArray | None = None
    model_params: npt.NDArray | None = None
    mu_glmin: npt.NDArray | None = None
    nu_glmin: npt.NDArray | None = None
    x_glmin: npt.NDArray | None = None
    t_total: float | None = None


class Output(NamedTuple):
    """Class representing an output from a BOSS run."""

    name: str  # name of the output in BOResults
    sql_type: type  # type used for output in the db
    order: int = 0  # tensorial order of the output
    sparse: bool = False  # whether the output is a SparseList
    array: bool = False  # whether the output is a np.ndarray


# Add new outputs available from the BOResults object here
OUTPUTS = (
    Output(name="X", sql_type=sa.LargeBinary, order=2, array=True),
    Output(name="Y", sql_type=sa.LargeBinary, order=2, array=True),
    Output(name="x_glmin", sql_type=sa.LargeBinary, order=2, sparse=True),
    Output(name="mu_glmin", sql_type=sa.LargeBinary, order=1, sparse=True),
    Output(name="nu_glmin", sql_type=sa.LargeBinary, order=1, sparse=True),
    Output(name="model_params", sql_type=sa.LargeBinary, order=1, sparse=True),
    Output(name="t_total", sql_type=sa.Float, order=0),
)


class BaseKeywords(Protocol):
    """Protocol for an ORM model representing BOSS keywords.

    This is mainly used for documentation, type hinting and autocompletion.
    Concrete types inheriting this class are created dynamically at
    runtime by the create_keywords_type method.
    """

    @abc.abstractmethod
    def __init__(
        self,
        bo_settings: dict[str, Any] | Settings,
        **extra_column_values: Any,
    ) -> None:
        """
        Creates a new instance of a Keywords ORM model.

        Note that this instance represents a row/record in the
        keywords table of the benchmark database.

        Parameters
        ----------
        bo_settings : dict[str, Any] | Settings
            A dict or Settings object containing BOSS keywords that will
            be used as columns in the SQL table.
        extra_column_values : Any
            Values for extra, non-keyword columns that have been added
            as attributes to the class
        """
        pass

    @abc.abstractmethod
    def aggregate_results(self) -> ResultArrays:
        """Combines results from all BOSS run repetitions using the current keywords.

        For each Results record that is related to the Keywords,
        the result arrays are stacked together for easy access.

        Returns
        -------
        ResultArrays
            Stacked arrays from all BOSS runs. Example: We run 3 repetitions
            with the current keywords, and each repetition consists of 5 bo iterations
            (including initial points), then ResultArrays.mu_glmin will be a 3 x 5
            array of predicted global mins for each repetition / iteration.

        """
        pass


class BaseResults(Protocol):
    """Protocol for an ORM model representing BOSS results.

    This is mainly used for documentation purposes and type hinting.
    Concrete types inheriting this class are created dynamically at
    runtime by the create_results_type method.
    """

    @abc.abstractmethod
    def __init__(self, bo_results: BOResults) -> None:
        """
        Creates a new instance of the Results ORM model.

        Note that this instance represents a row/record in the
        results table of the benchmark database.

        Parameters
        ----------
        bo_results : BOResults
            BOResults
        """
        pass


def create_keywords_type(
    base: type[DeclarativeBase],
    keywords: Iterable[str] | None = None,
    **extra_columns: sa.Column,
) -> type[BaseKeywords]:
    """
    Creates a sqlalchemy ORM class that defines a table for BOSS keywords.

    The class is created dynamically (inheriting BaseKeywords)
    to provide flexibility in what BOSS keywords are included as columns.
    In a database, a Keywords record together one or more Result record (defined below)
    describes a single BOSS run.

    Parameters
    ----------
    base: type
        A type inherited from DeclarativeBase
    bo_keywords : Iterable[str] | None
        BOSS keywords that will be included as columns in the database table.
        If none are specified, ALL available keywords will be used.
    extra_columns : sqlalchemy.Column
        Extra columns to include in the table. Only supports types that don't
        require special initialization (e.g., int, float, str, bool).

    Returns
    -------
    Keywords : Dynamically created type 'Keywords'
        A sqlalchemy ORM model for the selected BOSS keywords.
    """
    attrs = {}
    attrs["__tablename__"] = "keywords"
    attrs["id"] = sa.Column(sa.Integer, primary_key=True)
    attrs["results"] = relationship("Results", back_populates="keywords")

    cat_map = {
        (bool, 0): sa.Boolean,
        (int, 0): sa.Integer,
        (str, 0): sa.String,
        (float, 0): sa.Float,
        (int, 1): sa.String,
        (int, 2): sa.String,
        (float, 1): sa.String,
        (float, 2): sa.String,
        (str, 1): sa.String,
        (str, 2): sa.String,
    }

    # If explicit BOSS keyword names to include in the database are given use only them.
    if keywords is not None:
        for key in keywords:
            cat = bkw.find_category(key)
            try:
                attrs[key] = sa.Column(cat_map[cat], nullable=True)
            except KeyError:
                raise KeyError(f"{key} is not a recognized BOSS keyword")
    # No explicit keyword names given, so we use all BOSS keywords.
    else:
        for cat in bkw.categories:
            for key in bkw.categories[cat]:
                attrs[key] = sa.Column(cat_map[cat], nullable=True)

    for name, col in extra_columns.items():
        attrs[name] = col

    def __init__(
        self,
        bo_settings: dict[str, Any] | Settings,
        **extra_column_values: Any,
    ) -> None:
        keyword_overlap = set(bo_settings.keys()) & bkw.get_keyword_names()
        for key in keyword_overlap:
            cat = bkw.find_category(key)
            try:
                if cat_map[cat] == sa.String:
                    setattr(self, key, bkw.stringify(bo_settings[key]))
                else:
                    setattr(self, key, bo_settings[key])

            except KeyError:
                raise KeyError(f"{key} is not a recognized BOSS keyword")

        for col_name, col_val in extra_column_values.items():
            setattr(self, col_name, col_val)

    def aggregate_results(self) -> ResultArrays:
        aggregates = defaultdict(list)
        exceptions = ["Y"]
        outputs_mod = [out for out in OUTPUTS if out.name not in exceptions]
        for rec in self.results:
            for out in outputs_mod:
                if out.name in rec.__dict__.keys():
                    val = getattr(rec, out.name)
                    if out.order == 2:
                        aggregates[out.name].append(
                            np.frombuffer(val, dtype=np.float64).reshape(-1, rec.dim)
                        )
                    elif out.order == 1:
                        aggregates[out.name].append(
                            np.frombuffer(val, dtype=np.float64)
                        )
                    elif out.order == 0:
                        aggregates[out.name].append(val)

            # TODO: handle gradients and multi-task
            if "Y" in rec.__dict__.keys():
                aggregates["Y"].append(np.frombuffer(rec.Y, dtype=np.float64)[:, None])

        res_arrs = ResultArrays()
        for col, arrs in aggregates.items():
            setattr(res_arrs, col, np.stack(arrs))

        return res_arrs

    attrs["aggregate_results"] = aggregate_results
    attrs["__init__"] = __init__
    keywords_type = type("Keywords", (base,), attrs)
    return keywords_type


def create_results_type(base: Type[DeclarativeBase]) -> Type[BaseResults]:
    """
    Creates an sqlalchemy ORM class that defines a table for BOSS results.

    In a database, a Results record together with a Keywords record
    describes a single BOSS run. Note that many Results records can correspond
    to a single Keywords record. Note that BOSS result arrays are stored as
    binary blobs in the database and need to converted to arrays after retrieval.

    Parameters
    ----------
    base: type
        A type inherited from DeclarativeBase.

    Returns
    -------
    Results : BaseResults
        A sqlalchemy ORM model for BOSS results.
    """
    attrs = {}
    attrs["__tablename__"] = "results"
    attrs["id"] = sa.Column(sa.Integer, primary_key=True)
    attrs["keywords_id"] = sa.Column(sa.Integer, sa.ForeignKey("keywords.id"))
    attrs["keywords"] = relationship("Keywords", back_populates="results")
    attrs["dim"] = sa.Column(sa.Integer)

    for out in OUTPUTS:
        attrs[out.name] = sa.Column(out.sql_type, nullable=True)

    def __init__(self, bo_results: BOResults) -> None:
        self.dim = len(bo_results.settings["bounds"])

        for out in OUTPUTS:
            if out.array:
                setattr(self, out.name, bo_results[out.name].tobytes())
            elif out.sparse:
                setattr(self, out.name, bo_results[out.name].to_array(True).tobytes())
            else:
                setattr(self, out.name, bo_results[out.name])

    attrs["__init__"] = __init__
    results_type = type("Results", (base,), attrs)
    return results_type


@dataclass
class ColumnSpec:
    py_type: type
    get_value: Callable
    nullable: bool = False

    def to_column(self):
        type_map = {
            "int": sa.Integer,
            "float": sa.Float,
            "bool": sa.Boolean,
            "str": sa.String,
        }
        return sa.Column(type_map[self.py_type.__name__], nullable=self.nullable)


def get_callable_name(f: Callable) -> str:
    if isinstance(f, FunctionType):
        name = f.__name__
    else:
        name = getattr(f, "name", None)
        if name is None:
            name = f.__class__.__name__
    return name


def get_userfn_name(bo_settings: Settings | dict[str, Any]) -> str:
    if isinstance(bo_settings, Settings):
        f = bo_settings.f
    else:
        f = bo_settings["f"]
    return get_callable_name(f)


def get_existing_types(base: type) -> dict[str, type]:
    subclasses = base.__subclasses__()
    existing_types = {t.__name__: t for t in subclasses}
    return existing_types


class BenchmarkDatabase:
    """
    An interface to an SQL database that stores BOSS benchmark runs.

    This class simplifies querying and adding new records to the database
    so that users don't need any knowledge of sqlalchemy.
    """

    def __init__(
        self,
        name: str,
        keyword_columns: Iterable[str] | None = None,
        **custom_columns: ColumnSpec,
    ) -> None:
        """
        Creates a new BenchmarkDatabase with selected BOSS keywords and other
        user-specified columns (optional).

        Parameters
        ----------
        name : str
            Name of the database (including file extension).
        keywords : Iterable[str] | None
            BOSS keywords that
            will be included as columns in the database. If none are specified,
            ALL available keywords will be used.
        **custom_columns : ColumnSpec
            Additional kwargs describing custom columns to include in the database.
            Kwarg keys will be used as column names, values are ColumnSpec instances.

                Example: mycol = ColumnSpec(int, get_value) will create an integer
                column called mycol whose value is set using the get_value function.
                This function must be defined by the user and is called with Settings
                and row_id as argument.
        """
        # we always add a custom column for the objective function name
        self.name = name
        self.engine = sa.create_engine(f"sqlite:///{self.name}")
        f_spec = ColumnSpec(
            py_type=str, get_value=lambda sts, _: get_userfn_name(sts), nullable=False
        )
        self._col_specs = {"f": f_spec}
        self._col_specs.update(custom_columns)
        self._keyword_cols = set(keyword_columns) if keyword_columns else set()
        extra_cols = {n: cs.to_column() for n, cs in self._col_specs.items()}
        self._init_common(extra_cols)

    @classmethod
    def from_file(cls, name: str, **custom_columns: ColumnSpec) -> BenchmarkDatabase:
        self = cls.__new__(cls)
        self.name = name
        self.engine = sa.create_engine(f"sqlite:///{self.name}")
        if not Path(name).is_file():
            raise FileNotFoundError(f"Database {name} not found.")

        # add a custom column for the name of the objective function
        f_spec = ColumnSpec(
            py_type=str, get_value=lambda x, y: get_userfn_name(x), nullable=False
        )
        self._col_specs = {"f": f_spec}
        self._col_specs.update(custom_columns)

        inspector = sa.inspect(self.engine)
        col_info = inspector.get_columns("keywords")
        col_names = set([col["name"] for col in col_info])

        # extract the names of columns that correspond to BOSS keywords
        bkw_names = bkw.get_keyword_names()
        kw_col_names = col_names & bkw_names
        self._keyword_cols = kw_col_names

        # extract remaining non-keyword and non-custom cols
        other_col_names = col_names - bkw_names - self._col_specs.keys() - {"id"}
        other_col_info = filter(lambda c: c["name"] in other_col_names, col_info)

        # create dict mapping names to sa.Column for all non-BOSS columns
        extra_cols = {n: cs.to_column() for n, cs in self._col_specs.items()}
        other_cols = {
            c["name"]: sa.Column(c["type"], nullable=c["nullable"])
            for c in other_col_info
        }
        extra_cols.update(other_cols)
        self._init_common(extra_cols)
        return self

    def _init_common(self, extra_columns: dict[str, sa.Column]) -> None:
        """Common initialization for all factory methods"""
        Base = type("Base", (DeclarativeBase,), {})
        Keywords = create_keywords_type(Base, self._keyword_cols, **extra_columns)
        self.Keywords = Keywords
        self.Results = create_results_type(Base)
        Base.metadata.create_all(bind=self.engine)
        self._id_last = 0  # id of the last inserted Keyword row

    def select(
        self, result_names: Iterable[str] | str | None = "all", **bo_keywords: Any
    ) -> list:
        """
        Selects a subset of keyword and result records from the database.

        Parameters
        ----------
        result_names : Iterable[str] | str | None
            Names of the results that should be returned. Defaults to
            all possible results: X, Y, model_params, x_glmin, mu_glmin, nu_glmin

        bo_keywords : Any
            Keyword values to filter the database by.

        Returns
        ----------
        Records matching the selected keywords. Each records contains
        results (as specified by the result names) for all corresponding runs.
        """
        with Session(self.engine) as session:
            if result_names is None:
                opts = None
            elif result_names == "all":
                opts = selectinload(self.Keywords.results)
            else:
                col_names = ["dim"] + list(result_names)
                col_attrs = [getattr(self.Results, c) for c in col_names]
                opts = selectinload(self.Keywords.results).load_only(*col_attrs)
            if opts is None:
                output = session.execute(
                    sa.select(self.Keywords).filter_by(**bo_keywords)
                )
            else:
                output = session.execute(
                    sa.select(self.Keywords).options(opts).filter_by(**bo_keywords)
                )
            records = [t[0] for t in output]
        return records

    def add_keywords(self, bo_settings: Settings | dict[str, Any]) -> BaseKeywords:
        """
        Creates and adds a Keywords record to the database.

        Parameters
        ----------
        bo_settings : Settings | dict[str, Any]
            BOSS keywords to be included in the record.
        """
        extra_col_vals = {
            name: spec.get_value(bo_settings, self._id_last + 1)
            for name, spec in self._col_specs.items()
        }

        # If we only use a subset of BOSS keywords as columns we
        # filter those keywords here.
        if self._keyword_cols:
            settings = {k: bo_settings[k] for k in self._keyword_cols}
        else:
            settings = bo_settings

        keywords = self.Keywords(settings, **extra_col_vals)

        with Session(self.engine) as session:
            session.add(keywords)
            session.commit()
            self._id_last = keywords.id

        return keywords

    def add_results(
        self, bo_results: BOResults, keywords: BaseKeywords | None = None
    ) -> BaseResults:
        """
        Creates and adds a Results record to the database.

        Parameters
        ----------
        bo_results : BOResults
            BOSS results object to create the record from.
        keywords : BaseKeywords | None
            A Keywords record for the keywords used in the run.
            The new Results records will be related to this keyword
            record for ease of access.
        """
        results = self.Results(bo_results)
        if keywords is not None:
            results.keywords = keywords

        with Session(self.engine) as session:
            session.add(results)
            session.commit()
        return results
