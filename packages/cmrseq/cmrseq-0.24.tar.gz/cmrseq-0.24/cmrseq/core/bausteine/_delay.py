""" This module contains definition of a simple delay building block"""
__all__ = ["Delay"]

import numpy as np
from pint import Quantity

from cmrseq.core._system import SystemSpec

from cmrseq.core.bausteine._gradients import Gradient


class Delay(Gradient):
    """ Defines a gradient with zero magnitude and given duration"""

    def __init__(self, system_specs: SystemSpec,
                 duration: Quantity,
                 delay: Quantity = Quantity(0., "ms"),
                 name: str = "delay"):
        """ Defines a gradient with zero magnitude and given duration. This block only makes sense
        to use when concatenating it to a sequence.

        :param system_specs:
        :param duration:
        :param delay: Quantity[time] Leading time before object definition
        """
        time = Quantity(np.array([delay.m_as("ms"), (delay + duration).m_as("ms")]), "ms")
        dummy_gradient = Quantity(np.zeros([3, 2]), "mT/m")
        super(). __init__(time, dummy_gradient, system_specs, name, snap_to_raster=False)
