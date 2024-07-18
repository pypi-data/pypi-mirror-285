from typing import cast

from classiq.interface.model.native_function_definition import NativeFunctionDefinition

from classiq.qmod import (  # type:ignore[attr-defined]
    QArray,
    QBit,
    QCallable,
    QNum,
    Z,
    amplitude_estimation,
    qfunc,
)


@qfunc
def qmci(
    space_transform: QCallable[QArray[QBit], QBit],
    phase: QNum,
    packed_vars: QArray[QBit],
) -> None:
    amplitude_estimation(
        lambda reg: Z(reg[reg.len - 1]),
        lambda reg: space_transform(reg[0 : reg.len - 1], reg[reg.len - 1]),
        phase,
        packed_vars,
    )


QMCI_LIBRARY = [
    cast(
        NativeFunctionDefinition,
        qmci.create_model().function_dict["qmci"],
    ),
]
