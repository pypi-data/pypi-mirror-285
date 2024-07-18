
from pint import Quantity
import numpy as np
import scipy.integrate

from cmrseq import Sequence

def calculate_diffusion_weighting(seq: Sequence, return_bmatrix: bool = False,
                                  return_cumulative: bool = False):
    """Evaluates the b-value or b-matrix of arbitrary gradient waveforms by numerical integration.

    :param seq: Sequence object, which is gridded to obtain hte waveform
    :param return_bmatrix: If True returns the b-matrix instead of the scalar b-value
    :param return_cumulative: if True returns the bvalue on raster-time resolution
    :return: Quantity of shape (1, ) or (t, ) depending on `return_cumulative` argument
    """
    time, gradient_waveform = seq.gradients_to_grid()

    # Integrate the waveform to obtain the zeroth oder moment at all times
    gradient_moment = scipy.integrate.cumulative_trapezoid(gradient_waveform, x=time,
                                                           initial=True, axis=1)
    q_of_t = (Quantity(gradient_moment, "mT/m*ms") * seq._system_specs.gamma_rad).to("1/mm")

    # compute the dot product per time step to obtain the squared gradient moment
    q_squared = Quantity(np.einsum('it, jt -> ijt', q_of_t.m_as("1/mm"), q_of_t.m_as("1/mm")),
                         "1/mm**2")
    q_squared = q_squared.reshape(9, -1)

    if return_cumulative:
        b_val_unitless = scipy.integrate.cumulative_trapezoid(q_squared.m, x=time, initial=True,
                                                              axis=-1)
    else:
        b_val_unitless = scipy.integrate.trapz(q_squared.m, x=time, axis=-1)

    if not return_bmatrix:
        b_val_unitless = np.trace(b_val_unitless.reshape(3, 3, -1), axis1=0, axis2=1)
    bvals = Quantity(b_val_unitless, f"{q_squared.units} * ms")
    return bvals.to("s/mm**2")