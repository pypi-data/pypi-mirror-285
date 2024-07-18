""" This module contains functionality to read/write sequences from/to files.
Currently supported formats:

*Import*:
    - JSON

*Export*:
    - JSON

"""
__all__ = ["sequence_to_json", "sequence_from_json"]

import json
import importlib
from collections import OrderedDict

from pint import Quantity
import numpy as np

import cmrseq


def sequence_to_json(sequence: cmrseq.Sequence, file_name: str = None) -> OrderedDict:
    """ Converts a cmrseq.Sequence object to an ordered dictionary containing a JSON compatible
    representation of the sequence. The first node contains the system specifications and subsequent
    nodes contain the block definitions. After converting the sequence to a dict, this function
    serializes it to json format and saves it to the specified location (if not None).

    :param sequence:
    :param file_name: str - defaults to None. Specifies the saving location. If not specified, the
                        sequence representation is not saved but only returned as json compatible
                        dictionary.
    :return:
    """
    sequence.validate()
    block_names = sequence.blocks
    blocks = [sequence.get_block(bn) for bn in block_names]
    save_dict = OrderedDict(system_specs=_specs_to_dict(sequence._system_specs))  # pylint: disable=W0212
    save_dict.update({bn: _block_to_dict(b) for bn, b in zip(block_names, blocks)})

    with open(f"{file_name}.json", "w+", encoding="utf-8") as filep:
        json.dump(save_dict, filep)
    return save_dict

def sequence_from_json(file: str) -> 'cmrseq.Sequence':
    """ Loads json file from specified locations and reconstructs a Sequence object from it.

    :param file: str - file location containing the sequence definition
    :return: cmrseq.Sequence object
    """
    with open(file, "r", encoding="utf-8") as filep:
        sequence_dict = json.load(filep, object_pairs_hook=OrderedDict)
    specs = dict_to_specs(sequence_dict["system_specs"])
    blocks = [_dict_to_block(specs, b) for i, b in enumerate(sequence_dict.values()) if i > 0]
    return cmrseq.Sequence(blocks, system_specs=specs)


def _quantity_to_json_dict(quant: Quantity) -> dict:
    """ Creates json compatible representation of a pint.Quantity into dtype, unit and value.
    :param quant: Quantity
    :return: dict
    """
    temp = {}
    temp["unit"] = str(quant.units)
    temp["dtype"] = str(np.array(quant.m).dtype)
    if temp["dtype"] in ["complex64", "complex128"]:
        temp["val_real"] = np.array(quant.m).real.tolist()
        temp["val_imag"] = np.array(quant.m).imag.tolist()
    else:
        temp["val"] = np.array(quant.m).tolist()
    return temp


def _block_to_dict(block: 'cmrseq.core.bausteine.SequenceBaseBlock') -> dict:
    """ Creates a dictionary representation of a SequenceBaseBlock

    :param block:
    :return:
    """
    block_dict = dict(__class__=str(block.__class__).replace("<class '", "").replace("'>", ""))
    property_dict = {}
    for key, val in block.__dict__.items():
        if isinstance(val, Quantity):
            property_dict[key] = _quantity_to_json_dict(val)
        elif isinstance(val, (tuple, list)):
            temp = [_quantity_to_json_dict(vv) for vv in val]
            property_dict[key] = temp
        else:
            property_dict[key] = val
    block_dict["__dict__"] = property_dict
    return block_dict


def _specs_to_dict(system_specs: cmrseq.SystemSpec) -> dict:
    """ Converts the system-specification object into a dictionary of json compatible quantity
    representations

    :param system_specs:
    :return:
    """
    temp = {key: _quantity_to_json_dict(val) for key, val in system_specs.__dict__.items()
            if isinstance(val, Quantity)}
    temp.update({"enable_simulatenous_trasmit_receive": system_specs.enable_simulatenous_trasmit_receive})
    return temp


def _dict_to_quantity(input_dict: dict) -> Quantity:
    """ Reconstructs a pint.Quantity from a dictionary containing the keys
    (dtype, unit, val/(val_real, val_imag)). This is meant to be the inverse operation to
    _quantity_to_dict

    :param input_dict: dict(dtype, unit, val/(val_real, val_imag))
    :return: Quantity
    """
    dtype = np.dtype(str(input_dict["dtype"]))
    if dtype in (np.complex64, np.complex128):
        val = np.array(input_dict["val_real"]) + 1j * np.array(input_dict["val_imag"])
    else:
        val = np.array(input_dict["val"])
    return Quantity(val.astype(dtype), input_dict["unit"])


def dict_to_specs(input_dict: dict) -> cmrseq.SystemSpec:
    """ Creates a new cmrseq.SystemSpecs object and writes all attributes from the specified input
    dictionary to the system specifications after converting each entry to a pint.Quantity

    :param input_dict:
    :return:
    """
    specs = cmrseq.SystemSpec()
    for key, val in input_dict.items():
        if key == "enable_simulatenous_trasmit_receive":
            specs.enable_simulatenous_trasmit_receive = val
        else:
            specs.__dict__[key] = _dict_to_quantity(val)

    return specs


def _dict_to_block(specs: 'cmrseq.SystemSpecs', input_dict: dict) \
        -> cmrseq.bausteine.SequenceBaseBlock:
    """ Parses a json compatible dictionary containing the block definition and creates a
    corresponding child of a SequenceBaseBlock from it.

    :param input_dict:
    :return:
    """
    block = cmrseq.bausteine.SequenceBaseBlock(specs, "")
    class_name = input_dict["__class__"].split(".")[-1]
    module_name = ".".join(input_dict["__class__"].split(".")[0:-1])
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    block.__class__ = class_
    for key, val in input_dict["__dict__"].items():
        if isinstance(val, OrderedDict):
            if val.get("unit", None) is not None:
                block.__dict__[key] = _dict_to_quantity(val)
            else:
                block.__dict__[key] = (_dict_to_quantity(vv) for vv in val)
        elif isinstance(val, list):
            ret_val = []
            for vv in val:  # pylint: disable=C0103
                if vv.get("unit", None) is not None:
                    ret_val.append(_dict_to_quantity(vv))
                else:
                    ret_val.append(np.array(val))
            block.__dict__[key] = tuple(ret_val)
        else:
            block.__dict__[key] = val
    return block
