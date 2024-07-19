# usl/cli.py

import click
import importlib
from art import text2art
from termcolor import colored
from halo import Halo
from time import sleep
import pkgutil

#@click.group()
#def cli():
#    """Main entry point for the CLI."""
#    pass


#@click.group(invoke_without_command=True)
#@click.pass_context
#def cli(ctx):
#    """Main entry point for the CLI."""
#    if ctx.invoked_subcommand is None:
#        art = text2art("Tunnel Spider")
#        click.echo(art)
#        click.echo(ctx.get_help())

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Main entry point for the CLI."""
    if ctx.invoked_subcommand is None:
        ascii_art = text2art("Tunnel Spider")
        colored_art = colored(ascii_art, 'cyan')
        click.echo(colored_art)
        spinner = Halo(text='Loading', spinner='dots')
        spinner.start()
        sleep(1)  # Simulate a long-running task
        spinner.succeed('Done!')
        click.echo(cli.get_help(ctx))

# Dynamically load all commands from the commands directory
def load_commands():
    package = importlib.import_module('usl.commands')
    for _, name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f'usl.commands.{name}')
        cli.add_command(getattr(module, name))

load_commands()

if __name__ == "__main__":
    cli()
