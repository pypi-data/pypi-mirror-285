import os
import platform
import socket
import sys
import typing

import click

from ytservice import daemon

# Constants for response codes
RESULT_CODE_ERROR = 0
RESULT_CODE_SUCCESS = 1


def get_local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        return local_ip
    except socket.error:
        return "127.0.0.1"


def is_mac() -> bool:
    """
    is Mac
    :return:
    """
    return platform.system() == "Darwin"


# Helper function to build a standard response dictionary
def build_response(code: int = RESULT_CODE_SUCCESS,
                   data: typing.Any = None,
                   message: str = None) -> dict:
    response = {"code": code}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response


def run_service(app_name: str, signal: str, out_path: str = "/dev/null",
                error_path: str = "/dev/null"):
    """
    run service
    """
    if not is_mac():
        click.echo(message="Not Support")
        return
    try:
        cmd_path = os.path.abspath(sys.argv[0])
        if cmd_path.endswith(".py"):
            click.echo(message="Not Support", err=True)
            return
        if signal == "install":
            cmd = [cmd_path]
            environment = {"PATH": "/opt/homebrew/bin:/usr/local/bin"}
            daemon.mac_install(name=app_name, program_arguments=cmd, out_path=out_path, error_path=error_path,
                               environment_variables=environment)
            click.secho("Done", fg="green")
        elif signal == "start":
            daemon.mac_start(name=app_name)
            click.secho("Done", fg="green")
        elif signal == "stop":
            daemon.mac_stop(name=app_name)
            click.secho("Done", fg="green")
        elif signal == "status":
            is_install = daemon.mac_is_install(name=app_name)
            if is_install:
                is_running = daemon.mac_is_running(name=app_name)
                if is_running:
                    click.secho("Running", fg="green")
                else:
                    click.secho("Stopped", fg="red")
            else:
                click.secho("Not Install", fg="red")
        elif signal == "rm":
            daemon.mac_rm(name=app_name)
            click.secho("Done", fg="green")
        else:
            pass
    except RuntimeError as e:
        click.secho(e, fg="red")
