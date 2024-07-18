""" This modules contains compositions of building blocks commonly used for in defining actual
signal acqusition and spatial encoding
"""
__all__ = ["single_shot_epi"]

from typing import Tuple, Union
from copy import deepcopy

from pint import Quantity
import numpy as np

import cmrseq


def single_shot_epi(system_specs: cmrseq.SystemSpec, field_of_view: Quantity, 
                    matrix_size: np.ndarray,  blip_direction: str = "up",
                    partial_fourier_lines: int = 0, slope_sampling: bool = False,
                    water_fat_shift: Union[str, float] = "minimum", 
                    max_total_duration: Quantity = None, delay: Quantity = Quantity(0, "ms")) -> cmrseq.Sequence:
    """Defines a single shot EPI readout sequence according to the image configuration.
    Assumes the prephaser to be as short as possible. 

    :raises: - ValueError if shortest possible duration is longer than max_total_duration
             - ValueError if water-fat-shift=="maximum" but max_total_duration==None

    .. code-block:: python

        .                                                                     .
        .           ADC:     |||  |||  |||  |||  |||  |||                     .
        .                         ___       ___       ___                     .
        .           RO:          /   \     /   \     /   \                    .
        .                   \___/     \___/     \___/     \___/               .
        .                                                                     .
        .           PE:          ____/\___/\___/\___/\___/\_______            .
        .                   \___/                                             .
        .                                  |  |                               .
        .                                adc_duration                         .


    .. Dropdown:: Example with Slope sampling
        :animate: fade-in-slide-down
        :icon: graph
        :color: secondary

        .. image:: ../_static/api/EPI_slope_sampling.png

    .. Dropdown:: Example with Flat top sampling
        :animate: fade-in-slide-down
        :icon: graph
        :color: secondary

        .. image:: ../_static/api/bipolar_venc.svg


    :param system_specs: cmrseq.SystemSpecs
    :param field_of_view: Quantity[Length] - Defines the spatial extend in readout and
                            phase-encoding direction
    :param matrix_size: np.ndarray (2, ) - number of samples in readout/phase-encoding direction
                        if partial fourier is enabled the lines are subtracted from this parameter
    :param blip_direction: (str) from ['up', 'down'] specifies the direction of phase encoding steps
    :param partial_fourier_lines: (int) number of lines to be skipped before k-space center
    :param slope_sampling: if True the unbound method (epi_ramp_sampling) is used, otherwise the 
                            unbound method (epi_flat_sampling) is used. 
    :param max_total_duration: Quantity needs to be specified if water-fat-shift is set to maximum.
    :param water_fat_shift: one of ['minimum', 'maximum', #pixels(float)]. Determines
                            the echo-spacing therefore the duration of all according to the formula
                            :math:`P/(C * (N+1)) = T` with (P)ixels, (C)hemical shift
                            frequency, (N)umber of k-space lines and (T) Echo spacing
    :param delay: Time gap added before the sequence
    """
    # Calculate k-space definitions
    k_space_kwargs = _epi_fov_definition(field_of_view, matrix_size,
                                         blip_direction, partial_fourier_lines)
    
    # Create building blocks to assemble epi train
    if slope_sampling:
        _ = _epi_ramp_sampling(system_specs=system_specs, water_fat_shift=water_fat_shift, 
                               max_total_duration=max_total_duration, **k_space_kwargs)
        ro_prephaser, pe_prephaser, readout_gradient, blip_gradient, adc_block = _
    else:
        _ = _epi_flat_sampling(system_specs=system_specs, water_fat_shift=water_fat_shift, 
                               max_total_duration=max_total_duration, **k_space_kwargs)
        ro_prephaser, pe_prephaser, readout_gradient, blip_gradient, adc_block = _

    # Assemble single shot epi
    block_list = [ro_prephaser, pe_prephaser]
    for line_idx in range(matrix_size[1]-partial_fourier_lines):
        ro_block = deepcopy(readout_gradient)
        ro_block.shift(ro_prephaser.duration + line_idx * readout_gradient.duration)
        ro_block.scale_gradients((-1) ** line_idx)
        
        adc = deepcopy(adc_block)
        adc.shift(ro_prephaser.duration + line_idx * readout_gradient.duration)
        
        blip_block = deepcopy(blip_gradient)
        blip_block.shift(ro_prephaser.duration + (line_idx + 1) * readout_gradient.duration)
        block_list.extend([ro_block, adc, blip_block])
       
    seq = cmrseq.Sequence(block_list[:-1], system_specs)
    if delay is not None:
        seq.shift_in_time(delay)
    return seq         


def _epi_ramp_sampling(system_specs: cmrseq.SystemSpec,
                       num_samples: int,
                       k_readout: Quantity,
                       k_phase_start: Quantity,
                       k_phase_step: Quantity,
                       k_phase_lines: int,
                       max_total_duration: Quantity = None,
                       water_fat_shift: Union[str, float] = "minimum",
                       ) -> Tuple[cmrseq.bausteine.SequenceBaseBlock, ...]:
    """Defines the blocks (ro_prephaser, pe_prephaser, readout, blip, adc) used to compose epi-trains
    
    Sampling is already performed during readout ramps resulting in non-equidistant k-space
    sampling vectors. Blip time is choosen as shortest possible, and the specified k_readout is used
    to defined the interval between the two outmost k-space samples (therefore defining the highest
    theoretical resolution).

    **NOTE:** If the number of samples `num_samples` is even, the k-space center
            is found at `num_samples/2+1`.

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`
    :param k_phase_start: Quantity[1/Length] :math:`k_y` position for the first k-space line
    :param k_phase_step: Quantity[1/Length] :math:`\Delta k_y` step per blip
    :param k_phase_lines: Number of lines
    :param max_total_duration: 
    :param water_fat_shift: one of ['minimum', 'maximum', #pixels(float)]. Determines the
                            echo-spacing therefore the duration of all according to the formula
                            :math:`P/(C * (N+1)) = T` with (P)ixels, (C)hemical shift
                            frequency, (N)umber of k-space lines and (T) Echo spacing
    :return: (ro_prephaser, pe_prephaser, readout, blip, adc)
    """
   
    # Calculate Phase encoding Blip
    blip_amp, blip_rise, blip_flat = system_specs.get_shortest_gradient(np.abs(k_phase_step) /
                                                                        system_specs.gamma)
    blip_amp = np.sign(k_phase_step) * blip_amp
    blip_gradient = cmrseq.bausteine.TrapezoidalGradient(system_specs,
                                                         orientation=np.array([0., 1., 0.]),
                                                         amplitude=blip_amp,
                                                         flat_duration=blip_flat,
                                                         rise_time=blip_rise, name="blip")
    blip_gradient.shift(-blip_rise)

    # Calculate readout block overshoot to account for the blip duration.
    kro_overshoot = (blip_gradient.duration / 2) ** 2 * system_specs.max_slew * system_specs.gamma

     # Calculate prephaser gradients
    combined_kspace_traverse = np.sqrt((k_readout / 2 + kro_overshoot / 2) ** 2 + k_phase_start ** 2)    
    [_, prephaser_rise, prephaser_flat] = system_specs.get_shortest_gradient(combined_kspace_traverse / system_specs.gamma)
    prephaser_ro_area = (np.abs(k_readout) + kro_overshoot) / 2 / system_specs.gamma
    prephaser_pe_area = np.abs(k_phase_start) / system_specs.gamma
    
    pe_prephaser = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
                                      system_specs,
                                      orientation=np.array([0., 1., 0.]) * np.sign(k_phase_start),
                                      duration=prephaser_flat+prephaser_rise*2,
                                      area=prephaser_pe_area,
                                      name="pe_prephaser")
    ro_prephaser = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
                                      system_specs,
                                      orientation=np.array([-1., 0., 0.]),
                                      duration=prephaser_flat+prephaser_rise*2,
                                      area=prephaser_ro_area,
                                      name="ro_prephaser")

    kro_area = (np.abs(k_readout) + kro_overshoot) / system_specs.gamma
    _, ro_rise, ro_flat = system_specs.get_shortest_gradient(kro_area)

    ## set duration according to water-fat-shift bandwidth 
    shortest_echo_spacing = ro_flat + 2 * ro_rise
    longest_echo_spacing = _calculate_longest_echo_spacing(system_specs, max_total_duration, 
                                                           ro_prephaser.duration, k_phase_lines)
    echo_spacing = _set_echo_spacing_from_water_fat_shift(system_specs,
                                                          water_fat_shift=water_fat_shift,
                                                          n_epi_lines=k_phase_lines,
                                                          shortest_echo_spacing=shortest_echo_spacing,
                                                          longest_echo_spacing=longest_echo_spacing)
    readout_gradient = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
                                                          system_specs,
                                                          orientation=np.array([1., 0., 0.]),
                                                          duration=echo_spacing,
                                                          area=kro_area,
                                                          name="readout")
    # Instantiate ADC
    adc_duration = readout_gradient.duration - blip_gradient.duration
    adc_block = cmrseq.bausteine.SymmetricADC(system_specs, num_samples, duration=adc_duration, 
                                              delay=blip_rise, name="adc")
    
    
    return ro_prephaser, pe_prephaser, readout_gradient, blip_gradient, adc_block
   

# pylint: disable=W1401, R0913, R0914
def _epi_flat_sampling(system_specs: cmrseq.SystemSpec,
                      num_samples: int,
                      k_readout: Quantity,
                      k_phase_start: Quantity,
                      k_phase_step: Quantity,
                      k_phase_lines: int,
                      max_total_duration: Quantity = None,
                      water_fat_shift: Union[str, float] = "minimum",
                      ) -> Tuple[cmrseq.bausteine.SequenceBaseBlock, ...]:
    """Defines the blocks (ro_prephaser, pe_prephaser, readout, blip, adc) used to compose epi-trains

    Dispatch function for `epi_cartesian` that uses the k-space extend define the EPI trajectory. 
    Sampling is limited to the flat duration of the readout gradients, which can either be specified
    or if not is choosen to be shortest possible. The duration is mainly controlled by the assumption, 
    that the rise/fall-time of the readout-block occur only during the blips which is set to shortest if
    not specified.

    **NOTE:** If the number of samples `num_samples` is even, the k-space center is found at `num_samples/2+1`.

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`
    :param k_phase_start: Quantity[1/Length] :math:`k_y` position for the first k-space line
    :param k_phase_step: Quantity[1/Length] :math:`\Delta k_y` step per blip
    :param k_phase_lines: Number of lines
    :param max_total_duration: 
    :param water_fat_shift: one of ['minimum', 'maximum', #pixels(float)]. Determines the echo-spacing therefore the 
                            duration of all
                            according to the formula :math:`P/(C * (N+1)) = T` with (P)ixels, (C)hemicalf shift 
                            frequency, (N)umber of k-space lines and (T) Echo spacing
    :return: Sequence object containing RO- & PE-gradients as well as ADC events
    """

    # Calculate the readout gradients using flat-top sampling    
    ro_rise = system_specs.max_grad / system_specs.max_slew
    min_adc_duration = system_specs.time_to_raster(k_readout / system_specs.max_grad / system_specs.gamma).to("ms")
    
    shortest_echo_spacing = min_adc_duration + 2 * ro_rise
    longest_echo_spacing = _calculate_longest_echo_spacing(system_specs, max_total_duration, 
                                                          (ro_rise*2 + min_adc_duration) * 1.5, k_phase_lines)
    echo_spacing = _set_echo_spacing_from_water_fat_shift(system_specs, water_fat_shift=water_fat_shift, 
                                                          n_epi_lines=k_phase_lines,
                                                          shortest_echo_spacing=shortest_echo_spacing,
                                                          longest_echo_spacing=longest_echo_spacing)
    echo_spacing = system_specs.time_to_raster(echo_spacing, "grad")
    ## This optimization requires following assumptions:
    # - Triangular blips
    # - Rise time delta of readout and blip are the same
    # (1) $\Delta k_{PE} = \gamma G_{PE} \delta $ 
    # (2) $k_{RO_max} = \gamma G_{RO} (T_{Echo_spacing} + 2\delta)$ => replace delta using (1)
    # (3) $s_{max} = \sqrt{G_{RO}^2 + G_{PE}^2} / \delta  => solve for G_{RO}
    # => Replace G_RO in (2) using (3) hand to wolfram alpha for simplification
    # Results in the folowing polynomial:
    a = echo_spacing
    b = system_specs.max_slew
    c = (k_phase_step / system_specs.gamma)
    d = (k_readout / system_specs.gamma)
    p0 = - ((a * c) ** 2).to("(mT/m)**2 * ms**4")
    p1 = - (4 * a * c**2).to("(mT/m)**2 * ms**3")
    p2 = - (4*c**2 + d**2).to("(mT/m)**2 * ms**2")
    p3 = Quantity(0, "(mT/m)**2 * ms")
    p4 = ((a * b)**2).to("(mT/m)**2")
    p5 = - 4 *(a * b**2).to("(mT/m)**2 / ms")
    p6 = 4 * (b**2).to("(mT/m/ms)**2")
    coeffs = np.stack([p.m for p in [p0, p1, p2, p3, p4, p5, p6]])
    poly = np.polynomial.Polynomial(coef=coeffs)
    roots = poly.roots()
    acceptable_roots = roots[np.where(np.logical_and(roots.imag == 0., roots.real > 0.))].real
    acceptable_roots = Quantity(acceptable_roots, "ms")
    acceptable_roots = system_specs.time_to_raster(acceptable_roots)
    pe_grad_amps = (k_phase_step / system_specs.gamma / acceptable_roots).to("mT/m")
    ro_grad_amps = (k_readout / system_specs.gamma / (echo_spacing - 2 * acceptable_roots)).to("mT/m")
    grads_in_bounds = np.where(np.logical_and(np.sqrt(pe_grad_amps ** 2 + ro_grad_amps ** 2) <= system_specs.max_grad,
                                              echo_spacing-2*acceptable_roots >= 0 ))[0]
    if grads_in_bounds.size == 0:
        raise ValueError("No solution for triangular blips found. Decrease resolution in"
                         "PE-direction or try increasing the water-fat-shift.")
    
    shortes_root_idx = np.argmin(acceptable_roots[grads_in_bounds])
    ro_rise = acceptable_roots[grads_in_bounds][shortes_root_idx]
    ro_amp = ro_grad_amps[grads_in_bounds][shortes_root_idx]
    blip_amp = pe_grad_amps[grads_in_bounds][shortes_root_idx]

    ## End of Triangular blip optimization
    readout_gradient = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs, 
                                                            orientation=np.array([1., 0., 0.]),
                                                            flat_duration=echo_spacing-2*ro_rise,
                                                            rise_time=ro_rise,
                                                            amplitude=ro_amp, name='readout')
    adc_block = cmrseq.bausteine.SymmetricADC(system_specs, num_samples,
                                              duration=echo_spacing-2*ro_rise, delay=ro_rise)

    blip_gradient = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                         orientation=np.array([0., 1., 0.]),
                                                         flat_duration=Quantity(0, "ms"),
                                                         rise_time=ro_rise,
                                                         amplitude=blip_amp, name="blip")
    blip_gradient.shift(-ro_rise)

    # Calculate prephaser gradients
    prephaser_ro_area = np.abs(readout_gradient.area[0]) / 2 
    prephaser_pe_area = np.abs(k_phase_start) / system_specs.gamma
    combined_kspace_traverse = np.sqrt((prephaser_ro_area * system_specs.gamma ) ** 2 + k_phase_start ** 2)    
    [_, prephaser_rise, prephaser_flat] = system_specs.get_shortest_gradient(combined_kspace_traverse / system_specs.gamma)

    pe_prephaser = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs, 
                                                                      orientation=np.array([0., 1., 0.]) * np.sign(k_phase_start),
                                                                      duration=prephaser_flat+prephaser_rise*2, 
                                                                      area=prephaser_pe_area,
                                                                      name="pe_prephaser")
    ro_prephaser = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs, 
                                                                      orientation=np.array([-1., 0., 0.]),
                                                                      duration=prephaser_flat+prephaser_rise*2, 
                                                                      area=prephaser_ro_area, 
                                                                      name="ro_prephaser")  
    
    return ro_prephaser, pe_prephaser, readout_gradient, blip_gradient, adc_block  


def _epi_fov_definition(field_of_view: Quantity, matrix_size: np.ndarray, 
                       blip_direction: str = "up", partial_fourier_lines: int = 0) -> dict:
    """Transforms definition of the spatial extend of the fov to the required k-space definitions
      for EPI trajectories.

    For even number of phase encoding lines, k-max is only reached by the last line, where as for
    odd numbers -k-max and k-max is reached. This is necessary to guarantee the k-space center to
    be acquired in all cases.

    :raises: - ValueError if partial_fourier_lines > matrix_size[1]//2-1 to avoid too high
                    partial fourier factors

    :param field_of_view: Quantity[Length] - Defines the spatial extend in readout and
                            phase-encoding direction
    :param matrix_size: np.ndarray (2, ) - number of samples in readout/phase-encoding direction
                        if partial fourier is enabled the lines are subtracted from this parameter
    :param blip_direction: (str) from ['up', 'down'] specifies the direction of phase encoding steps
    :param partial_fourier_lines: (int) number of lines to be skipped before k-space center
    :return: Dict with keys (k_readout, k_phase_start, k_phase_step, k_phase_lines, num_samples)
    """
    n_pe_lines = matrix_size[1]
    n_pe_center_index = np.floor((matrix_size[1] - 1)/ 2)
    if n_pe_center_index - 1 < partial_fourier_lines:
        raise ValueError("Partial fourier factor too high. k-space centre won't be sampled")

    effective_kpe_lines = n_pe_lines - partial_fourier_lines
    resolution = Quantity(field_of_view.m_as("m") / matrix_size, "m")
    kmax = 1 / (2 * resolution)

    # definition for blip up:
    n_steps_to_kmax = n_pe_lines - n_pe_center_index
    kpe_step = kmax[1] / n_steps_to_kmax
    start_phase = -kpe_step * (n_pe_center_index - partial_fourier_lines)

    # definition for blip down:
    if blip_direction.lower() == "down":
        start_phase *= -1
        kpe_step *= -1

    return dict(k_readout = 1/ resolution[0], k_phase_start=start_phase, k_phase_step=kpe_step,
                k_phase_lines=effective_kpe_lines, num_samples=matrix_size[0])


def _set_echo_spacing_from_water_fat_shift(system_specs: cmrseq.SystemSpec,
                                           water_fat_shift: Union[str, float],
                                           n_epi_lines: int, 
                                           shortest_echo_spacing: Quantity,
                                           longest_echo_spacing: Quantity = None) -> Quantity:
    """ Sets the feasible echo-spacing time according to the target water-fat-shift within
    the specified boudnaries. Raises ValueErrors if time-constaints are not met
    
    :param system_specs:
    :param water_fat_shift: one of ['minimum', 'maximum', #pixels(float)]. Determines the echo-spacing therefore the 
                            duration of all
                            according to the formula :math:`P/(C * (N+1)) = T` with (P)ixels, (C)hemicalf shift 
                            frequency, (N)umber of k-space lines and (T) Echo spacing
    :param n_epi_lines: number of epi lines contained in epi-train
    :param shortest_echo_spacing: Shortest feasible (due to gradient limitations) echo spacing
                            Used for boundary checks
    :param longest_echo_spacing: Longest feasible (max-duration constraint) echo-spacing
    """
    if longest_echo_spacing is not None and np.around(shortest_echo_spacing.m_as("ms"), decimals=4) > np.around(longest_echo_spacing.m_as("ms"), decimals=4):
        raise ValueError(f"Water fat shift set such set minimal achivable duration is larger " 
                         f"than specified max duration: echo spacing [{shortest_echo_spacing}, {longest_echo_spacing}]")

    fat_shift = 3.4e-6

    if isinstance(water_fat_shift, str):
        if water_fat_shift.lower() == "minimum":
            echo_spacing = shortest_echo_spacing
        if water_fat_shift.lower() == "maximum":
            if longest_echo_spacing is None:
                raise ValueError("Can't set maximum water-fat-shift without specifing longest echo-spacing (got None)")
            echo_spacing = longest_echo_spacing
    elif isinstance(water_fat_shift, (float, int)):
        chemical_shift = (system_specs.gamma * system_specs.b0 * fat_shift).to("Hz")
        echo_spacing = (water_fat_shift / (chemical_shift * (n_epi_lines + 1))).to("ms")
        echo_spacing = system_specs.time_to_raster(echo_spacing, "grad")
        if echo_spacing < shortest_echo_spacing or echo_spacing > longest_echo_spacing:
            raise ValueError(f"Calculated echo spacing ({echo_spacing}) not in allowed" 
                             f"range [{shortest_echo_spacing}, {longest_echo_spacing}]")

    return echo_spacing


def _calculate_longest_echo_spacing(system_specs: cmrseq.SystemSpec, max_total_duration: Quantity,
                                    prephaser_duration: Quantity, n_lines: int):
    """ Calculates the longest feasible echo-spacing due to max-duration constaint. 
    
    """
    if max_total_duration is not None:
        longest_echo_spacing = (max_total_duration - prephaser_duration) / n_lines
        longest_echo_spacing_raster = system_specs.time_to_raster(longest_echo_spacing, "grad") 
        diff_to_raster = (longest_echo_spacing_raster - longest_echo_spacing)
        if diff_to_raster > 0:
            longest_echo_spacing_raster -= system_specs.grad_raster_time
        longest_echo_spacing = longest_echo_spacing_raster
    else:
        longest_echo_spacing = None
    return longest_echo_spacing
