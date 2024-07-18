__all__ = ["pc_gre","pc_gre_multivenc"]

from warnings import warn
from typing import List

import numpy as np
from pint import Quantity

from copy import deepcopy

import cmrseq

def pc_gre(system_specs: cmrseq.SystemSpec,
           matrix_size: np.ndarray,
           inplane_resolution: Quantity,
           slice_thickness: Quantity,
           adc_duration: Quantity,
           flip_angle: Quantity,
           pulse_duration: Quantity,
           repetition_time: Quantity,
           echo_time: Quantity,
           venc: Quantity,
           venc_direction: np.ndarray,
           venc_duration: Quantity = Quantity(0., "m"),
           slice_position_offset: Quantity = Quantity(0., "m"),
           time_bandwidth_product: float = 4.,
           dummy_shots: int = None,
           crusher_area: Quantity = Quantity(0.,'mT/m*ms'),
           crusher_duration:Quantity = Quantity(0.,'mT/m*ms')) -> List[cmrseq.Sequence]:
    """ Defines a 2D gradient echo sequence with bipolar velocity encoding.

    :param system_specs: SystemSpecifications
    :param matrix_size: array of shape (2, ) containing the resulting matrix dimensions
    :param inplane_resolution: Quantity[Length] of shape (2, ) containing the in-plane
                                voxel dimensions
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param repetition_time: Quantity[Time] containing the required repetition_time
    :param echo_time: Quantity[Time] containing the required echo-time. If too short for
                    given system specifications, it is increased to minimum and a warning is raised.
    :param venc: Quantity[Velocity] strength of velocity encoding gradient
    :param venc_duration: Quantity[Time] denoting the duration of applied VENC-gradients. If 0. the
                          resulting gradients will be the shortest for given system limits
    :param venc_direction: Vector (3, ) denoting the direction of velocity encoding in MPS coordinates
    :param flip_angle: Quantity[Angle] containing the required flip_angle
    :param pulse_duration: Quantity[Time] Total pulse duration (corresponds to flat_duration of the
                            slice selection gradient)
    :param slice_position_offset: Quantity[Length] positional offset in slice normal direction
                                  defining the frequency offset of the RF pulse
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :param dummy_shots: number of dummy shots (TRs) without adc-events, with k-space center
                        phase encoding
    :param crusher_area: Quantity[Gradient Area] crusher gradient area along slice direction. If set to
                         zero no crusher will be applied and phase encoder will not be rewound
    :param crusher_duration: Quantity[Time] duration of crusher. If set too short will default to
                             duration of phase encoder or shortest possible crusher
    :return: List of sequence objects, that each represent a single TR
    """
    rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(system_specs=system_specs,
                                                                  slice_thickness=slice_thickness,
                                                                  flip_angle=flip_angle,
                                                                  pulse_duration=pulse_duration,
                                                                  time_bandwidth_product=time_bandwidth_product,
                                                                  slice_position_offset=slice_position_offset,
                                                                  slice_normal=np.array([0., 0., 1.]))

    ro_blocks = cmrseq.seqdefs.readout.multi_line_cartesian(system_specs=system_specs,
                                                            fnc=cmrseq.seqdefs.readout.gre_cartesian_line,
                                                            matrix_size=matrix_size,
                                                            inplane_resolution=inplane_resolution,
                                                            adc_duration=adc_duration,
                                                            dummy_shots=dummy_shots)

    venc_gradient = cmrseq.seqdefs.velocity.bipolar(system_specs=system_specs, venc=venc, duration=venc_duration,
                                                    direction=venc_direction)

    if crusher_area != 0:
        crusher_area = crusher_area.to("mT/m*ms") - rf_seq.get_block("slice_select_0").area[2] / 2
        if crusher_duration == 0:
            crusher_duration = ro_blocks[0].get_block("pe_prephaser_0").duration
        if crusher_duration < (2*system_specs.get_shortest_gradient(crusher_area)[1] + system_specs.get_shortest_gradient(crusher_area)[2]):
            crusher = cmrseq.bausteine.TrapezoidalGradient.from_area(system_specs, orientation=np.sign(crusher_area)*np.array([0., 0., 1.]),
                                                                     area=np.abs(crusher_area.to("mT/m*ms")),
                                                                     name="crusher")
        else:
            crusher = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                         orientation=np.sign(crusher_area)*np.array([0., 0., 1.]),
                                                                         duration=crusher_duration,
                                                                         area=np.abs(crusher_area.to("mT/m*ms")),
                                                                         name="crusher")
        for seq in ro_blocks:
            pe_rewind = deepcopy(seq.get_block("pe_prephaser_0"))
            pe_rewind.name = "pe_rewind"
            pe_rewind.scale_gradients(-1)

            post = cmrseq.Sequence([crusher,pe_rewind],system_specs=system_specs)
            seq.append(post)

    adc_center = system_specs.time_to_raster(ro_blocks[0].get_block('adc_0').adc_center)

    minimal_tr = ro_blocks[0].duration + venc_gradient.duration + rf_seq.duration
    minimal_te = (rf_seq.duration - rf_seq.get_block("rf_excitation_0").rf_events[0] + adc_center + venc_gradient.duration)

    repetition_time = system_specs.time_to_raster(repetition_time)
    if repetition_time < minimal_tr:
        warn(f"PC GRE Sequence: Repetition time too short to be feasible, set TR to {minimal_tr}")
        repetition_time = minimal_tr

    maximum_te = repetition_time - (ro_blocks[0].duration - adc_center) \
                 - rf_seq.get_block("rf_excitation_0").rf_events[0]

    echo_time = system_specs.time_to_raster(echo_time)
    if echo_time < minimal_te:
        warn(f"PC GRE Sequence: Echo time too short to be feasible, set TE to {minimal_te}")
        echo_time = minimal_te

    if echo_time > maximum_te:
        warn(f"PC GRE Sequence: Echo time too long for given TR, set TE to {maximum_te}")
        echo_time = maximum_te

    te_delay = system_specs.time_to_raster(echo_time - minimal_te)
    tr_delay = system_specs.time_to_raster(repetition_time - minimal_tr - te_delay)

    # Concatenate readout blocks
    seq_list = []
    for ro_b in ro_blocks:
        seq = deepcopy(rf_seq)
        if te_delay > 0:
            seq.append(cmrseq.bausteine.Delay(system_specs=system_specs, duration=te_delay))
        seq.append(venc_gradient)
        seq.append(ro_b)
        if tr_delay > 0:
            seq.append(cmrseq.bausteine.Delay(system_specs=system_specs, duration=tr_delay))
        seq_list.append(seq)
    return seq_list

def pc_gre_multivenc(system_specs: cmrseq.SystemSpec,
                     matrix_size: np.ndarray,
                     inplane_resolution: Quantity,
                     slice_thickness: Quantity,
                     adc_duration: Quantity,
                     flip_angle: Quantity,
                     pulse_duration: Quantity,
                     repetition_time: Quantity,
                     echo_time: Quantity,
                     venc_list: List[Quantity],
                     venc_direction_list: List[np.ndarray],
                     venc_duration: Quantity = Quantity(0., "m"),
                     slice_position_offset: Quantity = Quantity(0., "m"),
                     time_bandwidth_product: float = 4.,
                     dummy_shots: int = None,
                     crusher_area: Quantity = Quantity(0., 'mT/m*ms'),
                     crusher_duration: Quantity = Quantity(0., 'mT/m*ms')) -> List[List[cmrseq.Sequence]]:

    mvenc = np.asarray([v.m_as("m/s") for v in venc_list])
    mvenc = mvenc[mvenc != 0.]
    min_venc = Quantity(np.min(np.abs(mvenc)), "m/s")

    venc_duration = cmrseq.seqdefs.velocity.bipolar(system_specs=system_specs, venc=min_venc, duration=venc_duration,
                                                    direction=np.array([1,0,0])).duration

    seq_list = []
    for venc, dir in zip(venc_list, venc_direction_list):

        seq_list.append(pc_gre(system_specs=system_specs,
                               matrix_size=matrix_size,
                               inplane_resolution=inplane_resolution,
                               slice_thickness=slice_thickness,
                               adc_duration=adc_duration,
                               flip_angle=flip_angle,
                               pulse_duration=pulse_duration,
                               repetition_time=repetition_time,
                               echo_time=echo_time,
                               venc=venc,
                               venc_direction=dir,
                               venc_duration=venc_duration,
                               slice_position_offset=slice_position_offset,
                               time_bandwidth_product=time_bandwidth_product,
                               dummy_shots=dummy_shots,
                               crusher_area=crusher_area,
                               crusher_duration=crusher_duration))

    return seq_list