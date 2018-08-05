import click
import shutil
from pathlib import Path

from .setup_venv import setup_venv, venv_pip
from .utils import render_template


@click.command()
@click.argument('name')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def create(ctx, name, debug):
    """Create sit smaple project from template."""
    DEBUG = ctx.obj['DEBUG'] or debug
    MODULE_PATH = ctx.obj['MODULE_PATH']
    TEMPLATE_PATH = ctx.obj['MODULE_PATH'] / 'templates' / 'local'

    PROJECT_PATH = Path(name)

    click.echo('')
    click.echo("Creating a new Flask app in {}.".format(
        click.style(str(PROJECT_PATH.resolve()), fg='green')
    ))
    click.echo('')

    # Copy project template
    shutil.copytree(TEMPLATE_PATH, PROJECT_PATH, copy_function=shutil.copyfile)
    (PROJECT_PATH / 'application').rename(PROJECT_PATH / name)
    (PROJECT_PATH / 'gitignore').rename(PROJECT_PATH / '.gitignore')
    (PROJECT_PATH / 'env').rename(PROJECT_PATH / '.env')

    # Render templates
    render_template(PROJECT_PATH / 'setup.py',
        project_name=name
    )
    render_template(PROJECT_PATH / '.env',
        project_name=name
    )
    render_template(PROJECT_PATH / 'MANIFEST.in',
        project_name=name
    )

    # Setup virtualenv
    dependencies = ['flask','python-dotenv']
    package_names = ', '.join(map(lambda x: click.style(x, fg='cyan'), dependencies[:-1]))
    package_names += ', and {}'.format(click.style(dependencies[-1], 'cyan'))

    click.echo("Installing packages. This might take a couple of minutes.")
    click.echo("Installing {}...".format(package_names))

    venv_path = PROJECT_PATH / 'venv'
    setup_venv(venv_path, dependencies=['pip','setuptools','wheel']+dependencies, debug=DEBUG)

    with open(PROJECT_PATH / 'requirements.txt', 'w') as file:
        file.write(venv_pip('list --format=freeze --not-required', venv_path))

    # QUESTION: Not necessary?
    # venv_pip('install -e {}'.format(PROJECT_PATH))

    # Print success messages
    success_messages = """
Success! Created {project_name} at {project_path}
Inside that directory, you can run several commands:

  {flask_run}
    Starts the development server.

  {sit_init}
    Prepares the deployment to the production server.

  {sit_deploy}
    Deploys the application to the production server.

We suggest that you begin by typing:

  {cd} {project_name}
  {sit_init}
  {sit_deploy}

Happy hacking!""".format(
        project_name=name,
        project_path=str(PROJECT_PATH.resolve()),
        flask_run=click.style('flask run', 'cyan'),
        sit_init=click.style('sit init', 'cyan'),
        sit_deploy=click.style('sit deploy', 'cyan'),
        cd=click.style('cd', 'cyan'),
        source=click.style('source', 'cyan'),
    )
    click.echo(success_messages)
