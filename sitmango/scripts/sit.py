import click
from pathlib import Path


@click.group()
@click.version_option()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj['DEBUG'] = debug
    ctx.obj['MODULE_PATH'] = Path(__file__).parent.parent


from .create import create
from .init import init
from .setup import setup
from .deploy import deploy
from .delete import delete
cli.add_command(create)
cli.add_command(init)
cli.add_command(setup)
cli.add_command(deploy)
cli.add_command(delete)


if __name__ == '__main__':
    cli()
