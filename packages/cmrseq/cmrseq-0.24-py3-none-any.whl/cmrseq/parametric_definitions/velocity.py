""" This module contains functions defining compositions of building blocks commonly used in
flow MRI """
__all__ = ["bipolar", "flow_comp"]

from warnings import warn
import numpy as np
from pint import Quantity

import cmrseq


# pylint: disable=W1401, R0913, R0914, C0103
def bipolar(system_specs: cmrseq.SystemSpec,
            venc: Quantity,
            direction: np.ndarray,
            duration: Quantity = Quantity(0., 'ms'),
            repetitions: int = 1,
            start_time: Quantity = Quantity(0., "ms")) -> cmrseq.Sequence:
    """ Simplified definition of a bipolar M0-compensated gradient waveform:

    .. code-block:: python

         .                      | Delta |                        .
         .                      _____________   _______              .
         .                     /             \         |             .
         .                    / |             \        G             .
         .                   /  |              \       |             .
         .                  /   |               \ _____|             .
         .                 |    |                                    .
         .                  delta                                    .

    .. math::

        M1     =& (3 \\delta \Delta  + \Delta^2  + 2 \\delta^2) G \\\\
        \delta          =& G/s_{max} \\ \\ (use\\ max\\ slew) \\\\
        0 \stackrel{!}{=}& G\Delta^2  + \\frac{3G^2}{s_{max}} \Delta + \\frac{2G^3}{s_{max}^2} - M1

    Solve the quadratic equation to obtain the flat duration :math:`\Delta`

    .. Dropdown:: Example Plots
        :animate: fade-in-slide-down
        :icon: graph
        :color: secondary

        .. image:: ../_static/api/bipolar_venc.svg

    :param system_specs: SystemSpecifications
    :param venc: Quantity[Length/Time] velocity that corresponds to a phase accrual of 2pi
    :param direction: Vector (3, ) denoting the direction of velocity encoding
    :param duration: Quantity[Time] denoting the duration of applied VENC-gradients. If 0. the
                    resulting gradients will be the shortest for given system limits
    :param repetitions: number of repetitions
    :param start_time: Quantity[Time]
    :return: sequence object
    """

    if venc == 0:
        delay = cmrseq.bausteine.Delay(system_specs=system_specs, duration=duration, name="velocity_encode_delay")
        return cmrseq.Sequence([delay], system_specs=system_specs)

    if venc < 0:
        venc = np.abs(venc)
        direction = -direction

    m1_desired = (Quantity(np.pi, "rad") / system_specs.gamma_rad / venc).to('T*s**2/m') / repetitions

    # Start by solving equation to find flat duration for given m1 and max gradient specs
    a = system_specs.max_grad
    b = 3 * system_specs.max_grad ** 2 / system_specs.max_slew
    c = 2 * system_specs.max_grad ** 3 / system_specs.max_slew ** 2 - m1_desired

    flat_time = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)

    if flat_time < 0:  # if flat time is negative we have a triangular gradient
        flat_time = Quantity(0, 'ms')
        # Solve slightly modified equation for G (set T=0, eq 2)
        grad = ((m1_desired / 2 * system_specs.max_slew ** 2) ** (1 / 3)).to("mT/m")
        # Get rise time
        delta = grad / system_specs.max_slew
        # Round to gradient raster
        delta = round((delta / system_specs.grad_raster_time).to("dimensionless"))
        delta = delta * system_specs.grad_raster_time

        # If rounded to zero, allow one gradient raster rise time
        if delta == 0:
            delta = system_specs.grad_raster_time

        # Solve again with T=0 (eq 1)
        grad = m1_desired / 2 / delta ** 2

        # If required gradient is too strong, add extra raster time and recalculate
        if grad > system_specs.max_grad:
            delta = delta + system_specs.grad_raster_time
            grad = m1_desired / 2 / delta ** 2
        # If we now exceed slew rate, add another raster time and recalculate
        if grad / delta > system_specs.max_slew:
            delta = delta + system_specs.grad_raster_time
            grad = m1_desired / 2 / delta ** 2
        tend = 2 * delta

        # Check edge case in which adding single raster flat time is faster than triangular
        # This is due to the raster time rounding, since we require symmetric lobes
        # By adding a single raster flat time, we avoid needing to extend each lobe by 2 rasters

        delta_singflat = delta - system_specs.grad_raster_time
        flat_singflat = system_specs.grad_raster_time
        grad_singflat = delta_singflat * system_specs.max_slew

        m1_test = (grad_singflat*flat_singflat**2 +
                   3*delta_singflat*grad_singflat*flat_singflat +
                   2*grad_singflat*delta_singflat**2)

        if m1_test >= m1_desired:
            flat_time = flat_singflat
            delta = delta_singflat
            grad = grad_singflat * m1_desired / m1_test
            tend = 2 * delta + flat_time

    else:  # We have a trapezoidal gradient

        # Get flat time and rise time and round to grid
        flat_time = system_specs.time_to_raster(flat_time, raster="grad")
        delta = system_specs.get_shortest_rise_time(system_specs.max_grad)

        # Solve for first moment given flat time and max slew
        m1_cur = (3 * delta * flat_time * system_specs.max_grad
                  + system_specs.max_grad * flat_time ** 2
                  + 2 * system_specs.max_grad * delta ** 2)

        # If we are below required M1, increase flat time until we reach
        while m1_cur < m1_desired:
            flat_time = flat_time + system_specs.grad_raster_time
            m1_cur = (3 * delta * flat_time * system_specs.max_grad
                      + system_specs.max_grad * flat_time ** 2
                      + 2 * system_specs.max_grad * delta ** 2)

        # scale down gradient strength to match desired M1
        grad = system_specs.max_grad * m1_desired / m1_cur

        tend = 2 * delta + flat_time

    # User defined duration

    # Round lobe duration onto gradient raster time
    durlobe = system_specs.time_to_raster(duration / 2 / repetitions, raster="grad")
    tend = system_specs.time_to_raster(tend, raster="grad")
    # Check if duration is shorter than the previously generated fastest gradients
    if tend > durlobe:
        if duration != 0:
            warn("Velocity Bipolar Gradient: Duration set too short")

    elif tend < durlobe:  # Duration is longer, we will generate a trapezoidal gradient

        # Solve quadratic equation to get number of max slew raster periods
        am = -durlobe * system_specs.max_slew * system_specs.grad_raster_time ** 2
        bm = durlobe ** 2 * system_specs.max_slew * system_specs.grad_raster_time
        cm = -m1_desired
        N = (-bm + np.sqrt(bm ** 2 - 4 * am * cm)) / (2 * am)

        # round up
        N = np.ceil(N)
        delta = N * system_specs.grad_raster_time
        flat_time = durlobe - 2 * delta
        grad = system_specs.max_slew * delta

        # Scale back gradient strength to match desired first moment
        m1_cur = 3 * delta * flat_time * grad + grad * flat_time ** 2 + 2 * grad * delta ** 2
        grad = grad * m1_desired / m1_cur

    rise_time = delta.to("ms")
    flat_time = flat_time.to("ms")
    amplitude = grad.to("mT/m")

    normed_direction = direction / np.linalg.norm(direction)
    lobe_1 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                  orientation=normed_direction,
                                                  amplitude=amplitude,
                                                  flat_duration=flat_time,
                                                  delay=start_time,
                                                  rise_time=rise_time,
                                                  name="velocity_encode")
    lobe_2 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                  orientation=-normed_direction,
                                                  amplitude=amplitude,
                                                  flat_duration=flat_time,
                                                  delay=start_time + (2 * rise_time + flat_time),
                                                  rise_time=rise_time,
                                                  name="velocity_encode")

    seq = cmrseq.Sequence([lobe_1, lobe_2], system_specs=system_specs)

    for _ in range(1, repetitions):
        lobe_1 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                      orientation=normed_direction,
                                                      amplitude=amplitude,
                                                      flat_duration=flat_time,
                                                      delay=Quantity(0., "ms"),
                                                      rise_time=rise_time,
                                                      name="velocity_encode")
        lobe_2 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                      orientation=-normed_direction,
                                                      amplitude=amplitude,
                                                      flat_duration=flat_time,
                                                      delay=(2 * rise_time + flat_time),
                                                      rise_time=rise_time,
                                                      name="velocity_encode")
        seq.extend([lobe_1, lobe_2], copy=False)
    time, gradient_waveform = seq.gradients_to_grid()
    return seq


# pylint: disable=C0103, R0913, R0914, R0915
def flow_comp(system_specs: cmrseq.SystemSpec,
              venc_eff: Quantity,
              direction: np.ndarray,
              period: Quantity = Quantity(0., 'ms'),
              repetitions: int = 1,
              start_time: Quantity = Quantity(0., "ms")) -> cmrseq.Sequence:
    """ Defines a sequence of concatenated trapezoidals with flow-compensation over the full
    duration.

    .. Dropdown:: Example Plots
        :animate: fade-in-slide-down
        :icon: graph
        :color: secondary

        .. image:: ../_static/api/flow_compensated.svg

    :param system_specs:
    :param venc_eff:
    :param direction:
    :param period:
    :param repetitions:
    :param start_time:
    :return:
    """

    if venc_eff == 0:
        delay = cmrseq.bausteine.Delay(system_specs=system_specs, duration=period*repetitions, name = "flowcomp_encode_delay")
        return cmrseq.Sequence([delay],system_specs=system_specs)

    if venc_eff<0:
        venc_eff = np.abs(venc_eff)
        direction = -direction

    m1_eff = (Quantity(np.pi, "rad") / system_specs.gamma_rad / venc_eff).to('T*s**2/m')

    # Start by solving for the fastest possible flow compensated gradient

    # Solve quadratic equation to determine the flat time required for the given max first moment. Assumes trapezoidal
    # gradients
    a = system_specs.max_grad * (repetitions - 1 / 8)
    b = system_specs.max_grad ** 2 / system_specs.max_slew * (3 * repetitions)
    c = system_specs.max_grad ** 3 / system_specs.max_slew ** 2 * (2 * repetitions + 1 / 8) - m1_eff

    flat_time = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)

    if flat_time < 0:
        # Since the solution was negative, we will assume a fully triangular gradient

        # Solve for gradient strength with triangular gradients
        grad = ((m1_eff / (2 * repetitions - 1 + 3 / 4 * np.sqrt(2))
                 * system_specs.max_slew ** 2) ** (1 / 3)).to("mT/m")

        delta = grad / system_specs.max_slew #rise time

        delta = system_specs.time_to_raster(delta, raster="grad") #round rise time up to raster

        grad = (m1_eff / (delta ** 2 * (2 * repetitions - 1 + 3 / 4 * np.sqrt(2)))).to("mT/m") #recalculate gradient with rounded raster

        # Check if max gradient strength is exceeded somehow
        if grad > system_specs.max_grad:
            # add extra raster time to rise time to decrease gradient strength and recalculate
            delta = delta + system_specs.grad_raster_time
            grad = m1_eff / (delta ** 2 * (2 * repetitions - 1 + 3 / 4 * np.sqrt(2)))
        # If we now exceed slew rate, add another raster time and recalculate
        if grad / delta > system_specs.max_slew:
            delta = delta + system_specs.grad_raster_time
            grad = m1_eff / (delta ** 2 * (2 * repetitions - 1 + 3 / 4 * np.sqrt(2)))

        # round side lobe duration
        delta_side = system_specs.time_to_raster(delta / np.sqrt(2), raster="grad")

        # recalculate side lobe gradient strength
        grad_side = ((-m1_eff + grad * delta ** 2 * (np.sqrt(2) + 2 * repetitions - 1))
                     / delta_side ** 2).to("mT/m")

        flat_time = Quantity(0., "ms")
        flat_time_ends = Quantity(0., "ms")
        amplitude_ends = grad_side.to("mT/m")
        rise_time_ends = delta_side.to("ms")

    elif flat_time - system_specs.max_grad / system_specs.max_slew < 0:
        # trapezoidal, but first and last lobes are triangular

        # In this case the polynomial gains a square root term, making the analytic solution much more involved.
        # Instead we will ignore the root term to get a starting point and do a few steps of Newton's method to get to
        # a good approximation of the solution
        a = system_specs.max_grad * (repetitions - 1 / 2)
        b = system_specs.max_grad ** 2 / system_specs.max_slew * (3 * repetitions - 3 / 2)
        c = system_specs.max_grad ** 3 / system_specs.max_slew ** 2 * (2 * repetitions - 1) - m1_eff

        flat_time = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)

        delta = system_specs.get_shortest_rise_time(system_specs.max_grad)
        # now do a few iterative loops to converge on actual flat time
        for _ in range(3):
            # calculate maximum first moment
            m1_max = system_specs.max_grad * ((3 / 2 * (flat_time + delta)
                                               * np.sqrt((flat_time + delta) * delta / 2))
                                              + flat_time ** 2 * (repetitions - 1 / 2)
                                              + flat_time * delta * (3 * repetitions - 3 / 2)
                                              + delta ** 2 * (2 * repetitions - 1))
            # Calculate the gradient of the first moment with respect to the flat time
            dMdT = system_specs.max_grad * (9 / 4 * np.sqrt((flat_time + delta) * delta / 2)
                                            + flat_time * (2 * repetitions - 1)
                                            + delta * (3 * repetitions - 3 / 2))
            # Update flat time according to Newton's method
            flat_time = ((m1_eff - m1_max) / (dMdT)).to("ms") + flat_time

        # round onto raster time
        flat_time = system_specs.time_to_raster(flat_time, raster="grad")

        # calculate first moment
        m1_max = system_specs.max_grad * ((3 / 2 * (flat_time + delta)
                                           * np.sqrt((flat_time + delta) * delta / 2))
                                          + flat_time ** 2 * (repetitions - 1 / 2)
                                          + flat_time * delta * (3 * repetitions - 3 / 2)
                                          + delta ** 2 * (2 * repetitions - 1))

        # If we are below required M1, increase flat time by raster time until we reach desired M1
        while m1_max < m1_eff:
            flat_time = flat_time + system_specs.grad_raster_time
            m1_max = system_specs.max_grad * ((3 / 2 * (flat_time + delta)
                                               * np.sqrt((flat_time + delta) * delta / 2))
                                              + flat_time ** 2 * (repetitions - 1 / 2)
                                              + flat_time * delta * (3 * repetitions - 3 / 2)
                                              + delta ** 2 * (2 * repetitions - 1))

        # scale down gradient strength to match desired M1
        grad = system_specs.max_grad * m1_eff / m1_max

        # now need to check sidelobes

        # Get sidelobe duration, assuming triangular
        delta_side = np.sqrt((flat_time + delta) * delta / 2)
        # Round to raster
        delta_side = system_specs.time_to_raster(delta_side, raster="grad")

        # final check

        # Calculate current max M1
        m1_max = grad * (3 / 2 * (flat_time + delta) * delta_side +
                         flat_time ** 2 * (repetitions - 1 / 2) +
                         flat_time * delta * (3 * repetitions - 3 / 2) +
                         delta ** 2 * (2 * repetitions - 1))

        # Calculate final gradient strengths
        grad = grad * m1_eff / m1_max
        grad_side = grad / 2 * (flat_time + delta) / delta_side

        flat_time_ends = Quantity(0., "ms")
        amplitude_ends = grad_side.to("mT/m")
        rise_time_ends = delta_side.to("ms")

    else:
        # fully trapezoidal
        flat_time = system_specs.time_to_raster(flat_time, raster="grad")
        # Rise time is the fastest possible
        delta = system_specs.get_shortest_rise_time(system_specs.max_grad)

        # if (flat_time-delta)/2 is not on the grid, need to increase flat time by single raster
        if round(((flat_time - delta) / system_specs.grad_raster_time).m_as("dimensionless")) % 2 != 0:
            flat_time = flat_time + system_specs.grad_raster_time

        # Solve for first moment given flat time and max slew
        m1_max = system_specs.max_grad * ((repetitions - 1 / 8) * flat_time ** 2
                                          + 3 * repetitions * flat_time * delta
                                          + (2 * repetitions + 1 / 8) * delta ** 2)

        # If we are below required M1, increase flat time until we reach
        while m1_max < m1_eff:
            flat_time = flat_time + 2 * system_specs.grad_raster_time
            m1_max = system_specs.max_grad * ((repetitions - 1 / 8) * flat_time ** 2
                                              + 3 * repetitions * flat_time * delta
                                              + (2 * repetitions + 1 / 8) * delta ** 2)

        # scale down gradient strength to match desired M1
        grad = system_specs.max_grad * m1_eff / m1_max

        flat_time_ends = system_specs.time_to_raster((flat_time - delta) / 2, raster="grad")
        amplitude_ends = grad.to("mT/m")

        if ((flat_time - system_specs.max_grad / system_specs.max_slew) / 2
                < system_specs.grad_raster_time):
            # our final gradient is too short, increase flat time
            flat_time = flat_time + 2 * system_specs.grad_raster_time
            m1_max = system_specs.max_grad * ((repetitions - 1 / 8) * flat_time ** 2
                                              + 3 * repetitions * flat_time * delta +
                                              (2 * repetitions + 1 / 8) * delta ** 2)
            grad = grad * m1_eff / m1_max
            flat_time_ends = system_specs.time_to_raster((flat_time - delta) / 2, raster="grad")
            amplitude_ends = grad.to("mT/m")
        rise_time_ends = delta.to("ms")

    rise_time = delta.to("ms")
    flat_time = flat_time.to("ms")
    amplitude = grad.to("mT/m")

    lobe_time = system_specs.time_to_raster(period / 2, raster="grad")

    # If the user has defined a lobe time, check if it is possible
    if flat_time + 2 * rise_time >= lobe_time:
        # We use the previously computed fastest possible gradients and warn the user
        if period != 0:
            warn("Velocity Flow Compensated Gradient: Period set too short")
    else:
        # Specified period results in a longer gradient than the fastest possible.
        # This theoretically means that the gradient will be trapezoidal, however with raster gridding restrictions the
        # analytic solution becomes very complicated.

        # Instead we will reformulate the M1 max equation to solve for N where N is the number of raster rise times
        # in the central lobes, with the duration of the lobes fixed according to the user defined duration

        # But this is now a 3rd order polynomial... So we solve the general cubic equation :(
        # https://en.wikipedia.org/wiki/Cubic_equation
        A = (-3 / 8 * system_specs.max_slew * system_specs.grad_raster_time ** 3).m_as("ms**2*mT/m")
        B = ((1 / 2 - repetitions) * lobe_time * system_specs.max_slew
             * system_specs.grad_raster_time ** 2).m_as("ms**2*mT/m")
        C = ((repetitions - 1 / 8) * lobe_time ** 2 * system_specs.max_slew
             * system_specs.grad_raster_time).m_as("ms**2*mT/m")
        D = (- m1_eff.to("ms**2*mT/m")).m_as("ms**2*mT/m")

        # Difference of 0 and 1 resultants of the cubic and its derivatives
        Q = (2 * B ** 3 - 9 * A * B * C + 27 * A ** 2 * D) ** 2 - 4 * (B ** 2 - 3 * A * C) ** 3

        # Next we need the square root of  Q, but here we want an imaginary number if Q is negative
        if Q < 0:
            Q = 1j * (-Q) ** (1 / 2)
        else:
            Q = (Q) ** (1 / 2)

        # Some intermediate term. On the wiki this is called C
        P = (1 / 2 * (Q + 2 * B ** 3 - 9 * A * B * C + 27 * A ** 2 * D)) ** (1 / 3)

        # In our case, somehow we will only ever need this root, as it ends up being to only non-negative, real root... hopefully
        root = (-B / (3 * A) + P / (6 * A) * (1 + 1j * 3 ** (1 / 2))
                + (B ** 2 - 3 * A * C) / (6 * A * P) * (1 - 1j * 3 ** (1 / 2)))

        # First root according to wikipedia.
        # r1 = -B/(3*A) - P/(3*A) - (B**2-3*A*C) / (3*A*P)

        # Another root
        # r3 = -B / (3 * A) + P / (6 * A) * (1 - 1j * 3 ** (1 / 2))
        #       + (B ** 2 - 3 * A * C) / (6 * A * P) * (
        #            1 + 1j * 3 ** (1 / 2))

        # Number of rist times needed, rounded up
        N = np.ceil(np.real(root))  # number of rise times needed

        # Calculate relevant timings
        delta = N * system_specs.grad_raster_time
        flat_time = lobe_time - 2 * delta
        grad = system_specs.max_slew * delta

        # Check if start and end lobes are trapezoidal
        if flat_time - delta < 0:
            # Start/end are triangular, but now its worse than before.
            # So we revert to a fully iterative method, increasing the number of rise times until we reach the desried
            # max M1

            # initalize times and gradient
            delta = system_specs.grad_raster_time
            flat_time = lobe_time - 2 * delta
            grad = system_specs.max_slew * delta

            # Calculate initial first moment
            m1_max = grad * ((3 / 2 * (flat_time + delta)
                              * np.sqrt((flat_time + delta) * delta / 2))
                             + flat_time ** 2 * (repetitions - 1 / 2)
                             + flat_time * delta * (3 * repetitions - 3 / 2)
                             + delta ** 2 * (2 * repetitions - 1))

            # increase rise time by raster time until we exceed desired moment
            while m1_max < m1_eff:
                delta = delta + system_specs.grad_raster_time
                flat_time = lobe_time - 2 * delta
                grad = system_specs.max_slew * delta

                m1_max = grad * ((3 / 2 * (flat_time + delta)
                                  * np.sqrt((flat_time + delta) * delta / 2))
                                 + flat_time ** 2 * (repetitions - 1 / 2)
                                 + flat_time * delta * (3 * repetitions - 3 / 2)
                                 + delta ** 2 * (2 * repetitions - 1))
            # scale back gradients to match moment
            grad = system_specs.max_grad * m1_eff / m1_max

            # Check side lobes
            delta_side = np.sqrt((flat_time + delta) * delta / 2)
            delta_side = system_specs.time_to_raster(delta_side, raster="grad")
            grad_side = grad / 2 * (flat_time + delta) / delta_side

            # final check
            m1_max = grad * (3 / 2 * (flat_time + delta) * delta_side +
                             flat_time ** 2 * (repetitions - 1 / 2) +
                             flat_time * delta * (3 * repetitions - 3 / 2) +
                             delta ** 2 * (2 * repetitions - 1))

            grad = grad * m1_eff / m1_max

            grad_side = grad / 2 * (flat_time + delta) / delta_side

            flat_time_ends = Quantity(0., "ms")
            rise_time_ends = delta_side.to("ms")
            amplitude_ends = grad_side.to("mT/m")
            flat_time = flat_time.to("ms")

        else:
            # Trapezoidal side lobes
            # if (flat_time-delta)/2 is not on the grid, need to increase flat time by single raster
            if round(((flat_time - delta) /
                      system_specs.grad_raster_time).m_as("dimensionless")) % 2 != 0:
                flat_time = flat_time + system_specs.grad_raster_time
            # calculate moment
            m1_max = grad * ((repetitions - 1 / 8) * flat_time ** 2
                             + 3 * repetitions * flat_time * delta
                             + (2 * repetitions + 1 / 8) * delta ** 2)
            # scale back gradient to match desired moment
            grad = grad * m1_eff / m1_max
            flat_time_ends = system_specs.time_to_raster((flat_time - delta) / 2, raster="grad")
            amplitude_ends = grad.to("mT/m")
            rise_time_ends = delta.to("ms")
            flat_time = flat_time.to("ms")

        rise_time = delta.to("ms")
        amplitude = grad.to("mT/m")

    # All timing calculation done, assemble gradients
    normed_direction = direction / np.linalg.norm(direction)

    # starting lobe
    lobe = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                orientation=-normed_direction,
                                                amplitude=amplitude_ends,
                                                flat_duration=flat_time_ends,
                                                delay=start_time,
                                                rise_time=rise_time_ends,
                                                name="flow_compensated")

    seq = cmrseq.Sequence([lobe], system_specs=system_specs)

    # iterate over middle lobes
    for di in range(0, 2 * repetitions - 1):
        lobe = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                    orientation=(-1) ** di * normed_direction,
                                                    amplitude=amplitude,
                                                    flat_duration=flat_time,
                                                    delay=Quantity(0., "ms"),
                                                    rise_time=rise_time,
                                                    name="flow_compensated")
        seq.append(cmrseq.Sequence([lobe], system_specs=system_specs))

    # final lobe
    lobe = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                orientation=-normed_direction,
                                                amplitude=amplitude_ends,
                                                flat_duration=flat_time_ends,
                                                delay=start_time,
                                                rise_time=rise_time_ends,
                                                name="flow_compensated")
    seq.append(cmrseq.Sequence([lobe], system_specs=system_specs))
    return seq
