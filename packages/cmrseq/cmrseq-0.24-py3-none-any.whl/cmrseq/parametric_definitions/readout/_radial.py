__all__ = ["radial_spoke","balanced_radial_spoke","radial_3D_spiral_phyllotaxis","radial_3D_spiral_Roos"]

from copy import deepcopy
from pint import Quantity
import numpy as np

import cmrseq

def balanced_radial_spoke(system_specs: cmrseq.SystemSpec,
                          num_samples: int,
                          kr_max: Quantity,
                          angle: Quantity,
                          adc_duration: Quantity,
                          delay: Quantity = Quantity(0., "ms"),
                          prephaser_duration: Quantity = None) -> cmrseq.Sequence:

    seq = radial_spoke(system_specs=system_specs,num_samples=num_samples,
                       kr_max=kr_max,angle=angle,adc_duration=adc_duration,
                       delay=delay,prephaser_duration=prephaser_duration)

    # Copy prephasers
    rewind_block = deepcopy(seq.get_block("radial_prephaser_0"))

    # Shift to end of readout
    ro_duration = seq.get_block("radial_readout_0").duration
    rewind_block.shift(ro_duration + rewind_block.duration)

    rewind_block.name = "radial_prephaser_balance"

    seq += cmrseq.Sequence([rewind_block], system_specs=system_specs)
    return seq


def radial_spoke(system_specs: cmrseq.SystemSpec,
                 num_samples: int,
                 kr_max: Quantity,
                 angle: Quantity,
                 adc_duration: Quantity,
                 delay: Quantity = Quantity(0., "ms"),
                 prephaser_duration: Quantity = None) -> cmrseq.Sequence:

    adc_duration = system_specs.time_to_raster(adc_duration, raster="grad")

    ro_amp = (2 * kr_max / adc_duration / system_specs.gamma).to("mT/m")

    readout_pulse = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        flat_duration=adc_duration,
        amplitude=ro_amp, delay=Quantity(0., "ms"),
        name="radial_readout"
    )

    prephaser_area = readout_pulse.area[0] / 2.
    [_, fastest_prep_ramp, fastest_prep_flatdur] = system_specs.get_shortest_gradient(prephaser_area)

    if prephaser_duration is None:
        prephaser_duration = fastest_prep_flatdur + 2 * fastest_prep_ramp
    else:
        # Check if duration is sufficient for _combined_ prephaser gradients
        if prephaser_duration < np.round(fastest_prep_flatdur + 2 * fastest_prep_ramp, 7):
            raise ValueError("Prephaser duration is to short for combined PE+RO k-space traverse.")

    readout_pulse.shift(prephaser_duration + delay)

    prephaser_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
        system_specs=system_specs,
        orientation=np.array([-1., 0., 0.]),
        duration=prephaser_duration,
        area=prephaser_area,
        delay=delay, name="radial_prephaser")

    if num_samples > 0:
        adc = cmrseq.bausteine.SymmetricADC(system_specs=system_specs, num_samples=num_samples,
                                            duration=adc_duration,
                                            delay=prephaser_duration + delay + readout_pulse.rise_time)
        seq = cmrseq.Sequence([prephaser_pulse, readout_pulse, adc],
                               system_specs=system_specs)
    else:
        seq = cmrseq.Sequence([prephaser_pulse, readout_pulse],
                               system_specs=system_specs)

    sa = np.sin(angle).m_as('dimensionless')
    ca = np.cos(angle).m_as('dimensionless')
    R = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])

    seq.rotate_gradients(R)

    return seq


def radial_3D_spiral_Roos(system_specs: cmrseq.SystemSpec,
                          fnc: callable,
                          num_interleaves: int,
                          spokes_per_interleave: int,
                          samples_per_spoke: int,
                          kr_max: Quantity,
                          adc_duration: Quantity,
                          single_hemisphere: bool = False,
                          **kwargs):
    ref_spoke = fnc(system_specs=system_specs, angle=Quantity(0., 'rad'), num_samples=samples_per_spoke, kr_max=kr_max,
                    adc_duration=adc_duration,
                    **kwargs)

    R = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])

    seq_list = []

    first_spoke = deepcopy(ref_spoke)
    first_spoke.rotate_gradients(R.T)
    if not single_hemisphere:
        seq_list.append([first_spoke])

    for interleave in range(num_interleaves):
        interleave_list = []
        for spoke in range(spokes_per_interleave):

            if single_hemisphere:
                z = 1 - (spoke + 1) / spokes_per_interleave
            else:
                z = -(2 * (spoke + 1) - spokes_per_interleave - 1) / spokes_per_interleave * (-1) ** interleave

            x = np.cos(np.sqrt(spokes_per_interleave / num_interleaves * np.pi) * np.arcsin(
                z) + 2 * interleave * np.pi / num_interleaves) * np.sqrt(1 - z ** 2)
            y = np.sin(np.sqrt(spokes_per_interleave / num_interleaves * np.pi) * np.arcsin(
                z) + 2 * interleave * np.pi / num_interleaves) * np.sqrt(1 - z ** 2)

            r = np.sqrt(x ** 2 + y ** 2)
            R = np.array([[x, -y / r, -z * x / r],
                          [y, x / r, -z * y / r], [z, 0, r]])

            sp = deepcopy(ref_spoke)
            sp.rotate_gradients(R.T)

            interleave_list.append(sp)
        seq_list.append(interleave_list)

    return seq_list


def radial_3D_spiral_phyllotaxis(system_specs: cmrseq.SystemSpec,
                                 fnc: callable,
                                 num_interleaves: int,
                                 spokes_per_interleave: int,
                                 samples_per_spoke: int,
                                 kr_max: Quantity,
                                 adc_duration: Quantity,
                                 single_hemisphere: bool = False,
                                 **kwargs):
    ref_spoke = fnc(system_specs=system_specs, angle=Quantity(0., 'rad'), num_samples=samples_per_spoke, kr_max=kr_max,
                    adc_duration=adc_duration,
                    **kwargs)

    N_total = num_interleaves * spokes_per_interleave
    GA = 137.51 / 180 * np.pi

    if single_hemisphere:  # As per publication
        angles_az = (np.arange(0, N_total) * GA).reshape(spokes_per_interleave, num_interleaves).T
        angles_polar = (np.pi / 2 * np.sqrt(np.arange(0, N_total) / N_total)).reshape(spokes_per_interleave,
                                                                                      num_interleaves).T
    else:  # Modified to continue traverse into second hemisphere
        N_hem1 = np.ceil(N_total / 2)
        N_hem2 = np.floor(N_total / 2)

        # Angles increase with sqrt(n) until equator, then reverse same scaling in second hemisphere
        angles_polar_1 = np.pi / 2 * np.sqrt(np.arange(0, N_hem1) / N_hem1)
        angles_polar_2 = np.pi / 2 * (2 - np.sqrt((N_hem2 - np.arange(0, N_hem2)) / N_hem1))

        # Azimuthal angles follow GA
        angles_az = (np.arange(0, N_total) * GA).reshape(spokes_per_interleave, num_interleaves).T

        # Combine set of angles and reshape into array
        angles_polar = np.concatenate([angles_polar_1, angles_polar_2])
        angles_polar = angles_polar.reshape(spokes_per_interleave, num_interleaves).T

        # Reverse every second spiral
        angles_polar[1::2, :] = np.flip(angles_polar[1::2, :], axis=1)
        angles_az[1::2, :] = np.flip(angles_az[1::2, :], axis=1)

    seq_list = []

    for az_interleave, polar_interleave in zip(angles_az, angles_polar):
        interleave = []
        for az, polar in zip(az_interleave, polar_interleave):
            ca = np.cos(az)
            sa = np.sin(az)

            cp = np.cos(polar)
            sp = np.sin(polar)

            R = np.array([[ca * sp, -sa, -cp * ca],
                          [sa * sp, ca, -cp * sa], [cp, 0, sp]])

            seq = deepcopy(ref_spoke)
            seq.rotate_gradients(R.T)
            interleave.append(seq)

        seq_list.append(interleave)

    return seq_list
