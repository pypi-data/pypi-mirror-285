""" This module contains in the implementation of radio-frequency pulse building blocks"""
__all__ = ["RFPulse", "SincRFPulse","HardRFPulse", "ArbitraryRFPulse"]

from typing import Tuple
from warnings import warn

from pint import Quantity
import numpy as np

from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core._system import SystemSpec


class RFPulse(SequenceBaseBlock):
    """Generic MRI-sequence radio-frequency building block 
    
    This class implements all functionality that should be provided by all subtypes of 
    RF-pulses. 

    The waveform (assuming linear interpolation between the points) and the time-points have to
    be specified on construction of the RF object, where the waveform is assumed to be real-valued.
    It also is assumed, that all RF-pulse subclasses correctly calculate and provide the following
    quantities:

    1. Pulse bandwidth
    2. Frequency offset 
    3. Phase offset

    The phase offset and frequency offset attributes are used to compute the complex rf-waveform
    representation using the `RFPulse.rf` - property.

    :param system_specs: 
    :param name:
    :param time: (# points) time-points defining the waveform duration
    :param rf_waveform: (#points) rf-amplitude
    :param phase_offset: 
    :param frequency_offset:
    :param rf_events:
    :param snap_to_raster:
    """
    #: Tuple containing defining points of RF-waveforms as np.array (wrapped as Quantity)
    #: with shape (time: (t, ), waveform: (3, t)). Between points, linear interpolation is assumed
    _rf: Tuple[Quantity, Quantity]
    #: Tuple containing rf events (time, flip_angle)
    rf_events: Tuple[Quantity, Quantity]
    #: RF pulse bandwidth in kilo Hertz. Used to calculate gradient strength
    bandwidth: Quantity
    #: RF phase offset in radians. This is used phase shift the complex rf amplitude in self.rf
    phase_offset: Quantity
    #: RF frequency offset in Hertz. This is used to modulate the complex rf amplitude in self.rf
    frequency_offset: Quantity

    def __init__(self, system_specs: SystemSpec, name: str,
                 time: Quantity, rf_waveform: Quantity,
                 frequency_offset: Quantity, phase_offset: Quantity, 
                 bandwidth: Quantity,
                 rf_events: Tuple[Quantity, Quantity],
                 snap_to_raster: bool = False):

        self._rf = (time.to("ms"), rf_waveform.to("uT"))
        self.rf_events = (rf_events[0].to("ms"), rf_events[1].to("degree"))

        self.phase_offset = phase_offset.to("rad")
        self.frequency_offset = frequency_offset.to("Hz")
        self.bandwidth = bandwidth.to("kHz")
        super().__init__(system_specs, name, snap_to_raster)

    @property
    def tmin(self) -> Quantity:
        return self._rf[0][0]

    @property
    def tmax(self) -> Quantity:
        return self._rf[0][-1]

    def validate(self, system_specs: SystemSpec):
        """ Validates if the contained rf-definition is valid for the given system-
                specifications"""
        t, wf = self._rf
        float_steps = t.m_as("ms") / system_specs.rf_raster_time.m_as("ms")
        n_steps = np.around(float_steps)
        ongrid = np.allclose(n_steps, float_steps, rtol=1e-6)
        if not all([ongrid]):
            raise ValueError(f"RF definition invalid:\n"
                             f"\t - definition on grid: {ongrid}\n")

        if np.max(np.abs(wf)) > system_specs.rf_peak_power:
            raise ValueError(f"RF definition invalid:\n"
                             f"\t - peak power exceeds system limits: {np.max(np.abs(wf))}\n")

        if not np.allclose([wf[0].m_as("uT"), wf[-1].m_as("uT")],
                           Quantity(0, "uT").m, atol=1e-3):
            start, end = [np.round(wf[i].m_as('uT'), decimals=3) for i in (0, -1)]
            raise ValueError(f"RF definition invalid:\n",
                             f"\t - start/end of waveform != 0: {start}/{end}\n")


    @property
    def rf(self) -> (Quantity, Quantity):
        """ Returns the complex RF-amplitude shifted/modulated by the phase/frequency offsets """
        t, amplitude = self._rf
        t_zero_ref = t - t[0]
        complex_amplitude = np.array((amplitude.m_as("uT") + 1j * np.zeros_like(amplitude.m_as("uT"))))
        phase_per_time = (self.phase_offset.m_as("rad") +
                          2 * np.pi * self.frequency_offset.m_as("kHz") * t_zero_ref.m_as("ms"))
        complex_amplitude = complex_amplitude * np.exp(1j * phase_per_time)
        return t, Quantity(complex_amplitude, "uT")

    @rf.setter
    def rf(self, value: Tuple[Quantity, Quantity]):
        self._rf = value

    @property
    def normalized_waveform(self) -> (np.ndarray, Quantity, np.ndarray, Quantity):
        """Computes the normalized waveform (scaling between -1, 1).

        :return: - Normalized amplitude between [-1, 1] [dimensionless] (flipped such that the
                    maximum normalized value is positive. Scaling with peak amplitude inverts the
                    shape again)
                 - Peak amplitude in uT
                 - Phase per timestep in rad
                 - Time raster definition points
        """
        t, amplitude = self._rf
        t_zero_ref = t - t[0]
        if amplitude.m_as("uT").dtype in [np.complex64, np.complex128]:
            phase = np.angle(amplitude.m_as("uT"))
            phase = phase - self.phase_offset.m_as("rad")
            phase -= (t_zero_ref * 2 * np.pi * self.frequency_offset).m_as("rad")
            amplitude = amplitude.m_as("uT") * np.exp(-1j * phase)
        else:
            phase = np.zeros(amplitude.shape, dtype=np.float64)
            amplitude = amplitude.m_as("uT")

        peak_amp_plus, peak_amp_minus = np.max(amplitude), np.min(amplitude)
        absolute_max_idx = np.argmax([np.abs(peak_amp_plus), np.abs(peak_amp_minus)])
        peak_amp = (peak_amp_plus, peak_amp_minus)[absolute_max_idx]
        normed_amp = np.divide(amplitude, peak_amp, out=np.zeros_like(amplitude),
                               where=(peak_amp != 0))
        return np.real(normed_amp), Quantity(peak_amp, "uT"), phase, t_zero_ref

    def shift(self, time_shift: Quantity) -> None:
        """Adds the time-shift to all rf definition points and the rf-center"""
        time_shift =  time_shift.to("ms")
        self._rf = (self._rf[0] + time_shift, self._rf[1])
        self.rf_events = (self.rf_events[0] + time_shift, self.rf_events[1])

    def flip(self, time_flip: Quantity = None):
        """Time reverses block by flipping about a given time point. If no
        time is specified, the rf center of this block is choosen."""
        if time_flip is None:
            time_flip = self.rf_events[0][0]
        self._rf = (np.flip(time_flip.to("ms") - self._rf[0], axis=0), np.flip(self._rf[1], axis=1))
        self.rf_events = (np.flip(time_flip.to("ms") - self.rf_events[0], axis=0),
                          np.flip(self.rf_events[1], axis=0))

    def scale_angle(self, factor: float):
        """Scales the contained waveform amplitude and corresponding rf_events by 
        given factor. Resulting in scaled flip angles.
        """
        self.rf_events = (self.rf_events[0].to("ms"), self.rf_events[1].to("degree") * factor)
        self._rf = (self._rf[0], self._rf[1] * factor)

    def snap_to_raster(self, system_specs: SystemSpec):
        warn("RF.snap_to_raster Warning: When calling snap_to_raster the waveform points are simply"
             f"rounded to their nearest neighbour if the difference is below the relative tolerance."
             f"Therefore this is not guaranteed to be precise anymore")

        t_rf = system_specs.time_to_raster(self._rf[0], "rf")
        self._rf = (t_rf.to("ms"), self._rf[1])


class SincRFPulse(RFPulse):
    """Defines a Sinc-RF pulse on a time grid with step length defined by system_specs. The
    window function used to temporally limit the waveform is given as:

    .. math::

        window = (1 - \\beta) + \\beta cos(2 \\pi n /N)

    where :math:`\\beta` is the specified apodization argument. If set to 0.5 the used window is a
    Hann window resulting in 0 start and end. using 0.46 results in the use of a Hamming window.

    .. warning::

        The sinc-pulse definition does not enforce 0 valued start and end of the wave-form.

    :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                        Values the flip-angle is stored as positive absolute plus a phase offset
                        of 180°
    :param duration: Quantity[Time] Total duration of the pulse
    :param time_bandwidth_product: float - Used to calculated the pulse-bandwidth. For a
                Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                half central-lobe-width
    :param center: float [0, 1] factor to compute the pulse center relative to duration
    :param delay:
    :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
    :param frequency_offset: Frequency offset in Hz in rotating frame ()
    :param phase_offset: Phase offset in rad.
    :param name:
    """
    # pylint: disable=R0913, R0914
    def __init__(self,
                 system_specs: SystemSpec,
                 duration: Quantity,
                 flip_angle: Quantity = Quantity(np.pi, "rad"),
                 time_bandwidth_product: float = 3.,
                 center: float = 0.5,
                 delay: Quantity = Quantity(0., "ms"),
                 apodization: float = 0.5,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "sinc_rf"):
        """ Defines a Sinc-RF pulse on a time grid with step length defined by system_specs.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                            Values the flip-angle is stored as positive absolute plus a phase offset
                            of 180°
        :param duration: Quantity[Time] Total duration of the pulse
        :param time_bandwidth_product: float - Used to calculated the pulse-bandwidth. For a
                    Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                    half central-lobe-width
        :param center: float [0, 1] factor to compute the pulse center relative to duration
        :param delay:
        :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """

        if flip_angle < Quantity(0, "rad"):
            phase_offset += Quantity(np.pi, "rad")
            flip_angle = -flip_angle

        time_points, unit_wf = self._get_unit_waveform(
                                            raster_time=system_specs.rf_raster_time, 
                                            time_bandwidth_product=time_bandwidth_product,
                                            duration=duration, apodization=apodization,
                                            center=center)

        # For Sinc-Pulse this t*bw/duration corresponds to half central lobe width
        bandwidth = Quantity(time_bandwidth_product / duration.to("ms"), "1/ms")

        unit_flip_angle = np.sum((unit_wf[1:] + unit_wf[:-1]) / 2) * system_specs.rf_raster_time.to("ms")\
                          * system_specs.gamma_rad.to("rad/mT/ms")

        amplitude = unit_wf * flip_angle.to("rad") / unit_flip_angle

        super().__init__(system_specs=system_specs, name=name,
                         time=time_points + delay, rf_waveform=amplitude,
                         frequency_offset=frequency_offset, phase_offset=phase_offset,
                         rf_events=(center * duration + delay, flip_angle),
                         bandwidth=bandwidth, snap_to_raster=False)
    
    @staticmethod
    def _get_unit_waveform(raster_time: Quantity, time_bandwidth_product: float,
                           duration: Quantity,
                           apodization: float, center: float) -> Quantity:
        """ Constructs the sinc-pulse waveform according to:

        .. math:: 

            wf = (1 - \Gamma + \Gamma cos(2\pi / \Delta * t)) * sinc(tbw/\Delta t)

        where

        .. math::
            \Gamma     :& apodization (typically 0.46) \\\\
            \Delta     :& Pulse duration \\\\
            tbw        :& Time-bandwidth-product \\\\
            t          :& time on raster where center defines 0.


        """   
        bandwidth = Quantity(time_bandwidth_product / duration.m_as("ms"), "1/ms")
        n_steps = np.around(duration.m_as("ms") / raster_time.m_as("ms"))
        time_points = Quantity(np.arange(0., n_steps+1, 1) * raster_time.m_as("ms"), "ms")
        time_rel_center = time_points.to("ms") - (center * duration.to("ms"))
        window = (1 - apodization) + apodization * np.cos(2 * np.pi * np.arange(-n_steps//2, n_steps//2+1, 1) / n_steps)
        unit_wf = np.sinc((bandwidth.to("1/ms") * time_rel_center).m_as("dimensionless")) * window
        unit_wf -= unit_wf[0]
        return time_points, unit_wf

    @classmethod
    def from_shortest(cls, system_specs: SystemSpec, flip_angle: Quantity,  
                      time_bandwidth_product: float = 3., center: float = 0.5,
                      delay: Quantity = Quantity(0., "ms"), 
                      apodization: float = 0.5,
                      frequency_offset: Quantity = Quantity(0., "Hz"), 
                      phase_offset: Quantity = Quantity(0., "rad"),
                      name: str = "sinc_rf"): 
        """Creates the shortest Sinc RF pulse for specified arguments.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                            Values the flip-angle is stored as positive absolute plus a phase offset
                            of 180°
        :param time_bandwidth_product: float - Used to calculated the pulse-bandwidth. For a
                    Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                    half central-lobe-width
        :param center: float [0, 1] factor to compute the pulse center relative to duration
        :param delay:
        :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """
        durations = Quantity(np.linspace(0.1, 1.5, 2), "ms")
        fas = []
        for dur in durations:
            _, unit_wf = cls._get_unit_waveform(raster_time=system_specs.rf_raster_time,
                                                time_bandwidth_product=time_bandwidth_product,
                                                duration=dur, apodization=apodization,
                                                center=center)
            max_wf =  unit_wf * system_specs.rf_peak_power.to("uT")
            fa = np.sum((max_wf[1:] + max_wf[:-1]) / 2 * system_specs.rf_raster_time.to("ms"))
            fa *= system_specs.gamma_rad.to("rad/mT/ms") 
            fas.append(fa.m_as("degree"))
        slope = Quantity(np.diff(durations.m_as("ms")) / np.diff(fas), "ms/degree")[0]
        target_duration = system_specs.time_to_raster(np.abs(flip_angle) * slope, "rf")
        
        return cls(system_specs, duration=target_duration,
                   flip_angle=flip_angle, time_bandwidth_product=time_bandwidth_product,
                   center=center, delay=delay, apodization=apodization,
                   frequency_offset=frequency_offset, phase_offset=phase_offset, name=name)
    
    # @classmethod
    # def from_bandwidth(cls, system_specs: SystemSpec,
    #                    band_width: Quantity,
    #                    flip_angle: Quantity,  
    #                    time_bandwidth_product: float = 4, 
    #                    center: float = 0.5,
    #                    delay: Quantity = Quantity(0., "ms"), 
    #                    apodization: float = 0., 
    #                    frequency_offset: Quantity = Quantity(0., "Hz"), 
    #                    phase_offset: Quantity = Quantity(0., "rad"),
    #                    name: str = "sinc_rf"):
    #     """
        
    #     """
    #     duration = Quantity(time_bandwidth_product / band_width.to("1/ms"), "ms")
    #     return cls(system_specs, duration=duration, flip_angle=flip_angle,
    #                time_bandwidth_product=time_bandwidth_product,
    #                center=center, delay=delay, apodization=apodization,
    #                frequency_offset=frequency_offset, phase_offset=phase_offset, name=name)


class HardRFPulse(RFPulse):
    """Defines a constant (hard) RF pulse on a time grid with step length defined by system_specs. """
    # pylint: disable=R0913, R0914
    def __init__(self,
                 system_specs: SystemSpec,
                 flip_angle: Quantity = Quantity(np.pi, "rad"),
                 duration: Quantity = Quantity(1., "ms"),
                 delay: Quantity = Quantity(0., "ms"),
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "hard_rf"):
        """ Defines a constant (hard) RF pulse on a time grid with step length defined by system_specs.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the RF Pulse. For negative
                            Values the flip-angle is stored as positive absolute plus a phase offset
                            of 180°
        :param duration: Quantity[Time] Total duration of the pulse
        :param delay:
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """

        if flip_angle < Quantity(0, "rad"):
            phase_offset += Quantity(np.pi, "rad")
            flip_angle = -flip_angle

        raster_time = system_specs.rf_raster_time.to("ms")

        # If duration is too short, we can not create a pulse due to raster time
        if duration<2*system_specs.rf_raster_time:
            duration = 2*system_specs.rf_raster_time


        # estimate number of steps at the plateau (if any)
        n_steps = np.around((duration.m_as("ms")-2*system_specs.rf_raster_time.m_as("ms")) / raster_time.m_as("ms"))

        # estimate amplitude
        amplitude = (flip_angle / system_specs.gamma_rad / (raster_time * (n_steps + 1))).to('mT')

        # First case, we are below max B1 and have triangular pulse
        if n_steps<1 and amplitude<=system_specs.rf_peak_power:
            time_points = Quantity(np.array([0,1,2]) * raster_time.m_as("ms"), "ms")
            amplitude = amplitude*np.array([0,1,0])
        # Second case, still below max B1 but now have trapezoidal pulse
        elif amplitude<=system_specs.rf_peak_power:
            time_points = Quantity(np.array([0,1,n_steps+1,n_steps+2]) * raster_time.m_as("ms"), "ms")
            amplitude = amplitude * np.array([0, 1, 1, 0])
        # Third case, need to recalculate duration at max B1
        else:
            n_steps = np.ceil((flip_angle/system_specs.gamma_rad/raster_time/system_specs.rf_peak_power-1).m_as(""))
            time_points = Quantity(np.array([0, 1, n_steps + 1, n_steps + 2]) * raster_time.m_as("ms"), "ms")
            amplitude = (flip_angle / system_specs.gamma_rad / (raster_time * (n_steps + 1))).to('mT') * np.array([0, 1, 1, 0])

        super().__init__(system_specs=system_specs, name=name,
                         time=time_points + delay, rf_waveform=amplitude,
                         frequency_offset=frequency_offset, phase_offset=phase_offset,
                         rf_events=(duration/2 + delay, flip_angle),
                         bandwidth=0.5/duration, snap_to_raster=False)


class ArbitraryRFPulse(RFPulse):
    """ Wrapper for arbitrary rf shapes, to adhere to building block concept. 
    The gridding is assumed to be on raster time and **not** shifted by half
    a raster time. This shift (useful for simulations) can be incorporated when
    calling the gridding function of the sequence.

    The waveform is assumed to start and end with values of 0 uT. If the given waveform does not
    adhere to that definition, the arrays are padded.

    The rf-center (time-point of effective excitation) is estimated from pulse maximum.

    If not specified, the bandwidth of the given waveform is estimated by using the full width
    at half maximum of the power-spectrum.

      .. warning::

        For very long pulses, the estimation of bandwidth might not be reasonable anymore, due to
        relaxation.


    :param system_specs:
    :param name:
    :param time_points: Shape (#steps)
    :param waveform: Shape (#steps) in uT as real-valued array
    :param bandwidth: in Hz, if not specified, the pulse bandwidth is estimated
    :param frequency_offset:
    :param phase_offset:
    :param snap_to_raster:
    """
    def __init__(self, system_specs: SystemSpec, name: str,
                 time_points: Quantity,
                 waveform: Quantity,
                 delay: Quantity = Quantity(0., "ms"),
                 bandwidth: Quantity = None,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 snap_to_raster: bool = False):
        """ 
        :param system_specs:
        :param name:
        :param time_points: Shape (#steps)
        :param waveform: Shape (#steps) in uT as complex array
        :param bandwidth: If not specified, the bandwidth is estimated from the spectrum as
                            full-width-half-maximum.
        :param frequency_offset:
        :param phase_offset:
        :param snap_to_raster:
        """

        if not np.isclose(waveform[0].m_as("uT"), 0., atol=1e-3):
            time_points = np.concatenate([[time_points[0] - system_specs.rf_raster_time],
                                           time_points], axis=0)
            waveform = np.concatenate([[Quantity(0., "uT")], waveform], axis=0)

        if not np.isclose(waveform[-1].m_as("uT"), 0., atol=1e-3):
            time_points = np.concatenate([time_points,
                                          [time_points[-1] + system_specs.rf_raster_time]], axis=0)
            waveform = np.concatenate([waveform, [Quantity(0., "uT")]], axis=0)

        center, center_index = self._calculate_rf_center(time=time_points.to("ms"),
                                                         rf_waveform=waveform)
        flip_angle = self._calculate_flipangle(time=time_points, rf_waveform=waveform,
                                               gamma_rad=system_specs.gamma_rad)

        ## This is a weird case that can occur on loading other format definitions
        if np.allclose(waveform.m_as("uT"), 0., atol=1e-3):
            bandwidth = Quantity(0, "Hz")

        if bandwidth is None:
            _, _, bandwidth = self._calculate_bandwidth(time=time_points, rf_waveform=waveform,
                                                        cut_off_percent=0.5,
                                                        min_frequency_resolution=Quantity(10, "Hz"))

        super().__init__(system_specs, name, frequency_offset=frequency_offset,
                         time=time_points.to("ms") + delay, rf_waveform=waveform.to("mT"),
                         phase_offset=phase_offset, bandwidth=bandwidth,
                         rf_events=(time_points[center_index] + delay, flip_angle.to("rad")),
                         snap_to_raster=snap_to_raster)

    @staticmethod
    def _calculate_flipangle(time: Quantity, rf_waveform: Quantity, gamma_rad: Quantity) \
            -> Quantity:
        """Numerical integration of the rf-waveform to obtain the flip-angle

        :param time: (#points, )
        :param rf_waveform: (#points, )
        :param gamma_rad: gyromagnetic ratio in units of radian
        :return: Quantity
        """
        flip_angle = gamma_rad * Quantity(np.trapz(rf_waveform.real.m_as("mT"), time.m_as("ms")),
                                          "mT ms")
        return flip_angle

    @staticmethod
    def _calculate_bandwidth(time: Quantity, rf_waveform: Quantity, cut_off_percent: float,
                             min_frequency_resolution : Quantity) -> \
            Tuple[Quantity, Quantity, Quantity]:
        """ Calculates the RF-bandwidth for the given waveform as the spectral width at
        cut-off-percent.

        :param time: Quantity[Time] (#points,  ) Time centered around the RF-center
        :param rf_waveform: Quantity[Tesla]  (#points, )
        :param cut_off_percent:
        :param min_frequency_resolution: Minimal frequency target frequency resolution for spectrum
        :return: (frequency_grid, power_spectrum, bandwidth)
        """

        if np.abs(time[-1] - time[0]) > Quantity(20, "ms"):
            warn(f"RF.calculate_bandwidth: Long pulses > 20ms might not be accurately covered "
                 f"using the bandwidth estimation method for arbitrary RF pulses.")

        resample_dt = Quantity(1, "us")
        duration = (time[-1] - time[0]).to("us")
        n_grid_points = np.round((duration / resample_dt).m_as("dimensionless")).astype(int)

        # Padding the resampled temporal grid is done to achieve acceptable frequency resolution
        # for bandwidth calculation
        padding_factor = (1 / min_frequency_resolution / duration / 2).m_as("dimensionless")

        resampled_t_grid = Quantity(np.arange(
                                        -np.floor(n_grid_points * padding_factor).astype(int),
                                        np.ceil(n_grid_points * (padding_factor + 1)).astype(int)),
                                   "dimensionless") * resample_dt
        interpolated_wf = np.interp(xp=(time - time[0]).m_as("ms"), fp=rf_waveform.m_as("uT"),
                                    x=resampled_t_grid.m_as("ms"), left=0, right=0)

        power_spectrum = np.abs(np.fft.fft(interpolated_wf))
        freq_grid = Quantity(np.fft.fftfreq(resampled_t_grid.shape[0], resample_dt.m_as("s")), "Hz")

        ## For ascending order of the frequency grid
        sort_indices = np.argsort(freq_grid)
        freq_grid  = freq_grid[sort_indices]
        power_spectrum = power_spectrum[sort_indices]

        peak = np.max(power_spectrum)

        above_threshold_indices = np.where(power_spectrum > peak * cut_off_percent)
        freq_band = freq_grid[above_threshold_indices].m_as("Hz")

        bandwidth = Quantity(freq_band[-1] - freq_band[0], "Hz")
        return freq_grid, power_spectrum, bandwidth

    @staticmethod
    def _calculate_rf_center(time: Quantity, rf_waveform: Quantity) -> Tuple[Quantity, int]:
        """Calculates the time point of effective rotation for a given rf-waveform.

        Assumptions: - Mean of Peaks of absolute defines center
                     - Index on grid by rounding to nearest neighbor

        :param time: Quantity[Time] (#points,  )
        :param rf_waveform: Quantity[Tesla]  (#points, )
        :return: (Quantity, int) time-center (not on necessarily on grid) and integer to
                    index the handed waveforms for a representation on grid
        """
        rf_max = np.max(np.abs(rf_waveform.m_as("uT")))
        peak_indices = np.where(np.abs(rf_waveform.m_as("uT")) >= rf_max * (1 - 1e-5))[0]
        time_center = np.mean([time.m_as("ms")[i] for i in peak_indices])
        center_index = np.round(np.mean(peak_indices)).astype(int)
        return Quantity(time_center, "ms"), center_index
