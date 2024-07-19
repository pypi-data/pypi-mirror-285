# usl/commands/query.py

import click
import requests
import json
import jmespath
from usl.utils.db import get_config

@click.command()
@click.argument('url')
@click.option('--query', required=True, help='JMESPath query string to filter JSON data')
@click.option('--output', default=None, help='Output file to save queried data')
@click.option('--display', is_flag=True, help='Display the queried data in the console')
def query(url, query, output, display):
    """Scrape the given URL, query the JSON data using JMESPath, and optionally save or display the result."""
    api_key = get_config('api_key')
    if not api_key:
        click.echo("API key not found. Please set it using the `config` command.")
        return

    click.echo(f"Sending scrape request for {url} to backend service.")
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(f"http://172.168.1.167:8002/api/v1/scrape-html?url={url}", headers=headers)
        response.raise_for_status()
        data = response.json()['data']
        
        # Apply JMESPath query
        filtered_data = jmespath.search(query, data)
        if filtered_data is None:
            click.echo(f"No data matched the query: {query}")
            return

        if display:
            click.echo(json.dumps(filtered_data, indent=4))

        if output:
            with open(output, 'w') as f:
                json.dump(filtered_data, f, indent=4)
            click.echo(f"Queried data from {url} and saved to {output}")

    except requests.RequestException as e:
        click.echo(f"Failed to scrape {url}: {e}", err=True)
    except json.JSONDecodeError as e:
        click.echo(f"Failed to decode JSON from scrape output: {e}", err=True)


