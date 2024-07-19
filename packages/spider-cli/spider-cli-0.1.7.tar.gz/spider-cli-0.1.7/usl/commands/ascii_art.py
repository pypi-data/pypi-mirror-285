# usl/commands/ascii_art.py

import click
from art import text2art

@click.command()
def ascii_art():
    """Generate and display ASCII art for 'Tunnel Spider'."""
    art = text2art("Tunnel Spider")
    click.echo(art)
