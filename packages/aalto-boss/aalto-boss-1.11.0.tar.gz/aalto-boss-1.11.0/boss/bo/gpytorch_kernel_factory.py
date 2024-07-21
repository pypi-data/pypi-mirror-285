import torch
import gpytorch
from gpytorch.constraints import Interval
from boss.settings import Settings
from boss.bo.kernel_factory import _resolve_thetainit, _resolve_thepriorpar


def select_kernel(settings: Settings) -> gpytorch.kernels:
    """Convenience function to initialize a kernel and apply hyperparameters."""
    kern = init_kernel(settings)
    apply_hyper_settings(kern, settings)
    return kern


def init_kernel(settings: Settings) -> gpytorch.kernels:
    """Creates a kernel according to the settings.

    The kernel will be a product kernel with parts specified by the
    kernel keyword, no priors or constraints will be set.
    """
    kernel_parts = [None] * (settings.dim)

    for i in range(settings.dim):
        ktype = settings["kernel"][i]
        if ktype == "stdp":
            kernel_parts[i] = gpytorch.kernels.PeriodicKernel(active_dims=[i])

        elif ktype == "rbf":
            kernel_parts[i] = gpytorch.kernels.RBFKernel(active_dims=[i])

        elif ktype == "mat32":
            kernel_parts[i] = gpytorch.kernels.MaternKernel(nu=1.5, active_dims=[i])

        elif ktype == "mat52":
            kernel_parts[i] = gpytorch.kernels.MaternKernel(nu=2.5, active_dims=[i])

        else:
            raise TypeError(f"Unknown kernel: {settings['kernel'][i]}")

    kern = kernel_parts[0]
    if len(kernel_parts) > 1:
        for i in range(1, len(kernel_parts)):
            kern = kern * kernel_parts[i]
    kernel = gpytorch.kernels.ScaleKernel(kern)

    return kernel


def apply_hyper_settings(kernel: gpytorch.kernels, settings: Settings) -> None:
    set_hyper_values(kernel, settings)
    set_hyper_priors(kernel, settings)
    set_hyper_constraints(kernel, settings)
    if settings.is_multi:
        raise TypeError(f"Multitask GpyTorch backend not supported yet!")


def set_hyper_values(kernel: gpytorch.kernels, settings: Settings) -> None:
    """
    Sets gyperparameter values
    """
    thetainit = _resolve_thetainit(settings)

    if isinstance(kernel.base_kernel, gpytorch.kernels.ProductKernel):
        kernel_parts = list(kernel.base_kernel.kernels)
    else:
        kernel_parts = list(kernel.sub_kernels())

    kernel._set_outputscale(
        torch.tensor(thetainit[0], dtype=torch.float, requires_grad=True)
    )

    for i, kpart in enumerate(kernel_parts):
        kpart[i]._set_lengthscale(
            torch.tensor(thetainit[i + 1], dtype=torch.float, requires_grad=True)
        )

        if settings["kernel"][i] == "stdp":
            kpart[i]._set_period_length(
                torch.tensor(
                    settings["periods"][i], dtype=torch.float, requires_grad=True
                )
            )


def set_hyper_priors(kernel: gpytorch.kernels, settings: Settings) -> None:
    """
    Sets hyperparameter priors on kernels.
    """
    # Instantiate prior of given type
    thetaprior = settings["thetaprior"]
    if thetaprior is None:
        return  # dont use a prior
    elif thetaprior == "gamma":
        set_gamma_prior(kernel, settings)
    else:
        raise TypeError(f"Prior type {thetaprior} not supported")


def set_gamma_prior(kernel: gpytorch.kernels, settings: Settings) -> None:
    """
    Sets a gamma prior on the kernel.
    """
    thetapriorpar = _resolve_thepriorpar(settings)
    # Now we can set the actual priors
    if isinstance(kernel.base_kernel, gpytorch.kernels.ProductKernel):
        kernel_parts = list(kernel.base_kernel.kernels)
    else:
        kernel_parts = list(kernel.sub_kernels())

    prior = gpytorch.priors.GammaPrior

    kernel.register_prior(
        "gamma_scale", prior(thetapriorpar[0, 0], thetapriorpar[0, 1]), "outputscale"
    )

    for i, kpart in enumerate(kernel_parts):
        kpart[i].register_prior(
            "gamma_length" + str(i),
            prior(
                thetapriorpar[i + 1, 0],
                thetapriorpar[i + 1, 1],
            ),
            "lengthscale",
        )


def set_hyper_constraints(kernel: gpytorch.kernels, settings: Settings) -> None:
    """
    Sets hyperparameter constraints on kernels.
    """
    if isinstance(kernel.base_kernel, gpytorch.kernels.ProductKernel):
        kernel_parts = list(kernel.base_kernel.kernels)
    else:
        kernel_parts = list(kernel.sub_kernels())

    # variance
    if settings["thetabounds"] is not None:  # by default not set
        kernel.outputscale_constraint = Interval(
            settings["thetabounds"][0][0], settings["thetabounds"][0][1]
        )

        for i, kpart in enumerate(kernel_parts):
            kpart.lengthscale_constraint = Interval(
                settings["thetabounds"][i + 1][0], settings["thetabounds"][i + 1][1]
            )

    # fix periods
    for i, kpart in enumerate(kernel_parts):
        if settings["kernel"][i] == "stdp":  # pbc
            kpart.period_length_constraint = Interval(
                settings["periods"][i], settings["periods"][i] + 1e-3
            )
            kpart.raw_period_length.requires_grad = False  # Fix period lengthscale
