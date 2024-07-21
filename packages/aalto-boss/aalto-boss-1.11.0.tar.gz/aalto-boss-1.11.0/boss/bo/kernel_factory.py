import GPy
import numpy as np
from boss.settings import Settings
from boss.utils.distributions import gammaparams


def select_kernel(settings: Settings) -> GPy.kern.Kern:
    """Convenience function to initialize a kernel and apply hyperparameters."""
    kern = init_kernel(settings)
    apply_hyper_settings(kern, settings)
    return kern


def init_kernel(settings: Settings) -> GPy.kern.Kern:
    """Creates a kernel according to the settings.

    The kernel will be a product kernel with parts specified by the
    kernel keyword, no priors or constraints will be set.
    """
    kernel_parts = [None] * (settings.dim)

    for i in range(settings.dim):
        ktype = settings["kernel"][i]
        if ktype == "stdp":
            kernel_parts[i] = GPy.kern.StdPeriodic(
                input_dim=1,
                variance=1.0,
                period=1.0,
                lengthscale=1.0,
                ARD1=True,
                ARD2=True,
                active_dims=[i],
                name="kern",
            )
        elif ktype == "rbf":
            kernel_parts[i] = GPy.kern.RBF(
                input_dim=1,
                variance=1.0,
                lengthscale=1.0,
                ARD=True,
                active_dims=[i],
                name="kern",
            )
        elif ktype == "mat32":
            kernel_parts[i] = GPy.kern.Matern32(
                input_dim=1,
                variance=1.0,
                lengthscale=1.0,
                ARD=True,
                active_dims=[i],
                name="kern",
            )
        elif ktype == "mat52":
            kernel_parts[i] = GPy.kern.Matern52(
                input_dim=1,
                variance=1.0,
                lengthscale=1.0,
                ARD=True,
                active_dims=[i],
                name="kern",
            )
        else:
            raise TypeError(f"Unknown kernel: {settings['kernel'][i]}")

    # multiply all kernel parts together
    kernel = kernel_parts[0]
    if len(kernel_parts) > 1:
        for i in range(1, len(kernel_parts)):
            kernel = kernel * kernel_parts[i]

    # add coregionalisation
    if settings.is_multi:
        kernel = _add_coreg(kernel, settings)

    return kernel


def apply_hyper_settings(kernel: GPy.kern.Kern, settings: Settings) -> None:
    _set_hyper_values(kernel, settings)
    _set_hyper_priors(kernel, settings)
    _set_hyper_constraints(kernel, settings)
    if settings.is_multi:
        _apply_coreg_settings(kernel, settings)


def _set_hyper_constraints(kernel: GPy.kern.Kern, settings: Settings) -> None:
    """
    Sets hyperparameter constraints on kernels.
    """
    if isinstance(kernel, GPy.kern.Prod):
        kernel_parts = kernel.parts
    else:
        kernel_parts = [kernel]

    # variance
    if settings["thetabounds"] is not None:
        kernel_parts[0].variance.constrain_bounded(
            settings["thetabounds"][0][0],
            settings["thetabounds"][0][1],
            warning=False,
        )
        # lengthscale
        for i in range(settings.dim):
            kernel_parts[i].lengthscale.constrain_bounded(
                settings["thetabounds"][i + 1][0],
                settings["thetabounds"][i + 1][1],
                warning=False,
            )
    # fix periods
    for i in range(settings.dim):
        if settings["kernel"][i] == "stdp":  # pbc
            kernel_parts[i].period.constrain_fixed(
                settings["periods"][i], warning=False
            )

    # fix variances for all but the first kernel
    if settings.dim > 1:
        for i in range(1, settings.dim):
            kernel_parts[i].variance.constrain_fixed(1.0, warning=False)


def _resolve_thetainit(settings: Settings) -> np.ndarray:
    """
    Resolve the initial values of theta parameters based on the settings.

    Parameters:
    settings: Settings object containing configuration for initialization.

    Returns:
    list: A list of initial values for theta parameters.
    """
    thetainit = settings["thetainit"]
    if thetainit is None:
        if settings["ynorm"]:
            diff = 1.0  # when observations are range-normalized
        else:
            yrange = settings["yrange"]
            # An yrange estimate is typically either estimated from GP initial data
            # or provided directly by the user, but if we still don't have one at
            # this point we resort to guessing.
            if yrange is None:
                yrange = [-10.0, 10.0]
                settings["yrange"] = yrange

            diff = yrange[1] - yrange[0]
        thetainit = [0.5 * diff]  # sig
        for i in range(settings.dim):  # lengthscales
            if settings["kernel"][i] == "stdp":  # pbc
                thetainit.append(np.pi / 10)
            else:  # nonpbc
                thetainit.append(settings["periods"][i] / 20)
        thetainit = np.asarray(thetainit)
        settings["thetainit"] = (
            thetainit  # important to set new setting as coreg depends on it
        )
    return thetainit


def _resolve_thepriorpar(settings: Settings) -> np.ndarray:
    """
    Resolve the prior distribution values of the hyperparameters based on the settings.

    Parameters:
    settings: Settings object containing configuration for initialization.

    Returns:
    list: A nested list of prior distribution values for each hyperparameter.
    """
    thetapriorpar = settings["thetapriorpar"]
    if thetapriorpar is None:
        if settings["ynorm"]:
            diff = 1.0  # when observations are range normalised
        else:
            yrange = settings["yrange"]
            # An yrange estimate is typically either estimated from GP initial data
            # or provided directly by the user, but if we still don't have one at
            # this point we resort to guessing.
            if yrange is None:
                yrange = [-10.0, 10.0]
                settings["yrange"] = yrange
            diff = yrange[1] - yrange[0]

        # Ulpu's heuristic prior
        shape = 2.00
        rate = 2.0 / (diff / 2.0) ** 2

        # Original solution, to be tested further
        # shape, rate = Distributions.gammaparams(
        #    (diff/4)**2, (10*diff/4)**2, 0.5, 0.99)
        # shape = 1.0    # NORMALIZATION
        # rate = 1.5     # NORMALIZATION
        thetapriorpar = [[shape, rate]]

        for i in range(settings.dim):
            if settings["kernel"][i] == "stdp":  # pbc
                shape = 3.3678
                rate = 9.0204
            else:  # nonpbc
                shape, rate = gammaparams(
                    settings["periods"][i] / 20, settings["periods"][i] / 2
                )
            thetapriorpar.append([shape, rate])
        thetapriorpar = np.asarray(thetapriorpar)
        settings["thetapriorpar"] = (
            thetapriorpar  # important to set new setting as coreg depends on it
        )
    return thetapriorpar


def _set_hyper_values(kernel: GPy.kern.Kern, settings: Settings) -> None:
    """
    Sets hyperparameter values
    """
    thetainit = _resolve_thetainit(settings)

    if isinstance(kernel, GPy.kern.Prod):
        kernel_parts = kernel.parts
    else:
        kernel_parts = [kernel]

    # Set all hyperparameters for non-coreg kernels
    kernel_parts[0].variance = thetainit[0]
    lim = None
    if settings.is_multi:
        lim = -1  # skip coreg which is always last
    for i, kpart in enumerate(kernel_parts[:lim]):
        kpart.lengthscale = thetainit[i + 1]
        if settings["kernel"][i] == "stdp":
            kpart.period = settings["periods"][i]


def _set_hyper_priors(kernel: GPy.kern.Kern, settings: Settings) -> None:
    """
    Sets hyperparameter priors on kernels.
    """
    # Instantiate prior of given type
    thetaprior = settings["thetaprior"]
    if thetaprior is None:
        return  # dont use a prior
    elif thetaprior == "gamma":
        _set_gamma_prior(kernel, settings)
    else:
        raise TypeError(f"Prior type {thetaprior} not supported")


def _set_gamma_prior(kernel: GPy.kern.Kern, settings: Settings) -> None:
    """
    Sets a gamma prior on the kernel.
    """

    thetapriorpar = _resolve_thepriorpar(settings)

    # Now we can set the actual priors
    if isinstance(kernel, GPy.kern.Prod):
        kernel_parts = kernel.parts
    else:
        kernel_parts = [kernel]

    prior = GPy.priors.Gamma
    kernel_parts[0].variance.set_prior(
        prior(thetapriorpar[0, 0], thetapriorpar[0, 1]),
        warning=False,
    )
    for i in range(settings.dim):
        kernel_parts[i].lengthscale.set_prior(
            prior(
                thetapriorpar[i + 1, 0],
                thetapriorpar[i + 1, 1],
            ),
            warning=False,
        )


def _add_coreg(kernel: GPy.kern.Kern, settings: Settings) -> GPy.kern.Kern:
    """
    Extends a basic kernel with coregionalisation.
    """
    # note: input is one kernel rather than kernel list. this is on
    # purpose as the model class is not equipped to handle other cases
    # atm
    kernel_list = [kernel]
    output_dim = settings["num_tasks"]
    kernel_multi = GPy.util.multioutput.LCM(
        settings.dim, output_dim, kernel_list, settings["W_rank"]
    )
    return kernel_multi


def _apply_coreg_settings(kernel_multi: GPy.kern.Kern, settings: Settings) -> None:
    """
    Sets coregionalisation values and priors.
    """
    # fix base kernel variance to 1
    kernel_multi.parameters[0].variance.unset_priors()
    kernel_multi.parameters[0].variance.constrain_fixed(1.0)

    # set initial values
    kappa_init = settings["kappa_init"]
    if kappa_init is None:
        kappa_init = settings["thetainit"][0] * np.ones(settings["num_tasks"])
    settings["kappa_init"] = kappa_init

    new_shape = (settings["num_tasks"], settings["W_rank"])
    kernel_multi.parameters[-1].W = settings["W_init"].reshape(new_shape)
    kernel_multi.parameters[-1].kappa = settings["kappa_init"]

    # set priors
    if settings["W_prior"] is not None:
        param = kernel_multi.parameters[-1].W
        pname = settings["W_prior"]
        ppars = settings["W_priorpar"]
        if pname == "fixed_value":
            param.constrain_fixed(ppars[0])
        elif pname == "gaussian":
            param.set_prior(GPy.priors.Gaussian(ppars[0], ppars[1]), warning=False)
        else:
            raise TypeError("Unknown W_prior: {}".format(pname))
    if settings["kappa_prior"] is not None:
        param = kernel_multi.parameters[-1].kappa
        pname = settings["kappa_prior"]
        ppars = settings["kappa_priorpar"]
        if pname == "fixed_value":
            param.constrain_fixed(ppars[0])
        elif pname == "gamma":
            param.set_prior(GPy.priors.Gamma(ppars[0], ppars[1]), warning=False)
        else:
            raise TypeError("Unknown kappa_prior: {}".format(pname))
