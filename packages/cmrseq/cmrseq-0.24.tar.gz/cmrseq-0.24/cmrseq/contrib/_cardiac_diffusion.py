__all__ = ["se_m012_ssepi"]

import itertools
from copy import deepcopy
from typing import List

import cmrseq
from pint import Quantity
import numpy as np


def se_m012_ssepi(echo_time: Quantity, slice_thickness: Quantity, slice_pos_offset: Quantity, 
                  field_of_view: Quantity, matrix_size: np.ndarray, b_vectors: Quantity, 
                  max_bval: Quantity = Quantity(450, "s/mm^2"), water_fat_shift = "minimum",
                  diff_raster_time: Quantity = Quantity(0.1, "ms"),
                  spoiler_duration = Quantity(1.5, "ms"),
                 ) -> List[cmrseq.Sequence]:
    """Defines a spin echo single shot EPI with second order motion compensated
    diffusion Weighting

    !!!WIP!!!
    """
    system_specs_diff = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                          max_slew=Quantity(100., "mT/m/ms"),
                                          b0=Quantity(1.5, "T"),
                                          rf_peak_power=Quantity(30, "uT"),
                                          grad_raster_time=diff_raster_time,
                                          rf_raster_time=diff_raster_time)
    
    system_specs_epi = cmrseq.SystemSpec(max_grad=Quantity(45, "mT/m"),
                                          max_slew=Quantity(80., "mT/m/ms"),
                                          b0=Quantity(1.5, "T"),
                                          rf_peak_power=Quantity(30, "uT"),
                                          grad_raster_time=diff_raster_time,
                                          rf_raster_time=diff_raster_time)
    
    excitation_seq = cmrseq.seqdefs.excitation.spectral_spatial_excitation(
                                        system_specs_diff, binomial_degree=3, 
                                        total_flip_angle=Quantity(90, "degree"), 
                                        slice_thickness=slice_thickness,
                                        time_bandwidth_product=4.5, chemical_shift=3.4)
    excite_rf_center = np.stack([excitation_seq.get_block(bn).rf_events[0]
                                 for bn in excitation_seq.blocks if "rf" in bn]).mean()

    refocus_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                    system_specs_diff, slice_thickness=slice_thickness,
                                    flip_angle=Quantity(180, "degree"), 
                                    time_bandwidth_product=4,
                                    slice_position_offset=slice_pos_offset)
    
    refocus_seq.remove_block("slice_select_rewind_0")
    refocus_seq.rename_blocks(["rf_excitation_0", "slice_select_0"],
                              ["rf_refocus", "slice_select_refocus"])
    refocus_rf_center = refocus_seq.get_block("rf_refocus_0").rf_events[0]
    refocus_seq.shift_in_time(excite_rf_center - refocus_rf_center + echo_time / 2)


    diffusion_seq = cmrseq.seqdefs.diffusion.shortest_m012(system_specs_diff, 
                                                           np.array([1, 0, 0]), 
                                                           bvalues=max_bval, flip_decoding=True)
    diff_decode_start = diffusion_seq.get_block("diffusion_decode_0").tmin
    
    diffusion_seq.shift_in_time(- diff_decode_start + refocus_seq.end_time + spoiler_duration)
    # diffusion_seq._system_specs = system_specs

    max_epi_duration = 2 * (echo_time + excite_rf_center - (diffusion_seq.end_time - refocus_rf_center)) - Quantity(5, "ms")
    
    epi_seq = cmrseq.seqdefs.readout.single_shot_epi(system_specs_epi, 
                                                     field_of_view=field_of_view,
                                                     matrix_size=matrix_size,
                                                     slope_sampling=True, 
                                                     water_fat_shift=water_fat_shift,
                                                     max_total_duration=max_epi_duration,
                                                     partial_fourier_lines=0                                                     
                                                     )
    
    k_center_time = epi_seq.get_block(f"adc_{np.floor(matrix_size[1]/2).astype(int)}").adc_center
    epi_seq.shift_in_time(-k_center_time + echo_time + excite_rf_center)
    epi_seq._system_specs = system_specs_diff
    base_seq = deepcopy(excitation_seq)
    base_seq += refocus_seq
    base_seq += epi_seq
          
    zeta = diffusion_seq.get_block("diffusion_encode_0").rise_time
    lambda_ = diffusion_seq.get_block("diffusion_encode_0").flat_duration
    sequences = []
    for b_vec in b_vectors:   
        b_value = Quantity(np.linalg.norm(b_vec.m_as("(s/mm^2)^(1/2)")) ** 2, "s/mm^2")
        if b_value > 0:
            diff_dir = (b_vec / np.sqrt(b_value)).m
        else:
            diff_dir = np.array([1., 0., 0.])
        diff_seq =  cmrseq.seqdefs.diffusion.m012(system_specs_diff, zeta, lambda_, diff_dir, 
                                                  bvalue=b_value, flip_decoding=True)
        diff_seq.shift_in_time(- diff_decode_start + refocus_seq.end_time + spoiler_duration)
        # diff_seq._system_specs = system_specs
        
        temp_seq = deepcopy(base_seq)
        temp_seq += diff_seq
        # temp_seq._system_specs = system_specs_diff
        sequences.append(temp_seq)  

    sequences_flip = [deepcopy(seq) for seq in sequences]
    for seq in sequences_flip:
        for bn in ["diffusion_encode_0", "diffusion_encode_1",
                   "diffusion_decode_0", "diffusion_decode_1"]:
            seq.get_block(bn).scale_gradients(-1)
    sequences.extend(sequences_flip)   
    
    return sequences    
    