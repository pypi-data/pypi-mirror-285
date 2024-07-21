from typing import *

import numpy as np

from boss.bo.acq.kb import KrigingBeliever
from boss.bo.acq.manager import BaseAcquisitionManager, Sequential
from boss.settings import Settings


def select_acq_manager(settings: Settings) -> BaseAcquisitionManager:
    """Selects an acquisition manager based on the provided settings.

    The selection is primarily determined by the batchtype keyword, for which
    the default value 'sequential' yields a basic sequential acquisition mananger.

    Parameters
    ----------
    settings : Settings
        The settings object based on which the acquisition manager will be decided.

    Returns
    -------
    BaseAcquisitionManager:
        The selected acquisition manager.
    """
    bounds = settings["bounds"]
    batchtype = settings["batchtype"].lower()
    if settings.is_multi:
        bounds = np.vstack((bounds, [[0, 0]]))

    acqfn = settings.acqfn

    if batchtype in ["seq", "sequential"]:
        acq_manager = Sequential(
            acqfn, bounds, optimtype=settings["optimtype"], acqtol=settings["acqtol"]
        )
    elif batchtype.lower() in ["kb", "kriging_believer"]:
        acq_manager = KrigingBeliever(
            acqfn,
            bounds=bounds,
            batchpts=settings["batchpts"],
            optimtype=settings["optimtype"],
        )
    else:
        raise ValueError("No matching acquisition manager found.")

    return acq_manager
