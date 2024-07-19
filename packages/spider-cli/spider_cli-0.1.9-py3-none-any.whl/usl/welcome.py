# usl/commands/welcome.py

import click
import requests
from usl.utils.db import get_config

@click.command()
def welcome():
    """Fetch and display the welcome message."""
    api_key = get_config('api_key')
    headers = {"apikey": api_key} if api_key else {}

    try:
        response = requests.get("https://api.minakilabs.dev/spider-api/", headers=headers)
        response.raise_for_status()
        data = response.json()
        click.echo(data["message"])
    except requests.RequestException as e:
        click.echo(f"Failed to fetch welcome message: {e}", err=True)
