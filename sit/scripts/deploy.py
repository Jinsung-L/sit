import click
from pathlib import Path
import traceback
import json
import re

from .setup import setup_remote
from .utils import execute, connect_ssh, remote_exec, remote_sudo


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
        click.echo("Remote server {server} is not set up. Setting up now...".format(
            server=click.style(SIT_CONFIG['remote_address'], 'cyan')
        ))

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
    click.echo("Installing dependencies. This might take a couple of minutes...")
    remote_exec(client, '{remote_path}/venv/bin/pip install --upgrade {dist_path}'.format(
        remote_path=SIT_CONFIG['remote_project_path'],
        dist_path=str(remote_dist_dir / build_filename)
    ), debug=debug)

    # Config Supervisor

    # Read project config
    with open(str(SIT_PATH / 'supervisord.conf')) as file:
        project_supervisord_conf = file.read()

    # Read remote config
    supervisord_conf_path = '/etc/supervisor/supervisord.conf'
    with sftp.open(supervisord_conf_path) as file:
        supervisord_conf = file.read().decode()

    # Modify remote config with local project config
    try:
        lines = supervisord_conf.splitlines()
        start = lines.index('[program:{}]'.format(PROJECT_NAME))

        try:
            end = lines.index('', start)
        except ValueError:
            end = len(lines)

        new_supervisord_conf = '\n'.join(lines[:start] + project_supervisord_conf.splitlines() + lines[end:])
    except ValueError:
        new_supervisord_conf = supervisord_conf + '\n' + project_supervisord_conf

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

    # Update sit config
    SIT_CONFIG['head'] = build_version
    with open(SIT_PATH / 'config.json', 'w') as file:
        json.dump(SIT_CONFIG, file, indent=4)


    app_url = "http://{}:{}/".format(SIT_CONFIG['remote_address'], SIT_CONFIG['gunicorn_port'])

    success_message = """
Success! Deployed {version} to {server}
You can now view {project_name} in the browser.

  {app_url}

Happy hacking!""".format(
        version=click.style(build_version, 'green'),
        server=click.style(SIT_CONFIG['remote_address'], 'cyan'),
        project_name=click.style(PROJECT_NAME, 'green'),
        # TODO: Drop the port after support of nginx
        app_url=click.style(app_url, underline=True)
    )
    click.echo(success_message)
