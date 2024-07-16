import subprocess
import click
import os
import getpass
from docker_shell import DockerShell
import docker

def create_docker_container(ports):
    """
    Creates a Docker container for running commands on Thunder in MacOS and Windows. If you are having trouble in your linux environment, this command may help.
    """

    args = [
        "-u",
        "root",
    ]
    for port in ports:
        args.extend(["-p", port])

    try:
        if len(ports) == 0:
            msg = "Launching thunder container without forwarding any ports. To forward ports please run the `tnr container` command with the -p flag set"
        else:    
            msg = "Launching thunder container and forwarding the following ports:"
            for port in ports:
                msg += f"\n  - {port}"
        click.echo(click.style(msg, fg="blue", bold=True))

        image = "thundercompute/thunder:latest"
        shell = DockerShell(image, shell="", dockerArgs=args)

        if shell.requiresPull():
            click.echo(click.style("Pulling thunder docker image for the first time, this will take a while ...", fg="blue", bold=True))
        
        # Always pull to get the latest version
        shell.pull()
        shell.launch()

    except Exception as e:
        click.echo(
            click.style(
                f"Failed to launch docker container: {e}.",
                bg="red",
                fg="white",
                bold=True,
            )
        )
