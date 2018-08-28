import click
from pathlib import Path
import traceback
import json
import re

from .utils import connect_ssh, remote_exec, remote_sudo


@click.command()
@click.option('--identify_file', '-i')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def delete(ctx, identify_file, debug):
    """Delete project from remote server."""
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

    if identify_file is None:
        # Input password
        PASSWORD = click.prompt("{user}@{addr}'s password".format(
            user=SIT_CONFIG['remote_username'],
            addr=SIT_CONFIG['remote_address'],
        ), hide_input=True)
    else:
        PASSWORD = None

    # Make SSH connection
    try:
        client = connect_ssh(
            address=SIT_CONFIG['remote_address'],
            username=SIT_CONFIG['remote_username'],
            password=PASSWORD,
            key_filename=identify_file
        )
        sftp = client.open_sftp()
    except:
        click.echo("{error} Can't connect to {addr}".format(
            error=click.style('ERROR:', 'red'),
            addr=click.style(SIT_CONFIG['remote_address'], 'cyan'),
        ))
        ctx.exit()

    click.echo("Deleting {project_name} from {server}. This might take a couple of minutes...".format(
        project_name=click.style(PROJECT_NAME, 'green'),
        server=click.style(SIT_CONFIG['remote_address'], 'cyan'),
    ))

    # Remove Supervisor config

    # Read remote config
    supervisord_conf_path = '/etc/supervisor/supervisord.conf'
    with sftp.open(supervisord_conf_path) as file:
        supervisord_conf = file.read().decode()

    # Erase local project config from the remote config
    try:
        lines = supervisord_conf.splitlines()
        start = lines.index('[program:{}]'.format(PROJECT_NAME))

        try:
            end = lines.index('', start)
        except ValueError:
            end = len(lines)

        new_supervisord_conf = '\n'.join(lines[:start] + lines[end+1:])
    except ValueError:
        new_supervisord_conf = supervisord_conf

    # Push temporary config file conatining new config
    temp_supervisord_conf_path = '{}/supervisord.conf'.format(SIT_CONFIG['remote_project_path'])
    with sftp.open(temp_supervisord_conf_path, 'w') as file:
        file.write(new_supervisord_conf)

    # sudo copy temp config file to /etc/supervisor/supervisord.conf
    command = 'sudo cp {} {}'.format(temp_supervisord_conf_path, supervisord_conf_path)
    remote_sudo(client, command, PASSWORD, debug=DEBUG)

    # Remove temp config file
    sftp.remove(temp_supervisord_conf_path)

    # Restart Supervisor
    remote_sudo(client, 'sudo supervisorctl reread', PASSWORD, debug=DEBUG)
    remote_sudo(client, 'sudo service supervisor restart', PASSWORD, debug=DEBUG)

    # Remove project directory
    remote_exec(client, 'rm -rf {}'.format(SIT_CONFIG['remote_project_path']), debug=DEBUG)

    # Update sit config
    SIT_CONFIG['head'] = None
    SIT_CONFIG['remote_setup'] = False
    with open(SIT_PATH / 'config.json', 'w') as file:
        json.dump(SIT_CONFIG, file, indent=4)

    success_message = """
{project_name} is completely deleted from {server}
If you want to deploy it again, just run:

  {sit_deploy}
    Deploys the application to the production server.

Happy hacking!""".format(
        project_name=click.style(PROJECT_NAME, 'green'),
        server=click.style(SIT_CONFIG['remote_address'], 'cyan'),
        sit_deploy=click.style('sit deploy', 'cyan')
    )
    click.echo(success_message)
