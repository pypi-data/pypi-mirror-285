"""Execution module for QuClo."""

import requests
from quclo.utils import QUCLO_API_URL
from quclo.models import Priority, Execution as ExecutionModel
from quclo.circuit import Circuit
from quclo.backend import Backend


class Execution:
    """An execution."""

    def __init__(
        self,
        circuit: Circuit,
        backend: Backend | None = None,
        priority: Priority | None = None,
    ):
        """Initialize the circuit."""
        assert ExecutionModel(
            circuit=circuit._to_model(),
            backend=backend._to_model() if backend else None,
            priority=priority if priority else None,
        )
        self.circuit = circuit
        self.backend = backend
        self.priority = priority

    def _get_circuit_data(self) -> str:
        """Get the data of the circuit."""
        return self.circuit.get_data()

    def _get_backend_name(self) -> str | None:
        """Get the name of the backend."""
        return self.backend.get_name() if self.backend else None

    def _get_priority_value(self) -> str | None:
        """Get the value of the priority."""
        return self.priority.value if self.priority else None

    def run(self) -> dict:
        """Run the circuit."""
        response = requests.post(
            f"{QUCLO_API_URL}executions/",
            json={
                "circuit": self._get_circuit_data(),
                "backend": self._get_backend_name(),
                "priority": self._get_priority_value(),
            },
        )
        return response.json()
