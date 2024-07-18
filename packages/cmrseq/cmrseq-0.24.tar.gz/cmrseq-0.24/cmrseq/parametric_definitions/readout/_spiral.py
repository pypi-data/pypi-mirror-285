""" Private submodule containing spiral trajectory generation code"""
__all__ = ["spiral_pipezwart","pipe_WHIRLED_PEAS"]

from pint import Quantity
import numpy as np

import cmrseq


# pylint: disable=W1401, R0913, R0914, C0103
def spiral_pipezwart(system_specs: cmrseq.SystemSpec,
                     interleaves: int,
                     kr_max: Quantity,
                     kr_delta: Quantity,
                     spiral_type: str = "archimedean",
                     gradient_rewind_type: str = "ramp down",
                     undersampling_type: str = "none",
                     undersampling_start: float = 1.,
                     undersampling_end: float = 1.,
                     undersampling_factor: float = 1.,
                     kz_max: Quantity = Quantity(1., "1/m"),
                     kz_delta: Quantity = Quantity(1., "1/m")
                     ) -> cmrseq.bausteine.ArbitraryGradient:
    """ Generates spiral trajectory. Ported from C code provided along with:
    Pipe JG, Zwart NR. Spiral trajectory design: A flexible numerical algorithm and base
    analytical equations. Magn. Reson. Med. 2014;71:278–285 doi: 10.1002/mrm.24675.

    Original C code can be found at https://www.ismrm.org/mri_unbound/sequence.htm

    Some small changes to indexing when defining rewinder gradients and to address slew rate
     violations

    :warning: If not rewound, gradient waveform does not end on 0 magnitude, therefore it is likely
                to violate subsequent sequence validation.

    :param system_specs: SystemSpecifications
    :param interleaves: number of interleaved spirals
    :param kr_max: :math:`FOV_{kr, max}` corresponding to minimal radial
                    resolution :math:`1/\Delta r`
    :param kr_delta: k-space radial step-length
    :param spiral_type: str from ['Archimedean', 'spherical dst'] denoting the type of spiral
    :param gradient_rewind_type:  From [None, 'ramp down', 'rewind to center'] denoting the type
                                  of gradient rewind. If None is specified, the gradient waveform
                                  will not end on 0 magnitude, potentially violating subsequent
                                  sequence-validation
    :param undersampling_type: str from ['linear', 'quadratic', 'hanning'] defining the type of
                                undersampling during acquisition
    :param undersampling_start:
    :param undersampling_end:
    :param undersampling_factor:
    :param kz_max:
    :param kz_delta:
    :return: Gradient block containing the spiral waveform
    """
    ## internal parameters
    raster_subdivision = 4

    max_array = int(100 / system_specs.grad_raster_time.m_as("ms"))  # Assuming maximum 100ms spiral

    internal_raster = system_specs.grad_raster_time / raster_subdivision

    nyquist = interleaves * kr_delta

    gamrast = internal_raster * system_specs.gamma
    dgc = internal_raster * system_specs.max_slew  # max gradient change per internal raster

    sub_gamrast = gamrast * raster_subdivision
    sub_dgc = dgc * raster_subdivision

    # initialize arrays
    gsign = np.ones(raster_subdivision * max_array)
    kx = Quantity(np.zeros(raster_subdivision * max_array), "1/m")
    ky = Quantity(np.zeros(raster_subdivision * max_array), "1/m")
    kz = Quantity(np.zeros(raster_subdivision * max_array), "1/m")
    gxarray = Quantity(np.zeros(max_array), "mT/m")
    gyarray = Quantity(np.zeros(max_array), "mT/m")
    gzarray = Quantity(np.zeros(max_array), "mT/m")

    # start out spiral going radially at max slew-rate for 2 time-points
    kr_lim = kr_max - kr_delta / 2

    kx[1] = gamrast * dgc
    kx[2] = 3 * gamrast * dgc

    if spiral_type.lower() == "spherical dst":
        kz[0] = kz_max
        kz[1] = np.sqrt(kz_max ** 2 * (1 - ((kx[1] ** 2 + ky[1] ** 2) / kr_max ** 2)))
        kz[2] = np.sqrt(kz_max ** 2 * (1 - ((kx[2] ** 2 + ky[2] ** 2) / kr_max ** 2)))

    i = 2
    kr = kx[2]

    # Main loop

    while (kr <= kr_lim) and (i < (raster_subdivision * max_array - 1)):

        # determine k position at i+0.5 given constant velocity
        kmx = 1.5 * kx[i] - 0.5 * kx[i - 1]  # kx[i] + 0.5*(kx[i] - kx[i-1])
        kmy = 1.5 * ky[i] - 0.5 * ky[i - 1]
        kmr = np.sqrt(kmx ** 2 + kmy ** 2)

        # Calculate radial spacing

        rnorm = kmr / kr_max  # normalized k-space radius on [0,1]

        if rnorm <= undersampling_start:
            rad_spacing = 1
        elif rnorm < undersampling_end:
            us_i = (rnorm - undersampling_start) / (undersampling_end - undersampling_start)
            if undersampling_type.lower() == "linear":
                # Linear
                rad_spacing = 1 + (undersampling_factor - 1) * us_i
            elif undersampling_type.lower() == "quadratic":
                # Quadratic
                rad_spacing = 1 + (undersampling_factor - 1) * us_i ** 2
            elif undersampling_type.lower() == "hanning":
                # Hanning
                rad_spacing = 1 + (undersampling_factor - 1) * 0.5 * (1 - np.cos(us_i * np.pi))
            else:
                rad_spacing = 1
        else:
            rad_spacing = undersampling_factor

        # Undersample spiral for Spherical-Distributed Spiral
        if spiral_type.lower() == "spherical dst":
            if rnorm < 1.:
                rad_spacing = min(kz_max / kz_delta, rad_spacing / np.sqrt(1.0 - rnorm ** 2))
            else:
                rad_spacing = kz_max / kz_delta
        # Fermat spiral for floret
        if spiral_type.lower() == "fermat:floret" and rnorm > 0:
            rad_spacing *= 1. / rnorm

        # Set up spiral

        alpha = np.arctan(2 * np.pi * kmr / (rad_spacing * nyquist))
        phi = np.arctan2(kmy, kmx)
        theta = phi + alpha

        ux = np.cos(theta)
        uy = np.sin(theta)
        uz = 0
        gz = 0

        # Spherical DST
        if spiral_type.lower() == "spherical dst":
            kmz = 1.5 * kz[i] - 0.5 * kz[i - 1]
            uz = -((ux * kmx + uy * kmy) / kr_max ** 2) * (kz_max ** 2 / kmz)
            umag = np.sqrt(ux ** 2 + uy ** 2 + uz ** 2)
            ux = ux / umag
            uy = uy / umag
            uz = uz / umag
            gz = (kz[i] - kz[i - 1]) / gamrast

        # Find largest gradient amplitude for max slew

        gx = (kx[i] - kx[i - 1]) / gamrast
        gy = (ky[i] - ky[i - 1]) / gamrast

        term = dgc ** 2 - (gx ** 2 + gy ** 2 + gz ** 2) + (ux * gx + uy * gy + uz * gz) ** 2

        if term >= 0:
            gm = min((ux * gx + uy * gy + uz * gz) + gsign[i] * np.sqrt(term),
                     system_specs.max_grad)
            gx = gm * ux
            gy = gm * uy

            kx[i + 1] = kx[i] + gx * gamrast
            ky[i + 1] = ky[i] + gy * gamrast

            if spiral_type.lower() == "spherical dst":
                kz[i + 1] = np.sqrt(kz_max ** 2
                                    * (1 - ((kx[i + 1] ** 2 + ky[i + 1] ** 2) / kr_max ** 2)))

            i += 1
        else:
            while i > 3 and gsign[i - 1] == -1:
                i -= 1
            gsign[i - 1] = -1
            i = i - 2

        kr = np.sqrt(kx[i] ** 2 + ky[i] ** 2)
    # End of main loop

    # Now work on rewinders

    i_end = i

    gxsum = 0
    gysum = 0
    gzsum = 0
    j = 0
    for j in range(1, int(np.floor(i_end / raster_subdivision))):
        i1 = j * raster_subdivision
        i0 = (j - 1) * raster_subdivision
        gxarray[j] = (kx[i1] - kx[i0]) / sub_gamrast
        gyarray[j] = (ky[i1] - ky[i0]) / sub_gamrast
        gzarray[j] = (kz[i1] - kz[i0]) / sub_gamrast
        gxsum += gxarray[j]
        gysum += gyarray[j]
        gzsum += gzarray[j]

    gm = np.sqrt(gxarray[j] ** 2 + gyarray[j] ** 2 + gzarray[j] ** 2)
    ux = gxarray[j] / gm
    uy = gyarray[j] / gm
    uz = gzarray[j] / gm

    # Ramp to zero gradient
    if gradient_rewind_type is not None and (gradient_rewind_type.lower() == "ramp down"
                                             or gradient_rewind_type.lower() == "rewind to center"):
        gz_sum_ramp = 0

        j += 1

        while gm > 0 and j < max_array - 1:
            gm = max(Quantity(0., "mT/m"), gm - sub_dgc)
            gxarray[j] = gm * ux
            gyarray[j] = gm * uy
            gzarray[j] = gm * uz
            gxsum += gxarray[j]
            gysum += gyarray[j]
            gzsum += gzarray[j]
            gz_sum_ramp += gzarray[j]
            j += 1
    rampdown_end = j

    # Return to k=0
    if gradient_rewind_type is not None and gradient_rewind_type.lower() == "rewind to center":
        # Get direction for rewinder
        gsum = np.sqrt(gxsum ** 2 + gysum ** 2 + gzsum ** 2)
        # Only rewind x and y for spherical DST
        if spiral_type.lower() == "spherical dst":
            gsum = np.sqrt(gxsum ** 2 + gysum ** 2 + gz_sum_ramp ** 2)
        gsum0 = gsum
        ux = -gxsum / gsum
        uy = -gysum / gsum
        uz = -gzsum / gsum
        if spiral_type.lower() == "spherical dst":
            uz = -gz_sum_ramp / gsum
        gsum_ramp = 0.5 * gm * (gm / sub_dgc)

        # Ramp up strength and hold until ramp down will take us just past the center
        while gsum_ramp < gsum and j < (max_array - 1):
            gm = min(system_specs.max_grad, gm + sub_dgc)
            gxarray[j] = gm * ux
            gyarray[j] = gm * uy
            gzarray[j] = gm * uz
            gsum -= gm
            j += 1
            gsum_ramp = 0.5 * gm * (gm / sub_dgc)

        # extra point to prevent slew rate issues
        gm = min(system_specs.max_grad, gm + sub_dgc)
        gxarray[j] = gm * ux
        gyarray[j] = gm * uy
        gzarray[j] = gm * uz
        gsum -= gm
        j += 1

        # ramp down (with some overshoot for now)
        while gm > 0 and j < max_array - 1:
            gm = max(Quantity(0., "mT/m"), gm - sub_dgc)
            gxarray[j] = gm * ux
            gyarray[j] = gm * uy
            gzarray[j] = gm * uz
            gsum -= gm
            j += 1
        rewind_end = j

        # Correct rewinder to take us exactly to k=0
        gradtweak = gsum0 / (gsum0 - gsum)

        if gradtweak > 1:
            raise ValueError("Something went wrong in rewinder calculation, slew rate exceeded")

        for j in range(rampdown_end, rewind_end):
            gxarray[j] *= gradtweak
            gyarray[j] *= gradtweak
            gzarray[j] *= gradtweak

    # end of gradient adjustments

    # Create a gradient objects

    time = system_specs.grad_raster_time * np.arange(0, j + 1)
    wf = np.transpose(
        np.concatenate((gxarray[0:(j + 1), np.newaxis],
                        gyarray[0:(j + 1), np.newaxis],
                        gzarray[0:(j + 1), np.newaxis]), axis=1))
    gradient = cmrseq.bausteine.ArbitraryGradient(system_specs=system_specs,
                                                  time_points=time, waveform=wf,
                                                  name="spiral_readout")
    return gradient


def pipe_WHIRLED_PEAS(system_specs: cmrseq.SystemSpec,
                      interleaves: int,
                      fov: Quantity,
                      kr_max: Quantity,
                      freq_max: Quantity = Quantity(0,'Hz')):
    """ Generates WHIRL trajectory from analytic equations from James Pipe.

     Pipe JG. WHIRLED PEAS: Analytical Equations for Spiral Trajectories and Matching Gradient Waveforms.
     ISMRM Annual Meeting 2023
     Original code can be found at https://github.com/jim-pipe/whirled-peas

     :param system_specs: SystemSpecifications
     :param interleaves: number of interleaved spirals
     :param fov: field of view
     :param kr_max: :math:`FOV_{kr, max}` corresponding to minimal radial
                     resolution :math:`1/\Delta r`
     :param freq_max: maximum frequency of spiral rotation, optional
     :return:
     """


    # convert units to match those of Pipe's code

    delta = (interleaves/(2*np.pi*fov)).m_as('1/m')

    gamma = system_specs.gamma.m_as('Hz/mT')
    m_slew = system_specs.max_slew.m_as('mT/m/s')
    m_grad = system_specs.max_grad.m_as('mT/m')
    grast = system_specs.grad_raster_time.m_as('s')
    krad_max = kr_max.m_as('1/m')
    m_omega = 2*np.pi*freq_max.m_as('Hz')

    # Code take from : https://github.com/jim-pipe/whirled-peas
    # Start of Pipe code with minor modifications:
    #   Remove k-space sample calculation
    #   change math to np
    #   change narms to interleaves
    #   Remove all used of GPI

    ######################################
    # Find compatible constraints, so each segment does not have "negative" duration
    ######################################
    omega1 = np.sqrt(2. * gamma * m_slew / (3. * delta))
    omega2 = 2. * gamma * m_grad / (3. * delta)
    if m_omega > 0:
        omega_max = min([m_omega, omega1, omega2])
    else:
        omega_max = min([omega1, omega2])

    slew1 = m_grad * omega_max
    slew2 = np.sqrt((omega_max ** 4.) * (krad_max * krad_max - delta * delta) / (gamma * gamma))
    slew_max = min([m_slew, slew1, slew2])

    grad1 = ((slew_max * slew_max) * (krad_max * krad_max - delta * delta) / (gamma * gamma)) ** 0.25
    grad_max = min([m_grad, grad1])

    ######################################
    # Find timings
    # segments start at tx0, end at tx1, with total time t_X
    ######################################
    # Arc
    ta0 = 0
    ta1 = (5 * np.pi + 1) / (6. * omega_max)
    t_arc = ta1 - ta0

    # Omega Constrained
    tw0 = 1. / omega_max
    tw1 = (gamma * slew_max) / (delta * omega_max ** 3.)
    t_omega = tw1 - tw0

    # Slew Constrained
    ts0 = (2. * gamma * slew_max) / (3. * delta * omega_max ** 3.)
    ts1 = (2. * gamma * grad_max ** 3.) / (3. * delta * slew_max * slew_max)
    t_slew = ts1 - ts0

    # Gradient Constrained
    tg0 = (gamma * grad_max ** 3.) / (2. * delta * slew_max * slew_max)
    tg1 = (krad_max * krad_max - delta * delta) / (2. * gamma * delta * grad_max)
    t_grad = tg1 - tg0

    # gradient rampdown is a Hanning Window
    # This may help a little with spiral-in (??)
    t_ramp = np.pi * grad_max / m_slew

    tau_total = t_arc + t_omega + t_slew + t_grad
    tgd_total = tau_total + t_ramp

    ##########################
    # Compute waveforms
    ##########################

    gpts = int(tau_total // grast)
    rpts = int(t_ramp // grast)

    # gradient waveforms
    grad_out = np.zeros((interleaves, gpts + rpts, 2))

    ##########################
    # Define some constants
    ##########################
    arc_ta = np.pi / (3. * omega_max)
    arc_tb = (1 + 2. * np.pi) / (6. * omega_max)

    cga = delta * omega_max / (3. * gamma)
    cgw = (delta * omega_max * omega_max / gamma)
    cgs = (3. * delta * slew_max * slew_max / (2. * gamma)) ** (1. / 3.)
    cgg = grad_max

    cta = omega_max / 3.
    ctw = omega_max
    cts = (9. * gamma * slew_max / (4. * delta)) ** (1. / 3.)
    ctg = np.sqrt(2. * gamma * grad_max / delta)

    csa = cga / grad_max
    csw = cgw / grad_max
    css = cgs / grad_max
    csg = cgg / grad_max

    #######################
    # Compute GRADIENT
    #######################
    for i in range(gpts):
        t = float(i) * grast

        # -----
        # ARC |
        # -----
        if t < ta1:
            if t < arc_ta:
                gmag = cga * (1 - np.cos(3. * omega_max * t))
                theta = cta * (t - (np.sin(3. * omega_max * t) / (3. * omega_max)))
                theta = theta + 1 - (0.5 * np.pi)
            elif t < (arc_ta + arc_tb):
                tt = t - arc_ta
                gmag = 2. * cga
                theta = cta * (arc_ta + 2. * tt)
                theta = theta + 1 - (0.5 * np.pi)
            else:
                tt = t - arc_ta - arc_tb
                gmag = cga * (3 - np.cos(3. * omega_max * tt))
                theta = cta * (
                            arc_ta + (2. * arc_tb) + 3. * tt - (np.sin(3. * omega_max * tt) / (3. * omega_max)))
                theta = theta + 1 - (0.5 * np.pi)
        else:
            t = t - ta1 + tw0

            # -----
            # FRQ |
            # -----
            if t < tw1:
                gmag = cgw * t
                theta = ctw * t
            else:
                t = t - tw1 + ts0

                # ------
                # SLEW |
                # ------
                if t < ts1:
                    gmag = cgs * (t ** (1. / 3.))
                    theta = cts * (t ** (2. / 3.))
                else:
                    t = t - ts1 + tg0

                    # ------
                    # GRAD |
                    # ------
                    if t < tg1:
                        gmag = cgg
                        theta = ctg * np.sqrt(t)

        grad_out[0, i, 0] = gmag * np.cos(theta)
        grad_out[0, i, 1] = gmag * np.sin(theta)

    #############################
    # Compute GRADIENT RAMPDOWN #
    #############################

    for i in range(gpts, gpts + rpts):
        t = float(i) * grast - ta1 + tw0 - tw1 + ts0 - ts1 + tg0
        theta = ctg * np.sqrt(t)
        t = float(i - gpts) * grast
        gmag = cgg * 0.5 * (1. + np.cos(np.pi * t / t_ramp))
        grad_out[0, i, 0] = gmag * np.cos(theta)
        grad_out[0, i, 1] = gmag * np.sin(theta)


    # End of Pipe code, now convert to CMRseq format
    time = system_specs.grad_raster_time * np.arange(0, gpts+rpts)
    wf = Quantity(np.transpose(
        np.concatenate((grad_out[0, :, :],
                        np.zeros((gpts+rpts, 1))), axis=1)), 'mT/m')
    gradient = cmrseq.bausteine.ArbitraryGradient(system_specs=system_specs,
                                                  time_points=time, waveform=wf,
                                                  name="WHIRL_readout")

    return cmrseq.Sequence([gradient], system_specs=system_specs)