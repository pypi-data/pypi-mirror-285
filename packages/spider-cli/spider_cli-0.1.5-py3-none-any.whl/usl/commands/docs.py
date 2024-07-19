# usl/commands/docs.py

import click
import webbrowser
from usl.utils.db import get_config

@click.command()
def docs():
    """Open the API documentation in a web browser."""
    api_key = get_config('api_key')
    if not api_key:
        click.echo("API key not found. Please set it using the `config` command.")
        return

    docs_url = f"http://127.0.0.1:8000/docs?apikey={api_key}"
    click.echo(f"Opening documentation at {docs_url}")
    webbrowser.open(docs_url)
