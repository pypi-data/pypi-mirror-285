"""Circuit module for QuClo."""

from quclo.models import Circuit as CircuitModel


class Circuit:
    """A circuit."""

    def __init__(
        self,
        data: str,
    ):
        """Initialize the circuit."""
        assert CircuitModel(data=data)
        self.data = data

    def get_data(self) -> str:
        """Get the data of the circuit."""
        return self.data

    def _to_model(self) -> CircuitModel:
        """Return the circuit model."""
        return CircuitModel(data=self.data)
