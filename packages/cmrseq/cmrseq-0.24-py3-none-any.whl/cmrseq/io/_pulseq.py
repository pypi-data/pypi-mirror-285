__all__ = ["PulseSeqFile"]

from typing import Tuple, List, Iterable
import os
import re
from collections import OrderedDict
import hashlib

import numpy as np
from pint import Quantity
from tqdm import tqdm

import cmrseq
from cmrseq import bausteine
from cmrseq import SystemSpec, Sequence


class PulseSeqFile:
    """ API for reading and writing Pulseq definition files"""
    #: Tuple of strings defining the Semantic delimiters of the file
    # Definitions, Extensions, signature
    SECTION_HEADERS: Tuple[str, ...] = ("[VERSION]", "[DEFINITIONS]", "[BLOCKS]",
                                        "[GRADIENTS]", "[RF]", "[TRAP]", "[ADC]",
                                        "[EXTENSIONS]", "[SHAPES]", "[SIGNATURE]")
    #: Required definitions in [DEFINITIONS] - section
    REQUIRED_DEFINITIONS: Tuple[str, ...] = ("AdcRasterTime", "BlockDurationRaster",
                                             "GradientRasterTime", "RadiofrequencyRasterTime")

    #: Assembled python like version number
    version: str
    #: Dictionary containing Quantities[Time] for 'grad', 'rf', 'adc' and 'block' raster time
    raster_times: dict
    #: Dictionary containing values specified in the [DEFINITIONS] section
    additional_defs: dict
    #: Integer array (n_blocks, 8) containing the Block-definitions
    block_array: np.ndarray
    #: Dictionary (id: shape) containing the uncompressed shape definitions
    shape_table: OrderedDict
    #: Dictionary containing the RF definitions per shape_id as dictionary with following keys:
    #: dict_keys=(phase_offset, frequency_offset, delay,
    #             shape_ids=[mag, phase, time], amplitude)
    rf_table: OrderedDict
    #: Dictionary containing the ADC definition per shape_id as dictionary with following keys:
    #: dict_keys=(num_samples, dwell, delay, frequency_offset, phase_offset)
    adc_table: OrderedDict
    #: Dictionary containing the trapezoidal gradient definitions per shape_id as dictionary
    #  with following keys: dict_keys=(amplitude, rise_time, flat_duration, fall_time, delay)
    traps_table: OrderedDict
    #: Dictionary containing the shape-gradient definitions per shape_id as dictionary
    #: dict_keys=(delay, shape_ids=[amp, time], amplitude)
    grads_table: OrderedDict
    #: Dictionary containing the extensions definiton
    ext_table: OrderedDict

    def __init__(self, file_path: str = None, sequence: Sequence = None):

        if (file_path is not None and sequence is not None) or  \
                (file_path is None and sequence is None):
            raise ValueError("Exactly one of the input sources must be specified.")

        if file_path is not None:
            self.from_pulseq_file(file_path)
        elif sequence is not None:
            self.from_sequence(sequence)

    def from_pulseq_file(self, filepath: str):
        """ Loads a *.seq file and parses all sections into the

        :raise: ValueError if file does not exist
        :param filepath: path to a file of type *.seq
        """

        if not os.path.exists(filepath):
            raise ValueError(f"No pulseq file found at specified location:\n\t{filepath}")

        with open(filepath, "r") as seqfile:
            all_lines = seqfile.read().splitlines()
        all_lines = [re.sub(r'\s+', ' ', line.strip()) for line in all_lines]

        # Find section starts and calculate number of lines per section
        sections = self._subdivide_sections(all_lines)

        # Parse Meta information (version and definitions)
        self.version = self._parse_version(sections["[VERSION]"])
        self.raster_times, self.additional_defs = self._parse_definitions(sections["[DEFINITIONS]"])

        # Parse block definitions
        self.block_array = np.genfromtxt(sections["[BLOCKS]"], comments="#",
                                         delimiter=" ", dtype=int)

        # Parse lookup tables for block definitions
        shape_table, rf_table, adc_table, traps_table, grads_table, ext_table = [{} for _ in
                                                                                 range(6)]
        if "[SHAPES]" in sections.keys():
            shape_table = self._parse_shapes(sections["[SHAPES]"])
        self.shape_table = shape_table

        if "[RF]" in sections.keys():
            # If any RF is specified, SHAPES must be present in definitons as well
            rf_table = self._parse_rf(sections["[RF]"], self.shape_table)
        self.rf_table = rf_table

        if "[ADC]" in sections.keys():
            adc_table = self._parse_adc(sections["[ADC]"])
        self.adc_table = adc_table

        if "[TRAP]" in sections.keys():
            traps_table = self._parse_traps(sections["[TRAP]"])
        self.traps_table = traps_table

        if "[GRADIENTS]" in sections.keys():
            grads_table = self._parse_gradients(sections["[GRADIENTS]"], self.shape_table)
        self.grads_table = grads_table

        if "[EXTENSIONS]" in sections.keys():
            print(2)
        self.ext_table = ext_table

    @staticmethod
    def _subdivide_sections(all_lines) -> OrderedDict:
        """ Parses the file for the pre-defined sections and divides the lines according
         to captions. Lines per section is returned in a dictionary whose keys are the actually
         provided section headers.

        :param all_lines: List[str]
        :return: OrderedDict(section_header=List[str])
        """
        # Find line-indices that match the section headers
        section_starts = OrderedDict((line.strip(), line_idx + 1)
                                     for line_idx, line in enumerate(all_lines)
                                     if line.strip() in PulseSeqFile.SECTION_HEADERS)

        # Roll the indices of the actually specified sections to define the end-of-section lines
        provided_sections = list(section_starts.keys())
        section_ends = {k: section_starts[k_next] - 1 for k_next, k
                        in zip(provided_sections[1:], provided_sections[:-1])}
        section_ends[PulseSeqFile.SECTION_HEADERS[-1]] = len(all_lines)

        # Index the given lines according to sections and store them in a dictionary
        sections_dict = OrderedDict([(k, all_lines[section_starts[k]:section_ends[k]])
                                     for k in provided_sections])
        return sections_dict

    @staticmethod
    def _parse_version(version_lines: List[str]) -> str:
        """ Converts the following lines to a major.minor.revision version number:

        .. code-block::

            [VERSION]
            major X
            minor Y
            revision z

        :param version_lines: List[str]
        :return: str
        """
        cleaned_lines = [v.strip() for v in version_lines if (len(v) > 0 and v[0] != "#")]
        version_str = "".join(cleaned_lines).replace("major ", "").replace("minor ", ".")
        return version_str.replace("revision ", ".")

    @staticmethod
    def _parse_definitions(definition_lines: List[str]) -> (dict, dict):
        """ Converts the following lines to two dictionaries (required, optional):

        .. code-block::

            [DEFINITIONS]
            AdcRasterTime float                         (required)
            BlockDurationRaster float                   (required)
            GradientRasterTime float                    (required)
            RadiofrequencyRasterTime float              (required)
            AdditionalProperty any                      (optional)
            ...

        :raises: ValueError if the definition does not contain all of the required properties

        :param definition_lines: List[str]
        :return: dict, dict -> required_properties, addition_properties
        """
        definition_lines = [line.strip() for line in definition_lines
                            if (len(line) > 0 and line[0] != "#")]
        definitions = {l.split()[0]: l.split()[1] for l in definition_lines}
        if not all([k in definitions.keys() for k in PulseSeqFile.REQUIRED_DEFINITIONS]):
            raise ValueError("Given definition section does not contain all required values:\n"
                             f"\tGot: {definitions.keys()}\n"
                             f"\tExpected: {PulseSeqFile.REQUIRED_DEFINITIONS}")
        raster_times = dict(
            grad=Quantity(float(definitions["GradientRasterTime"]), "s"),
            rf=Quantity(float(definitions["RadiofrequencyRasterTime"]), "s"),
            adc=Quantity(float(definitions["AdcRasterTime"]), "s"),
            blocks=Quantity(float(definitions["BlockDurationRaster"]), "s")
        )
        [definitions.pop(k) for k in PulseSeqFile.REQUIRED_DEFINITIONS]
        additional_definitions = definitions
        return raster_times, additional_definitions

    @staticmethod
    def _parse_rf(rf_lines: List[str], shape_table: dict) -> dict:
        """ Parses the RF definitions given in following format

        .. code-block::

            # Format of RF events:
            # id amplitude mag_id phase_id time_shape_id delay freq phase
            # ..        Hz   ....     ....          ....    us   Hz   rad
            [RF]
            1         2500 1 2 3 100 0 0
            ...

        :param rf_lines: List[str] starting from the first line after [RF]
        :return: dict(rf_id = dict([time_points, waveform, phase_offset, frequency_offset, delay]))
        """
        rf_lines = [line.strip() for line in rf_lines if (len(line) > 0 and line[0] != "#")]
        rf_defs = []
        for line in rf_lines:
            line = np.genfromtxt([line, ], delimiter=" ")
            id_ = int(line[0])
            amplitude_scaling = Quantity(float(line[1]), "Hz")
            delay = Quantity(float(line[5]), "us")
            frequency_offset = Quantity(line[6], "Hz")
            phase_offset = Quantity(line[7], "rad")
            rf_defs.append((id_, dict(phase_offset=phase_offset, frequency_offset=frequency_offset,
                                      delay=delay, shape_ids=[int(line[i]) for i in (2, 3, 4)],
                                      amplitude=amplitude_scaling)))
        return OrderedDict(rf_defs)

    @staticmethod
    def _parse_gradients(gradient_lines: List[str], shape_table: dict) \
            -> dict:
        """  Parses the arbitrary gradient definitions given in following format

        .. code-block::

            # Format of arbitrary gradients:
            #   time_shape_id of 0 means default timing (stepping with grad_raster starting
            #     at 1/2 of grad_raster)
            # id amplitude amp_shape_id time_shape_id delay
            # ..      Hz/m       ..         ..          us
            [GRADIENTS]
            1 -1.10938e+06 3 4 230
            2  1.10938e+06 5 6 0
            ...


        :param gradient_lines:
        :return:
        """
        gradient_lines = [line.strip() for line in gradient_lines
                          if (len(line) > 0 and line[0] != "#")]

        grad_defs = []
        for line in gradient_lines:
            line = np.genfromtxt([line, ], delimiter=" ", dtype=np.float64, comments="#")
            id_ = int(line[0])
            amplitude_scaling = Quantity(line[1], "Hz/m")
            amp_shape_id, time_shape_id = int(line[2]), int(line[3])
            delay = Quantity(line[4], "us")
            grad_defs.append((id_, dict(delay=delay, shape_ids=[amp_shape_id, time_shape_id],
                                        amplitude=amplitude_scaling)))
        return OrderedDict(grad_defs)

    @staticmethod
    def _parse_traps(trap_lines: List[str]):
        """ Parses trapezoidal gradient definitions

        .. code-block::

            # Format of trapezoid gradients:
            # id amplitude rise flat fall delay
            # ..      Hz/m   us   us   us    us
            [TRAP]
             4 -1.09777e+06 190  340 190   0
             5  1.09777e+06 190  340 190   0
             7 -1.06902e+06 180  360 180   0

        :param trap_lines: List[str] starting from the first line after [TRAP]
        :return:
        """
        trap_lines = [line.strip() for line in trap_lines if (len(line) > 0 and line[0] != "#")]
        trap_defs = []
        for line in trap_lines:
            line = np.genfromtxt([line, ], delimiter=" ")
            trap_defs.append((int(line[0]),
                              dict(amplitude=Quantity(float(line[1]), "Hz/m"),
                                   rise_time=Quantity(float(line[2]), "us"),
                                   flat_duration=Quantity(float(line[3]), "us"),
                                   fall_time=Quantity(float(line[4]), "us"),
                                   delay=Quantity(float(line[5]), "us"))
                              ))
        return OrderedDict(trap_defs)

    @staticmethod
    def _parse_adc(adc_lines: List[str]) -> dict:
        """ Parses the ADC definitions given in following format

            .. code-block::

                # Format of ADC events:
                # id num dwell delay freq phase
                # ..  ..    ns    us   Hz   rad
                [ADC]
                1 256 10000 740 0 3.14159
                2 256 10000 740 0 0

            :param adc_lines: List[str] starting from the first line after [RF]
            :return: dict(rf_id=dict([num dwell delay freq phase]))
        """
        adc_lines = [line.strip() for line in adc_lines if (len(line) > 0 and line[0] != "#")]
        adc_defs = []
        for line in adc_lines:
            line = np.genfromtxt([line, ], delimiter=" ")
            id_ = int(line[0])
            adc_defs.append((id_, dict(num_samples=int(line[1]),
                                       dwell=Quantity(float(line[2]), "ns"),
                                       delay=Quantity(float(line[3]), "us"),
                                       frequency_offset=Quantity(line[4], "Hz"),
                                       phase_offset=Quantity(line[5], "rad")))
                            )
        return OrderedDict(adc_defs)

    @staticmethod
    def _parse_shapes(shape_lines: List[str]) -> dict:
        """ Parses shapes stored in following format:

        .. code-block::
            [SHAPES]

            shape_id 1
            num_samples N2
            ...  (compressed samples)

            ...

        Specification of the compression format can be found at:
        https://pulseq.github.io/specification.pdf

        :raises: AssertionError if num_samples mismatches the actually provided number of samples

        :param shape_lines: List[str]
        :return: dict(shape_id=np.array) dictionary of uncompressed shapes
        """
        header_lines = [idx for idx, line in enumerate(shape_lines) if "shape_id" in line] + [-1]
        shapes = {}
        for hidx, hidx_next in zip(header_lines[0:-1], header_lines[1:]):
            id_ = int(re.findall(r'\d+', shape_lines[hidx])[0])
            n_samples = int(re.findall(r'\d+', shape_lines[hidx + 1])[0])
            shape_arr = np.genfromtxt(shape_lines[hidx + 2:hidx_next])

            if n_samples > shape_arr.shape[0]:
                shape_arr = PulseSeqFile._decompress_shape(shape_arr)
                assert shape_arr.shape[0] == n_samples

            shapes.update({id_: shape_arr})
        return shapes

    @staticmethod
    def _decompress_shape(shape_arr: np.ndarray):
        """Inverts pseudo run-length encoding of shape definitions
        From definition:

            When used as amplitude shapes for gradient or RF objects, the decompressed
            samples must be in the normalised range of [-1, 1] (e.g. the absolute value of
            the shape must be normalized to the range of [0  1]). Since the purpose of this
            section is to define the basic shape of a gradient or RF pulse, the amplitude
            information is defined in the events section. This allows the same shape to be
            used with different amplitudes, without repeated definitions.
            The number of points after decompressing all samples defined in a shape must
            equal the number declared in num_samples.

        :param shape_arr:
        :return:
        """
        expansion_points = np.where(shape_arr > 1)
        expansion_factors = shape_arr[expansion_points].astype(int)
        repeating_value = shape_arr[(expansion_points[0] - 1,)]
        insertion_indices = np.concatenate([np.zeros(f) + p for f, p
                                            in zip(expansion_factors, expansion_points)], axis=0)
        insertion_values = np.concatenate([np.zeros(f) * v for f, v
                                           in zip(expansion_factors, repeating_value)], axis=0)
        shape_arr = np.insert(shape_arr, insertion_indices.astype(int), insertion_values)
        shape_arr = shape_arr[np.where(np.abs(shape_arr) <= 1)]
        out = np.empty(shape_arr.shape, dtype=np.float64)
        np.cumsum(shape_arr, out=out)
        out[0] = 0.
        return out

    def write(self, filepath: str):
        """

        :raises: ValueError if file at specified location already exists

        :param filepath:
        :return: None
        """
        # if os.path.exists(filepath):
        #     raise ValueError("File at specified location already exists")

        version_sec = self._format_version(self.version)
        definition_sec = self._format_definitions(self.raster_times, self.additional_defs)
        block_sec = self._format_blocks_def(self.block_array)
        rf_sec = self._format_rf(self.rf_table)
        grad_sec = self._format_gradients(self.grads_table)
        trap_sec = self._format_traps(self.traps_table)
        adc_sec = self._format_adc(self.adc_table)
        shape_sec = self._format_shapes(self.shape_table)

        total = "\n".join([version_sec, definition_sec, block_sec, rf_sec,
                           grad_sec, trap_sec, adc_sec, shape_sec])

        total = self._sign_definition(total)

        with open(filepath, "w+") as wfile:
            wfile.write(total)

    @staticmethod
    def _format_version(version_str: str) -> str:
        major, minor, revision = version_str.split(".")
        try:
            version = cmrseq.__version__
        except AttributeError:
            version = "0.0"

        return_string = f"#Pulseq sequence file\n#Exported from python package " \
                         f"cmrseq {version}\n\n[VERSION]\n"
        return return_string + f"major {major}\nminor {minor}\nrevision {revision}\n"

    @staticmethod
    def _format_definitions(raster_times: dict, additional_info: dict) -> str:
        return_string = f"[DEFINITIONS]\n" + \
                        f"AdcRasterTime {raster_times['adc'].m_as('s')}\n" + \
                        f"BlockDurationRaster {raster_times['blocks'].m_as('s')}\n" + \
                        f"GradientRasterTime {raster_times['grad'].m_as('s')}\n" + \
                        f"RadiofrequencyRasterTime {raster_times['rf'].m_as('s')}\n"
        return_string += "\n".join([f"{k} {v}" for k, v in additional_info.items()])
        return return_string + "\n"

    @staticmethod
    def _format_blocks_def(block_array: np.ndarray) -> str:
        header = "# Format of blocks:\n"
        header += " ".join([f"{s:<6}" for s in ("# NUM", "DUR", "RF", "GX", "GY", "GZ", "ADC", "EXT")])
        header += "\n[BLOCKS]\n"
        arr_string = "\n".join([np.array2string(row, prefix="", separator=" ",
                                                formatter={'int':lambda x: f"{x:<6}"})[1:-1].strip()
                                for row in block_array])
        return header+arr_string + "\n"

    @staticmethod
    def _format_rf(rf_table) -> str:
        return_string = "# Format of RF events:\n" \
                        "# id amplitude mag_id phase_id time_shape_id delay freq phase\n"
        return_string += f"# {'..':<3} {'Hz':<13} {'..':<5} {'..':<5} " \
                         f"{'..':<5} {'us':<7} {'Hz':<7} {'rad':<6}\n[RF]\n"
        for id_, rfdef in rf_table.items():
            peak_amp = float(rfdef["amplitude"].m_as("Hz"))
            delay = rfdef["delay"].m_as("us")
            phase = rfdef["phase_offset"].m_as("rad")
            freq = rfdef["frequency_offset"].m_as("Hz")
            mag_id, phase_id, t_id = rfdef["shape_ids"]
            line = f"{id_:<5} {peak_amp:<13.5e} {mag_id:<5} {phase_id:<5} {t_id:<5}" \
                   f" {delay:<7} {freq:<7} {phase:1.6f}\n"
            return_string += line
        return return_string

    @staticmethod
    def _format_gradients(grad_table) -> str:
        return_string = "# Format of arbitrary gradients:\n#   time_shape_id of 0 means default" \
                        " timing (stepping with grad_raster starting at 1/2 of grad_raster)\n" \
                        "# id amplitude amp_shape_id time_shape_id delay\n" \
                        f"# {'..':<3} {'Hz':<13} {'..':<5} {'..':<5} {'us':<7}\n[GRADIENTS]\n"
        for id_, gdef in grad_table.items():
            peak_amp = float(gdef["amplitude"].m_as("Hz/m"))
            delay = int(gdef["delay"].m_as("us"))
            mag_id, t_id = gdef["shape_ids"]
            line = f"{id_:<5} {peak_amp:<13.5e} {mag_id:<5} {t_id:<5} {delay:<7}\n"
            return_string += line
        return return_string

    @staticmethod
    def _format_traps(traps_table) -> str:
        return_string = "# Format of trapezoid gradients:\n# id amplitude rise flat fall delay\n"
        return_string += f"# {'..':<3} {'Hz/m':<13} {'us':<7} {'us':<7} {'us':<7} {'us':<7}\n[TRAP]\n"
        for id_, tdef in traps_table.items():
            peak_amp = float(tdef["amplitude"].m_as("Hz/m"))
            rise, flat, fall, delay = [int(tdef[k].m_as("us")) for k in
                                       ("rise_time", "flat_duration", "fall_time", "delay")]
            line = f"{id_:<5} {peak_amp:<13.5e} {rise:<7.3} {flat:7.3} {fall:<7.3} {delay:7.3}\n"
            return_string += line
        return_string += "\n"
        return return_string

    @staticmethod
    def _format_adc(adc_table) -> str:
        return_string = "# Format of ADC events::\n# id num dwell delay freq phase\n"
        return_string += f"# {'..':<3} {'..':<6} {'ns':<9} {'us':<6.3} {'Hz/m':<13} {'rad':<6}\n[ADC]\n"
        for id_, adcdef in adc_table.items():
            num = adcdef['num_samples']
            dwell = adcdef['dwell'].m_as("ns")
            delay = adcdef['delay'].m_as("us")
            freq = adcdef['frequency_offset'].m_as("Hz")
            phase = adcdef['phase_offset'].m_as("rad")
            line = f"{id_:<5} {num:<6} {dwell:<9} {delay:<6} {freq:<13.5e} {phase:<5}\n"
            return_string += line
        return return_string

    @staticmethod
    def _format_shapes(shape_table: dict) -> str:
        return_string = "# Sequence Shapes\n[SHAPES]\n\n"
        for shape_id, shape_arr in shape_table.items():
            return_string += f"shape_id {shape_id}\nnum_samples {shape_arr.shape[0]}\n"
            if np.max(np.abs(shape_arr)) <= 1:
                compressed_shape = PulseSeqFile._compress_shape(np.around(shape_arr, decimals=12))
            else:
                compressed_shape = shape_arr
            arr_str = np.array2string(compressed_shape, separator="\n",
                                      floatmode="maxprec_equal", threshold=int(1e5))[1:-1]
            return_string += arr_str.replace(" ", "").replace(" ", "").replace(" ", "")
            return_string += "\n\n"
        return return_string

    @staticmethod
    def _compress_shape(shape_arr) -> np.ndarray:
        """ Pseudo run-length encoding algorithm, compressing MR-shape definitions according to the
        PulseSeq format (https://pulseq.github.io/specification.pdf).

        Algorithm:

        .. code-block::

            1. compute derivative
            2. find consecutively at least 4 times reoccuring values
            3. replace re-occuring values from 3rd position on by the number of occurences


        :param shape_arr: 1D np.darray
        :param force_compression: if true applies compression even if the number of samples is not
                                    smaller
        :return:
        """
        num_samples = shape_arr.shape[0]
        quantization_factor = 1e-7
        shape_arr_q = shape_arr / quantization_factor
        datq = np.around(np.concatenate([shape_arr_q[0:1], np.diff(shape_arr_q)], axis=0))
        qerr = shape_arr_q - np.cumsum(datq)

        qcor = np.concatenate([[0, ], np.diff(qerr)], axis=0)
        datq = datq + qcor
        mask_changes = np.concatenate([[True, ], np.diff(datq) != 0], axis=0)
        vals = datq[mask_changes] * quantization_factor

        k, = np.where(np.concatenate([mask_changes, [True]], axis=0))
        n = np.diff(k)
        n_extra = (n-2).astype(np.float32)
        vals2 = vals
        vals2[n_extra < 0] = np.nan
        n_extra[n_extra < 0] = np.nan
        v = np.stack([vals, vals2, n_extra], axis=0).flatten()
        v[np.abs(v) < 1e-10] = 0
        if v.shape[0] < num_samples:
            return v[np.isfinite(v)]
        else:
            return shape_arr

    @staticmethod
    def _sign_definition(total: str):
        string_hash = hashlib.md5(total.encode('utf-8')).hexdigest()
        template = "\n[SIGNATURE]\n# This is the hash of the Pulseq file, calculated right" \
                   " before the [SIGNATURE] section was added\n# It can be reproduced/verified" \
                   " with md5sum if the file trimmed to the position right above [SIGNATURE]\n#" \
                   " The new line character preceding [SIGNATURE] BELONGS to the signature " \
                   "(and needs to be sripped away for recalculating/verification)\n"
        template += f"Type md5\nHash {string_hash}"
        return total + template


    def to_cmrseq(self, gyromagentic_ratio: Quantity, max_slew: Quantity,
                  max_grad: Quantity, block_indices: Iterable[int] = None) -> List[Sequence]:
        """ Converts the parsed file into a list of cmrseq.Sequence objects.

        :param gyromagentic_ratio: in MHz/T
        :param max_slew: in mT/m
        :param max_grad: in mT/m/ms
        :param block_indices: Iterable[int] specifiying which blocks to convert if None all blocks
                                are converted
        :return: List of cmrseq.Sequence each representing one block of the pulseseq definition
        """
        if block_indices is None:
            block_indices = range(self.block_array.shape[0])

        # TODO: Incorporate additional meta info?
        system_specs = SystemSpec(gamma=gyromagentic_ratio.to("MHz/T"),
                                  grad_raster_time=self.raster_times["grad"],
                                  max_grad=max_grad.to("mT/m"),
                                  max_slew=max_slew.to("mT/m/ms"),
                                  rf_raster_time=self.raster_times["rf"],
                                  adc_raster_time=self.raster_times["adc"])

        sequence_objects = []
        # Assumption: each block can contain one each of the classes (RF, GX, GY, GZ, ADC, EXT)
        for idx in tqdm(block_indices):
            sequence_blocks = []
            block_def = self.block_array[idx]

            # Construct RF
            rf_def = self.rf_table.get(block_def[2], None)
            if rf_def is not None:
                rf_object = self._rfdef_to_block(rf_def, system_specs, name=f"rf_id_{block_def[2]}")
                sequence_blocks.append(rf_object)

            # Construct Gradients
            gradients_per_dir = self._graddef_to_block(block_def, system_specs)
            sequence_blocks.extend(gradients_per_dir)

            # Construct ADC
            adc_def = self.adc_table.get(block_def[6], None)
            if adc_def is not None:
                adc_object = bausteine.SymmetricADC(system_specs=system_specs,
                                                    **adc_def)
                sequence_blocks.append(adc_object)

            # Only block duration is specified --> Delay
            if len(sequence_blocks) == 0:
                sequence_blocks.append(bausteine.Delay(system_specs=system_specs,
                            duration=float(block_def[1]) * self.raster_times["blocks"])                            )
            sequence_objects.append(Sequence(sequence_blocks, system_specs=system_specs))
        return sequence_objects


    def _rfdef_to_block(self, rf_def: dict, system_specs: SystemSpec, name: str) ->\
            'bausteine.RFPulse':
        """ Converts a Pulseq definition of a RF pulse to a cmrseq RFPulse object

        :param grad_def:
                Expected dictionary keys:
                    - phase_offset  (rad)
                    - frequency_offset (Hz)
                    - delay (us)
                    - shape_ids ()
                    - amplitude (Hz)
        :return: ArbitraryRFPulse
        """
        # TODO: revert shift by rastertime half
        mag_id, phase_id, time_id = rf_def["shape_ids"]
        normed_magnitude = self.shape_table[mag_id]
        phase_shape = Quantity(self.shape_table[phase_id], "rad")
        if time_id == 0:
            # if no shape is specified (id==0), raster time is assumed where RF shapes are
            # gridded with half a raster-time shift in pulseq-definition
            time_shape = (np.arange(0, normed_magnitude.shape[0], 1) + 0.5)
            time_shape *= self.raster_times["rf"]
        else:
            time_shape = Quantity(self.shape_table[time_id], "us")

        amplitude_scaling = (rf_def["amplitude"] / system_specs.gamma.to("Hz/uT")).to("uT")
        waveform = normed_magnitude * amplitude_scaling * np.exp(1j * phase_shape.m_as("rad"))
        delay, foffset, poffset = [rf_def[k] for k in ("delay", "frequency_offset", "phase_offset")]
        rf = bausteine.ArbitraryRFPulse(system_specs, time_points=time_shape,
                                        waveform=waveform, delay=delay, frequency_offset=foffset,
                                        phase_offset=poffset, snap_to_raster=True, name=name)
        return rf

    def _graddef_to_block(self, block_def: dict, system_specs: SystemSpec) -> \
                    List['bausteine.Gradient']:
        """
        :param block_def: (id, duration, rf, gx, gy, gz, adc, ext)
        :param system_specs:
        :return:
        """
        gradient_blocks = []
        for dir_idx, direction in zip([3, 4, 5], np.eye(3, 3)):
            # Check if index belongs to a trapezoidal, otherwise construct arbitrary
            if block_def[dir_idx] != 0:
                g_def = self.traps_table.get(block_def[dir_idx], None)
                if g_def is not None:
                    amplitude = (g_def["amplitude"] / system_specs.gamma.to("Hz/mT")).to("mT/m")
                    gradient_object = bausteine.TrapezoidalGradient(system_specs,
                        amplitude=amplitude, rise_time=g_def["rise_time"],
                        flat_duration=g_def["flat_duration"], fall_time=g_def["fall_time"],
                        delay=g_def["delay"], orientation=direction,
                        name=f"trapezoidal_id{block_def[dir_idx]}", snap_to_raster=True)
                else:
                    # TODO: revert shift by rastertime half
                    g_def = self.grads_table.get(block_def[dir_idx], None)
                    amp_shape_id, time_shape_id = g_def["shape_ids"]
                    amplitude_scaling = (g_def["amplitude"] / system_specs.gamma.to("Hz/mT"))
                    waveform = self.shape_table[amp_shape_id] * amplitude_scaling.to("mT/m")

                    if time_shape_id == 0:
                        # if no shape is specified (id==0), raster time is assumed where arbitrary gradient
                        # shapes are gridded with half a raster-time shift in pulseq-definition
                        time_points = (np.arange(0, waveform.shape[0])) * self.raster_times["grad"]
                    else:
                        time_points = self.shape_table[time_shape_id] * self.raster_times["grad"]

                    waveform = waveform[np.newaxis] * direction[:, np.newaxis]
                    gradient_object = bausteine.ArbitraryGradient(system_specs=system_specs,
                        waveform=waveform, time_points=time_points, delay=g_def["delay"],
                        name=f"shape_gradient_id{block_def[dir_idx]}", snap_to_raster=True)
                gradient_blocks.append(gradient_object)
        return gradient_blocks

    def from_sequence(self, seq: Sequence):
        """ Creates a pulseq-style sequence definition from a cmrseq.sequence object.

        """
        self.version = "1.4.0"
        rf_blocks, gradient_blocks, adc_blocks = self._sort_sequence_blocks(seq)
        self.raster_times = dict(rf=seq._system_specs.rf_raster_time,
                                 grad=seq._system_specs.grad_raster_time,
                                 adc=seq._system_specs.adc_raster_time)
        self.raster_times["blocks"] = Quantity(1., "us")

        global_breakpoints, rfadc_per_pulseq_block = self._combine_rf_adc_breakpoints(
                                                                rf_blocks, adc_blocks)
        global_breakpoints = np.concatenate([global_breakpoints, [seq.end_time, ]], axis=0)

        n_blocks = rfadc_per_pulseq_block.shape[0]
        non_zero_rf_refs = np.concatenate([np.where(rfadc_per_pulseq_block[:, 0] == idx + 1)
                                           for idx in range(len(rf_blocks))]).flatten()
        non_zero_adc_refs = np.concatenate([np.where(rfadc_per_pulseq_block[:, 1] == idx + 1)
                                            for idx in range(len(adc_blocks))]).flatten()
        rf_reference_times = global_breakpoints[non_zero_rf_refs]
        adc_reference_times = global_breakpoints[non_zero_adc_refs]
        self.block_array = np.zeros([n_blocks, 8], dtype=np.int32)
        self.block_array[:, 0] = np.arange(1, n_blocks + 1, 1)

        # Block durations are determined by global breakpoints
        self.block_array[:, 1] = np.diff((global_breakpoints - seq._system_specs.rf_raster_time).m_as("us"))

        # Create unique rf-definitions and register the block associations into block-array
        # The unique shapes for all rf pulses instantiate the shape table, where the gradients
        # are added to afterwards
        self.shape_table, self.rf_table, block_associations = self._unique_rf_shapes_and_events(
                     rf_blocks, rf_reference_times, seq._system_specs.rf_raster_time, id_offset=0)
        for k in self.rf_table.keys():
            self.rf_table[k]["amplitude"] *= seq._system_specs.gamma.to("Hz/uT")

        self.block_array[non_zero_rf_refs, 2] = block_associations
        # Create unique adc-events and register the block associations into block-array
        self.adc_table, block_associations = self._unique_adc_events(adc_blocks,
                                                                     adc_reference_times)
        self.block_array[non_zero_adc_refs, 6] = block_associations
        # Create unique arbitray gradient shapes and register them into block-array
        # Note: No trapezoidals are defined as it only increases compelxity while the
        # representation is still valid and not really longer using only shapes ...
        t_shapes, grad_shapes, self.grads_table, block_associations = self._unique_gradient_shapes(
                            gradient_blocks, global_breakpoints, self.raster_times["grad"],
                            id_offset=len(self.shape_table.keys()), system_specs=seq._system_specs)
        self.block_array[:, 3:6] = block_associations
        self.shape_table.update(grad_shapes)
        self.shape_table.update(t_shapes)

        self.traps_table = OrderedDict()
        self.additional_defs = OrderedDict()

    @staticmethod
    def _sort_sequence_blocks(seq: Sequence) -> \
            (List[bausteine.RFPulse], List[bausteine.Gradient], List[bausteine.ADC]):
        """ Returns a list of block per class that is sorted according to the start time of the
        contained blocks of the sequence per class.

        :param seq:
        :return:
        """
        rf_blocks, gradient_blocks, adc_blocks = [], [], []
        for block_name in seq.blocks:
            block = seq.get_block(block_name)
            if isinstance(block, bausteine.RFPulse):
                rf_blocks.append(block)
            elif isinstance(block, bausteine.Gradient):
                gradient_blocks.append(block)
            elif isinstance(block, bausteine.ADC):
                adc_blocks.append(block)

        rf_blocks.sort(key=lambda b: b._rf[0][0])
        adc_blocks.sort(key=lambda b: b.adc_timing[0])
        gradient_blocks.sort(key=lambda b: b.tmin)
        return rf_blocks, gradient_blocks, adc_blocks

    @staticmethod
    def _unique_rf_shapes_and_events(rf_blocks: List[bausteine.RFPulse],
                rf_reference_times: List[Quantity], raster_time: Quantity, id_offset: int = 0) \
                -> (List[dict], List[int]):
        """
        :param rf_blocks: Sorted list of RF blocks
        :param raster_time:
        :return: - OrderedDict containing the rf-shape definitions
                 - OrderedDict containing the block-definitions (equivalent to self.rf_table)
        """
        unique_wf_shapes = OrderedDict()
        unique_phase_shapes = OrderedDict()
        unique_time_shapes = OrderedDict()
        block_definitions = OrderedDict()
        block_associations = np.zeros(len(rf_reference_times), dtype=np.int32)

        for block_idx, rfb in enumerate(rf_blocks):
            normed_wf, peak_amp, phase, time = rfb.normalized_waveform

            # Check if waveform is already in set of unique shapes
            # and insert if not
            shape_id = PulseSeqFile._find_shape_in_set(unique_wf_shapes, normed_wf)
            if shape_id is None:
                nunique_wfs = len(unique_wf_shapes.keys())
                shape_id = nunique_wfs + 1
                unique_wf_shapes[shape_id] = np.around(normed_wf, decimals=10).flatten()

            # Check if phase is already in set of unique shapes and insert if not
            phase_id = PulseSeqFile._find_shape_in_set(unique_phase_shapes, phase)
            if phase_id is None:
                nunique_phases = len(unique_phase_shapes.keys())
                phase_id = nunique_phases + 1
                unique_phase_shapes[phase_id] = np.around(phase, decimals=8).flatten()

            # Check if time is on rastertime and if not if it is already in set of unique shapes
            # and insert if not
            unique_dt = np.unique(np.around(np.diff(time.m_as("ms")), decimals=8))
            if len(unique_dt) == 1 and np.isclose(unique_dt[0], raster_time.m_as("ms"), atol=8):
                time_id = 0
            else:
                time_id = PulseSeqFile._find_shape_in_set(unique_time_shapes, time)
                if time_id is None:
                    nunique_t = len(unique_wf_shapes.keys())
                    time_id = nunique_t + 1
                    unique_time_shapes[time_id] = np.around(time.m_as("us"), decimals=5).flatten()

            # Assemble block definition according to PulseSeqFile.rf_table
            delay = Quantity(np.around((rfb.tmin - rf_reference_times[block_idx]).m_as("us")), "us")
            freq = rfb.frequency_offset.to("Hz")
            phase_off = rfb.phase_offset.to("rad")
            shape_ids = [shape_id, phase_id, time_id]
            # Check if block definition already exists
            defidx = 0
            for defidx, bdef in block_definitions.items():
                temp = [(bdef[k], q) for k, q in zip(
                    ["amplitude", "delay", "frequency_offset", "phase_offset"],
                    [peak_amp, delay, freq, phase_off])]
                temp.append((np.array(bdef["shape_ids"]), np.array(shape_ids)))
                if all([np.allclose(a, b, rtol=1e-6) for a, b in temp]):
                    block_associations[block_idx] = defidx
                    break

            if defidx == len(block_definitions.keys()) and block_associations[block_idx] == 0:
                block_definitions[len(block_definitions.keys()) + 1] = dict(
                    phase_offset=phase_off, shape_ids=shape_ids,
                    frequency_offset=freq, delay=delay, amplitude=peak_amp)
                block_associations[block_idx] = defidx + 1

        # Fuse the three shape dictionaries and correct the indice in block definitions
        unique_shapes = OrderedDict()
        n_wf_shapes = len(unique_wf_shapes.keys())
        n_phase_shapes = len(unique_phase_shapes.keys())
        unique_shapes.update({i + id_offset: s for i, s in unique_wf_shapes.items()})
        unique_shapes.update({i + n_wf_shapes + id_offset: s for i, s in unique_phase_shapes.items()})
        unique_shapes.update({i + n_wf_shapes + n_phase_shapes + id_offset: s
                              for i, s in unique_time_shapes.items()})

        for block_def in block_definitions.values():
            block_def["shape_ids"][1] += n_wf_shapes
            if block_def["shape_ids"][2] > 0:  # special case of time_id = 0
                block_def["shape_ids"][2] += n_wf_shapes + n_phase_shapes
        return unique_shapes, block_definitions, block_associations

    @staticmethod
    def _find_shape_in_set(unique_set: dict, arr: np.ndarray, tolerance=1e-8):
        shape_id = None
        for id_, shape_arr in unique_set.items():
            if shape_arr.shape[0] == arr.shape[0]:
                if np.allclose(shape_arr - arr, 0., atol=tolerance):
                    shape_id = id_
                    break
        return shape_id

    @staticmethod
    def _unique_adc_events(adc_blocks: List[bausteine.ADC], adc_ref_times: List[Quantity]):
        """

        :param adc_blocks:
        :param unique_rf_table: corresponds to PulseSeqFile.rf_table
        :param padded_interleaved_types:
        :return:
        """

        block_definitions = OrderedDict()
        block_associations = np.zeros(len(adc_ref_times), dtype=np.int32)
        for block_idx, adcb in enumerate(adc_blocks):
            delay = Quantity(np.around((adcb.tmin - adc_ref_times[block_idx]).m_as("us"),
                                       decimals=8), "us")
            timings = adcb.adc_timing
            dwell = Quantity(np.around((timings[1] - timings[0]).m_as("ns"), decimals=8), "ns")
            num_samples = timings.shape[0]

            # Check if that block is already defined
            defidx = 0
            for defidx, bdef in block_definitions.items():
                if all([np.allclose(bdef[k], q, rtol=1e-6) for k, q in zip(
                         ["num_samples", "dwell", "delay", "phase_offset", "frequency_offset"],
                         [num_samples, dwell, delay, adcb.phase_offset, adcb.frequency_offset])]):
                    block_associations[block_idx] = defidx
                    break

            if defidx == len(block_definitions.keys()) and block_associations[block_idx] == 0:
                block_definitions[len(block_definitions.keys()) + 1] = dict(
                        num_samples=num_samples, dwell=dwell, delay=delay,
                        phase_offset=adcb.phase_offset, frequency_offset=adcb.frequency_offset)
                block_associations[block_idx] = defidx + 1

        return block_definitions, block_associations

    @staticmethod
    def _combine_rf_adc_breakpoints(rf_blocks: List[Quantity], adc_blocks: List[Quantity]) -> \
            (Quantity, np.ndarray):
        """

        Assumptions:
            - No ADC event starts before the preceeding RF-Pulse ended
            - There can be consecutive RF-Pulses without ADC in between
            - There can be consecutive ADC events without RF-pulses in between
            - There is no ADC event without a preceeding RF-Pulse
                (i.e. the first breakpoint is always an RF-Pulse)
            - The set of block-breakpoints is achieved by inserting consecutive ADC event-bps
                into the RF-Pulse bps

        :param sorted_rf_starts:
        :param sorted_adc_starts:
        :return:
        """
        sorted_rf_starts = [rfb.tmin.m_as("us") for rfb in rf_blocks]
        sorted_adc_starts = [adcb.tmin.m_as("us") for adcb in adc_blocks]
        all_starts = np.concatenate([sorted_rf_starts, sorted_adc_starts], axis=0)
        all_types = np.concatenate([np.ones_like(sorted_rf_starts),
                                    -np.ones_like(sorted_adc_starts)], axis=0)
        sorted_indices = np.argsort(all_starts)
        interleaved_starts = all_starts[sorted_indices]
        interleaved_types = all_types[sorted_indices]
        consecutive_adc_idx, = np.where(np.logical_and(np.diff(interleaved_types) == 0,
                                                    interleaved_types[1:] == -1))
        insertion_idx = consecutive_adc_idx + 1
        insertion_vals = interleaved_starts[consecutive_adc_idx]
        global_breakpoints = np.insert(np.array(sorted_rf_starts), insertion_idx, insertion_vals)

        # Make sure that one block only contains 1 instance of ADC and RF each as this usually
        # defines the maximum duration of blocks. If 2 RFPUlses or ADC occur consequtively insert
        # a zero at the corresponding position of the missing event.
        padded_interleaved_types = np.insert(interleaved_types,
                                             np.where(np.diff(interleaved_types) == 0)[0] + 1, 0)

        if padded_interleaved_types[-1] > 0.5:
            padded_interleaved_types = np.concatenate([padded_interleaved_types, [0]])
        if padded_interleaved_types[0] < -0.5:
            padded_interleaved_types = np.concatenate([[0], padded_interleaved_types])
        if global_breakpoints[0] > 0:
            global_breakpoints[0] = 0

        adc_block_iter = iter(range(1, len(adc_blocks) + 1))
        rf_block_iter = iter(range(1, len(rf_blocks) + 1))
        block_associations = np.zeros(padded_interleaved_types.reshape(-1, 2).shape, dtype=np.int32)
        for bidx, (rft, adct) in enumerate(padded_interleaved_types.reshape(-1, 2)):
            if rft > 0.5:
                block_associations[bidx, 0] = next(rf_block_iter)
            if adct < -0.5:
                block_associations[bidx, 1] = next(adc_block_iter)

        return Quantity(global_breakpoints, "us"), block_associations

    @staticmethod
    def _unique_gradient_shapes(gradient_blocks: List[bausteine.Gradient],
                                global_breakboints: List[Quantity],
                                raster_time: Quantity, system_specs: SystemSpec,
                                id_offset: int = 0)\
            -> (OrderedDict, OrderedDict, OrderedDict, List):
        """ Separates the gradient axes (x,y,z) and constructs either trapezoidal

        Assumptions: - The start of adcs/rf-pulses always co-incide with simultaneous breakpoints
                        on all gradient axes

        :param gradient_blocks: List of cmrseq.SequenceBaseBlocks
        :return: - List of unique Gradient shapes (one for each direction)
                 - List of indices marking the association of given blocks to shapes
        """
        unique_arbitrary_wf = OrderedDict()
        unique_arbitrary_t = OrderedDict()
        block_definitions = OrderedDict()

        # Sort gradient blocks into global break point intervals based on their start-times.
        # For cases where the gradient lasts into the next block this is resolved in the next step
        sorted_indices = np.argsort([g.tmin.m_as("us") for g in gradient_blocks])
        sorted_indices_iter = iter(sorted_indices)

        grad_block = gradient_blocks[next(sorted_indices_iter)]
        blocks_per_bp_interval = []
        for glob_bp in global_breakboints:
            current_block_list = []
            while grad_block.tmin < glob_bp:
                current_block_list.append(grad_block)
                try:
                    next_idx = next(sorted_indices_iter)
                except StopIteration:
                    break
                grad_block = gradient_blocks[next_idx]
            blocks_per_bp_interval.append(current_block_list)
        # Get every block left in iterator:
        blocks_after_last_bp = [gradient_blocks[i] for i in sorted_indices_iter]
        if len(blocks_after_last_bp) > 0:
            blocks_per_bp_interval.append(blocks_after_last_bp)

        # Combine all breakpoints per gradient axis into one arbitrary shape
        # Residual breakpoints are shifted into next interval
        # NOTE: This assumes that the start of adcs/rf-pulses always co-incide with simultaneous
        # breakpoints on all gradient axes
        block_associations = []
        residuals = (Quantity([], "ms"), Quantity(np.zeros([3, 0]), "mT/m"))
        for interval_idx, glob_bp in enumerate(global_breakboints):
            time, grad_points = sum(blocks_per_bp_interval[interval_idx], start=residuals)
            # This is the case if there are no gradients in before the current bp that have not yet been registered
            if len(time) < 1:
                if glob_bp > 0:
                    block_associations.extend([0, 0, 0])
                continue
            temp_grad = bausteine.ArbitraryGradient(system_specs, time, grad_points)
            (time_points, (xwf, ywf, zwf)), residuals = temp_grad.split(glob_bp)
            t_zero_ref = time_points.m_as("us") - time_points.m_as("us")[0]
            delay = time_points[0] - global_breakboints[interval_idx - 1]
            if not np.allclose(np.diff(time_points.m_as("ms")), raster_time.m_as("ms"), atol=1e-10):
                time_id = PulseSeqFile._find_shape_in_set(unique_arbitrary_t, t_zero_ref, 1e-10)
                if time_id is None:
                    n_unique_ts = len(unique_arbitrary_t.keys())
                    time_id = n_unique_ts + id_offset + 1
                    unique_arbitrary_t[time_id] = np.around(t_zero_ref / raster_time.m_as("us"))
            else:
                time_id = 0

            for wf in (xwf, ywf, zwf):
                block_associations.append(0)
                if not np.allclose(wf.m_as("mT/m"), 0.,  atol=1e-10):
                    # peak_amp_plus, peak_amp_minus = np.max(wf.m_as("mT/m")), np.min(wf.m_as("mT/m"))
                    # absolute_max_idx = np.argmax([np.abs(peak_amp_plus), np.abs(peak_amp_minus)])
                    # peak_amp = (peak_amp_plus, peak_amp_minus)[absolute_max_idx]
                    wf = wf.to("mT/m") * system_specs.gamma.to("Hz/mT")
                    peak_amp = Quantity(np.max(np.abs(wf.m_as("Hz/m"))), "Hz/m")
                    normed_amp = np.divide(wf.m_as("Hz/m"), peak_amp.m_as("Hz/m"),
                                        out=np.zeros_like(wf.m_as("Hz/m")), where=(peak_amp.m != 0))
                    wf_id = PulseSeqFile._find_shape_in_set(unique_arbitrary_wf, normed_amp, 1e-10)
                    if wf_id is None:
                        n_unique_wfs = len(unique_arbitrary_wf.keys())
                        wf_id = n_unique_wfs + id_offset + 1
                        unique_arbitrary_wf[wf_id] = normed_amp

                    # Check if that block is already defined
                    defidx = 0
                    for defidx, bdef in block_definitions.items():
                        if all([np.allclose(bdef[k], q, rtol=1e-6) for k, q in zip(
                                                    ["delay", "shape_ids", "amplitude"],
                                                    [delay, [wf_id, time_id], peak_amp])]):
                            block_associations[-1] = defidx
                            break

                    if defidx == len(block_definitions.keys()) and block_associations[-1] == 0:
                        block_definitions[len(block_definitions.keys()) + 1] = dict(
                            delay=delay, shape_ids=[wf_id, time_id], amplitude=peak_amp)
                        block_associations[-1] = defidx + 1


        block_associations = np.array(block_associations).reshape(-1, 3)
        n_wf_shapes = len(unique_arbitrary_wf.keys())
        unique_arbitrary_t = {k + n_wf_shapes : v for k, v in unique_arbitrary_t.items()}
        for bdef in block_definitions.values():
            bdef["shape_ids"][1] += n_wf_shapes
        return unique_arbitrary_t, unique_arbitrary_wf, block_definitions, block_associations


if __name__ == "__main__":
    import cmrseq
    import matplotlib.pyplot as plt
    from copy import deepcopy


    # pf2 = PulseSeqFile(sequence=seq1)
    # pf2.write("trufi2.seq")
    # #
    # pf3 = PulseSeqFile("trufi2.seq")
    # sequence_list2 = pf3.to_cmrseq(gyromagentic_ratio=Quantity(42, "MHz/T"),
    #                                 max_grad=Quantity(40, "mT/m"),
    #                                 max_slew=Quantity(200, "mT/m/ms"))
    #
    # f, a = plt.subplots(8, 1)
    # for i in range(8):
    #     cmrseq.plotting.plot_sequence(sequence_list[i], axes=a[i])
    #
    #
    # seq2 = deepcopy(sequence_list2[0])
    # seq2.extend(sequence_list2[1:30], copy=False)
    # #
    # f, a = plt.subplots(1, 1)
    # cmrseq.plotting.plot_sequence(seq2, axes=a)
    # plt.show()
    #
    # # seq2 = sequence_list[1]
    # # seq2.extend(sequence_list[4:6])
    # # cmrseq.plotting.plot_sequence(seq1, axes=a[0])
    # # cmrseq.plotting.plot_sequence(seq2, axes=a[1])
    # # plt.show()
