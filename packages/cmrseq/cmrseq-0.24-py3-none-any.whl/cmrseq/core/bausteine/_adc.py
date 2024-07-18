""" Module containing the implementation of sampling blocks"""
__all__ = [ "ADC", "SymmetricADC", "GridSamplingADC"]

import decimal
import math

import numpy as np
from pint import Quantity

from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core._system import SystemSpec


class ADC(SequenceBaseBlock):
    """ ADC-specific extension to the SequenceBaseBlock, serves as base class for all
    ADC implementations.

    :param system_specs: System Limits specification object
    :param name:
    :param adc_timing: Quantity array of dimension time, containing all sampling event timings.
    :param adc_center: Time point defining the center of the ADC object
    :param phase_offset:  Phase-offset for all adc-samples, added when computing the adc-phase.
    :param frequency_offset: Frequency offset for all adc-samples, converted to an additional phase
                            offset per sample
    """
    #: Timing of ADC-sampling events. Exact definition of the meaning of that sampling time
    #: is delegated to subclass implementation. Quantity[ms]
    adc_timing: Quantity
    #: Time defining the center of the adc-events. Meant to synchronize the ADC block with echo
    #: times. Quantity[ms]
    adc_center: Quantity
    #: Phase-offset for all adc-samples, added when computing the adc-phase property. Quantity[rad]
    phase_offset: Quantity
    #: Frequency offset for all adc-samples, converted to an additional phase offset per sample and
    #: added when computing the adc-phase property. Quantity[Hz]
    frequency_offset: Quantity

    def __init__(self, system_specs: SystemSpec, name: str,
                 adc_timing: Quantity, adc_center: Quantity,
                 frequency_offset: Quantity, phase_offset: Quantity):
        super().__init__(system_specs, name)
        self.adc_timing : Quantity = adc_timing.to("ms")
        self.adc_center : Quantity = adc_center.to("ms")
        self.frequency_offset : Quantity = frequency_offset.to("Hz")
        self.phase_offset : Quantity = phase_offset.to("rad")

    @property
    def adc_phase(self) -> Quantity:
        """Returns the phase :math:`\\phi_s` at each adc sample :math:`s` in radians given the
        phase offset :math:`\\phi_0` and frequency offset :math:`\\delta f` according to the
        formular:

        .. math::

            \\phi_s = \\phi_0 + 2 * \\pi * \\delta f
        """
        t = self.adc_timing
        t_zero_ref = t - t[0]
        phase_per_time = (self.phase_offset.m_as("rad") +
                          2 * np.pi * self.frequency_offset.m_as("kHz") * t_zero_ref.m_as("ms"))
        return phase_per_time

    @property
    def tmin(self) -> Quantity:
        return self.adc_timing[0]

    @property
    def tmax(self) -> Quantity:
        return self.adc_timing[-1]

    def validate(self, system_specs: SystemSpec):
        return

    def shift(self, time_shift: Quantity) -> None:
        """Adds the time-shift to all adc definition points and the adc-center"""
        time_shift = time_shift.to("ms")
        self.adc_timing += time_shift
        self.adc_center += time_shift

    def flip(self, time_flip: Quantity = None):
        if time_flip is None:
            time_flip = self.tmax
        self.adc_timing = np.flip(time_flip.to("ms") - self.adc_timing, axis=0)
        self.adc_center = np.flip(time_flip.to("ms") - self.adc_center, axis=0)

    def snap_to_raster(self, system_specs: SystemSpec) -> None:
        pass


class SymmetricADC(ADC):
    """ ADC with instantaneous encoding events at k-space positions.

    Defines an ADC with sampling events uniformly distributed over
    the given duration. The central time point is allways contained as sampling event.

    .. note::

        For **even** number of samples the left border of the dwell time interval is defined as
        sampling events.
        For **odd** number of samples, the events are symmetric around center time.

    :param num_samples: number of sampling events over duration
    :param system_specs: cmrseq.SystemSpec object
    :param dwell: Quantity[time] Interval length associated with 1 sampling event.
                        Corresponds to kspace extend in readout-direction (1/FOV_kx).
    :param duration: Quantity[time] Total sampling duration corresponding to (1 / \Delta kx).
                      Usually is the same as flat_duration of accompanying trapezoidal gradient.
    :param delay: Quantity[time] Leading time without sampling events
    :param frequency_offset:
    :param phase_offset:
    """
    #: Total number of samples.
    _n_samples: int
    #:
    _dwell: Quantity
    
    def __init__(self, system_specs: SystemSpec,
                 num_samples: int,
                 dwell: Quantity = None,
                 duration: Quantity = None,
                 delay: Quantity = None,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "adc"):

        if (dwell is None and duration is None) or not (dwell is None or duration is None):
            raise ValueError("Either dwell or duration must be defined")

        if duration:
            dwell = duration / num_samples

        delay = Quantity(0, "ms") if delay is None else delay
        if num_samples % 2 == 1:
            adc_timing = (np.arange(0, num_samples) + 0.5) * dwell + delay
        else:
            adc_timing = (np.arange(0, num_samples)) * dwell + delay

        frequency_offset=frequency_offset.to("Hz")
        phase_offset=phase_offset.to("rad")
     
        self._n_samples = int(num_samples)
        self._dwell = dwell
        adc_center = adc_timing[int(np.floor(num_samples / 2))]
        
        super().__init__(system_specs=system_specs, name=name, 
                         adc_timing=adc_timing, adc_center=adc_center,
                         phase_offset=phase_offset, 
                         frequency_offset=frequency_offset)              

    @property
    def tmin(self) -> Quantity:
        """ Returns the time of the first sampling event. Behavior varies for odd/even number of
        samples:

            - **odd**: Returns the time of the first sampling event minus half a dwell time on
                       gradient raster time.
            - **even**: Returns the time of the first sampling event

        In both cases this corresponds to the start of the plateau of a readout gradient
        """
        first_sample_time = self.adc_timing[0]
        if self._n_samples % 2 != 0:  # odd number of samples
            start_ = first_sample_time - self._dwell / 2
        else:
            start_ = first_sample_time
        return start_

    @property
    def tmax(self) -> Quantity:
        """Returns the time of the last sampling event. Behavior varies for odd/even number of
        samples:

            - **odd**: Returns the time of the last sampling event plus half a dwell time.
            - **even**: Returns the time of the last sampling event plus a full dwell time.

        In both cases this corresponds to the end of the plateau of a readout gradient
        """
        last_sample_time = self.adc_timing[-1]
        if self._n_samples % 2 == 0:
            end_ = last_sample_time + self._dwell
        else:
            end_ = last_sample_time + self._dwell / 2
        return end_


class GridSamplingADC(ADC):
    """ Defines an oversampling adc-block on system adc_raster_time"""

    def __init__(self, system_specs: SystemSpec,
                 duration: Quantity,
                 delay: Quantity = Quantity(0, "ms"),
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"), name: str = "adc"):
        """

        :param system_specs:
        :param duration:
        :param delay:
        :param frequency_offset:
        :param phase_offset:
        :param name:
        """
        
        rounded_raster_time = decimal.Decimal(str(float(np.round(system_specs.adc_raster_time.m_as("ms"), decimals=6))))
        delay_dec = decimal.Decimal(str(float(np.round(delay.m_as("ms"), decimals=6))))
        duration_dec = decimal.Decimal(str(float(np.round(duration.m_as("ms"), decimals=6))))
        if not (delay_dec % rounded_raster_time == decimal.Decimal("0.0")):
            raise ValueError(f"Specified delay {delay:1.6} is not on adc_raster_time")
        if not (duration_dec % rounded_raster_time == decimal.Decimal("0.0")):
            raise ValueError(f"Specified duration {duration:1.6} is not on adc_raster_time")
        n_steps = math.ceil(duration / system_specs.adc_raster_time)
        time_grid = np.arange(0, n_steps+1, 1) * system_specs.adc_raster_time.m_as("ms")
        
        super().__init__(system_specs=system_specs, name=name,
                         adc_timing=Quantity(time_grid, "ms") + delay, 
                         adc_center=system_specs.time_to_raster(duration / 2, "adc") + delay,
                         frequency_offset=frequency_offset,
                         phase_offset=phase_offset)             

    @property
    def tmin(self) -> Quantity:
        return self.adc_timing[0]

    @property
    def tmax(self) -> Quantity:
        return self.adc_timing[-1]
