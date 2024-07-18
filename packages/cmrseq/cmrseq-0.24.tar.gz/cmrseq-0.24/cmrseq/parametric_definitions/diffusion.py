""" This module contains functions defining compositions of building blocks commonly used in
diffusion MRI """
__all__ = ["bipolar", "m012", "shortest_m012"]

from typing import Union, List

import numpy as np
from pint import Quantity
import scipy.optimize

import cmrseq
from cmrseq import bausteine, Sequence, SystemSpec


# pylint: disable=W1401, R0913, C0103
def bipolar(system_specs: SystemSpec,
            dt: Quantity,
            Dt: Quantity,
            amplitude: Quantity,
            direction: np.ndarray,
            start_time: Quantity = Quantity(0., "ms"),
            rise_time: Quantity = None,
            flip_decoding: bool = False) -> Sequence:
    """ Defines a bipolar M0-compensated gradient waveform:

    .. code-block:: python

        .                  |-dt-|               |-dt-|                  .
        .                   _____                                       .
        .                  /     \                                      .
        .        _________/       \___________         _____            .
        .        |-delay-|        |----Dt----|\       /                 .
        .                                      \_____/                  .
        .                 |-|   |-|          |-|     |-|                .
        .                          rise_time                            .

    :param system_specs:
    :param dt: Quantity - flat duration of lobes
    :param Dt: Quantity - flat duration between lobes
    :param amplitude: Quantity - amplitude of lobes
    :param direction: (3, ) direction of gradient axis (is normalized internally)
    :param start_time: time offset before first lobe (to begin of rise)
    :param rise_time: time of rise/fall, if not provide, system default is used
    :param flip_decoding: In case of spin-echo sequences, the decoding lobes need
            to be inverted. If this argument is set to True the inversion is done
            internally.
    :return: sequence object

    """

    normed_direction = direction / np.linalg.norm(direction)
    if rise_time is None:
        rise_time = system_specs.get_shortest_rise_time(amplitude)

    lobe_1 = bausteine.TrapezoidalGradient(system_specs=system_specs, name="diffusion_encode",
                                           orientation=normed_direction, amplitude=amplitude,
                                           flat_duration=dt, delay=start_time, rise_time=rise_time)
    lobe_2 = bausteine.TrapezoidalGradient(system_specs=system_specs, name="diffusion_decode",
                                           orientation=-normed_direction,
                                           amplitude=amplitude, flat_duration=dt,
                                           delay=start_time+2*rise_time+dt+Dt, rise_time=rise_time)
    seq = Sequence([lobe_1, lobe_2], system_specs=system_specs)

    if flip_decoding:
        lobe_2.scale_gradients(-1)
    return seq


# pylint: disable=R0914
def m012(system_specs: SystemSpec,
         zeta: Quantity, lambda_: Quantity,
         direction: np.ndarray,
         amplitude: Quantity = None, bvalue: Quantity = None,
         start_time: Quantity = Quantity(0., "ms"),
         flip_decoding: bool = False) -> Union[Sequence, List[Sequence]]:
    """ Defines a M012-compensated diffusion gradient waveform according to Stoeck et al.
    (DOI: 10.1002/mrm.25784):

     .. code-block:: python

        .           lambda               Delta               lambda           .
        .           _____                       _________                     .
        .          /     \                     /         \                    .
        .       __/       \             ______/           \         _____     .
        .                  \           /                   \       /          .
        .                   \_________/                     \_____/           .
        .         |-|          Lambda             Lambda                      .
        .         zeta                                                        .


    .. math::

        \Lambda =& 2\lambda + \zeta  \\\\
        \Delta  =& 2\zeta + \lambda \\\\
        G_{max} = s_{max} \zeta

    .. Dropdown:: Example Plots
        :animate: fade-in-slide-down
        :icon: graph
        :color: secondary

        .. image:: ../_static/api/m012bval_calculation.svg

    :raises: - ValueError if either both or none of amplitude/bvalue is specified
             - ValueError if specified b-value is not feasible for given system limits
             - ValueError if directions is not broad-castable or matching the length
               of amplitude/bvalue

    :param system_specs:
    :param lambda_: Flat duration of first trapezoidal
    :param zeta: Rise time of ramps with maximum slew-rate
    :param direction: (3, ) or (n, 3) direction of gradient axis (is normalized internally)
    :param amplitude: Amplitude in mT/m  Either scalar or (n, ) long.
    :param bvalue: B-Value in (s/mm^2). Either scalar or (n, ) long.
    :param start_time: time offset before first lobe (to begin of rise)
    :param flip_decoding: In case of spin-echo sequences, the decoding lobes need
            to be inverted. If this argument is set to True the inversion is done
            internally.
    :return: Sequence or list of Sequence containing the waveform per specified bvalues
    """

    if (amplitude is None and bvalue is None) or (amplitude is not None and bvalue is not None):
        raise ValueError("Exactly one argument of amplitude/b-value must be specified. You "
                         f"specified neither or both!\n\t- amp:{amplitude}\n\t-bvalue:{bvalue}")

    if bvalue is not None:
        slew_ = Quantity(1., "mT/m") / zeta
        ref_bval = _m012_bval(zeta, lambda_, slew_, system_specs.gamma_rad, return_cumulative=False)
        factor = np.sqrt(bvalue.m_as("s/mm^2") / ref_bval.m_as("s/mm^2"))
        amplitude = Quantity(1., "mT/m") * factor

    amplitude = Quantity(np.array(amplitude.m).reshape(-1), amplitude.units)

    if len(direction.shape) == 1:
        direction = direction.reshape(1, 3)
    if len(direction) == 1 and len(amplitude) > 0:
        direction = np.repeat(direction, len(amplitude), 0)
    if len(direction) != len(amplitude):
        raise ValueError("Not broadcast dimensions of specified directions and amplitudes:"
                         f"\n\t\t amp: {amplitude.shape}  |  directions: {direction.shape}")

    flat1 = lambda_
    flat2 = 2*lambda_ + zeta
    flat3 = 2*zeta + lambda_
    rise = zeta
    delays = [0., 2*rise+flat1, 4*rise+flat1+flat2+flat3, 6*rise+flat1+flat2+flat3++flat2]

    seqlist = []
    for amp, direc in zip(amplitude, direction):
        lobe_kwargs = []
        for flat, delay in zip([flat1, flat2, flat2, flat1], delays):
            lobe_kwargs.append(dict(amplitude=amp, flat_duration=flat, rise_time=rise,
                                    delay=delay+start_time))
        normed_direction = direc / np.linalg.norm(direc)

        default_dir = np.array([1., 0., 0.])
        lobe_1 = bausteine.TrapezoidalGradient(system_specs=system_specs, name="diffusion_encode",
                                               orientation=default_dir, **lobe_kwargs[0])
        lobe_2 = bausteine.TrapezoidalGradient(system_specs=system_specs, name="diffusion_encode",
                                               orientation=-default_dir, **lobe_kwargs[1])
        lobe_3 = bausteine.TrapezoidalGradient(system_specs=system_specs, name="diffusion_decode",
                                               orientation=default_dir, **lobe_kwargs[2])
        lobe_4 = bausteine.TrapezoidalGradient(system_specs=system_specs, name="diffusion_decode",
                                               orientation=-default_dir, **lobe_kwargs[3])
        seq = Sequence([lobe_1, lobe_2, lobe_3, lobe_4], system_specs=system_specs)

        for lobe in [lobe_1, lobe_2, lobe_3, lobe_4]:
            lobe.gradients = (lobe.gradients[0],
                              np.einsum('n, i -> in', lobe.gradients[1][0], normed_direction))

        if flip_decoding:
            lobe_3.scale_gradients(-1)
            lobe_4.scale_gradients(-1)
        seqlist.append(seq)

    if len(amplitude) == 1:
        return seq
    else:
        return seqlist


# pylint: disable=R0914
def shortest_m012(system_specs: SystemSpec,
                  direction: np.ndarray, bvalues: Quantity,
                  start_time: Quantity = Quantity(0., "ms"),
                  flip_decoding: bool = False) -> cmrseq.Sequence:
    """ Finds the shortest possible second order motion compensated diffusion weighting
    gradient waveform according to Stoeck et al. (DOI: 10.1002/mrm.25784).

    Compare cmrseq.seqdefs.diffusion.m012 for more information

    :param system_specs:
    :param direction:
    :param bvalues:
    :param start_time:
    :param flip_decoding:
    :return:
    """
    max_b = np.max(bvalues.to("s/mm^2"))
    zeta, lambda_, actual_gmax, actual_smax, actual_b = _optimize_m012(system_specs, max_b)
    return m012(system_specs, zeta=zeta, lambda_=lambda_, direction=direction,
                bvalue=bvalues, start_time=start_time, flip_decoding=flip_decoding)


def _m012_bval(zeta: Quantity, lambda_: Quantity, slew: Quantity, gamma: Quantity,
               return_cumulative: bool = False) -> Quantity:
    """ Evaluates the b-value of a m012 diffusion weighting gradient waveform by using
    analytically obtained integration formulas.

    .. dropdown:: Additional explanation

        The following plot shows how the analytical piecewise integration can be performed.
        The gray, vertical dashed lines are the gradient (gray curve) breakpoints which serve
        as integration interval borders. The orange, horizontal dashed line mark the offset
        values (c0,c1,c2)(c0, c1, c2)(c0,c1,c2) of the function q2(t)q^2(t)q2(t) (orange curve)
        at the interval borders. There are 5 distinct areas to be calculated, which when summed up
        result into the b-value. Red crosses are the cumulative sum of the interval areas calculated
        anaylitcally and the blue curve is the numerically integrated b-value.

        .. image:: ../../_static/api/m012bval_calculation.svg

    :param zeta: rise-time of all gradients in ms
    :param lambda_: flat duration of the first (shorter) trapezoidal
    :param slew: slew rate of gradients used for the waveform
    :param gamma: gyromagnetic ratio of diffusion encoded media in (rad/mT/ms)
    :param return_cumulative: If True, all bvalues at gradient breakpoints are returned
    :return: b-value either (1, ) or (13, )
    """

    n = lambda_ / zeta
    if return_cumulative:
        a0 = zeta ** 5 / 20 * slew ** 2 * gamma ** 2
        a1 = gamma ** 2 * zeta ** 5 * slew ** 2 * (n ** 3 / 3 + n / 4)
        a2 = gamma ** 2 * zeta ** 5 * slew ** 2 * ((n + 1) ** 2 - 1 / 20)
        a3 = gamma ** 2 * zeta ** 5 * slew ** 2 * 2 / 3 * (n + 1 / 2) ** 3
        ad = gamma ** 2 * zeta ** 5 * slew ** 2 * (n + 1) ** 2 * (n + 2)

        bvals = np.stack([a0, a1, a2, a2, a3, a2, ad, a2, a3, a2, a2, a1, a0]).reshape(-1)
        bvals = Quantity(np.cumsum(bvals.m_as("s/mm**2")), "s/mm**2")
    else:

        bvals = (gamma ** 2 * slew ** 2 * (
                    3 * lambda_ ** 3 * zeta ** 2 + 12 * lambda_ ** 2 * zeta ** 3
                    + 37 / 2 * lambda_ * zeta ** 4 + 239 / 30 * zeta ** 5)).to("s/mm**2")
    return bvals.to("s/mm**2")


def _optimize_m012(system_specs: SystemSpec, max_bval: Quantity) \
        -> (Quantity, Quantity, Quantity, Quantity):
    """Finds the shortest possible M012 diffusion wavefrom reaching the required
    b-value according to  definition in Stoeck et. al (DOI: 10.1002/mrm.25784) for
    the given system specifications.

    .. note::
        :caption: Assumption in optmization

        - Maximal gradient strength is used
        - Maximal slew rate is used  --> g_max = zeta * s_max

    :param system_specs: System specifications object containing the system limits
    :param max_bval: target b-value of dimension (time/length**2)
    :return: - zeta: rise time of the trapezoidal
             - lambda: flat duration of fist trapezoidal
             - gmax: actually used max-gradient
             - slew: actually used slew-rate
             - b_actual: actual resulting b-value
    """
    # Strip units consistently for scipy optimize call
    gamma = system_specs.gamma_rad.m_as("1/ms/mT")
    max_slew = system_specs.max_slew.m_as("mT/m/ms") * 0.97
    gmax = system_specs.max_grad.m_as("mT/m") * 0.97
    zeta = system_specs.time_to_raster(Quantity(gmax / max_slew, "ms"))
    zeta = zeta.m

    def _optim(x): # Minimize total duration
        return 12 * zeta + 7 * x[0]

    def _constraint(x): # Match the target b-value
        return gamma ** 2 * max_slew ** 2 * (
                    3 * x[0] ** 3 * zeta ** 2 + 12 * x[0] ** 2 * zeta ** 3 +
                    37 / 2 * x[0] * zeta ** 4 + 239 / 30 * zeta ** 5) - max_bval.m_as("ms/m**2")

    inital_guess = np.array((5,))
    res = scipy.optimize.minimize(fun=_optim, x0=inital_guess,
                                  constraints={"type": "eq", "fun": _constraint})

    # Adjustment due to raster time rounding
    lraster = system_specs.time_to_raster(Quantity(res.x[0], "ms"), "grad")
    while _m012_bval(Quantity(zeta, "ms"), lraster,
                    Quantity(max_slew, "mT/m/ms"), gamma=system_specs.gamma_rad) > max_bval:
        lraster -= system_specs.grad_raster_time

    b_actual = _m012_bval(Quantity(zeta, "ms"), lraster,
                          Quantity(max_slew, "mT/m/ms"),
                          gamma=system_specs.gamma_rad)

    return (Quantity(zeta, "ms"), Quantity(lraster, "ms"),
            Quantity(gmax, "mT/m"), Quantity(max_slew, "mT/m/ms"), b_actual)

