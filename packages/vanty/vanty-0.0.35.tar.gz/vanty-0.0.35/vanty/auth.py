import rich
import typer

from vanty._client import Client
from vanty.config import _store_user_config, config, user_config_path
from vanty.utils.console_printer import vlog

app = typer.Typer(name="auth", help="Manage tokens.", no_args_is_help=True)


@app.command(
    help="Set license token for connecting to advantch.com."
    "If not provided with the command, you will be prompted"
    " to enter your credentials."
)
def set(license_token: str):
    server_url = config.get("server_url")
    rich.print(f"Verifying token against [blue]{server_url}[/blue]")
    data = Client.verify(server_url, license_token)
    if data.is_valid:
        rich.print("[green]Token verified successfully[/green]")
        _store_user_config(
            {"token_id": data.token_id, "token_secret": data.token_secret}
        )
        rich.print(f"Token written to {user_config_path}")
        return data.token_id

    else:
        rich.print(
            "[red]Unable to verify invalid[/red]. "
            "Please check your license id and try again."
        )
        rich.print("If this problem persists, please contact support@advantch.com")
        return None


@app.command(help="Remove the token from the config file.")
def remove():
    _store_user_config({"token_id": None, "token_secret": None})
    vlog.info(f"Token removed from {user_config_path}")
    return None


@app.command(help="Log in to obtain an authentication token for browsing projects.")
def login(username: str = typer.Option(..., prompt=True),
          password: str = typer.Option(..., prompt=True, hide_input=True)):
    response = Client.login(username, password)
    if response.is_valid:
        _store_user_config({"auth_token": response.token})
        rich.print("[green]Login successful![/green]")
        rich.print(f"Authentication token written to {user_config_path}")
        return response.token
    else:
        rich.print(f"[red]Login failed: {response.message}[/red]")
        return None

@app.command(help="Log out and remove authentication token.")
def logout():
    if Client.logout():
        _store_user_config({"auth_token": None})
        rich.print("[green]Logged out successfully[/green]")
    else:
        rich.print("[red]Logout failed[/red]")

@app.command(help="Display current authentication status.")
def status():
    status_data = Client.check_status()
    if status_data["is_authenticated"]:
        rich.print("[green]Authenticated[/green]")
    else:
        rich.print(f"[red]Not authenticated: {status_data.get('message', 'Unknown reason')}[/red]")
