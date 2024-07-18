import json
from pathlib import Path
from typing import Optional

from classiq.interface.model.model import Model, SerializedModel

from classiq.qmod.native.pretty_printer import DSLPrettyPrinter
from classiq.qmod.utilities import DEFAULT_DECIMAL_PRECISION

_QMOD_SUFFIX = "qmod"
_SYNTHESIS_OPTIONS_SUFFIX = "synthesis_options.json"


def write_qmod(
    serialized_model: SerializedModel,
    name: str,
    directory: Optional[Path] = None,
    decimal_precision: int = DEFAULT_DECIMAL_PRECISION,
) -> None:
    model = Model.parse_raw(serialized_model)
    pretty_printed_model = DSLPrettyPrinter(decimal_precision=decimal_precision).visit(
        model
    )

    synthesis_options = model.dict(
        include={"constraints", "preferences"}, exclude_unset=True
    )

    synthesis_options_path = Path(f"{name}.{_SYNTHESIS_OPTIONS_SUFFIX}")
    if directory is not None:
        synthesis_options_path = directory / synthesis_options_path

    synthesis_options_path.write_text(json.dumps(synthesis_options, indent=2))

    native_qmod_path = Path(f"{name}.{_QMOD_SUFFIX}")
    if directory is not None:
        native_qmod_path = directory / native_qmod_path

    native_qmod_path.write_text(pretty_printed_model)
