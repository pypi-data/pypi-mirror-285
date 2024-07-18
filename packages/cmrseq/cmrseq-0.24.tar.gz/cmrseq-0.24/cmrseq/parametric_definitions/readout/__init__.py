""" This modules contains compositions of building blocks commonly used for in defining actual
signal acqusition and spatial encoding"""
import importlib
mod_handles = [importlib.import_module(f"cmrseq.parametric_definitions.readout.{m}")
               for m in ("_epi", "_spiral", "_cartesian_single_lines","_radial")]
__all__ = [item for m in mod_handles for item in getattr(m, '__all__')]


from cmrseq.parametric_definitions.readout._epi import *
from cmrseq.parametric_definitions.readout._spiral import *
from cmrseq.parametric_definitions.readout._cartesian_single_lines import *
from cmrseq.parametric_definitions.readout._radial import *
