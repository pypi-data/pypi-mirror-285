from typing import Dict, Literal, Mapping, Union

import pydantic

from classiq.interface.generator.amplitude_loading import (
    AMPLITUDE_IO_NAME,
    TARGET_OUTPUT_NAME,
)
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumAssignmentOperation,
)
from classiq.interface.model.quantum_type import QuantumBit, QuantumNumeric, QuantumType

from classiq.exceptions import ClassiqValueError

MULTI_VARS_UNSUPPORTED_ERROR = (
    "Amplitude Loading with more than one input variable is unsupported."
)

VAR_TYPE_ILLEGAL = "Amplitude Loading input variable should be a quantum numeric"


class AmplitudeLoadingOperation(QuantumAssignmentOperation):
    kind: Literal["AmplitudeLoadingOperation"]

    _result_type: QuantumType = pydantic.PrivateAttr(default_factory=QuantumBit)

    @property
    def wiring_inouts(
        self,
    ) -> Mapping[
        str, Union[SlicedHandleBinding, SubscriptHandleBinding, HandleBinding]
    ]:
        inouts = {self.result_name(): self.result_var}
        if len(self.var_handles) == 1:
            inouts[AMPLITUDE_IO_NAME] = self.var_handles[0]
        return inouts

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        return {}

    def initialize_var_types(
        self,
        var_types: Dict[str, QuantumType],
        machine_precision: int,
    ) -> None:
        if len(var_types) != 1:
            raise ClassiqValueError(MULTI_VARS_UNSUPPORTED_ERROR)
        var_type = list(var_types.values())[0]
        if not isinstance(var_type, QuantumNumeric):
            raise ClassiqValueError(VAR_TYPE_ILLEGAL)
        super().initialize_var_types(var_types, machine_precision)

    @classmethod
    def result_name(cls) -> str:
        return TARGET_OUTPUT_NAME
