__all__ = ["GveCmrConvert", "GVEFile"]

from copy import deepcopy
from typing import List
import os
from warnings import warn

from scipy.spatial.transform import Rotation as ScipyRotation
from pint import Quantity
from tqdm import tqdm
import numpy as np

import cmrseq

RASTER_TIME = 6.4e-3  # ms

from time import perf_counter

class GVEFile:
    rf_amps: List
    rf_fm: List
    sequence_objects: List
    grad_waveforms: List
    filename: str
    version: str

    _VERSION_HR = ['SY', 'AQEX', 'AQCMPEX', 'RFEX', 'GREX']
    _VERSION_ALL = 2 ** 5 - 1
    _sq_object_sizes: List[dict]

    def __init__(self, filename: str):
        assert os.path.exists(filename)

        # self.rf_amps, self.rf_fm, self.sequence_objects, self.grad_waveforms = [], [], [], []
        self.filename = filename
        with open(self.filename, "rb") as _file_handle:
            id_version = np.fromfile(_file_handle, np.int32, 1)

            # Read raw waveform samples
            n_gradient_blocks = int(np.fromfile(_file_handle, np.int32, 1))
            self.grad_waveforms = [self.read_waveform(_file_handle) for _ in range(n_gradient_blocks)]

            n_rf_blocks = int(np.fromfile(_file_handle, np.int32, 1))
            self.rf_amps = [self.read_waveform(_file_handle) for _ in range(n_rf_blocks)]

            n_rf_blocks = int(np.fromfile(_file_handle, np.int32, 1))
            self.rf_fm = [self.read_waveform(_file_handle) for _ in range(n_rf_blocks)]

            # Read sequence objects
            n_sequence_objects = int(np.fromfile(_file_handle, np.int32, 1))
            self.sequence_objects = [self.parse_sequence_objects(_file_handle) for _ in
                                    tqdm(range(n_sequence_objects),
                                        desc="Reading sequence objects ...")]

            for sq_id in range(n_sequence_objects):
                self.sequence_objects[sq_id]["id"] = sq_id

            try:
                self._read_gveex(file=_file_handle)
            except Exception as e:
                import traceback
                warn(f"GVEFile: Encountered error in parsing information after actual waveforms. "
                    f"This could mean the GVE file is corrupted. Raised Exception:")
                traceback.print_exc()

    @staticmethod
    def read_waveform(file):
        """ Extracts the id, size and number of samples from the given file assuming the
        byte pointer is at the location of the waveform"""
        waveform = {}
        waveform["id"] = int(np.fromfile(file, np.int32, 1))
        waveform["size"] = int(np.fromfile(file, np.int32, 1))
        waveform["samples"] = np.fromfile(file, np.float32, waveform["size"])
        return waveform

    def parse_sequence_objects(self, file):

        sq_obj = dict()
        sq_obj["name"] = "".join([chr(c) for c in np.fromfile(file, np.int8, 32)]).strip()
        sq_obj["dur"] = float(np.fromfile(file, np.float32, 1))
        sq_obj["ref"] = float(np.fromfile(file, np.float32, 1))

        # Sequence block specific gradient parameters defining the name of the
        # gradient, the reference time point of the gradient, the gradient id
        # (connecting it to a certain gradient shape, see later in the script),
        sq_obj["gradients"] = []
        for ori_idx in range(3):
            n_gradient_blocks = int(np.fromfile(file, np.int32, 1))
            ori_grads = [self.read_gradient(file) for _ in range(n_gradient_blocks)]
            sq_obj["gradients"].append(ori_grads)

        # Sequence Breakpoints (Times at which ?one? gradient changes)
        sq_obj["breakpoints"] = [{}, {}, {}]
        for axis in range(3):
            length = int(np.fromfile(file, np.int32, 1))
            time, _str = np.fromfile(file, np.float32, 2*length).reshape(length, 2).T
            sq_obj["breakpoints"][axis].update(dict(time=time, str=_str))

        # Gradient shapes in x,y,z-dimension
        sq_obj["gradients_xyz"] = []
        for axis in range(3):
            length = int(np.fromfile(file, np.int32, 1))
            time, _str, _id, dur = np.fromfile(file, np.float32, 4 * length).reshape(length, 4).T
            sq_obj["gradients_xyz"].append(dict(time=time, str=_str, id=_id, dur=dur))

        # RF-pulse properties (shape, scale, ...)
        n_rf = int(np.fromfile(file, np.int32, 1))
        sq_obj["rf"] = [self.read_rf(file) for _ in range(n_rf)]

        # Aquisition objects (time of acquisition, ...)
        n_aq = int(np.fromfile(file, np.int32, 1))
        sq_obj["aq"] = [self.read_aq(file) for _ in range(n_aq)]

        return sq_obj


    @staticmethod
    def find_waveform(gradient_waveforms: List[dict], identifier: int):
        id_list = [wf["id"] for wf in gradient_waveforms]
        idx = id_list.index(identifier) if identifier in id_list else None
        if idx is not None:
            return gradient_waveforms[idx]
        return None

    def read_gradient(self, file):
        """ Parses a gradient object from the given byte-stream file object assuming following
        byte-order:

        name: (32bytes -> character arrray)
        time: (4bytes -> float32)
        ref: (4bytes -> float32)
        id: (4bytes -> int32)
        #break-points: (4bytes -> int32)

        break-point-timings, break-point-strength -> (4bytes, 4bytes) x #break-points -> (8x#bp)byte

        :param file:
        :return: gradient dictionary with keywords: (name, time, ref, id, bp)
        """

        name = "".join([chr(c) for c in np.fromfile(file, np.int8, 32)]).strip()
        dt = np.dtype("f4, f4, i4, i4")
        time, ref, id_, n_breakpoint = np.fromfile(file, dt, 1)[0]

        if n_breakpoint > 0:
            bp_time, _str = np.fromfile(file, np.float32, 2*n_breakpoint).reshape(-1, 2).T
            bp = dict(time=bp_time, str=_str)
            bp["time_resolved"] = bp_time - ref + time
        else:
            bp = dict(time=np.empty([n_breakpoint], np.float64),
                      str=np.empty([n_breakpoint], np.float64))

        gradient = dict(name=name, time=time, ref=ref, id=id_, bp=bp)

        if gradient["id"] != -1:
            waveform = {}
            g_wf = self.find_waveform(self.grad_waveforms, gradient["id"])
            waveform["str"] = (bp["str"][0] * g_wf["samples"]).flatten()
            waveform["time"] = np.arange(0, waveform["str"].shape[0]) * RASTER_TIME
            gradient["bp"] = waveform

        return gradient

    def read_rf(self, file):
        name = "".join([chr(c) for c in np.fromfile(file, np.int8, 32)])
        mem_block_names = ["start", "dur", "ref", "sign", "invert", "rep", "interval",
                           "am_id", "am_scale", "fm_id", "fm_scale", "nucleus"]
        mem_block_dtypes = ["f4", "f4", "f4", "i4", "i4", "i4", "i4", "i4", "f4", "i4", "f4", "i4"]
        mem_dt = [(n, d) for n, d in zip(mem_block_names, mem_block_dtypes)]
        temp = np.fromfile(file, mem_dt, 1)[0]
        s = {n:v for n, v in zip(mem_block_names, temp)}
        s.update(dict(name=name, am_waveform=[], fm_waveform=[]))

        if s["am_id"] != -1:
            s["am_waveform"] = self.find_waveform(self.rf_amps, s["am_id"])
        if s["fm_id"] != -1:
            s["fm_waveform"] = self.find_waveform(self.rf_fm, s["fm_waveform"])
        return s

    @staticmethod
    def read_aq(file):
        name = "".join([chr(c) for c in np.fromfile(file, np.int8, 32)])
        mem_block_names = ["start", "dur", "ref", "rep", "interval", "samples", "nucleus"]
        mem_block_dtypes = ["f4", "f4","f4", "i4", "f4", "i4", "i4"]
        mem_dt = [(n, d) for n, d in zip(mem_block_names, mem_block_dtypes)]
        temp = np.fromfile(file, mem_dt, 1)[0]
        s = {n:v for n, v in zip(mem_block_names, temp)}
        s["name"] = name.strip()
        return s

    def _read_gveex(self, file):
        version = np.fromfile(file, np.int32, 1)
        
        # If file is exhausted no extensions were appended
        if version.size == 0:
            return 
        version = int(version)

        self.version = 'legacy'
        if not (1 <= version < self._VERSION_ALL):
            warn("GVEFile: GVE Extension not found. Skipping. \n")
            return

        for n in range(len(self._VERSION_HR)):
            # Version is stored as binary mask for the 5  version_hr entries
            if bin(version)[2:][-(n + 1)] == "1":
                self.version = self.version + ":" + self._VERSION_HR[n]

        if "RFEX" in self.version:
            warn('GVEFile: GVE Extension found but RFEX not implemented yet. Skipping.\n')

        sq_add = int(np.fromfile(file, np.int32, 1))
        for n in tqdm(range(sq_add), desc=f"Reading extension info of version {self.version}"):
            sq_id = int(np.fromfile(file, np.int32, 1))
            try:
                self.sequence_objects[sq_id] = self.read_sqex(file, self.sequence_objects[sq_id])
            except IndexError:
                warn(f"GVEFile: Corrupted idx loaded for index {n} -> {sq_id} "
                     f"not in [0, {len(self.sequence_objects)}]")

    def read_sqex(self, file, sq_obj):

        if 'SY' in self.version:
            n_sy = int(np.fromfile(file, np.int32, 1))
            sy = [self.read_sy(file) for _ in range(n_sy)]
        else:
            sy = []
        sq_obj["sy"] = sy

        if "AQEX" in self.version:
            aq_check = int(np.fromfile(file, np.int32, 1))
            if not aq_check == len(sq_obj["aq"]):
                raise ValueError(f"In Sq ID {sq_obj['id']} (SQ: {sq_obj['name']}). AQEX check"
                                 f" failed: expected {aq_check} but got {len(sq_obj['aq'])}")
            for n in range(aq_check):
                sq_obj["aq"][n].update(self.read_aqex(file))

        if "AQCMPEX" in self.version:
            aq_check = int(np.fromfile(file, np.int32, 1))
            if not aq_check == len(sq_obj["aq"]):
                raise ValueError(f"In Sq ID {sq_obj['id']} (SQ: {sq_obj['name']}). AQCMPEX check"
                                 f" failed: expected {aq_check} but got {len(sq_obj['aq'])}")
            list_of_acq_dicts = [self.read_aqcmpex(file) for _ in range(aq_check)]
            sq_obj["aq"][0:aq_check] = list_of_acq_dicts

        b3 = perf_counter()
        if "RFEX" in self.version:
            rf_check = int(np.fromfile(file, np.int32, 1))
            if not rf_check == len(sq_obj["rf"]):
                raise ValueError(f"In Sq ID {sq_obj['id']} (SQ: {sq_obj['name']}). RFEX check"
                                 f" failed: expected {rf_check} but got {len(sq_obj['rf'])}")
        b4 = perf_counter()
        if "GREX" in self.version:
            for ori in range(3):
                gr_check = int(np.fromfile(file, np.int32, 1))
                if not gr_check == len(sq_obj["gradients"][ori]):
                    raise ValueError(f"In Sq ID {sq_obj['id']} (SQ: {sq_obj['name']}). GFEX check"
                                     f" failed: expected {gr_check} but got "
                                     f"{len(sq_obj['gradients'][ori])}")
                for n in range(gr_check):
                    sq_obj["gradients"][ori][n] = self.read_grex(file, sq_obj["gradients"][ori][n])

        return sq_obj

    @staticmethod
    def read_sy(file):
        name = "".join([chr(c) for c in np.fromfile(file, np.int8, 32)])
        mem_block_names = ["time", "pulse_dur", "scope", "graph_marker", "scan", "mpex", "pulse_bit"]
        mem_block_types = ["f4", "f4", "i4", "i4", "i4", "i4", "i4"]
        mem_dt = np.dtype([(n, d) for n, d in zip(mem_block_names, mem_block_types)])
        mem_read = np.fromfile(file, mem_dt, 1)[0]
        s = dict(name=name, **{n:v for n, v in zip(mem_block_names, mem_read)})
        return s

    @staticmethod
    def read_aqex(file):
        mem_block_names = ["measurement", "row_nr", "y_prof_nr", "z_prof_nr", "card_phase",
                           "dyn_scan", "echo", "location", "mix", "rtop_offset", "monitor_flag",
                           "rec_phase", "rf_echo"]
        mem_block_types = ["i4", ] * len(mem_block_names)
        mem_dt = np.dtype([(n, d) for n, d in zip(mem_block_names, mem_block_types)])
        mem_read = np.fromfile(file, mem_dt, 1)[0]
        s = {n:v for n, v in zip(mem_block_names, mem_read)}
        return s

    def read_aqcmpex(self, file):
        s = self.read_aqex(file)

        mem_block_names = ["progress_cnt", "diff_dir", "trigger_delay", "x_prof_nr",
                           "cur_index", "comp_elements"]

        mem_read = np.fromfile(file, np.int32, len(mem_block_names)).reshape(-1)
        s.update({n:v for n, v in zip(mem_block_names, mem_read)})
        element_names = ("x_profile", "y_profile", "z_profile", "sign", "grad_echo")
        n_elements = s["comp_elements"]
        temp = np.fromfile(file, np.int32, n_elements*len(element_names))
        s.update({n:v for n, v in zip(element_names, temp.reshape(-1, len(element_names)).T)})

        return s

    @staticmethod
    def read_grex(file, gradient_obj):
        name = "".join([chr(c) for c in np.fromfile(file, np.int8, 32)]).strip()
        if gradient_obj["name"] != name:
            raise ValueError(f"In 'read_grex' for gradient object '{gradient_obj['name']}' "
                             f"a non-matching extension for '{name}' was found")
        mem_block_names = ["repetition", "skip_x2", "interval", "skip_x1", "nRepetitions",
                           "alt_factor", "matrix_id"]
        mem_block_types = ["i4", "i8", "f4", "i4", "i4", "i4", "i4"]
        mem_dt = np.dtype([(n, d) for n, d in zip(mem_block_names, mem_block_types)])
        mem_read = np.fromfile(file, mem_dt, 1)[0]
        gradient_obj.update({n: v for n, v in zip(mem_block_names, mem_read) if "skip" not in n})

        if gradient_obj["matrix_id"] >= 2000000000:
            gradient_obj["matrix_id"] = []
            gradient_obj["o_matrix"] = []
        else:
            mem_block_names = ["m_direction_x", "m_direction_y", "m_direction_z",
                               "p_direction_x", "p_direction_y", "p_direction_z",
                               "s_direction_x", "s_direction_y", "s_direction_z",
                               "rotation_axis", "rotation_step", "rotation_factor"]
            mem_block_types = ["f4", "f4","f4","f4", "f4", "f4", "f4", "f4", "f4", "i4", "f4", "i4"]
            mem_dt = np.dtype([(n, d) for n, d in zip(mem_block_names, mem_block_types)])

            mem_read = np.fromfile(file, mem_dt, 1)[0]
            matrix = np.array([mem_read[i] for i in range(9)]).reshape(3, 3).T

            gradient_obj["o_matrix"] = dict(m_orient=matrix[:, 0],
                                            p_orient=matrix[:, 1],
                                            s_orient=matrix[:, 2],
                                            matrix=matrix,
                                            rotation_axis=mem_read[9],
                                            rotation_step=mem_read[10],
                                            rotation_factor=mem_read[11])
            axis = np.eye(3, 3)[:, mem_read[9]]
            rotation_obj = ScipyRotation.from_rotvec(mem_read[10] * mem_read[11] * axis / 180 * np.pi)
            gradient_obj["o_matrix"]["matrix_rotated"] = np.stack([rotation_obj.apply(matrix[:, i])
                                                                   for i in range(3)], axis=-1)

        haswf = int(np.fromfile(file, np.int32, 1))
        if haswf > 0:
            str_ = float(np.fromfile(file, np.float32, 1))
            size_ = int(np.fromfile(file, np.int32, 1))
            samples_ = np.fromfile(file, np.float32, size_)

            gradient_obj["bp"]["time"] = np.arange(0, size_) * RASTER_TIME
            gradient_obj["bp"]["str"] = samples_ * str_
            gradient_obj["bp"]["time_resolved"] = (gradient_obj["bp"]["time"]
                                                   - gradient_obj["ref"] + gradient_obj["time"])
        return gradient_obj


class GveCmrConvert(GVEFile):
    _block_lookup: dict

    def __init__(self, system_specs: cmrseq.SystemSpec, filepath: str = None):
        super(GveCmrConvert, self).__init__(filepath)
        self.system_specs = system_specs
        self._block_lookup = self._unique_name_lookup()

    def _unique_name_lookup(self):
        lut = {}
        for idx, seq_ob in enumerate(self.sequence_objects):
            block_list = lut.get(seq_ob["name"], None)
            if block_list is None:
                block_list = []
                lut[seq_ob["name"]] = block_list
            block_list.append(idx)
        return {f"{key}_{j}": idx for key in lut.keys() for j, idx in enumerate(lut[key])}

    @property
    def blocknames(self):
        return list(self._block_lookup.keys())

    def __call__(self, sq_names: list = None, rotate_to_xyz: bool = False):
        """Converts from the nested list/dict form of the loaded sequence to CMRseq objects

        :param sq_names: list of strings representing the sequence objects to convert, if None
            converts all
        """
        if sq_names is not None:
            seq_objs_to_use = [self.sequence_objects[self._block_lookup[name]] for name in sq_names]
        else:
            seq_objs_to_use = self.sequence_objects

        sequences = []
        for seq_obj in tqdm(seq_objs_to_use, desc="Converting to sequence"):
            kernel_list = self._parse_single_kernel(seq_obj, rotate_to_xyz)
            if len(kernel_list) > 0:
                cmrseq_obj = cmrseq.Sequence(building_blocks=kernel_list,
                                             system_specs=self.system_specs)
                sequences.append(cmrseq_obj)
        return sequences

    def _parse_single_kernel(self, seq_obj, rotate_to_xyz: bool):

        # Process Gradient events
        g_list = self._make_gradients(seq_obj, rotate_to_xyz)

        # Process RF events
        rf_list = [self._make_rf_block(rf_dict=rf) for rf in seq_obj["rf"]]

        # Process AQ events
        aq_list = [self._make_aq_block(aq_dict=aq) for aq in seq_obj["aq"] if aq.get("samples", 0) > 0]
        aq_list = [b for l in aq_list for b in l]

        # TODO: Translate seq_obj ref time to delay.
        return g_list + rf_list + aq_list

    def _make_gradients(self, sequence_obj, rotate_to_xyz: bool):
        sequence_blocks = []
        for direction, gradients in zip(np.eye(3, 3), sequence_obj["gradients"]):
            is_trap = [self._is_trapezoidal(g) for g in gradients]
            trapezoidals = [gradients[i] for i, v in enumerate(is_trap) if v]
            delays = [gradients]
            other_waveforms = [gradients[i] for i, v in enumerate(is_trap) if not v]
            sequence_blocks.extend(self._make_trapezoidals(trapezoidals, direction, rotate_to_xyz))
            sequence_blocks.extend([self._make_arbitrary_grad(g, direction, rotate_to_xyz)
                                    for g in other_waveforms])
        return sequence_blocks

    @staticmethod
    def _is_trapezoidal(gradient_block: dict):
        relative_time = gradient_block["bp"]["time"]
        amp = gradient_block["bp"]["str"]
        len_cond = len(relative_time) == 4
        top_cond = np.isclose(amp[1], amp[2], atol=1e-6)
        start_end_cond = np.isclose(amp[0], amp[0], atol=1e-6)
        return len_cond and top_cond and start_end_cond

    def _make_trapezoidals(self, gradients: List[dict], direction: np.ndarray, rotate_to_xyz: bool):
        gradients = [g for g in gradients if not self._is_all_zero(g)]
        grads_valid = [self._is_valid_trapezoidal(g) for g in gradients]
        inv_grads = [gradients[i] for i, v in enumerate(grads_valid) if not v]
        if len(inv_grads) == 2:
            new_grad = self._fuse_segmented_gradients(*inv_grads)
            gradients = [gradients[i] for i, v in enumerate(grads_valid) if v] + [new_grad, ]

        sequence_blocks = []
        for gradient_block in gradients:
            rise, flat, fall = Quantity(np.diff(gradient_block["bp"]["time"]), "ms")
            amplitude = Quantity(gradient_block["bp"]["str"], "mT/m")
            delay = Quantity(gradient_block["bp"]["time_resolved"][0], "ms")
            seq_block = cmrseq.bausteine.TrapezoidalGradient(
                system_specs=self.system_specs,
                orientation=direction, amplitude=amplitude[1],
                rise_time=rise, flat_duration=flat, fall_time=fall,
                delay=delay, name=gradient_block["name"].strip(),
                snap_to_raster=True)
            o_matrix = gradient_block.get("o_matrix", None)
            if o_matrix is not None and rotate_to_xyz:
                seq_block.rotate_gradients(o_matrix["matrix_rotated"])
            sequence_blocks.append(seq_block)
        return sequence_blocks

    @staticmethod
    def _is_all_zero(gradient_block: dict):
        return np.allclose(gradient_block["bp"]["str"], 0., atol=1e-4)

    @staticmethod
    def _is_valid_trapezoidal(gradient_block: dict):
        delta_t = np.diff(gradient_block["bp"]["time"])
        delta_amp = np.diff(gradient_block["bp"]["str"])
        valid_intervals = all([(dt > 0 or (dt == 0 and da == 0))
                               for dt, da in zip(delta_t, delta_amp)])
        return valid_intervals

    @staticmethod
    def _fuse_segmented_gradients(g1, g2):
        times = np.around(np.concatenate([np.array(g["bp"]["time_resolved"]) for g in (g1, g2)]),
                          decimals=6)
        amps = np.concatenate([np.array(g["bp"]["str"]) for g in (g1, g2)])
        unique_times = np.unique(times)
        assert unique_times.shape[0] == 4
        unique_amps_per_unique_timing = [np.unique(amps[np.where(times == t)]) for t in
                                         unique_times]
        assert all([len(v) in (1, 2) for v in unique_amps_per_unique_timing])
        amps = [a[i] for a, i in zip(unique_amps_per_unique_timing, [0, -1, -1, 0])]
        g_new = deepcopy(g1)
        g_new["bp"]["time_resolved"] = unique_times
        g_new["bp"]["time"] = unique_times - unique_times[0]
        g_new["bp"]["str"] = amps
        g_new["name"] = g1["name"].strip() + g2["name"].strip()
        g_new["ref"] = min(g1["ref"], g2["ref"])
        g_new["time"] = g1["time"]
        return g_new

    def _make_arbitrary_grad(self, gradient_block: dict, direction: np.ndarray, rotate_to_xyz: bool) \
            -> 'cmrseq.bausteine.ArbitraryGradient':
        """ Creates a cmrseq ArbitraryGradient the given GVE-gradient block definition.

        .. note::

            Required fields in the gradient_block defintions:

                - ["bp"]["time"]: 'Break points' of gradient object in 'ms' starting at 0
                - ["bp"]["str"]: magnitude scaling in 'mT/m'

            Optional fields:
                - ["bp"]["time_resolved"]: 'Break points' of gradient object in 'ms' with
                        sequence-base object reference. If not present, the 'time' field is used.
                - "o_matrix": if specified, the gradient object is rotated according to the matrix

        :param gradient_block: dictionary at least containing the breakpoints of the gradient
        :param direction: (3, ) vector specifying the direction of the gradient in MPS coordinates
        :return: building block instance of type ArbitraryGradient
        """
        time = Quantity(gradient_block["bp"]["time"], "ms")
        amplitude = Quantity(gradient_block["bp"]["str"], "mT/m")[np.newaxis]

        time_to_ref = gradient_block["bp"].get("time_resolved", time)
        delay = Quantity(time_to_ref[0], "ms")
        seq_block = cmrseq.bausteine.ArbitraryGradient(system_specs=self.system_specs,
                                                       time_points=time + delay,
                                                       waveform=amplitude * direction[:, np.newaxis],
                                                       name=gradient_block["name"].strip(),
                                                       snap_to_raster=True)
        o_matrix = gradient_block.get("o_matrix", None)
        if o_matrix is not None and rotate_to_xyz:
            seq_block.rotate_gradients(o_matrix["matrix_rotated"])
        return seq_block

    def _make_rf_block(self, rf_dict: dict):
        delay = Quantity(rf_dict["start"] - rf_dict["ref"], "ms")
        wf = Quantity(rf_dict["am_waveform"]["samples"] * rf_dict["am_scale"], "uT")
        t = Quantity(np.linspace(0, rf_dict["dur"], rf_dict["am_waveform"]["size"]), "ms") + delay
        rf_block = cmrseq.bausteine.ArbitraryRFPulse(system_specs=self.system_specs,
                                                     time_points=t,
                                                     waveform=wf,
                                                     name=rf_dict["name"].strip(),
                                                     snap_to_raster=True)
        return rf_block

    def _make_aq_block(self, aq_dict: dict) -> List[cmrseq.bausteine.SymmetricADC]:
        number_of_composite_aqs = aq_dict["rep"]
        delay_first = self.system_specs.time_to_raster(Quantity(aq_dict["start"] - aq_dict["ref"], "ms"))
        delay_add = Quantity(aq_dict["dur"], "ms") + Quantity(aq_dict["interval"], "ms")

        adc_blocks = []
        for n in range(number_of_composite_aqs):
            adc = cmrseq.bausteine.SymmetricADC(system_specs=self.system_specs,
                                                duration=Quantity(aq_dict["dur"], "ms"),
                                                delay=delay_first + delay_add * n,
                                                num_samples=aq_dict["samples"])
            adc_blocks.append(adc)
        return adc_blocks
