__all__ = ["balanced_ssfp", "radial_balanced_ssfp"]

from typing import List
from copy import deepcopy
from warnings import warn
import numpy as np
from pint import Quantity

import cmrseq


def balanced_ssfp(system_specs: cmrseq.SystemSpec,
                  matrix_size: np.ndarray,
                  inplane_resolution: Quantity,
                  slice_thickness: Quantity,
                  adc_duration: Quantity,
                  flip_angle: Quantity,
                  pulse_duration: Quantity,
                  repetition_time: Quantity,
                  slice_position_offset: Quantity = Quantity(0., "m"),
                  time_bandwidth_product: float = 4.,
                  dummy_shots: int = None,
                  fuse_slice_rewind_and_prephaser: bool = True) -> List[cmrseq.Sequence]:
    """ Defines a balanced steady state free precession sequence with a/2-TR/2 preparation, 
    with a cartesian readout.

    Intended behaviour for certain combinations of specified arguments:

    .. Dropdown:: TR \& ADC-duration are specified

        If the specified TR is sufficiently long, 
         

    .. code-block::

        .                 |                  TR                  |                 .
        .                     |       TE         |                                 .
        .                                                                          .
        .            RF:     /\                                                    .
        .            ADC   \/  \/      |||||||||||||||||||||                       .
        .                  ______                                                  .
        .            SS:  /      \    _______________________                      .
        .                         \__/                       \__/                  .
        .                              _____________________                       .
        .            RO:  ________    /                     \                      .
        .                         \__/                       \__/                  .
        .                                                    __                    .
        .            PE:  ________    ______________________/  \                   .
        .                         \__/                                             .


    .. note::

        Assumptions in temporal optimization for combinations of specified arguments:
        - *TR and adc_duration is provided*:  

        1. Pre-phasers are as short as possible, determined by the maximal k-space 
            traverse within a single TR
        2. If not specified, the acquisition time (total sampling duration per line) 
            is minimal 
        3. If not specified, the repetition time is set to the shortest possible 


    :param system_specs: SystemSpecification
    :param matrix_size: array of shape (2, )
    :param inplane_resolution: Quantity[Length] of shape (2, )
    :param repetition_time: Quantity[Time] containing the required repetition_time 
                            If None or too short, the shortest possible time under system 
                            constraints is used.
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param flip_angle: Quantity[Angle] containing the required flip_angle
    :param pulse_duration: Quantity[Time] Total pulse duration (corresponds to flat_duration of the
                            slice selection gradient)
    :param slice_position_offset: Quantity[Length] positional offset in slice normal direction
                              defining the frequency offset of the RF pulse
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :param dummy_shots: number of shots(TRs) without adc-events before starting the acquisition
    :param fuse_slice_rewind_and_prephaser: If True, the slice selection rewinder is recalculated
            to match the duration of the prephaser, resulting in the fastest possible 3D k-space
            traverse.
    :return: List of length (n_dummy+matrix_size[1]) containting one Sequence object per TR
    """

    # Step 0: Create a slice-selective excitation
    rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                    system_specs=system_specs,
                                    slice_thickness=slice_thickness,
                                    flip_angle=flip_angle,
                                    pulse_duration=pulse_duration,
                                    time_bandwidth_product=time_bandwidth_product,
                                    slice_position_offset=slice_position_offset,
                                    slice_normal=np.array([0., 0., 1.]))
    ss_refocus = rf_seq["slice_select_rewind_0"]
    
    # Step 1: Determine ADC-duration depending on one of four cases:
    k_max_inplane, _, kro_traverse = cmrseq.seqdefs.readout.matrix_to_kspace_2d(matrix_size, inplane_resolution)

    # Case 1: Maximize sampling time for fixed TR
    if repetition_time is not None and adc_duration is None:
        if fuse_slice_rewind_and_prephaser:
            time_to_fill = repetition_time - rf_seq[0].duration
        else:
            time_to_fill = repetition_time - rf_seq.duration - ss_refocus.duration
        add_k_traverse = Quantity([k_max_inplane[1].m_as("1/m"), 
                                   (ss_refocus.area[-1] * system_specs.gamma).m_as("1/m")],
                                  "1/m")
        prephaser, rograd = cmrseq.seqdefs.readout.get_longest_adc_duration(
                                        system_specs, time_to_fill, 
                                        matrix_size[0], inplane_resolution[0],
                                        balanced=True,
                                        additional_kspace_traverse=add_k_traverse)
        internal_adc_duration = rograd.flat_duration
    # Case 2: If tr is not set, set it to minimum. 
    elif repetition_time is None and adc_duration is None:
        min_adc_duration, _, _ = cmrseq.seqdefs.readout.get_shortest_adc_duration(
                                        system_specs, matrix_size[0], inplane_resolution[0]
                                        )
        internal_adc_duration = min_adc_duration
    # Case 3: Specified adc_duration infeasible, therefore set it to minimum and
    # increase TR accordingly
    # Case 4: Both are specified, hence given value is used and TR is increased if
    # it is too short for given sampling duration
    else:
        min_adc_duration, _, _ = cmrseq.seqdefs.readout.get_shortest_adc_duration(
                                system_specs, matrix_size[0], inplane_resolution[0]
                                )
        if adc_duration < min_adc_duration:
            internal_adc_duration = min_adc_duration
            warn(f"ADC-duration set from {adc_duration} to {min_adc_duration}", 
                cmrseq.err.AutomaticOptimizationWarning)
        else:
            internal_adc_duration = adc_duration
    
    # Step 2: Construct a dummy readout with prephaser with minimal duration
    ro_dummy = cmrseq.seqdefs.readout.balanced_gre_cartesian_line(system_specs, matrix_size[0], 
                                                                  kro_traverse, k_max_inplane[1],
                                                                  internal_adc_duration)
        
    # Step 3 Compute shortest prephaser-duration    
    if fuse_slice_rewind_and_prephaser:
    
        k_max_x = (ro_dummy["ro_prephaser_0"].area[0] * system_specs.gamma).m_as("1/m")
        k_max_y = (ro_dummy["pe_prephaser_0"].area[1] * system_specs.gamma).m_as("1/m") 
        kz_refocus = (ss_refocus.area * system_specs.gamma).m_as("1/m")
        total_kspace_traverse = Quantity([k_max_x, k_max_y, kz_refocus[-1]], "1/m")
        _amp, _rise, _flat = system_specs.get_fastest_kspace_traverse(total_kspace_traverse)
        prephaser_duration = system_specs.time_to_raster(2 *_rise +  _flat, "grad")
    
        rf_seq.remove_block("slice_select_rewind_0")
        ss_rewind = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                       np.array([0., 0., -1.]),
                                                                       duration=prephaser_duration,
                                                                       area=ss_refocus.area[-1],
                                                                       name="slice_select_rewind")
        rf_seq.append(ss_rewind)
    else:
        prephaser_duration = ro_dummy[0].duration
    
    # Step 4: Calculate padding for extra time in longer TRs
    if fuse_slice_rewind_and_prephaser:
        minimal_tr = (ro_dummy["trapezoidal_readout_0"].duration + 
                      2 * prephaser_duration + rf_seq["slice_select_0"].duration)
    else:
        minimal_tr = (ro_dummy["trapezoidal_readout_0"].duration + 2 * prephaser_duration +
                      rf_seq.duration + rf_seq["slice_select_rewind_0"].duration)
    internal_repetition_time = repetition_time
    if repetition_time is None: 
        internal_repetition_time = minimal_tr
    elif repetition_time < minimal_tr:
        warn(f"TR set from {repetition_time} to {minimal_tr}", 
             cmrseq.err.AutomaticOptimizationWarning)
        internal_repetition_time = minimal_tr
    delay_dur = (internal_repetition_time - minimal_tr) /2

    # Step 5: Construct the readout and phase encoding gradients    
    ro_blocks = cmrseq.seqdefs.readout.multi_line_cartesian(
                                    system_specs=system_specs,
                                    fnc=cmrseq.seqdefs.readout.balanced_gre_cartesian_line,
                                    matrix_size=matrix_size,
                                    inplane_resolution=inplane_resolution,
                                    adc_duration=internal_adc_duration,
                                    prephaser_duration=prephaser_duration,
                                    dummy_shots=dummy_shots)

    # Step 6: Create the slice selection compensation
    ss_compensate = deepcopy(rf_seq["slice_select_rewind_0"])
    ss_compensate.name = "slice_select_balance"
    ss_compensate.shift(-ss_compensate.tmin)
    if fuse_slice_rewind_and_prephaser:
        ss_compensate.shift(-prephaser_duration)

    # Step 7: Adjust alternating phase offset for adc-events
    for ro_idx, ro_b in enumerate(ro_blocks):
        phase_offset = Quantity(np.mod(ro_idx, 2) * np.pi, "rad")
        adc_block = ro_b.get_block("adc_0")
        if adc_block is not None:
            adc_block.phase_offset = phase_offset

    # Step 8: Add delay to match TR/2 after the first exication
    catalyst_shot = deepcopy(rf_seq)
    catalyst_shot["rf_excitation_0"].scale_angle(0.5)
    catalyst_shot.append(cmrseq.bausteine.Delay(system_specs, 
                         system_specs.time_to_raster(internal_repetition_time/2 - catalyst_shot.duration, "grad")))

    # Assemble blocks to list of sequences each representing one TR
    seq_list = [catalyst_shot]
    for tr_idx, ro_b in enumerate(ro_blocks):
        flip_angle_phase = (-1) ** tr_idx
        seq = deepcopy(rf_seq)
        seq["rf_excitation_0"].scale_angle(flip_angle_phase)

        if fuse_slice_rewind_and_prephaser:
            ro_b.shift_in_time(-prephaser_duration)
        
        seq.append(ro_b, copy=False) 
        seq.append(ss_compensate, copy=True)

        # insert padding around the readout to match TR
        if delay_dur > 0:
            part1 = seq.partial_sequence(copy_blocks=False,
                                        partial_string_match=("readout", "adc"))
            part1.shift_in_time(delay_dur)
            
            part2 = seq.partial_sequence(copy_blocks=False, 
                                        partial_string_match=("balance"))
            part2.shift_in_time(delay_dur*2)
        seq_list.append(seq)
    return seq_list


def radial_balanced_ssfp(system_specs: cmrseq.SystemSpec,
                         samples_per_spoke: int,
                         inplane_resolution: Quantity,
                         slice_thickness: Quantity,
                         adc_duration: Quantity,
                         flip_angle: Quantity,
                         pulse_duration: Quantity,
                         repetition_time: Quantity,
                         spoke_angle_increment: Quantity = None,
                         num_spokes: int = None,
                         slice_position_offset: Quantity = Quantity(0., "m"),
                         time_bandwidth_product: float = 4.,
                         dummy_shots: int = 0,
                         fuse_slice_rewind_and_prephaser: bool = True) -> List[cmrseq.Sequence]:

    rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
        system_specs=system_specs,
        slice_thickness=slice_thickness,
        flip_angle=flip_angle,
        pulse_duration=pulse_duration,
        time_bandwidth_product=time_bandwidth_product,
        slice_position_offset=slice_position_offset,
        slice_normal=np.array([0., 0., 1.]))
    ss_refocus = rf_seq.get_block("slice_select_rewind_0")

    kr_max = 1 / (2 * inplane_resolution.m_as("m"))

    if fuse_slice_rewind_and_prephaser:
        # Recalculate ss-gradient combined with ro prephaser

        kz_refocus = (ss_refocus.area * system_specs.gamma).m_as("1/m")

        total_kspace_traverse = Quantity(np.linalg.norm([kr_max, kz_refocus[-1]]), "1/m")
        combined_gradient_area = total_kspace_traverse / system_specs.gamma.to("1/mT/ms")
        prephaser_duration = cmrseq.bausteine.TrapezoidalGradient.from_area(
            system_specs, np.array([1., 0., 0]), combined_gradient_area).duration

        rf_seq.remove_block("slice_select_rewind_0")
        ss_refocus = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                        np.array([0., 0., -1.]),
                                                                        prephaser_duration,
                                                                        ss_refocus.area[-1],
                                                                        delay=rf_seq.duration,
                                                                        name="slice_select_rewind")
        rf_seq.add_block(ss_refocus)
    else:
        prephaser_duration = None

    ro_ref = cmrseq.seqdefs.readout.balanced_radial_spoke(system_specs=system_specs, num_samples=samples_per_spoke,
                                                          kr_max=Quantity(kr_max, '1/m'), angle=Quantity(0, 'rad'),
                                                          adc_duration=adc_duration,
                                                          prephaser_duration=prephaser_duration)

    dummy_ref = cmrseq.seqdefs.readout.balanced_radial_spoke(system_specs=system_specs, num_samples=0,
                                                             kr_max=Quantity(kr_max, '1/m'), angle=Quantity(0, 'rad'),
                                                             adc_duration=adc_duration,
                                                             prephaser_duration=prephaser_duration)

    if prephaser_duration is None:
        prephaser_duration = ro_ref.get_block("radial_prephaser_0").duration


    # Create the slice selection compensation
    ss_compensate = deepcopy(ss_refocus)
    ss_compensate.name = "slice_select_prewind"


    readout_gradient_duration = ro_ref.get_block("radial_readout_0").duration
    max_ssref_prephaser = max(ss_refocus.duration, prephaser_duration)

    if fuse_slice_rewind_and_prephaser:
        minimal_tr = readout_gradient_duration + 2 * max_ssref_prephaser + rf_seq.duration - ss_refocus.duration
    else:
        minimal_tr = ro_ref.duration + rf_seq.duration + ss_compensate.duration

    repetition_time = system_specs.time_to_raster(repetition_time)
    if repetition_time < minimal_tr:
        warn(f"Radial bSSFP Sequence: Repetition time too short to be feasible, set TR to {minimal_tr}")
        repetition_time = minimal_tr


    tr_delay_half = system_specs.time_to_raster((repetition_time - minimal_tr)/2)

    ss_compensate.shift(-ss_compensate.tmin+ repetition_time - ss_compensate.duration)

    # Generate catalyst with TR/2 duration
    rf_catalyst= deepcopy(rf_seq)
    rf_catalyst.append(cmrseq.bausteine.Delay(system_specs, repetition_time / 2 - rf_seq.duration))

    # Concatenate readout blocks
    seq_list = [rf_catalyst]

    # Start with dummy shots
    for idx in range(dummy_shots):
        # Alternating RF pulse phase
        flip_angle_phase = (-1) ** (idx+1) * flip_angle
        rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                                    system_specs=system_specs,
                                                    slice_thickness=slice_thickness,
                                                    flip_angle=flip_angle_phase,
                                                    pulse_duration=pulse_duration,
                                                    slice_position_offset=slice_position_offset,
                                                    time_bandwidth_product=time_bandwidth_product,
                                                    slice_normal=np.array([0., 0., 1.]))
        rf_seq.remove_block("slice_select_rewind_0")
        rf_seq.append(cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                         np.array([0., 0., -1.]),
                                                                         prephaser_duration,
                                                                         ss_refocus.area[-1],
                                                                         name="slice_select_rewind"))

        cur_ro = deepcopy(dummy_ref)
        if fuse_slice_rewind_and_prephaser:
            cur_ro.shift_in_time(
                rf_seq.duration - min(ss_refocus.duration, prephaser_duration)+tr_delay_half)
        else:
            cur_ro.shift_in_time(
                rf_seq.duration + tr_delay_half)
        seq = rf_seq + cur_ro + cmrseq.Sequence([ss_compensate, ], system_specs)
        seq_list.append(seq)

    # Calculate angle increment scheme
    if num_spokes is None:
        if spoke_angle_increment is not None:
            warn(f"Radial bSSFP Sequence: Can not set spoke angle increment without"
                 f" setting number of spokes, defaulting to satisfy nyquist")

        num_spokes = np.ceil(samples_per_spoke*np.pi/2) # Nyquist criteria for radial sampling

        spoke_angles = np.linspace(0,np.pi,int(num_spokes), endpoint=False)
    else:
        if spoke_angle_increment is None:
            warn(f"Radial bSSFP Sequence: Spoke angle not set while spoke count set, "
                 f"defaulting to even spacing of spokes")
            spoke_angles = np.linspace(0,np.pi,int(num_spokes), endpoint=False)
        else:
            spoke_angles = np.array(range(num_spokes))*spoke_angle_increment.to('rad').m_as('dimensionless')

    # Readout shots
    for angle,idx in zip(spoke_angles,range(len(spoke_angles))):
        # Alternating RF pulse phase
        flip_angle_phase = (-1) ** (idx + dummy_shots + 1) * flip_angle
        rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
            system_specs=system_specs,
            slice_thickness=slice_thickness,
            flip_angle=flip_angle_phase,
            pulse_duration=pulse_duration,
            slice_position_offset=slice_position_offset,
            time_bandwidth_product=time_bandwidth_product,
            slice_normal=np.array([0., 0., 1.]))
        if fuse_slice_rewind_and_prephaser:
            rf_seq.remove_block("slice_select_rewind_0")
            rf_seq.append(cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                             np.array([0., 0., -1.]),
                                                                             prephaser_duration,
                                                                             ss_refocus.area[-1],
                                                                             name="slice_select_rewind"))

        cur_ro = deepcopy(ro_ref)
        sa = np.sin(angle)
        ca = np.cos(angle)
        R = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])

        cur_ro.rotate_gradients(R)
        if fuse_slice_rewind_and_prephaser:
            cur_ro.shift_in_time(
                rf_seq.duration - min(ss_refocus.duration, prephaser_duration)+tr_delay_half)
        else:
            cur_ro.shift_in_time(
                rf_seq.duration + tr_delay_half)

        # Adjust alternating phase offset for adc-events
        phase_offset = Quantity(np.mod(idx + dummy_shots + 1, 2) * np.pi, "rad")
        adc_block = cur_ro.get_block("adc_0")
        if adc_block is not None:
            adc_block.phase_offset = phase_offset

        seq = rf_seq + cur_ro + cmrseq.Sequence([ss_compensate, ], system_specs)
        seq_list.append(seq)

    return seq_list