"""The CLI to interface with the Celestical Serverless Cloud."""
import logging
from logging import Logger
from typing import Optional
from typing_extensions import Annotated

import typer

from celestical.compose import (
    upload_compose,
    upload_images)
from celestical.docker_local import list_local_images
from celestical.helper import cli_panel, print_text, print_feedback , confirm_user
from celestical.user import user_login, user_register,load_config
from celestical.configuration import cli_logger, welcome
from celestical.apps import list_creator_apps


cli_logger.info("Starting CLI.")

app = typer.Typer(pretty_exceptions_short=False,
                  no_args_is_help=True,
                  help=welcome(),
                  rich_markup_mode="rich")

# @app.callback(invoke_without_command=True)
@app.command()
def apps():
    """List all apps from current user."""
    list_creator_apps()


@app.command()
def login() -> None:
    """Login to Parametry's Celestical Cloud Services via the CLI."""
    user_login()


@app.command()
def register():
    """Register as a user for Celestical Cloud Services via the CLI."""
    flag = user_register()
    config = load_config()
    if flag == 0:
        print_text("User already exists or We could not connect.")
    if flag in (1,3):
        mgs = "You can now login with user "
        mgs += f"[yellow]{config['username']}[/yellow] using [blue]celestical login[/blue]"
        cli_panel(mgs)


@app.command()
def images():
    """ List all local docker images for you.
        Similar to 'docker image ls'.
    """
    table = list_local_images()

    if table is None:
        cli_panel("Docker service is [red]unaccessible[/red]\n")
    else:
        cli_panel("The following are your local docker images\n"
                 +f"{table}")


@app.command()
def deploy(compose_path: Annotated[Optional[str], typer.Argument()] = "./"):
    """Select, prepare and push your applications (docker-compose.yml) to the Celestical Cloud."""
    # --- First the compose enrichment:
    # 1- find compose file
    # 2- enrich it
    enriched_compose = upload_compose(compose_path)

    # --- Upload images according to response
    # 1- read response, and feedback user on status
    # 2- if 200, select the list of images in response.
    # 3- compress concerned images
    # 4- upload concerned images
    # .. keep feedback to user whenever progress is made
    if enriched_compose is None:
        msg = "To continue with deployment you need a celestical account.\n"
        msg += "see command: [yellow]celestical register[/yellow]"
        cli_panel(msg)
        return

    upload_images(app_uuid=enriched_compose["celestical"]["app_id"], e_compose=enriched_compose)


