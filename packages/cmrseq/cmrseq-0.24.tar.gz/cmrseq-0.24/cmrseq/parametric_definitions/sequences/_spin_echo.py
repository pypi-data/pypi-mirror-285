""" This module contains parametric definitions of complete multi-TR SE-based sequences"""
__all__ = ["single_line_cartesian2d", "se_ssepi"]

from typing import List, Union
from warnings import warn
from types import SimpleNamespace

import numpy as np
from pint import Quantity

import cmrseq


# pylint: disable=R0913, R0914
def single_line_cartesian2d(system_specs: 'cmrseq.SystemSpec',
                            echo_time: Quantity,
                            repetition_time: Quantity,
                            matrix_size: np.ndarray,
                            inplane_resolution: Quantity,
                            slice_thickness: Quantity,
                            adc_duration: Quantity,
                            pulse_duration: Quantity,
                            time_bandwidth_product: float = 4.) -> List[cmrseq.Sequence]:
    """ Constructs a basis spin echo single line acquisition scheme for a cartesian
    trajectory.

    :raises: ValueError - if repetition time is smaller than the composite of elements within one TR

    :param system_specs: SystemSpecification
    :param echo_time:
    :param repetition_time: Quantity[Time] containing the required repetition_time
    :param matrix_size: array of shape (2, )
    :param inplane_resolution: Quantity[Length] of shape (2, )
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param pulse_duration: Quantity[Time] Total pulse duration (corresponds to flat_duration of the
                            slice selection gradient)
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :return: List of length (matrix_size[1]) containting one Sequence object per TR
    """

    rf_block = cmrseq.seqdefs.excitation.slice_selective_se_pulses(
                                                    system_specs, echo_time,
                                                    slice_thickness=slice_thickness,
                                                    pulse_duration=pulse_duration,
                                                    slice_orientation=np.array([0., 0., 1]),
                                                    time_bandwidth_product=time_bandwidth_product)
    ss_ramptime = (rf_block.gradients[0][0][1] - rf_block.gradients[0][0][0])
    ro_blocks = cmrseq.seqdefs.readout.multi_line_cartesian(
                                            system_specs=system_specs,
                                            fnc=cmrseq.seqdefs.readout.se_cartesian_line,
                                            matrix_size=matrix_size,
                                            inplane_resolution=inplane_resolution,
                                            echo_time=echo_time,
                                            pulse_duration=pulse_duration + 2 * ss_ramptime,
                                            excitation_center_time=pulse_duration / 2 + ss_ramptime,
                                            adc_duration=adc_duration)

    if repetition_time < (ro_blocks[0] + rf_block).duration:
        raise ValueError("Specified repetition time is too short")

    sequence_list = []
    for readout_block in ro_blocks:
        seq = readout_block + rf_block
        seq.append(cmrseq.bausteine.Delay(system_specs, repetition_time - seq.duration))
        sequence_list.append(seq)
    return sequence_list


def se_ssepi(system_specs: cmrseq.SystemSpec,
             field_of_view: Quantity,
             matrix_size: np.ndarray,
             echo_time: Quantity,
             slice_thickness: Quantity,
             slice_orientation: np.ndarray,
             pulse_duration: Quantity,
             epi_slope_sampling: bool = False,
             tbw_product: float = 4,
             max_epi_duration: Quantity = None,
             epi_water_fat_shift: Union[str, float, int] = "minimum",
             partial_fourier_lines: int = 0,
             blip_direction: str = "up"):
    """Defines a single shot EPI sequence. If the specified echo time is too short, the shortest
    possible echo-time is used.

    .. note::

        The sequence object returned by this function contains the SimpleNamespace "additional_info"
        as attribute, which contains the k-space center index, actually used echo-time and the
        absolute value of the echo-formation time



    :param system_specs:  SystemSpecification
    :param field_of_view: spatial extend in readout and phase encoding direction; shape = (2, )
    :param matrix_size: number of pixels in readout and phase encoding direction; shape = (2, )
    :param echo_time: Time at which the central k-space line is placed
    :param slice_thickness: Thickness of slice-selective excitation definitions
    :param slice_orientation: Slice normal of excitation slice
    :param pulse_duration: Duration of the excitation & refocusing pulses
    :param epi_slope_sampling: If yes the epi readout uses slope sampling
    :param tbw_product: Time-bandwidth product of the inc-Pulses used for excitation and refocus
    :param max_epi_duration: See documentation (cmrseq.seqdefs.readout.single_shot_epi)
    :param epi_water_fat_shift: See documentation (cmrseq.seqdefs.readout.single_shot_epi)
    :param partial_fourier_lines: number of lines to skip before k-space center, allowing shorter
                                    echo times
    :param blip_direction: from ["up", "down"] defining the direction of phase-encoding kspace
                                travers
    :return: sequence object
    """
    # Define EPI-readout
    readout = cmrseq.seqdefs.readout.single_shot_epi(system_specs=system_specs,
                                                     field_of_view=field_of_view,
                                                     matrix_size=matrix_size,
                                                     blip_direction=blip_direction,
                                                     partial_fourier_lines=partial_fourier_lines,
                                                     slope_sampling=epi_slope_sampling,
                                                     water_fat_shift=epi_water_fat_shift,
                                                     max_total_duration=max_epi_duration)
    k_center_idx = int(np.floor(matrix_size[1] / 2) - partial_fourier_lines)

    # Construct the excitation blocks
    excitation = cmrseq.seqdefs.excitation.slice_selective_se_pulses(
                                                system_specs=system_specs,
                                                echo_time=echo_time,
                                                slice_thickness=slice_thickness,
                                                pulse_duration=pulse_duration,
                                                slice_orientation=slice_orientation,
                                                time_bandwidth_product=tbw_product)

    # check if minimal TE is smaller than the specified TE
    epi_duration_to_center = readout.adc_centers[k_center_idx]
    rf_post_duration = excitation.end_time - excitation.rf_events[-1][0]
    minimal_te = system_specs.time_to_raster((epi_duration_to_center + rf_post_duration)) * 2

    if minimal_te > echo_time:
        warn("SSEPI Sequence: TE is shorter than possible for the given readout and diffusion "
            f"weighting configuration. Setting the echo time to {minimal_te}")
        refocus = excitation.partial_sequence(partial_string_match=['rf_excitation_0', 'slice_select_refocus_0'],
                                              copy_blocks=False)
        refocus.shift_in_time((minimal_te - echo_time) / 2)
        echo_time = minimal_te

    ro_shift = system_specs.time_to_raster(
        echo_time - readout.adc_centers[k_center_idx] + excitation.rf_events[0][0], "grad")
    readout.shift_in_time(ro_shift)

    seq = excitation + readout
    seq.additional_info = SimpleNamespace(kcenter_idx=k_center_idx,
                                          echo_time=echo_time,
                                          echo_formation_time=readout.adc_centers[k_center_idx])
    return seq
