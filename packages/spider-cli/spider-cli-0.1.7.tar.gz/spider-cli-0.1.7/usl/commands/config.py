# usl/commands/config.py

import click
from usl.utils.db import set_config, get_config

@click.command()
@click.option('--set', multiple=True, type=(str, str), help="Set configuration key-value pairs")
@click.option('--show', is_flag=True, help="Show current configuration")
@click.option('--api-key', help="Set the API key")
def config(set, show, api_key):
    """Configure the scraping tool settings."""
    if api_key:
        set_config('api_key', api_key)
        click.echo("API key updated.")

    if set:
        for key, value in set:
            set_config(key, value)
        click.echo(f"Configuration updated: {set}")

    if show:
        config_data = get_config()
        click.echo("Current configuration:")
        click.echo(config_data)

