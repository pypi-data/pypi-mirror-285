import click
import webbrowser
import os
from dotenv import load_dotenv
from usl.utils.db import set_config

# Load environment variables from .env file
load_dotenv()

# This needs to be .com not .dev by default
# Get the KONG_URL from environment variables
KONG_URL = os.getenv("SPIDER_URL", "https://spider.minakilabs.com")

LOGIN_URL = f"{KONG_URL}/login"

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
