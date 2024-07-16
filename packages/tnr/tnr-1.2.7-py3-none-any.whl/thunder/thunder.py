import click
from thunder import auth
import sys
import os
from thunder import thunder_helper
from thunder import container_helper
from importlib.metadata import version
import requests
from packaging import version as version_parser
from thunder import api

PACKAGE_NAME = "tnr"  # update if name changes
# Get the directory of the current file (thunder.py), then go up two levels to the root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, "..", "..")

# Add the src directory to sys.path
sys.path.append(root_dir)


class DefaultCommandGroup(click.Group):
    def resolve_command(self, ctx, args: list):
        try:
            # Try to resolve the command normally
            check_for_update()
            return super(DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.exceptions.UsageError:
            # If no command is found, default to 'run' and include the args
            return "run", run, args


@click.group(
    cls=DefaultCommandGroup,
    help="This CLI is the interface between you and Thunder Compute.",
    context_settings={'ignore_unknown_options': True, 'allow_extra_args': True},
)
@click.option('--version', '--v', is_flag=True, help="Show the CLI version.")
@click.pass_context
def cli(ctx, version):
    if version:
        click.echo(f"{PACKAGE_NAME} version {get_version()}")
        ctx.exit()


@cli.command(
    help="Runs a specified task on Thunder Compute. This is the default behavior of the tnr command. Please see thundergpu.net for detailed documentation.",
    context_settings={'ignore_unknown_options': True, 'allow_extra_args': True},
)
@click.option("--ngpus", default=1, help="Specify the number of GPUs to use.")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run(ngpus, args):
    if not args:  # Check if args is empty
        click.echo("No arguments provided. Exiting...")
        sys.exit(0)

    id_token, refresh_token, uid = auth.load_tokens()

    if not id_token or not refresh_token:
        click.echo("Please log in to begin using Thunder Compute.")
        id_token, refresh_token, uid = auth.login()

        if not id_token or not refresh_token:
            return
    
    if not api.is_token_valid(id_token):
        id_token, refresh_token, uid = auth.handle_token_refresh(refresh_token)


    # Create an instance of Task with required arguments
    task = thunder_helper.Task(ngpus, args, uid)

    # Initialize the session with the current auth token
    if not task.get_password(id_token):
        id_token, refresh_token, uid = auth.handle_token_refresh(refresh_token)
        if not id_token or not refresh_token or not uid:
            click.echo("Token, Refresh Token, or UID is invalid. Please log in again.")
        if not task.get_password(id_token):
            click.echo("Failed to retrieve password for session.")
            return

    # Execute the task
    if not task.execute_task(id_token):
        return

    # Close the session
    if not task.close_session(id_token):
        click.echo("Failed to close the session.")

@click.option('--port', '-p', multiple=True, help="Port(s) to forward from the container. To specify a continuous range use <start_port>:<end_port> syntax. To specify multiple port / ranges add another --port / -p flag.")
@cli.command(
    help="Creates a Docker container for running commands on Thunder Compute in MacOS and Windows. If you are having trouble in your linux environment, this command may help."
)
def container(port):
    container_helper.create_docker_container(port)


@cli.command(help="Logs in to Thunder Compute.")
def login():
    auth.login()


@cli.command(help="Logs out from the Thunder Compute CLI.")
def logout():
    auth.logout()


def check_for_update():
    try:
        current_version = version(PACKAGE_NAME)
        response = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=1)
        json_data = response.json() if response else {}
        latest_version = json_data.get("info", {}).get("version", None)
        if version_parser.parse(current_version) < version_parser.parse(latest_version):
            click.echo(
                f"Update available: {latest_version}. Run `pip install --upgrade {PACKAGE_NAME}` to update.",
                err=True,
            )
    except Exception as e:
        click.echo(f"Error checking for update: {e}", err=True)


def get_version():
    return version(PACKAGE_NAME)


if __name__ == "__main__":
    cli()