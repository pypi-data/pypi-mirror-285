"""Data models for QuClo."""

from enum import Enum
from typing_extensions import Annotated
from annotated_types import Predicate
from pydantic import BaseModel, EmailStr
from quclo.utils import check_qasm, check_qir


OpenQASM3 = Annotated[str, Predicate(check_qasm)]
QIR = Annotated[str, Predicate(check_qir)]


class Priority(str, Enum):
    """A priority."""

    BEST = "best"
    """Best backend for the circuit."""
    SPEED = "speed"
    """Backend with the fastest gate speed."""
    ACCURACY = "accuracy"
    """Backend with the highest accuracy."""
    COST = "cost"
    """Backend with the lowest cost."""
    QUEUE = "queue"
    """Backend with the shortest queue time."""


class User(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    token: str | None = None  # access token or api key

    def __init__(self, **data):
        super().__init__(**data)
        if not (self.email and self.password) and not self.token:
            raise ValueError("Email and password or API key is required.")


class Backend(BaseModel):
    name: str


class Circuit(BaseModel):
    data: OpenQASM3 | QIR


class Execution(BaseModel):
    circuit: Circuit
    backend: Backend | None = None
    priority: Priority | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.backend and self.priority:
            raise ValueError("Cannot specify both backend and priority.")
        if not (self.backend or self.priority):
            raise ValueError("Either backend or priority is required.")
