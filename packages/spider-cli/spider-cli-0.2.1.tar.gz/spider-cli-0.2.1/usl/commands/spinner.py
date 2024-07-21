# usl/commands/spinner.py

import click
from halo import Halo
import time

@click.command()
def spinner():
    """Display a fancy loading spinner."""
    spinner = Halo(text='Loading', spinner='dots')
    spinner.start()
    time.sleep(5)  # Simulate a long-running task
    spinner.stop()
    click.echo("Done!")

