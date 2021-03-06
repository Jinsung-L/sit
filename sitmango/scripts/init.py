import click
from pathlib import Path
import shutil
import json
import re

from .utils import render_template


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

    # Check if project initiated
    SIT_PATH = PROJECT_PATH / '.sit'
    if SIT_PATH.is_dir():
        # Load config
        with open(SIT_PATH / 'config.json') as file:
            SIT_CONFIG = json.load(file)

        # Check if remote server is set up
        if SIT_CONFIG['remote_setup']:
            click.confirm('Remote server is already set up. Do you want to proceed it anyway?', abort=True)

    REMOTE_ADDRESS = click.prompt('Remote server address', type=str)
    REMOTE_USER = click.prompt('Remote user', type=str)

    # Create .sit directory
    SIT_PATH = PROJECT_PATH / '.sit'
    SIT_PATH.mkdir(parents=True, exist_ok=True)

    # Create config.json
    config = {
        'remote_address': REMOTE_ADDRESS,
        'remote_username': REMOTE_USER,
        'remote_project_path': '/home/{}/sit/{}'.format(REMOTE_USER, PROJECT_NAME),
        'remote_setup': False,
        # TODO: Update this to 'localhost' after support of nginx
        'gunicorn_host': '0.0.0.0',
        'gunicorn_port': 8000,
        'gunicorn_user': REMOTE_USER,
        'gunicorn_group': REMOTE_USER,
        'server_name': '',
    }

    CONFIG_PATH = SIT_PATH / 'config.json'

    with open(str(CONFIG_PATH), 'w') as file:
        json.dump(config, file, indent=4)

    # Copy supervisord.conf
    shutil.copyfile(
        MODULE_PATH / 'templates/sit/supervisord.conf',
        SIT_PATH / 'supervisord.conf'
    )

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
You can manually configure this file.

Now you can make your first deployment by running:

  {sit_deploy}
    Deploys the application to the production server.

This will set up the remote server at the first run.
After then, it'll just deploy your application.""".format(
        sit=click.style('sit', 'cyan'),
        project_name=click.style(PROJECT_NAME, 'green'),
        config_path=click.style(str(CONFIG_PATH), 'green'),
        sit_deploy=click.style('sit deploy', 'cyan')
    )
    click.echo(success_message)
