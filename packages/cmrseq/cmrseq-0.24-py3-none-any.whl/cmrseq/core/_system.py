""" This Module contains the implementation of the core functionality SystemSpec """

__all__ = ["SystemSpec"]

from typing import Tuple
from copy import deepcopy

from pint import Quantity
import numpy as np


# pylint: disable=R0902, R0913, C0103
class SystemSpec:
    """Bundles the system limit specifications, meant to be passed as object for creating
    sequences and building blocks.

    In addition to store all relevant system specifications this class implements the methods
    to calculate quantities that depend on these limits (e.g. get_shortest_rise_time).

    :param gamma: Gyromagnetic Ratio of the target nucleus with dimensions equivalent to[MHz / T]
    :param grad_raster_time: Raster time for gradient definitions with dimension [Time]
    :param max_grad: Maximal allowed gradient strength for combined gradient channels in dimension
                     equivalent to [mT/m]
    :param max_slew: Maximal allow gradient slew-rate for combined gradient channels in dimensions
                     equivalent to [mT/m/ms]
    :param rf_peak_power: Maximal allowed peak rf power defined as B1 field strength with dimensions
                          equivalent to [uT]
    :param rf_raster_time: Raster time for radio-frequency waveform definitions with dimension [Time]
    :param rf_dead_time: Minimum time between consecutive RF-pulses, due to switching delays in the
                           transmit chain.
    :param rf_ringdown_time: Defines the minimum delay between a RF-pulse and and acquisition block.
                             Corresponds to the time scale of self induced currents in the transmit
                             coil, which could result in receive chain damages and sampling
                             distortion.
    :param rf_lead_time: Defines the minimum delay between an acquisition block and a subsequent
                         RF-pulse. This corresponds to the delay caused by switching from receive to
                         transmit.
    :param adc_raster_time: Raster time for signal sampling  definitions with dimension [Time]
    :param adc_dead_time: Minimum time between consecutive Sampling (ADC) blocks, due to switching
                           delays in the receive chain.
    :param b0: Static field strength in dimension of [T]
    :param enable_simulatenous_trasmit_receive: System flag for sequence validation. If true,
                            RF and ADC blocks are allowed to be occur simultaneously (ignoring)
                            rf_ringdown_time in validation.
    """
    #: Quantity[mT/m]: Maximum gradient amplitude
    max_grad: Quantity
    #: Quantity[mT/m/ms]: Maximum gradient slew rate
    max_slew: Quantity
    #: Quantity[uT]: Peak power for B1 fields (in micro tesla)
    rf_peak_power: Quantity
    #: Quantity[ms]:Minimum time between consecutive RF-pulses, due to switching delays
    #: in the transmit chain.
    rf_dead_time: Quantity
    #: Quantity[ms]: Defines the minimum delay between a RF-pulse and acquisition block.
    rf_ringdown_time: Quantity
    #: Quantity[ms]: Defines the minimum delay between an acquisition block and a subsequent RF-pulse.
    rf_lead_time: Quantity
    #: Quantity[ms]: Minimum time between consecutive Sampling (ADC) blocks, due to switching
    #: delays in the receiver-chain.
    adc_dead_time: Quantity
    #: Quantity[ms]: delta t of radio-frequency grid, defaults to 10us
    rf_raster_time: Quantity
    #: Quantity[ms]: delta t of gradient grid, defaults to 10us
    grad_raster_time: Quantity
    #: Quantity[ms]: delta t of adc grid, defaults to 10us
    adc_raster_time: Quantity
    #: Quantity[MHz/T]: Gyromagnetic ratio for nucleus the system is working on
    gamma: Quantity
    #: Quantity[rad/s/T]: Gyromagnetic ratio for nucleus the system is working on in rad/s
    gamma_rad: Quantity
    #: System flag for sequence validation. If true, RF and ADC blocks are allowed to occur.
    #: simultaneously (ignoring)
    enable_simulatenous_trasmit_receive: bool

    def __init__(self,
                 gamma: Quantity = Quantity(42.576, "MHz/T"),
                 grad_raster_time: Quantity = Quantity(1e-2, "ms"),
                 max_grad: Quantity = Quantity(40, "mT/m"),
                 max_slew: Quantity = Quantity(120, "mT/m/ms"),
                 rf_peak_power: Quantity = Quantity(30, "uT"),
                 rf_raster_time: Quantity = Quantity(1e-2, "ms"),
                 rf_dead_time: Quantity = Quantity(0., "ms"),
                 rf_ringdown_time: Quantity = Quantity(0., "ms"),
                 rf_lead_time: Quantity = Quantity(0., "ms"),
                 adc_raster_time: Quantity = Quantity(1e-2, "ms"),
                 adc_dead_time: Quantity = Quantity(0., "ms"),
                 b0: Quantity = Quantity(1.5, "T"),
                 enable_simulatenous_trasmit_receive: bool = False):

        if max_grad.to_base_units().units == Quantity(1., "1/m/s").units:
            max_grad = (max_grad * gamma).to("mT/m")

        if max_slew.to_base_units().units == Quantity(1., "1/m/s**2").units:
            max_slew = (max_slew * gamma).to("mT/m/ms")

        self.rf_peak_power = rf_peak_power.to("uT")
        self.rf_dead_time = rf_dead_time.to("ms")
        self.rf_ringdown_time = rf_ringdown_time.to("ms")
        self.rf_lead_time = rf_lead_time.to("ms")
        self.adc_dead_time = adc_dead_time.to("ms")
        self.rf_raster_time = rf_raster_time.to("ms")
        self.grad_raster_time = grad_raster_time.to("ms")
        self.adc_raster_time = adc_raster_time.to("ms")
        self.gamma = gamma.to("MHz/T")
        self.gamma_rad = gamma.to("rad/T/s") * 2 * np.pi

        self.max_grad = max_grad
        self.max_slew = max_slew
        
        self.b0 = b0.to("T")
        self.enable_simulatenous_trasmit_receive = enable_simulatenous_trasmit_receive
        
    def __str__(self):
        return_string = "System limits:"
        return_string += "\n\tmax_grad: " + str(self.max_grad)
        return_string += "\n\tmax_slew: " + str(self.max_slew)
        return_string += "\n\trf_dead_time: " + str(self.rf_dead_time)
        return_string += "\n\trf_ringdown_time: " + str(self.rf_ringdown_time)
        return_string += "\n\trf_lead_time: " + str(self.rf_lead_time)
        return_string += "\n\tadc_dead_time: " + str(self.adc_dead_time)
        return_string += "\n\trf_raster_time: " + str(self.rf_raster_time)
        return_string += "\n\tgrad_raster_time: " + str(self.grad_raster_time)
        return_string += "\n\tadc_raster_time: " + str(self.adc_raster_time)
        return_string += "\n\tminmax_risetime:" + str(self.minmax_risetime)
        return_string += "\n\tgamma: " + str(self.gamma)
        return return_string

    def __repr__(self):
        return self.__str__()

    @property
    def minmax_risetime(self):
        return self.time_to_raster((self.max_grad / self.max_slew).to("ms"), raster="grad")
        
    def get_shortest_rise_time(self, delta_amplitude: Quantity) -> Quantity:
        """ Calculates the shortest ramp duration for the specified amplitude difference.

        :param delta_amplitude: Quantity[mT/m]
        :return: delta t - Quantity[ms] which is guaranteed to be a multiple of grad_raster_time
        """
        delta_amplitude = np.abs(delta_amplitude)
        shortest_ramp_dur = np.around((delta_amplitude / self.max_slew).to("ms"), decimals=6)
        return self.time_to_raster(shortest_ramp_dur, raster="grad")

    def get_shortest_gradient(self, area: Quantity) -> Tuple[Quantity, Quantity, Quantity]:
        """ Calculates the shortest gradient of a given area, obeying system limits

        :param area: Quantity[mT/m*s]
        :return: Tuple(amplitude, rise time, flat time)
        """

        if not area.check("T/m*s"):
            raise ValueError("Unit of gradient area incorrect, must be mT/m*s or equivalent")

        fastest_ramp = self.get_shortest_rise_time(self.max_grad)

        if area == 0:
            return Quantity(0, 'mT/m'), Quantity(0, 'ms'), Quantity(0, 'ms')

        if fastest_ramp*self.max_grad > area:
            # Triangular
            ramp_time = np.sqrt(area / self.max_slew)
            ramp_time = self.time_to_raster(ramp_time, raster="grad")
            amplitude = area / ramp_time
            flat_time = Quantity(0., 'ms')
        else:
            # Trapezoid
            ramp_time = fastest_ramp
            flat_time = area / self.max_grad - fastest_ramp
            flat_time = self.time_to_raster(flat_time, raster="grad")
            amplitude = area / (fastest_ramp + flat_time)
        return amplitude, ramp_time, flat_time

    def get_fastest_kspace_traverse(self, k_space_vector: Quantity) -> Tuple[Quantity, Quantity, Quantity]:
        """ Computes the shortest gradient, resulting in a k-space traverse along the
        specified vector. 

        .. note:

            This assumes the isotropic gradient limits, hence the norm of the gradient 
            vector adhering to the system limits.
        
        :param k_space_vector: (3, ) for X, Y, Z
        :return: Amplitude, ramp- and flat-duration of the resulting gradient pulse
        """
        from scipy.optimize import minimize
        max_dir = np.argmax(np.abs(k_space_vector.m_as("1/m")))
        optim_area = np.abs((k_space_vector[max_dir] / self.gamma).m_as("mT/m*ms"))
        combined_area = (Quantity(np.linalg.norm(k_space_vector.m_as("1/m")), "1/m") / self.gamma).m_as("mT/m*ms")

        s = self.max_slew.m_as("mT/m/ms")
        def _dur(x):
            return (x[0] / s + x[1])

        def _given_area(x):
            return (x[0]**2 / s + x[1] * x[0]) - optim_area

        def _combined_gradients(x):
            return - combined_area / (x[0] / s + x[1]) + self.max_grad.m_as("mT/m") 

        cons = ({'type': 'eq', 'fun': _given_area},
                {'type': 'ineq', 'fun': _combined_gradients},
                {'type': 'ineq', 'fun': lambda x: x[0]},
                {'type': 'ineq', 'fun': lambda x: (-x[0] / s + s)},
                {'type': 'ineq', 'fun': lambda x: x[1]},
               )

        initial_guess = np.array([1, 0.01])
        res = minimize(fun=_dur, x0=initial_guess, constraints=cons)
        rise_time = self.time_to_raster(Quantity(res.x[0] / s, "ms"))
        flat_dur = self.time_to_raster(Quantity(res.x[1], "ms"))
        amplitude = (k_space_vector / self.gamma).m_as("mT/m*ms") / (2 * rise_time + flat_dur)
        return amplitude, rise_time, flat_dur

        # total_kspace_traverse = Quantity(np.linalg.norm(k_space_vector.m_as("1/m")), "1/m")
        # combined_gradient_area = total_kspace_traverse / self.gamma.to("1/mT/ms")
        # return self.get_shortest_gradient(combined_gradient_area)

    def time_to_raster(self, time: Quantity, raster: str = "grad") -> Quantity:
        """ Calculates the time projected onto the either gradient or rf raster.

        :param time: Quantity[s]
        :param raster: from [grad, rd]
        :return: Quantity[ms]
        """
        if raster.lower() == "grad":
            raster = self.grad_raster_time.to("ms")
        elif raster.lower() == "rf":
            raster = self.rf_raster_time.to("ms")
        elif raster.lower() == "adc":
            raster = self.adc_raster_time.to("ms")
        else:
            raise ValueError(f"Invalid raster choice: {raster} not in [grad, rf, adc]")
        time = np.around(time.m_as("ms"), decimals=8)
        time_ndt = np.ceil(np.around(time / raster.m, decimals=8))
        time_ndt = time_ndt * raster
        return time_ndt

    def modified_copy(self, **kwargs) -> 'SystemSpec':
        """
        :param kwargs: keyword argument according to instantiation, with the updated
                        value
        :return: SystemSpecs
        """
        tmp = deepcopy(self)
        for  k, v in kwargs.items():
            tmp.__setattr__(k, v)
        return tmp

