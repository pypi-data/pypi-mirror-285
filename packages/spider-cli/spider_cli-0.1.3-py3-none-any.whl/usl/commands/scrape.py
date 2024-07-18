# usl/commands/scrape.py

import click
import requests
import json
from usl.utils.db import get_config

@click.command()
@click.argument('url')
@click.option('--output', default=None, help='Output file to save scraped data')
@click.option('--display', is_flag=True, help='Display the scraped data in the console')
def scrape(url, output, display):
    """Scrape the given URL and save the data to an output file or display it in the console."""
    api_key = get_config('api_key')
    if not api_key:
        click.echo("API key not found. Please set it using the `config` command.")
        return

    click.echo(f"Sending scrape request for {url} to backend service.")
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    try:
        response = requests.post("https://api.minakilabs.dev/spider-api/api/v1/scrape-html", params={"url": url}, headers=headers)
        response.raise_for_status()
        data = response.json()

        if display:
            click.echo(json.dumps(data, indent=4))

        if output:
            with open(output, 'w') as f:
                json.dump(data, f, indent=4)
            click.echo(f"Scraped data from {url} and saved to {output}")

    except requests.RequestException as e:
        click.echo(f"Failed to scrape {url}: {e}", err=True)

