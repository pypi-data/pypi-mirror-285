import webbrowser
from urllib.parse import urljoin

from classiq.interface.generator.quantum_program import QuantumProgram

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function
from classiq.analyzer.url_utils import circuit_page_uri, client_ide_base_url


async def handle_remote_app(circuit: QuantumProgram) -> None:
    circuit_dataid = await ApiWrapper.call_analyzer_app(circuit)
    app_url = urljoin(
        client_ide_base_url(),
        circuit_page_uri(circuit_id=circuit_dataid.id, circuit_version=circuit.version),
    )
    print(f"Opening: {app_url}")  # noqa: T201
    webbrowser.open_new_tab(app_url)


async def _show_interactive(self: QuantumProgram) -> None:
    await handle_remote_app(circuit=self)


QuantumProgram.show = syncify_function(_show_interactive)  # type: ignore[attr-defined]
QuantumProgram.show_async = _show_interactive  # type: ignore[attr-defined]
