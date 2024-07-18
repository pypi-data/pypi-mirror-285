from typing import TYPE_CHECKING
from collections import OrderedDict
import numpy as np
from pint import Quantity

if TYPE_CHECKING:
    from cmrseq import Sequence

def report(seq: 'cmrseq.Sequence', format: str = "str"):
    """Creates Sequence report in specified format.
    Contained values:
      - Counter per block type
      - Non-unique block names
      - Flip angles of RF-events
      - RF-peak power of RF-waveforms
      - Center-timing of acquisition events
      - Max gradient per channel
      - Max gradient magnitude (norm of all axes)
      - Max gradient slew per channel
      - Max gradient slew norm

    :raises: NotImplementedError if format not in [str, json, html]

    :return: string in specified format
    """
    _report = _report_dict(seq)
    if format=="str":
        out = "Sequence Report:\n\t" + "\n\t".join([f"{k:<20}: {v}" for k, v in _report.items()])
    elif format=="json":
        import json
        out = json.dumps({k:str(v) for k,v in _report.items()})
    elif format=="html":
        out = '<table>'
        out += '<tr>' + "<th>Sequence Report</th>" + f" <th>  </th>" + '</tr>'
        for k, v in _report.items():
            out += '<tr>' + f" <td>{k:<20}</td>" + f" <td>{v} </td>" + '</tr>'
        out += '</table>'
    else:
        raise NotImplementedError(f"Specified format '{format}' not in available formats: [str, json, html]")
    return out


def _report_dict(seq: 'cmrseq.Sequence') -> OrderedDict:
    """ Creates a report of the given sequence in the specified format.

    :param seq:
    """
    block_counts = _count_blocks_per_type(seq)
    non_unique_names = set(["_".join(bn.split("_")[:-1]) for bn in seq.blocks])
    flip_angles = [_[1] for _ in seq.rf_events]
    rf_centers = [_[0] for _ in seq.rf_events]
    if flip_angles:
        peak_rf_power = np.max([np.max(np.abs(r.m_as("uT"))) for t, r in seq.rf])
    else:
        peak_rf_power = None
    adc_centers = np.stack(seq.adc_centers)
    t, grads = seq.combined_gradients()
    max_grad = Quantity(np.max(np.abs(grads), axis=1), "mT/m")
    max_grad_magnitude = Quantity(np.max(np.linalg.norm(grads, axis=0)), "mT/m")
    slew = np.diff(grads, axis=1) / np.diff(t)[np.newaxis]
    max_slew = Quantity(np.max(np.abs(slew), axis=1), "T/m/s")
    max_slew_magnitude = Quantity(np.max(np.linalg.norm(slew, axis=0)), "T/m/s")
    return OrderedDict(block_counts=block_counts, non_unique_names=non_unique_names,
                flip_angles=flip_angles, peak_rf_power=peak_rf_power,adc_centers=adc_centers,
                max_grad_perchannel=max_grad, max_grad_magn=max_grad_magnitude,
                max_slew_perchannel=max_slew, max_slew_magn=max_slew_magnitude)


def _count_blocks_per_type(seq: 'cmrseq.Sequence'):
    block_counts = {}
    for block in seq:
        btype = str(type(block)).split(".")[-1]
        current_count = block_counts.get(btype, 0)
        block_counts.update({btype:current_count+1})
    return block_counts

