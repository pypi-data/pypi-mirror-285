"""This module contains implementation for gradient blocks"""
__all__ = ["Gradient", "TrapezoidalGradient", "ArbitraryGradient"]

from typing import Tuple
from warnings import warn
import numpy as np
from pint import Quantity

import cmrseq
from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core._system import SystemSpec


class Gradient(SequenceBaseBlock):
    """Generic implementation of a MRI-sequence building block containing gradient waveforms on
    3 channels.

    This class implements all functionality that should be provided by all types of gradients. 
    Special cases of gradients are meant to be inherited from this class.

    Some of the implemented functionalities and their underlying assumptions are described below.

    **Addition**:
    Gradient instances can be added using the :code:`+` operator, where breakpoints are combined and 
    linear interpolation of the waveform per channel inbetween the breakpoints is assumed.
    The result of adding two :code:`Gradient` objects, is a tuple containing the time and waveform 
    definition as shown in the example code below.

    .. Dropdown:: Example addition
        :animate: fade-in-slide-down
        :icon: graph
        :color: secondary
        
        .. code::

            trap1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs,
                                                                orientation=np.array([1., 0., 0.]),
                                                                duration=Quantity(1, "ms"),
                                                                amplitude=Quantity(10, "mT/m"),
                                                                 name="trap_1")

            trap2 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs,
                                                                orientation=np.array([1., 0., 0.]),
                                                                duration=Quantity(1, "ms"),
                                                                 amplitude=Quantity(10, "mT/m"),
                                                                 delay=Quantity(0.2, "ms"),
                                                                 name="trap_2")
            combined_t, combined_wf = trap1 + trap2
            combined_gradient = cmrseq.bausteine.ArbitraryGradient(system_specs, combined_t,
                                                                combined_wf, name="combined_trap")
            seq = cmrseq.Sequence([combined_gradient], system_specs)

    **Split**:
    This functionality mainly is required to adhere to the pulseq file format, which requires
    the gradient definition to be sub-divided into blocks, such that the each gradient channel
    has at max one gradient block. The :code:`split` function allows to separate the gradient 
    definition at an arbitrary time.


    **Validation**:
    Gradient objects are validated against the system-specifications with regard to:
    1. Maximal gradient strength
    2. Maximal gradient slew-rate
    3. Adherence to the gradient-raster time
    
    If the raster time does not match, one option is to apply the snap to raster method, 
    which rounds all temporal definitions to the closest raster point. In most cases this
    includes unwanted side-effects e.g changing moments. If all time-points are offset 
    from the grid by the same amount this methods should not have unwanted side effects.    
    """
    #: Tuple containing defining points of gradient waveforms as np.array (wrapped as Quantity)
    #: with shape (time: (t, ), waveform: (3, t)). Between points, linear interpolation is assumed
    gradients: Tuple[Quantity, Quantity]

    def __init__(self, t: Quantity, grads: Quantity, system_specs: 'cmrseq.SystemSpec',
                 name: str, snap_to_raster: bool):
        self.gradients = (t, grads)
        super().__init__(system_specs=system_specs, name=name, snap_to_raster=snap_to_raster)

    def __add__(self, other) -> (Quantity, Quantity):
        """ Add to gradient definition and always returns a Tuple (time_points[n], waveforms[3, n])

        :param other:
        :return:
        """
        if isinstance(other, Gradient):
            tother, wfother = other.gradients
        elif isinstance(other, tuple):
            if len(other) != 2 or any(not isinstance(o, Quantity) for o in other):
                raise NotImplementedError
            tother, wfother = other
            if len(tother) == 0:
                return self.copy()
        else:
            raise NotImplementedError(f"Addition of {self.__class__} and {other.__class__} not "
                                      f"implemented")

        tself, wfself = self.gradients
        tother, wfother, tself, wfself = [np.around(_, decimals=10) for _ in
                                          [tother.m_as("ms"), wfother.m_as("mT/m"),
                                           tself.m_as("ms"), wfself.m_as("mT/m")]]
        if tother[-1] == tself[0] and np.allclose(wfother[:, -1], wfself[:, 0]):
            tother = tother[:-1]
            wfother = wfother[:, :-1]
        if tself[-1] == tother[0] and np.allclose(wfself[:, -1], wfother[:, 0]):
            tself = tself[:-1]
            wfself = wfself[:, :-1]
        t_combined = np.unique(np.sort([*tself, *tother]))
        wfself_interp = np.stack([np.interp(t_combined, tself, wf, left=0, right=0)
                                  for wf in wfself])
        wfother_interp = np.stack([np.interp(t_combined, tother, wf, left=0, right=0)
                                   for wf in wfother])
        wfself_interp[:, t_combined < tself[0]] = 0
        wfself_interp[:, t_combined > tself[-1]] = 0
        wfother_interp[:, t_combined < tother[0]] = 0
        wfother_interp[:, t_combined > tother[-1]] = 0

        return Quantity(t_combined, "ms"), Quantity(wfother_interp + wfself_interp, "mT/m")

    def __radd__(self, other):
        return self.__add__(other)

    def split(self, t: Quantity) -> (Quantity, Quantity):
        """ Splits the gradient waveform at given time and returns to new definining tuples
        that both include the split point.
        This output is meant to yield the original waveform when calling the __add__ functions on
        the result

        :param t:
        :return:
        """
        split_is_on_def = np.isclose(t.to("ms"), self.gradients[0].to("ms"))
        tself, wfself = self.gradients

        if np.any(split_is_on_def):
            split_index, = np.where(split_is_on_def)
            split_index = split_index[0]
            return (tself[:split_index+1], wfself[:, :split_index+1]), \
                   (tself[split_index:], wfself[:, split_index:])
        tself, wfself, t = tself.to("ms"), wfself.to("mT/m"), t.to("ms")
        insertion_index = np.searchsorted(tself, t)
        insertion_val = np.stack([np.interp(t, tself, wfself[i]) for i in range(3)])
        wfself = Quantity(np.insert(wfself, insertion_index, insertion_val, axis=1), "mT/m")
        tself = Quantity(np.insert(tself, insertion_index, t), "ms")
        split_index = insertion_index
        return (tself[:split_index+1], wfself[:, :split_index+1]), \
               (tself[split_index:], wfself[:, split_index:])

    @property
    def tmin(self) -> Quantity:
        return self.gradients[0][0]

    @property
    def tmax(self) -> Quantity:
        return self.gradients[0][-1]

    def scale_gradients(self, factor: float) -> None:
        """ Scales gradients by given factor if gradients are defined.

        :param factor: factor to globally scale the amplitude of gradient defintion.
        """
        t, grads = self.gradients
        self.gradients = (t, factor * grads)

    def rotate_gradients(self, rotation_matrix: np.ndarray) -> None:
        """ Rotates gradients to according to the gradient axes transformation:

        [[1 0 0][0 1 0][0 0 0]].T -> rotation matrix

        :raises: ValueError - if rotation_matrix is not valid : must be an orthogonal matrix

        :param rotation_matrix: (3, 3) rotation matrix containing the new column basis vectors
                                (meaning in [:, i], i indexes the new orientation of MPS).
                                Vectors are normalized along axis=0 to ensure same magnitude
        """
        valid_rotation = np.all(np.isclose((np.matmul(rotation_matrix, rotation_matrix.T)),
                                           np.identity(3), rtol=1e-10))
        if not valid_rotation:
            raise ValueError(f"Rotation matrix is not valid\n "
                             f"{np.matmul(rotation_matrix, rotation_matrix.T)} \n"
                             f"should be identity")

        t, wf = self.gradients
        vector_norms = np.linalg.norm(rotation_matrix, axis=0, keepdims=True)
        rotation_matrix = rotation_matrix / vector_norms
        wf_rot = np.einsum("it, ij -> jt", wf.m_as("mT/m"), rotation_matrix)
        self.gradients = (t, Quantity(wf_rot, "mT/m"))

    def _clean(self):
        """ If gradient definition contains duplicate consecutive points, the second one is
        removed"""
        t = self.gradients[0].to("ms").m
        g = self.gradients[1].to("mT/m").m
        deltat = np.diff(np.around(t, decimals=6), axis=0)
        deltag = np.diff(np.around(g, decimals=6), axis=1)
        duplicate_idx = np.where(np.logical_and(deltat == 0., np.all(deltag == 0., axis=0)))
        cleaned_t = Quantity(np.delete(t, duplicate_idx), "ms")
        cleaned_g = Quantity(np.delete(g, duplicate_idx, axis=1), "mT/m")
        self.gradients = (cleaned_t, cleaned_g)

    def validate(self, system_specs: SystemSpec) -> None:
        """ Validates if the contained gradient_definition is valid for the given system-
        specifications.
        """
        t = self.gradients[0].m_as("ms")
        g = self.gradients[1].m_as("mT/m")
        max_grad_in_specs = np.all(np.abs(g) <= system_specs.max_grad.m_as("mT/m") + 1e-6)
        grad_slew = (np.diff(g, axis=1) / np.diff(t, axis=0)[np.newaxis])
        grad_slew_in_specs = np.all(np.abs(np.around(grad_slew, decimals=6))
                                    <= system_specs.max_slew.m_as("mT/m/ms"))
        tgridded = t / system_specs.grad_raster_time.m_as("ms")
        grad_on_grid = np.allclose(tgridded, np.around(tgridded), rtol=1e-6)
        if not all([max_grad_in_specs, grad_slew_in_specs, grad_on_grid]):
            raise ValueError(f"Gradient definition of {self.name} invalid:\n"
                             f"\t- max grad: {max_grad_in_specs} "
                             f"[{np.max(self.gradients[1].m_as('mT/m'))}"
                             f" {'<' if max_grad_in_specs else '<'} "
                             f"{system_specs.max_grad.m_as('mT/m')}]\n"
                             f"\t- max slew: {grad_slew_in_specs} [{np.max(grad_slew)} "
                             f"{'<' if grad_slew_in_specs else '<'} "
                             f"{system_specs.max_slew.m_as('mT/m/ms')}] \n"
                             f"\t- definition on grid: {grad_on_grid}")

    def snap_to_raster(self, system_specs: SystemSpec):
        warn("Gradient.snap_to_raster Warning: When calling snap_to_raster the waveform points are simply"
             f"rounded to their nearest neighbour if the difference is below the relative tolerance."
             f"Therefore this is not guaranteed to be precise anymore")
        time_ndt = np.around(self.gradients[0].m_as("ms") /
                             system_specs.grad_raster_time.m_as("ms"), decimals=0)
        time_ndt = time_ndt * system_specs.grad_raster_time.to("ms")
        self.gradients = (time_ndt.to("ms"), self.gradients[1].to("mT/m"))

    def shift(self, time_shift: Quantity):
        """Adds the time-shift to all gradient definition points"""
        self.gradients = (self.gradients[0] + time_shift.to("ms"), self.gradients[1])

    def flip(self, time_flip: Quantity = None):
        """Time reverses block by flipping about a given time point. If no
        time is specified, the center of this gradient block is choosen."""
        if time_flip is None:
            time_flip = self.tmin + (self.tmax - self.tmin) / 2
        self.gradients = (np.flip(time_flip.to("ms") - self.gradients[0], axis=0),
                          np.flip(self.gradients[1], axis=1))


class TrapezoidalGradient(Gradient):
    """ Module implementing a trapezoidal gradient pulse, from specified parameters"""

    # pylint: disable=R0913
    def __init__(self,
                 system_specs: SystemSpec,
                 orientation: np.ndarray,
                 amplitude: Quantity,
                 flat_duration: Quantity,
                 rise_time: Quantity,
                 fall_time: Quantity = None,
                 delay: Quantity = Quantity(0., "ms"),
                 name: str = "trapezoidal",
                 snap_to_raster: bool = False):
        r""" Defines a trapezoidal gradient pulse:

        **Diagram**:

        .. code-block:: python

            .                     |-flat_dur-|                                      .
            .                     ____________                                      .
            .          |-delay-| /            \           |      amplitude          .
            .          _________/              \______    |                         .
            .                  |--|         |--|                                    .
            .                rise_time    fall_time                                 .
            .          |--------duration-------|                                    .

        :param system_specs: System-Limit context (SystemSpec instance)
        :param orientation: np.array of shape (3, ). Vector defining the gradient orientation
                            in (gx, gy, gz) channels. Is normalized internally
        :param amplitude: Quantity[Tesla/Length] Desired amplitude of specified gradient pulse
        :param flat_duration: Quantity[Time] Duration of gradient-plateau
        :param rise_time: Quantity[Time] Duration of rising slope.
        :param fall_time: Quantity[Time] Duration falling slope. If not specified symmetric
                                rise/fall time is assumed.
        :param delay: Quantity[Time] Leading time without gradients
        """
        norm = np.linalg.norm(orientation)
        if norm > 0:
            orientation /= norm

        if fall_time is None:
            fall_time = rise_time
        rise_time = rise_time.m_as("ms")
        fall_time = fall_time.m_as("ms")
        flat_duration = flat_duration.m_as("ms")

        time_points = np.around(np.stack([
            0, rise_time,
            rise_time + flat_duration,
            fall_time + rise_time + flat_duration]
        ), decimals=6)

        time_points = Quantity(time_points, "ms") + delay
        grads_amp = np.stack([0., amplitude, amplitude, 0.])
        grads = grads_amp[np.newaxis] * orientation[:, np.newaxis]
        super().__init__(time_points, grads, system_specs=system_specs,
                         name=name, snap_to_raster=snap_to_raster)

    @property
    def rise_time(self) -> Quantity:
        """ Duration of the first trapezoidal gradient slope """
        return self.gradients[0][1] - self.gradients[0][0]

    @property
    def fall_time(self) -> Quantity:
        """ Duration of the second trapezoidal gradient slope """
        return self.gradients[0][-1] - self.gradients[0][-2]

    @property
    def flat_duration(self) -> Quantity:
        """ Duration of the trapezoidal gradient plateau """
        return self.gradients[0][-2] - self.gradients[0][1]

    @property
    def amplitude(self) -> Quantity:
        """ Amplitude of the trapezoidal gradient plateau in mT/m"""
        warn("Please use the new property 'magnitude', as amplitude will"
             "be used as signed amplitude per channel in the next release",DeprecationWarning,stacklevel=2)
        return Quantity(np.linalg.norm(self.gradients[1][:, 1].m_as("mT/m")), "mT/m")

    @property
    def magnitude(self) -> Quantity:
        """ Magnitude (norm over spatial dimensions) of the trapezoidal
        gradient plateau in mT/m"""
        return Quantity(np.linalg.norm(self.gradients[1][:, 1].m_as("mT/m")), "mT/m")

    @property
    def signed_amplitude(self) -> Quantity:
        """ Signed amplitude the amplitude per gradient channel """
        return self.gradients[1][:, 1].to("mT/m")

    @property
    def area(self) -> Quantity:
        """ Area of the trapezoidal gradient:
         ((rise_time + fall_time + flat_duration) * amplitude)"""
        area = (self.rise_time / 2 + self.fall_time / 2 + self.flat_duration) * \
               self.gradients[1][:, 1]
        return np.abs(area)

    @classmethod
    def from_area(cls, system_specs: SystemSpec, orientation: np.ndarray, area: Quantity,
                  delay: Quantity = Quantity(0., "ms"),
                  name: str = "trapezoidal") -> 'TrapezoidalGradient':
        """Constructs the shortest Trapezoidal or triangular gradient pulse with specified area
         given the system limits:

         :raises AssertionError: If area < 0

         :param system_specs: System-Limit context (SystemSpec instance)
         :param area: Quantity[Tesla/Length*Time] Desired first moment of the Gradient Pulse
         :param orientation: np.array of shape (3, ). Vector defining the gradient orientation
                             in (gx, gy, gz) channels. Is normalized internally
         :param delay: Quantity[Time] Leading time without gradients, defaults to 0. ms
         :param name:
         :return: TrapezoidalGradient object
         """
        assert area.m >= 0
        amplitude, rise_time, flat_time = system_specs.get_shortest_gradient(area.to("mT/m*ms"))
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_time.to("ms"), rise_time=rise_time.to("ms"),
                                   delay=delay, name=name)

    @classmethod
    # pylint: disable=W1401
    def from_dur_area(cls, system_specs: SystemSpec, orientation: np.ndarray, duration: Quantity,
                      area: Quantity, delay: Quantity = Quantity(0., "ms"),
                      name: str = "trapezoidal") -> 'TrapezoidalGradient':
        """ Constructs the Trapezoidal or triangular gradient pulse with specified area and duration
        (flat + 2 ramp), given the system limits. Ramp time is calculated under the assumption of
        using maximal slew rate.
        Is equivalent to solving:

        .. math::
            a=amplitude, A=area, \delta=ramp, D=duration, s_m=max slew \n
            Triangular: \n
            A = a (D-\delta) \ \ and \ \ \delta * s_m= a \n
            \\rightarrow \delta = (D/2)-\sqrt{(D/2)^2 - A/s_m}

        :raises ValueError: - Duration is not on gradient raster time
                            - If area is not feasible with given duration and system limits \n
        :raises AssertionError: If area < 0
        :return: TrapezoidalGradient object
        """
        assert area.m >= 0
        amplitude, rise_time, flat_time = system_specs.get_shortest_gradient(area)
        min_duration = rise_time * 2 + flat_time
        if duration.m_as("ms") < min_duration.m_as("ms") - 1e-6:
            message = f"Infeasible with given system limits, minimal value: {min_duration} > {duration}"
            raise cmrseq.err.BuildingBlockArgumentError(argument='duration', message=message,
                                                        class_name='TrapezoidalGradient')

        duration_raster = system_specs.time_to_raster(duration)
        if not np.isclose((duration - duration_raster).m_as("ms"), 0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        p_half = (duration_raster / 2.)
        q = area / system_specs.max_slew  # pylint: disable=C0103

        radicant = (p_half ** 2 - q).to("ms**2")
        if np.isclose(radicant.m, 0., atol=1e-5):
            radicant = Quantity(0, "ms**2")

        rise_time_p = system_specs.time_to_raster(np.abs(p_half + np.sqrt(radicant)), raster="grad")
        rise_time_m = system_specs.time_to_raster(np.abs(p_half - np.sqrt(radicant)), raster="grad")
        if 2 * rise_time_p > duration_raster:
            rise_time = rise_time_m
        else:
            rise_time = rise_time_p
        flat_duration = duration_raster - 2 * rise_time
        amplitude = area / (flat_duration + rise_time)

        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude,
                                   flat_duration=flat_duration,
                                   rise_time=rise_time, delay=delay, name=name)

    @classmethod
    # pylint: disable=W1401
    def from_fdur_area(cls, system_specs: SystemSpec, orientation: np.ndarray,
                       flat_duration: Quantity, area: Quantity,
                       delay: Quantity = Quantity(0., "ms"), name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified area
        and flat duration, given the system limits. Ramp time is calculated under the assumption of
        using maximal slew rate. Is equivalent to solving:

        .. math::
            a=amplitude, A=area, \delta=ramp, \Delta=flatduration, s_m=max slew \n
            Triangular: \n
            A = a (\Delta + \delta) \ \ and \ \ \delta * s_m = a \n
            \\rightarrow \delta = -(\Delta/2) + \sqrt{(\Delta/2)^2 - A/s_m}

        :raises ValueError: - Flat duration is not on gradient raster time
        :raises ValueError: - If area is not feasible with given duration and system limits
        :raises AssertionError: If area < 0

        :return: TrapezoidalGradient object """
        assert area.m >= 0
        amplitude, rise_time, flat_time = system_specs.get_shortest_gradient(area.to("mT/m*ms"))
        if flat_duration < flat_time:
            message = f"Infeasible with given system limits, minimal value: {flat_time} > {flat_duration}"
            raise cmrseq.err.BuildingBlockArgumentError(argument='flat_duration', message=message,
                                                        class_name='TrapezoidalGradient')

        duration_raster = system_specs.time_to_raster(flat_duration, raster="grad")
        if not np.isclose(flat_duration.m_as("ms") - duration_raster.m_as("ms"), 0., rtol=1e-6):
            message = (f"Specified duration not on raster: {flat_duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")
            raise cmrseq.err.BuildingBlockArgumentError(argument='flat_duration', message=message,
                                                        class_name='TrapezoidalGradient')

        p_half = flat_duration / 2.
        q = - area / system_specs.max_slew 
        radicant = (p_half ** 2 - q).to("ms**2")
        if np.isclose(radicant.m, 0., atol=1e-5):
            radicant = Quantity(0, "ms**2")
            rise_time = system_specs.time_to_raster(np.abs(p_half), raster="grad")
        else:
            rise_time_p = system_specs.time_to_raster(np.abs(p_half + np.sqrt(radicant)), raster="grad") 
            rise_time_m = system_specs.time_to_raster(np.abs(p_half - np.sqrt(radicant)), raster="grad") 
            rise_time = min(rise_time_m, rise_time_p)
        amplitude = area / (flat_duration + rise_time)
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)

    @classmethod
    def from_dur_amp(cls, system_specs: SystemSpec, orientation: np.ndarray, duration: Quantity,
                     amplitude: Quantity, delay: Quantity = Quantity(0., "ms"),
                     name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified duration
                and amplitude, given the system limits. Ramp time is calculated under the
                assumption of using maximal slew rate.

        :raises ValueError: If duration is not on grid & If amplitude is not reachable within
                            specified duration / 2 with given system limits
        """
        duration_raster = system_specs.time_to_raster(duration)
        if not np.isclose(duration.m_as("ms") - duration_raster.m_as("ms"), 0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        if duration / 2 * system_specs.max_slew < amplitude:
            raise ValueError("Specified amplitude not reachable with given slewrate and duration")

        rise_time = system_specs.get_shortest_rise_time(amplitude)
        flat_duration = duration - 2 * rise_time
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)

    @classmethod
    def from_fdur_amp(cls, system_specs: SystemSpec, orientation: np.ndarray,
                      flat_duration: Quantity, amplitude: Quantity,
                      delay: Quantity = Quantity(0., "ms"), name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified flat
        duration and amplitude, given the system limits. Ramp time is calculated under the
        assumption of using maximal slew rate.

        :raises ValueError: If flat_duration is not on grid
        """
        flat_duration_raster = system_specs.time_to_raster(flat_duration)
        if not np.isclose(flat_duration.m_as("ms") - flat_duration_raster.m_as("ms"),
                          0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {flat_duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        rise_time = system_specs.get_shortest_rise_time(amplitude)
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)

    @classmethod
    def from_fdur_farea(cls, system_specs: SystemSpec, orientation: np.ndarray,
                        flat_duration: Quantity, flat_area: Quantity,
                        delay: Quantity = Quantity(0., "ms"), name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified flat
        duration and flat_area, given the system limits. Ramp time is calculated under the
        assumption of using maximal slew rate.

        :raises ValueError: If flat_duration is not on grid
        """
        assert flat_area.m >= 0
        flat_duration_raster = system_specs.time_to_raster(flat_duration)
        if not np.isclose(flat_duration.m_as("ms") - flat_duration_raster.m_as("ms"),
                          0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {flat_duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        amplitude = flat_area / flat_duration
        rise_time = system_specs.get_shortest_rise_time(amplitude)
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)


class ArbitraryGradient(Gradient):
    """ Wraps a definition of an arbitrary waveform defined as numpy arrays."""

    def __init__(self, system_specs: SystemSpec,
                 time_points: Quantity,
                 waveform: Quantity,
                 delay: Quantity = Quantity(0, "ms"),
                 name: str = "name",
                 snap_to_raster: bool = False):
        """ Wraps a definition of waveform in numpy arrays.

        :param system_specs:
        :param time_points: Quantity[Time] - array of shape (#steps, ) containing the defining
                                time-points of the gradient waveform
        :param waveform: Quantity[Tesla/Length] - array of shape (3, #steps) containing the
                                gradient amplitudes corresponding to time_points
        """
        super().__init__(time_points + delay, waveform,
                         system_specs=system_specs, name=name, snap_to_raster=snap_to_raster)
