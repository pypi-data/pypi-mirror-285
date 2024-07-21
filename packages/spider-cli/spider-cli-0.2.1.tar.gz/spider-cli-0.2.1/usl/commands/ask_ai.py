# usl/commands/ask_ai.py

import click
import requests
from usl.utils.db import get_config

@click.command()
@click.argument('question')
def ask_ai(question):
    """Ask a question to the AI and get an answer."""
    api_key = get_config('api_key')
    if not api_key:
        click.echo("API key not found. Please set it using the `config` command.")
        return

    url = "https://api.minakilabs.dev/spider-api/api/v1/ask-ai"
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    data = {
        "question": question
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        answer = response.json().get('answer')
        click.echo(f"Answer: {answer}")
    except requests.HTTPError as http_err:
        click.echo(f"HTTP error occurred: {http_err}", err=True)
    except requests.RequestException as req_err:
        click.echo(f"Request error occurred: {req_err}", err=True)
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)
