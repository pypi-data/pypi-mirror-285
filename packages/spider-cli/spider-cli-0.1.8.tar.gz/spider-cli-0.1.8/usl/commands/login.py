# usl/commands/login.py

import click
import webbrowser
from usl.utils.db import set_config

LOGIN_URL = "https://spider.minakilabs.dev/login"

@click.command()
def login():
    """
    Guide the user through the login process.
    """
    click.echo(f"Please log in at the following URL: {LOGIN_URL}")
    webbrowser.open(LOGIN_URL)
    api_key = click.prompt("Enter your API key")

    # Save the API key to the database
    set_config("api_key", api_key)

    click.echo("API key saved successfully.")

if __name__ == "__main__":
    login()
