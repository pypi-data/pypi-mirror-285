"""Main module for the QuClo CLI."""

import typer
from importlib.metadata import version
from typing import Optional
from typing_extensions import Annotated
from quclo.user import User
from quclo.execution import Execution
from quclo.circuit import Circuit
from quclo.backend import Backend
from quclo.config import Config
from quclo.models import Priority

app = typer.Typer()
create_app = typer.Typer()
list_app = typer.Typer()
get_app = typer.Typer()
edit_app = typer.Typer()

app.add_typer(create_app, name="create", help="Create a new resource")
app.add_typer(list_app, name="list", help="List all resources")
app.add_typer(get_app, name="get", help="Get details of a resource")
app.add_typer(edit_app, name="edit", help="Edit a resource")


# Version callback
def version_callback(value: bool):
    """Show the version information."""
    if value:
        typer.echo(f"QuClo version: {version('quclo')}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Show the version information",
        is_eager=True,
    ),
):
    """CLI entry point."""
    return


# Create user command
@create_app.command(help="Create a new user")
def user(
    email: Annotated[str, typer.Option(help="Email for the user")],
    password: Annotated[
        str,
        typer.Option(
            prompt=True,
            confirmation_prompt=True,
            hide_input=True,
            help="Password for the user",
        ),
    ],
):
    """Create a new user."""
    resource = User(email=email, password=password)
    resource.create()
    typer.echo(f"User created with email: {email}")


# Create apikey command
@create_app.command(help="Create a new API key")
def apikey(
    email: Annotated[str, typer.Option(help="Email of the user")],
    password: Annotated[
        str,
        typer.Option(
            prompt=True,
            hide_input=True,
            help="Password of the user",
        ),
    ],
    duration: Annotated[
        Optional[int], typer.Option(help="Duration of the API key")
    ] = None,
):
    """Create a new API key."""
    resource = User(email=email, password=password)
    api_key = resource.get_api_key(duration=duration)
    typer.echo(
        f"API key created for email: {email} with duration: {duration if duration is not None else '∞'} days"
    )


# Create circuit command
@create_app.command(help="Create a new circuit")
def circuit(
    file: Annotated[
        Optional[str], typer.Option(help="Path to the QASM or QIR file")
    ] = None,
    qasm: Annotated[
        Optional[str], typer.Option(help="QASM code for the circuit")
    ] = None,
    qir: Annotated[
        Optional[str], typer.Option(help="QIR or LLVM IR code for the circuit")
    ] = None,
    backend: Annotated[
        Optional[str], typer.Option(help="Name of the backend to run the circuit")
    ] = None,
    priority: Annotated[
        Optional[Priority], typer.Option(help="Priority for the backend")
    ] = None,
):
    """Create a new circuit."""
    data = qasm or qir or (open(file).read() if file is not None else None)
    assert data, "No data provided for the circuit"
    resource = Execution(
        circuit=Circuit(data=data),
        backend=Backend(name=backend) if backend else None,
        priority=priority if priority else None,
    )
    typer.echo("Circuit created")


# Create config command
@create_app.command(help="Create a new configuration")
def config(
    email: Annotated[
        Optional[str], typer.Option(help="Email of the default user")
    ] = None,
    password: Annotated[
        Optional[str],
        typer.Option(
            prompt=True,
            hide_input=True,
            help="Password of the default user",
        ),
    ] = None,
    backend: Annotated[
        Optional[str], typer.Option(help="Name of the default backend")
    ] = None,
    priority: Annotated[
        Optional[Priority], typer.Option(help="Priority for the default backend")
    ] = None,
):
    """Create a new configuration."""
    if backend and priority:
        typer.echo("Cannot specify both backend and priority")
        raise typer.Exit(1)
    config = Config()
    if email:
        config.save_default_user(email)
    if backend:
        config.save_default_backend(backend)
    if priority:
        config.save_default_priority(priority)
    typer.echo("Configuration created")


# List backends command
@list_app.command(help="List all available backends")
def backends():
    """List all available backends."""
    typer.echo("List of all available backends")


# List circuits command
@list_app.command(help="List all submitted circuits")
def circuits():
    """List all submitted circuits."""
    typer.echo("List of all submitted circuits")


# Get backend details command
@get_app.command(help="Get details of a backend")
def backend(name: Annotated[str, typer.Argument(help="Name of the backend")]):
    """Get details of a backend."""
    backend = Backend(name=name)
    typer.echo(f"Details of backend: {name}")


# Get circuit details command
@get_app.command(help="Get details of a circuit")
def circuit(circuit_id: Annotated[str, typer.Argument(help="ID of the circuit")]):
    """Get details of a circuit."""
    typer.echo(f"Details of circuit with ID: {circuit_id}")


# Get user details command
@get_app.command(help="Get details of a user")
def user(email: Annotated[str, typer.Argument(help="Email of the user")]):
    """Get details of a user."""
    typer.echo(f"Details of user with email: {email}")


# Get config details command
@get_app.command(help="Get details of the configuration")
def config():
    """Get details of the configuration."""
    typer.echo("Details of the configuration")


# Edit circuit command
@edit_app.command(help="Edit a circuit")
def circuit(
    circuit_id: Annotated[str, typer.Argument(help="ID of the circuit")],
    qasm: Annotated[
        Optional[str], typer.Option(help="QASM code for the circuit")
    ] = None,
    qir: Annotated[
        Optional[str], typer.Option(help="QIR or LLVM IR code for the circuit")
    ] = None,
    file: Annotated[
        Optional[str], typer.Option(help="Path to the QASM or QIR file")
    ] = None,
    backend: Annotated[Optional[str], typer.Option(help="Name of the backend")] = None,
    priority: Annotated[
        Optional[str], typer.Option(help="Priority for the backend")
    ] = None,
):
    """Edit a circuit."""
    typer.echo(f"Circuit with ID: {circuit_id} edited")


# Edit user details command
@edit_app.command(help="Edit user details")
def user(
    email: Annotated[str, typer.Option(help="New email for the default user")],
    password: Annotated[
        Optional[str],
        typer.Option(
            prompt=True,
            confirmation_prompt=True,
            hide_input=True,
            help="New password for the default user",
        ),
    ] = None,
):
    """Edit user details."""
    typer.echo(f"User details updated for email: {email}")


# Edit config details command
@edit_app.command(help="Edit configuration details")
def config(
    email: Annotated[
        Optional[str], typer.Option(help="Email of the default user")
    ] = None,
    password: Annotated[
        Optional[str],
        typer.Option(
            prompt=True,
            hide_input=True,
            help="Password of the default user",
        ),
    ] = None,
    backend: Annotated[
        Optional[str], typer.Option(help="Name of the default backend")
    ] = None,
    priority: Annotated[
        Optional[str], typer.Option(help="Priority for the default backend")
    ] = None,
):
    """Edit configuration details."""
    if backend and priority:
        typer.echo("Cannot specify both backend and priority")
        raise typer.Exit(1)
    config = Config()
    if email:
        config.save_default_user(email)
    if backend:
        config.save_default_backend(backend)
    if priority:
        config.save_default_priority(priority)
    typer.echo("Configuration updated")


if __name__ == "__main__":
    app()
