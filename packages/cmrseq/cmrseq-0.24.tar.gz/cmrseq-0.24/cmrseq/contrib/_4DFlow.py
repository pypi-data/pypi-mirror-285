__all__ = ["gen_4DFlow_sequence","generate_4Dflow_LUT"]

import scipy.io
from warnings import warn
from typing import List
import numpy as np
from pint import Quantity
from copy import deepcopy
import cmrseq
from tqdm.auto import tqdm
from time import perf_counter


def generate_4Dflow_LUT(matrix, total_prof_per_phase, card_phases, encoding_segments,
                        prof_per_phase, spiral_inout:bool=False, self_gate:bool=True,
                        r_max_search: int = 10):

    # Initialize some parameters
    golden_increment = 1.8416

    spiral_twist = 1

    theta = 0
    radius = 0. if spiral_inout else 1.
    sampled_center = False
    prof_counter = 0

    d_r = 1 / (prof_per_phase - 1)

    # Define LUT
    LUT = np.zeros([2, total_prof_per_phase, card_phases, encoding_segments])

    # define sampling matrix
    sampling_mtx = np.zeros([matrix[1], matrix[2], card_phases, encoding_segments])

    mtx_center = (np.floor(matrix[1] / 2).astype(int), np.floor(matrix[2] / 2).astype(int))
    mtx_max = (np.floor((matrix[1] - 1) / 2), np.floor((matrix[2] - 1) / 2))

    # generate map for optimal nearest search
    mi, mj = np.meshgrid(np.arange(-r_max_search, r_max_search + 1), np.arange(-r_max_search, r_max_search + 1))
    r_map = np.sqrt(mi ** 2 + mj ** 2)
    rsearch_map = list(np.unravel_index(np.argsort(r_map.flatten()), np.shape(r_map)))
    rsearch_map[0] = rsearch_map[0] - rsearch_map[0][0]
    rsearch_map[1] = rsearch_map[1] - rsearch_map[1][0]

    for seg in range(encoding_segments):
        for card in range(card_phases):
            for prof in range(total_prof_per_phase):
                rad = radius

                # Jitter radius
                if np.abs(rad)>d_r/2:
                    rad = rad - d_r*np.random.rand()

                # Get profile positions
                py = np.round(np.cos(theta-spiral_twist*np.pi*rad/2)*rad*mtx_max[0]).astype(int)
                pz = np.round(np.sin(theta-spiral_twist*np.pi*rad/2)*rad*mtx_max[1]).astype(int)

                # Convert to sampling matrix coordianates
                iy = py + mtx_center[0]
                iz = pz + mtx_center[1]

                # Keep center sample if not sampled already
                if py==0 and pz==0 and not sampled_center:
                    sampling_mtx[iy,iz,card,seg] = sampling_mtx[iy,iz,card,seg] + 1
                    sampled_center=True
                else: # Search for nearest available point to fill
                    # find closest zero
                    # We loop over the shifts from the point we want
                    for si, sj in zip(rsearch_map[0], rsearch_map[1]):

                        if sampling_mtx[np.clip(iy + si, a_min=0, a_max=sampling_mtx.shape[0] - 1),
                                        np.clip(iz + sj, a_min=0, a_max=sampling_mtx.shape[1] - 1),
                                        card, seg] == 0:
                            # If we find an in-bounds zero, we update that point
                            iy = iy + si
                            iz = iz + sj
                            sampling_mtx[iy, iz, card, seg] = sampling_mtx[iy, iz, card, seg] + 1
                            break
                        # otherwise we will just stay at the original point

                LUT[0, prof, card, seg] = iy - mtx_center[0]
                LUT[1, prof, card, seg] = iz - mtx_center[1]

                # Increment profile counter
                prof_counter += 1

                # If we reach the number of profiles per cardiac interval,
                # the spiral angle is incremented by the golden angle and radius is reset
                if prof_counter == prof_per_phase:
                    prof_counter = 0
                    theta = theta + golden_increment
                    radius = 0. if spiral_inout else 1.
                    # If we are self-gating, also we resample the center point on the next interval
                    if self_gate: sampled_center = False
                else:
                    # Otherwise we just update the radius
                    radius = radius + d_r if spiral_inout else radius - d_r

            # Cardiac phase finished, reset
            prof_counter = 0
            radius = 0. if spiral_inout else 1.
            sampled_center = False

    return LUT, sampling_mtx


def gen_4DFlow_sequence(system_specs: cmrseq.SystemSpec,
                        LUT: np.ndarray,
                        prof_per_phase: int,
                        matrix: np.ndarray,
                        resolution: np.ndarray,
                        venc_list:tuple,
                        venc_dir:tuple,
                        spoil_moments: tuple,
                        slice_thickness: Quantity,
                        adc_duration: Quantity,
                        flip_angle: Quantity,
                        pulse_duration: Quantity,
                        slice_position_offset: Quantity = Quantity(0., "m"),
                        time_bandwidth_product: float = 4.,
                        venc_duration:Quantity = Quantity(0.,'ms'),
                        rf_spoiling:bool=False,
                        balanced:bool=False,
                        bal_norewind:bool=False):

    # kspace extent
    k_ext = 1 / resolution.to('m')

    num_samples = matrix[0]

    # kspace step size
    dk = k_ext / matrix

    # --- Generate reference sequence blocks ---

    if balanced:
        spoil_moments = (0,0,0)
    # First calculate spoiling area
    spoiler_area = (Quantity(spoil_moments,'rad')/system_specs.gamma_rad/resolution).to('mT/m*ms')


    # Get reference sequence that will have P and S prewind/rewind gradients scaled later
    fastseq = spoiled_3D_cartesian_line(system_specs=system_specs,
                                         num_samples=num_samples,
                                         k_M_total=k_ext[0],
                                         k_P=k_ext[1] / 2,
                                         k_S=k_ext[2] / 2,
                                         adc_duration=adc_duration,
                                         spoiler_area=spoiler_area)
    # Scale P and S to unit area
    fastseq.get_block('prephaser_P_0').scale_gradients(1/fastseq.get_block('prephaser_P_0').area[1].m_as('mT/m*ms'))
    fastseq.get_block('prephaser_S_0').scale_gradients(1/fastseq.get_block('prephaser_S_0').area[2].m_as('mT/m*ms'))

    fastseq.get_block('prephaser_P_rewind_0').scale_gradients(1/fastseq.get_block('prephaser_P_rewind_0').area[1].m_as('mT/m*ms'))
    fastseq.get_block('prephaser_S_rewind_0').scale_gradients(1/fastseq.get_block('prephaser_S_rewind_0').area[2].m_as('mT/m*ms'))

    if slice_thickness is not None:
        # generate RF pulse
        rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(system_specs=system_specs,
                                                                      slice_thickness=slice_thickness,
                                                                      flip_angle=flip_angle,
                                                                      pulse_duration=pulse_duration,
                                                                      time_bandwidth_product=time_bandwidth_product,
                                                                      slice_position_offset=slice_position_offset,
                                                                      slice_normal=np.array([0., 0., 1.]))

        #Add prewinder to RF
        rf_prewind = deepcopy(rf_seq.get_block('slice_select_rewind_0'))
        rf_prewind.shift(-rf_prewind.tmin)

        rf_seq.shift_in_time(rf_prewind.duration)
        rf_seq.add_block(rf_prewind)

    else:
        rf_pulse = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                                flip_angle=flip_angle,
                                                duration=pulse_duration,
                                                name='rf_excitation')
        rf_seq = cmrseq.Sequence([rf_pulse],system_specs=system_specs)

    # generate bipolar gradient
    # First generate fastest bipolar for the strongest case (minimum venc)
    vms = np.array([_.m_as('m/s') for _ in venc_list])
    vms = vms[np.nonzero(vms)]
    # If there are no non-zero values, set min venc to zero
    if len(vms)==0:
        venc_min = Quantity(0., 'm/s')
    else: # Otherwise we calculate the fastest gradient
        venc_min = Quantity(np.min(vms), 'm/s')
        bip_fastest = cmrseq.parametric_definitions.velocity.bipolar(system_specs=system_specs,
                                                                     venc=venc_min,
                                                                     direction=np.array([0.,0.,1.]))
        if bip_fastest.duration > venc_duration:
            venc_duration = bip_fastest.duration


    bipolars = []
    for venc,dir in zip(venc_list,venc_dir):
        bip = cmrseq.parametric_definitions.velocity.bipolar(system_specs=system_specs,
                                                             venc=venc,
                                                             duration=venc_duration,
                                                             direction=dir)
        bipolars.append(bip)


    # Scaling area by this factor results in a traverse of dk
    dk_area_scale = (dk/system_specs.gamma).m_as('mT/m*ms')

    # number of expected blocks of all segs
    expected_blocks = np.ceil(LUT.shape[1] / prof_per_phase).astype(int)

    seq_list = []

    # Array containing empty lists
    LUT_return = np.zeros([4, LUT.shape[1]*LUT.shape[2]*LUT.shape[3]])
    scount = 0
    rf_phase_init = Quantity(117,'degree').to('rad')

    pbar = tqdm(range(expected_blocks), desc="Loop - Blocks")
    for block in pbar:
        pbar2 = tqdm(range(LUT.shape[3]), desc="Loop - Encoding directions",leave=False)
        for seg in pbar2:

            # Every segment represents a new heartbeat
            seq_beat_list = []
            # Loop over heart phases
            for phase in range(LUT.shape[2]):

                # Loop over profiles per phase
                for prof in range(prof_per_phase):

                    if prof+prof_per_phase*block >= LUT.shape[1]:
                        break

                    # Extract P and S locations and make one TR
                    kP = LUT[0, prof + prof_per_phase * block, phase, seg]
                    kS = LUT[1, prof + prof_per_phase * block, phase, seg]

                    # Store some info for sorting during recon
                    LUT_return[0,scount] = kP
                    LUT_return[1, scount] = kS
                    LUT_return[2, scount] = seg
                    LUT_return[3, scount] = phase

                    readout = deepcopy(fastseq)
                    readout.get_block('prephaser_P_0').scale_gradients(kP * dk_area_scale[1])
                    readout.get_block('prephaser_S_0').scale_gradients(kS * dk_area_scale[2])

                    readout.get_block('prephaser_P_rewind_0').scale_gradients(kP * dk_area_scale[1])
                    readout.get_block('prephaser_S_rewind_0').scale_gradients(kS * dk_area_scale[2])

                    seq = deepcopy(rf_seq)

                    seq.append(bipolars[seg],copy=True)

                    seq.append(readout,copy=False)

                    # RF quadratic RF spoiling formula based on:
                    # 1. Zur Y, Wood ML, Neuringer LJ.
                    # Spoiling of transverse magnetization in steady‐state sequences.
                    # Magn. Reson. Med. 1991;21:251–263 doi: 10.1002/mrm.1910210210.
                    if rf_spoiling and not balanced:
                        rf_offset = rf_phase_init/2*(scount**2+scount+2)
                        seq.get_block('rf_excitation_0').phase_offset = rf_offset
                        seq.get_block('adc_0').phase_offset = rf_offset

                    # If balanced, we adjust RF phase and add rewinder for bipolar at same time
                    elif balanced:

                        rf_offset = Quantity(np.mod(scount,2)*np.pi,'rad')
                        seq.get_block('rf_excitation_0').phase_offset = rf_offset
                        seq.get_block('adc_0').phase_offset = rf_offset

                        # if no rewind flag set, only add delay
                        if bal_norewind:
                            bip_rew = cmrseq.bausteine.Delay(system_specs=system_specs,
                                                             duration=venc_duration,
                                                             name='rewind_delay')
                            bip_rew = cmrseq.Sequence([bip_rew],system_specs=system_specs)
                        else:
                            bip_rew = deepcopy(bipolars[seg])
                            bip_rew.invert_gradients()

                        seq.append(bip_rew)



                    # Append this sequence to the list of the current heartbeat
                    seq_beat_list.append(seq)

                    scount = scount + 1

            # Once we have gone through all the phases, we are done with one heartbeat
            # This list, representing one heartbeat, is appended to the overall result
            seq_list.append(seq_beat_list)

    return seq_list, LUT_return

def _3D_cartesian_line(system_specs: cmrseq.SystemSpec,
                       num_samples: int,
                       k_M_total: Quantity,
                       k_P: Quantity,
                       k_S: Quantity,
                       adc_duration: Quantity,
                       delay: Quantity = Quantity(0., "ms"),
                       prephaser_duration: Quantity = None) -> cmrseq.Sequence:

    ro_amp = (k_M_total / adc_duration / system_specs.gamma).to("mT/m")
    adc_duration = system_specs.time_to_raster(adc_duration, raster="grad")

    readout_pulse = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        flat_duration=adc_duration,
        amplitude=ro_amp, delay=Quantity(0., "ms"),
        name="trapezoidal_readout"
    )

    prephaser_M_area = readout_pulse.area[0] / 2.
    prephaser_P_area = np.abs(k_P / system_specs.gamma)
    prephaser_S_area = np.abs(k_S / system_specs.gamma)

    # Total gradient traverse is a combination of ro and pe directions.
    # Need to solve as single gradient to ensure slew and strength restrictions are met
    combined_kspace_traverse = np.sqrt((prephaser_M_area * system_specs.gamma) ** 2 + k_P ** 2 + k_S ** 2)
    [_, fastest_prep_ramp, fastest_prep_flatdur] = system_specs.get_shortest_gradient(
        combined_kspace_traverse / system_specs.gamma)

    # If prephaser duration was not specified use the fastest possible prephaser
    if prephaser_duration is None:
        prephaser_duration = fastest_prep_flatdur + 2 * fastest_prep_ramp
        rise_time = fastest_prep_ramp
        flat_time=fastest_prep_flatdur
    else:
        # Check if duration is sufficient for _combined_ prephaser gradients
        if prephaser_duration < np.round(fastest_prep_flatdur + 2 * fastest_prep_ramp, 7):
            raise ValueError("Prephaser duration is to short for combined PE+RO k-space traverse.")
        # Recalculate combined traverse gradient based on prephaser duration
        combined_traverse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        duration=prephaser_duration,
        area=combined_kspace_traverse / system_specs.gamma,
        delay=Quantity(0,'ms'), name="comb")

        rise_time = combined_traverse.rise_time
        flat_time = combined_traverse.flat_duration

    readout_pulse.shift(prephaser_duration + delay)

    # Calculate gradients pulse for to be scaled

    g_unit = 1/(flat_time+rise_time)

    ro_prep_pulse = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                         orientation=np.array([-1., 0., 0.]),
                                                         flat_duration=flat_time,
                                                         rise_time=rise_time,
                                                         amplitude=g_unit*prephaser_M_area,
                                                         delay=delay, name="prephaser_M")

    prep_pulse_P = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                         orientation=np.array([0., 1., 0.]) * np.sign(k_P),
                                                         flat_duration=flat_time,
                                                         rise_time=rise_time,
                                                         amplitude=g_unit*prephaser_P_area,
                                                         delay=delay, name="prephaser_P")

    prep_pulse_S = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                         orientation=np.array([0., 0., 1.]) * np.sign(k_S),
                                                         flat_duration=flat_time,
                                                         rise_time=rise_time,
                                                         amplitude=g_unit*prephaser_S_area,
                                                         delay=delay, name="prephaser_S")

    if num_samples > 0:
        adc = cmrseq.bausteine.SymmetricADC(system_specs=system_specs, num_samples=num_samples,
                                            duration=adc_duration,
                                            delay=prephaser_duration + delay + readout_pulse.rise_time)
        seq = cmrseq.Sequence([ro_prep_pulse, prep_pulse_P, prep_pulse_S, readout_pulse, adc],
                              system_specs=system_specs)
    else:
        seq = cmrseq.Sequence([ro_prep_pulse, prep_pulse_P, prep_pulse_S, readout_pulse],
                              system_specs=system_specs)

    return seq


def balanced_3D_cartesian_line(system_specs: cmrseq.SystemSpec,
                               num_samples: int,
                               k_M_total: Quantity,
                               k_P: Quantity,
                               k_S: Quantity,
                               adc_duration: Quantity,
                               delay: Quantity = Quantity(0., "ms"),
                               prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """
    """

    # Generate reference 3D line
    seq = _3D_cartesian_line(system_specs=system_specs,
                             num_samples=num_samples,
                             k_M_total=k_M_total,
                             k_P=k_P,
                             k_S=k_S,
                             adc_duration=adc_duration,
                             delay=delay,
                             prephaser_duration=prephaser_duration)

    # Extract the prewinders and copy
    post_M = deepcopy(seq.get_block("prephaser_M_0"))
    post_P = deepcopy(seq.get_block("prephaser_P_0"))
    post_S = deepcopy(seq.get_block("prephaser_S_0"))

    # Flip P and S
    post_P.scale_gradients(-1)
    post_S.scale_gradients(-1)

    post_M.name = "prephaser_M_rewind"
    post_P.name = "prephaser_P_rewind"
    post_S.name = "prephaser_S_rewind"

    # Append to end of sequence
    rewind = cmrseq.Sequence([post_M, post_P, post_S], system_specs=system_specs)
    seq.append(rewind)

    return seq


def spoiled_3D_cartesian_line(system_specs: cmrseq.SystemSpec,
                              num_samples: int,
                              k_M_total: Quantity,
                              k_P: Quantity,
                              k_S: Quantity,
                              adc_duration: Quantity,
                              spoiler_area: List[Quantity],
                              delay: Quantity = Quantity(0., "ms"),
                              prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """
    """

    # Generate balanced reference 3D line
    seq = balanced_3D_cartesian_line(system_specs=system_specs,
                                     num_samples=num_samples,
                                     k_M_total=k_M_total,
                                     k_P=k_P,
                                     k_S=k_S,
                                     adc_duration=adc_duration,
                                     delay=delay,
                                     prephaser_duration=prephaser_duration)

    # get rewinders
    rewind_M = seq.get_block("prephaser_M_rewind_0")
    rewind_P = seq.get_block("prephaser_P_rewind_0")
    rewind_S = seq.get_block("prephaser_S_rewind_0")

    # Assume worst case scenario for adding gradients

    area_M = np.abs(spoiler_area[0]) + rewind_M.area[0]
    area_P = np.abs(spoiler_area[1]) + rewind_P.area[1]
    area_S = np.abs(spoiler_area[2]) + rewind_S.area[2]

    total_area = np.sqrt(area_M**2+area_P**2+area_S**2)

    # create combined readout and spoil gradient

    [_, rise_time, flat_time] = system_specs.get_shortest_gradient(total_area)

    # Re-generate the rewinders
    # First calculate area given these
    amp_rewind_M = rewind_M.area[0] / (rise_time+flat_time)
    amp_rewind_P = rewind_P.area[1] / (rise_time + flat_time)
    amp_rewind_S = rewind_S.area[2] / (rise_time + flat_time)

    rewind_M_new = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                        orientation=np.array([1., 0., 0.]) * np.sign(rewind_M.signed_amplitude[0]),
                                                        flat_duration=flat_time,
                                                        rise_time=rise_time,
                                                        amplitude=amp_rewind_M,
                                                        name="prephaser_M_rewind")

    rewind_P_new = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                        orientation=np.array([0., 1., 0.]) * np.sign(rewind_P.signed_amplitude[1]),
                                                        flat_duration=flat_time,
                                                        rise_time=rise_time,
                                                        amplitude=amp_rewind_P,
                                                        name="prephaser_P_rewind")

    rewind_S_new = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                        orientation=np.array([0., 0., 1.]) * np.sign(rewind_S.signed_amplitude[2]),
                                                        flat_duration=flat_time,
                                                        rise_time=rise_time,
                                                        amplitude=amp_rewind_S,
                                                        name="prephaser_S_rewind")

    spoil_rewind = cmrseq.Sequence([rewind_M_new,rewind_P_new,rewind_S_new],system_specs=system_specs)

    # Generate spoilers and add
    if not spoiler_area[0] == 0:
        area_spoil_M = np.abs(spoiler_area[0]) / (rise_time+flat_time)
        spoiler_M = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                        orientation=np.array([1., 0., 0])*np.sign(spoiler_area[0]),
                                                        flat_duration=flat_time,
                                                        rise_time=rise_time,
                                                        amplitude=area_spoil_M,
                                                        name="spoil_M")
        spoil_rewind.add_block(spoiler_M)

    if not spoiler_area[1] == 0:
        area_spoil_P = np.abs(spoiler_area[1]) / (rise_time+flat_time)
        spoiler_P = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                        orientation=np.array([0., 1., 0])*np.sign(spoiler_area[1]),
                                                        flat_duration=flat_time,
                                                        rise_time=rise_time,
                                                        amplitude=area_spoil_P,
                                                        name="spoil_P")
        spoil_rewind.add_block(spoiler_P)

    if not spoiler_area[2] == 0:
        area_spoil_S = np.abs(spoiler_area[2]) / (rise_time+flat_time)
        spoiler_S = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                        orientation=np.array([0., 0., 1])*np.sign(spoiler_area[2]),
                                                        flat_duration=flat_time,
                                                        rise_time=rise_time,
                                                        amplitude=area_spoil_S,
                                                        name="spoil_S")
        spoil_rewind.add_block(spoiler_S)


    # Remove old rewinders

    seq.remove_block("prephaser_M_rewind_0")
    seq.remove_block("prephaser_P_rewind_0")
    seq.remove_block("prephaser_S_rewind_0")

    # append new rewind/spoil
    seq.append(spoil_rewind)

    return seq