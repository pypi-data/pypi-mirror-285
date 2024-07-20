import click
import requests
import json
from dotenv import load_dotenv
import os
from usl.utils.db import get_config

# Load environment variables from .env file
load_dotenv()

# Get the base URL from environment variables
KONG_URL = os.getenv('KONG_URL', 'https://api.minakilabs.dev')

@click.command()
@click.argument('url')
@click.option('-o', '--output', default=None, help='Output file to save scraped data')
@click.option('-d', '--display', is_flag=True, help='Display the scraped data in the console')
def scrape(url, output, display):
    """Scrape the given URL and save the data to an output file or display it in the console."""
    api_key = get_config('api_key')
    if not api_key:
        click.echo("API key not found. Please set it using the `config` command.")
        return

    click.echo(f"Sending scrape request for {url} to backend service.")
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    params = {"url": url}

    try:
        response = requests.post(
            f"{KONG_URL}/spider-api/api/v1/scrape-html",
            headers=headers,
            params=params  # Send URL as a query parameter
        )
        response.raise_for_status()

        data = response.json()  # Ensure response is JSON

        if display:
            click.echo(json.dumps(data, indent=4))

        if output:
            with open(output, 'w') as f:
                json.dump(data, f, indent=4)
            click.echo(f"Scraped data from {url} and saved to {output}")

        return data  # Return the JSON data

    except requests.HTTPError as http_err:
        click.echo(f"HTTP error occurred: {http_err}", err=True)
        click.echo(f"Response content: {response.text}", err=True)
    except requests.RequestException as req_err:
        click.echo(f"Request error occurred: {req_err}", err=True)
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)
    return None
