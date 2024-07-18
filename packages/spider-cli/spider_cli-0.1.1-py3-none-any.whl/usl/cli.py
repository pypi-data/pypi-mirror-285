# usl/cli.py

import click
import importlib
import pkgutil

@click.group()
def cli():
    """Main entry point for the CLI."""
    pass

# Dynamically load all commands from the commands directory
def load_commands():
    package = importlib.import_module('usl.commands')
    for _, name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f'usl.commands.{name}')
        cli.add_command(getattr(module, name))

load_commands()

if __name__ == "__main__":
    cli()
