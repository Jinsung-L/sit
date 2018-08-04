import click
import subprocess
from pathlib import Path
import os, shutil
import json
import re


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def init(ctx, debug):
    """Initiate sit project on current folder."""
    DEBUG = ctx.obj['DEBUG'] or debug
    MODULE_PATH = ctx.obj['MODULE_PATH']

    PROJECT_PATH = Path('.')
    PROJECT_NAME = PROJECT_PATH.resolve().name

    # Check if there is package.
    if not (PROJECT_PATH / 'setup.py').is_file():
        click.echo(click.style('ERROR: ', 'red')+"There is no python package found in this directory.")
        ctx.exit()

    REMOTE_ADDRESS = click.prompt('Remote server address', type=str)
    REMOTE_USER = click.prompt('Remote user', type=str)

    # Create .sit directory
    SIT_PATH = PROJECT_PATH / '.sit'
    SIT_PATH.mkdir(parents=True, exist_ok=True)

    # Create config.json file
    config = {
        'remote_address': REMOTE_ADDRESS,
        'remote_username': REMOTE_USER,
        'remote_project_path': '/home/{}/sit/{}/'.format(REMOTE_USER, PROJECT_NAME),
        'remote_setup': False,
    }

    CONFIG_PATH = SIT_PATH / 'config.json'

    with open(str(CONFIG_PATH), 'w') as file:
        json.dump(config, file, indent=4)

    # Append .gitignore
    GITIGNORE_PATH = PROJECT_PATH / '.gitignore'

    with open(str(GITIGNORE_PATH)) as file:
        gitignore = file.read()

    if re.search(r'# sit', gitignore) is None:
        with open(str(GITIGNORE_PATH), 'a') as file:
            file.write("\n# sit\n.sit/\n")

    success_message = """
Initiated {sit} for {project_name}

Configuration file is created at {config_path}
You can manually configure your setup by edit this file.

Now you can make your first deployment

  {sit_deploy}
    Deploys the application to the production server.

This will setup the remote server at the first run.
After then, it'll just deploy your application.""".format(
        sit=click.style('sit', 'cyan'),
        project_name=click.style(PROJECT_NAME, 'green'),
        config_path=click.style(str(CONFIG_PATH), 'green'),
        sit_deploy=click.style('sit deploy', 'cyan')
    )
    click.echo(success_message)
