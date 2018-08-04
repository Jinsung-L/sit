import click
import paramiko
import subprocess
from pathlib import Path
import traceback
import os, shutil
import json
import re

from .setup import setup_remote
from .utils import execute, connect_ssh, remote_exec


@click.command()
@click.option('--dist-version')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def deploy(ctx, dist_version, debug):
    """Deploy to the remote server."""
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

    # Check if remote server is setup
    if not SIT_CONFIG['remote_setup']:
        click.echo("Remote server {server} is not setup. Setting up now...".format(
            server=click.style(SIT_CONFIG['remote_address'], 'cyan')
        ))

        # Update config
        try:
            SIT_CONFIG['remote_setup'] = setup_remote(SIT_CONFIG, PASSWORD, debug=DEBUG)

            with open(SIT_PATH / 'config.json', 'w') as file:
                json.dump(SIT_CONFIG, file, indent=4)
        except Exception as e:
            traceback.print_exc()
            click.echo("{error} Failed setting up {addr}".format(
                error=click.style('ERROR:', 'red'),
                addr=click.style(SIT_CONFIG['remote_address'], 'cyan'),
            ))
            ctx.exit()

    # Build source distribution
    if dist_version is None:
        click.echo("Building source distribution...")
        results = execute('{project_path}/venv/bin/python {project_path}/setup.py sdist --dist-dir={sit_path}/dist/'.format(
            project_path=PROJECT_PATH,
            sit_path=SIT_PATH,
        ).split(' '), debug=DEBUG)

        build_version = re.search(r'removing \'(?P<version>.+)\' \(and everything under it\)', results)
        if build_version is None:
            click.echo("{error} Build failed.".format(error=click.style('ERROR:', 'red')))
            ctx.exit()

        build_version = build_version.group('version')
    else:
        build_version = dist_version

    click.echo("Build version: {}".format(click.style(build_version, 'green')))

    # Push distribution
    remote_dist_dir = Path(SIT_CONFIG['remote_project_path']) / 'dist'
    build_filename = '{}.tar.gz'.format(build_version)

    remote_exec(client, 'mkdir -p {}'.format(str(remote_dist_dir)), debug=debug)

    sftp = client.open_sftp()
    sftp.put(
        str(SIT_PATH / 'dist' / build_filename),
        str(remote_dist_dir / build_filename),
    )

    # Install distribution
    click.echo("Installing dependencies. This might take a couple of minutes")
    remote_exec(client, '{remote_path}/venv/bin/pip install --upgrade {dist_path}'.format(
        remote_path=SIT_CONFIG['remote_project_path'],
        dist_path=str(remote_dist_dir / build_filename)
    ), debug=debug)


    SIT_CONFIG['head'] = build_version
    with open(SIT_PATH / 'config.json', 'w') as file:
        json.dump(SIT_CONFIG, file, indent=4)


#     success_message = """
# """.format(
#     )
#     click.echo(success_message)
