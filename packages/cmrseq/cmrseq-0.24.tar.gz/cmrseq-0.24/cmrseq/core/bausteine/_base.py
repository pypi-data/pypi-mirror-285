""" This module contains the implementation of the base class of all building blocks used in
Sequences"""
__all__ = ["SequenceBaseBlock"]

from abc import abstractmethod
from copy import deepcopy
from types import SimpleNamespace

from pint import Quantity

from cmrseq.core._system import SystemSpec


# pylint: disable=C0103
class SequenceBaseBlock(SimpleNamespace):
    """ Base class for all building blocks, defining the abstract interface for generic
    interaction with blocks.

    All subclases must implent the abstract methods, and all general methods on 
    blocks must only access the implemented methods when no sub-class type check 
    is performed.

    Furthermore, all subclasses must call the base-class constructor.
    
    :param system_specs:
    :param name: 
    :param snap_to_raster: 
    """
    # Field that should be used to describe the semantic meaning of the block object
    name: str

    def __init__(self, system_specs: SystemSpec, name: str, snap_to_raster: bool = False):
        """ Must be called as last line of subclass.__init__"""
        super().__init__(name=name)
        if snap_to_raster:
            self.snap_to_raster(system_specs)
        self._clean()
        self.validate(system_specs)

    def __deepcopy__(self, memodict={}) -> "SequenceBaseBlock":
        ret = SequenceBaseBlock(system_specs=None, name=self.name)
        ret.__class__ = self.__class__  # pylint: disable=W0201
        ret.__dict__.update(deepcopy(self.__dict__))
        return ret

    def copy(self) -> 'SequenceBaseBlock':
        """Returns a deep copied building block object"""
        return self.__deepcopy__()

    @abstractmethod
    def snap_to_raster(self, system_specs: SystemSpec) -> None:
        pass

    def _clean(self):
        pass

    @abstractmethod
    def validate(self, system_specs: SystemSpec) -> None:
        """Should raise a ValueError if subclass logic is not met by definition
        :param system_specs:
        :return:
        """
        return

    @property
    def tmin(self) -> Quantity:
        """ Calculates the smallest time occuring in all contained definitions.
        :return: Quantity[time]
        """
        return Quantity(0, "ms")

    @property
    def tmax(self) -> Quantity:
        """ Calculates the largest time occuring in all contained definitions.
        :return: Quantity[time]
        """
        return Quantity(0, "ms")

    @property
    def duration(self) -> Quantity:
        return self.tmax - self.tmin

    @abstractmethod
    def flip(self, time_flip: Quantity = None):
        """Flips block around specified time point"""
        return

    @abstractmethod
    def shift(self, time_shift: Quantity) -> None:
        """Shifts block in time"""
        return
