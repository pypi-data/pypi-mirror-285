__all__ = ["custom_warning_format", "AutomaticOptimizationWarning", "SystemLimitViolationError"]

# Set default warning signature
import warnings
import os
import inspect


def custom_warning_format(message, category, filename, lineno, file=None, line=None) -> str:
    if category.__name__=="AutomaticOptimizationWarning":
        return (f"CMRSeq - {category.__name__}: {os.path.abspath(filename)}:{lineno} \n   "
                f"+ In parametric sequence definition, arguments were overritten due to "
                f"potential system limit violations\n   + {message}\n")
    return f"{message}\n"

class AutomaticOptimizationWarning(UserWarning):
    pass

class SystemLimitViolationError(ValueError):
    pass

class SequenceArgumentError(ValueError):
    def __init__(self, message: str, argument: str):
        function_name = inspect.stack()[1].function
        tmp = (f"\n\tInfeasible value for argument: '{argument}' "
               f"\n\tin parametric sequence definition: '{function_name}'."
               f"\n\tReason: {message}")
        super().__init__(tmp)

class SequenceOptimizationError(ValueError):
    def __init__(self, message: str):
        function_name = inspect.stack()[1].function
        tmp = (f"\n\tNumerical optimization of sequence timing in {function_name} did not converge"
               f"\n{message}")
        super().__init__(tmp)

class SequenceValidationError(ValueError):
    pass

class BuildingBlockArgumentError(ValueError):
    def __init__(self, message: str, argument: str, class_name: str):
        function_name = inspect.stack()[1].function
        tmp = (f"\n\tInfeasible value for argument: '{argument}' "
               f"\n\tin building block definition: '{class_name}.{function_name}'"
               f"\n\tReason: {message}")
        super().__init__(tmp)