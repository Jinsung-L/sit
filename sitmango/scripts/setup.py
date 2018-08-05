import click
from pathlib import Path
import traceback
import json
import re

from .utils import connect_ssh, remote_exec, remote_sudo


def setup_remote(SIT_CONFIG, PASSWORD, debug=False):
    try:
        client = connect_ssh(
            address=SIT_CONFIG['remote_address'],
            username=SIT_CONFIG['remote_username'],
            password=PASSWORD
        )
    except:
        click.echo("{error} Can't connect to {addr}".format(
        error=click.style('ERROR:', 'red'),
        addr=click.style(SIT_CONFIG['remote_address'], 'cyan'),
        ))
        raise Exception("Can't connect to remote.")

    # Create project directory
    remote_exec(client, 'mkdir -p {}'.format(SIT_CONFIG['remote_project_path']), debug=debug)

    # Install Ubuntu packages through APT
    try:
        click.echo("Installing required ubuntu packages. This might take a couple of minutes...")
        remote_sudo(client, 'sudo apt update', PASSWORD, debug=debug)
        remote_sudo(client, 'sudo apt install python3', PASSWORD, debug=debug)
        remote_sudo(client, 'sudo apt install python3-pip', PASSWORD, debug=debug)
        remote_sudo(client, 'sudo apt install supervisor', PASSWORD, debug=debug)
    except:
        raise Exception("Failed to install ubuntu packages.")

    # Setup virtualenv
    try:
        remote_exec(client, 'rm -rf {}/venv/'.format(SIT_CONFIG['remote_project_path']), debug=debug)

        if debug: click.echo("Creating new virtualenv...")
        remote_exec(client, 'python3 -m venv {}/venv'.format(SIT_CONFIG['remote_project_path']), debug=debug)

        click.echo("Installing pip requirements. This might take a couple of minutes...")
        remote_exec(client, '{}/venv/bin/pip install --upgrade pip'.format(SIT_CONFIG['remote_project_path']), debug=debug)
        remote_exec(client, '{}/venv/bin/pip install --upgrade setuptools'.format(SIT_CONFIG['remote_project_path']), debug=debug)
        remote_exec(client, '{}/venv/bin/pip install --upgrade wheel'.format(SIT_CONFIG['remote_project_path']), debug=debug)
        remote_exec(client, '{}/venv/bin/pip install --upgrade python-dotenv gunicorn'.format(SIT_CONFIG['remote_project_path']), debug=debug)
    except:
        remote_exec(client, 'rm -rf {}/venv/'.format(SIT_CONFIG['remote_project_path']), debug=debug)
        raise Exception("Failed to set up virtualenv.")

    # Copy template

    return True


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def setup(ctx, debug):
    """Setup remote server."""
    DEBUG = ctx.obj['DEBUG'] or debug
    MODULE_PATH = ctx.obj['MODULE_PATH']

    PROJECT_PATH = Path('.')
    PROJECT_NAME = PROJECT_PATH.resolve().name

    # Check if there is package.
    if not (PROJECT_PATH / 'setup.py').is_file():
        click.echo("{} There is no python package found in this directory.", click.style('ERROR:', 'red'))
        ctx.exit()

    # Check if project initiated
    SIT_PATH = PROJECT_PATH / '.sit'
    if not SIT_PATH.is_dir():
        click.echo("{error} Sit is not configured. Run {} first.".format(
            click.style('ERROR:', 'red'),
            click.style('sit init', 'cyan'),
        ))
        ctx.exit()

    # Load config
    with open(SIT_PATH / 'config.json') as file:
        SIT_CONFIG = json.load(file)

    # Check if remote server is set up
    if SIT_CONFIG['remote_setup']:
        click.confirm('Remote server is already set up. Do you want to proceed it anyway?', abort=True)

    click.echo("Setting up remote server: {addr}".format(
        addr=click.style(SIT_CONFIG['remote_address'], 'cyan')
    ))

    # Input password
    PASSWORD = click.prompt("{user}@{addr}'s password".format(
        user=SIT_CONFIG['remote_username'],
        addr=SIT_CONFIG['remote_address'],
    ), hide_input=True)


    # Make SSH connection
    try:
        client = connect_ssh(
            address=SIT_CONFIG['remote_address'],
            username=SIT_CONFIG['remote_username'],
            password=PASSWORD
        )
    except:
        click.echo("{error} Can't connect to {addr}".format(
            error=click.style('ERROR:', 'red'),
            addr=click.style(SIT_CONFIG['remote_address'], 'cyan'),
        ))
        ctx.exit()

    # Setup remote
    try:
        SIT_CONFIG['remote_setup'] = setup_remote(SIT_CONFIG, PASSWORD, debug=DEBUG)
    except Exception as e:
        traceback.print_exc()
        click.echo("{error} Failed setting up {addr}".format(
            error=click.style('ERROR:', 'red'),
            addr=click.style(SIT_CONFIG['remote_address'], 'cyan'),
        ))
        ctx.exit()

    # Update config
    with open(SIT_PATH / 'config.json', 'w') as file:
        json.dump(SIT_CONFIG, file, indent=4)

    success_message = """
Successfuly set up the remote server {server}
at {server}:{path}

Now you can deploy your application:

  {sit_deploy}
    Deploys the application to the production server.

Then your flask app will be online.""".format(
        server=click.style(SIT_CONFIG['remote_address'], 'cyan'),
        path=click.style(SIT_CONFIG['remote_project_path'], 'green'),
        sit_deploy=click.style('sit deploy', 'cyan')
    )
    click.echo(success_message)
