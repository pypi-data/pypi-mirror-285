import click
import requests
import json
import jmespath
from dotenv import load_dotenv
import os
from usl.utils.db import get_config

# Load environment variables from .env file
load_dotenv()

# Get the base URL from environment variables
KONG_URL = os.getenv('KONG_URL', 'https://api.minakilabs.dev')

@click.command()
@click.argument('url')
@click.option('-q', '--query', required=True, help='JMESPath query string to filter JSON data')
@click.option('-o', '--output', default=None, help='Output file to save queried data')
@click.option('-d', '--display', is_flag=True, help='Display the queried data in the console')
def query(url, query, output, display):
    """Scrape the given URL, query the JSON data using JMESPath, and optionally save or display the result."""
    api_key = get_config('api_key')
    if not api_key:
        click.echo("API key not found. Please set it using the `config` command.")
        return

    headers = {"apikey": api_key, "Content-Type": "application/json"}
    params = {"url": url}  # URL as a query parameter
    data = {}  # No data in the body

    try:
        response = requests.post(
            f"{KONG_URL}/spider-api/api/v1/scrape-html",
            params=params,
            json=data,
            headers=headers
        )
        response.raise_for_status()
        response_data = response.json().get('data', {})

        # Apply JMESPath query
        filtered_data = jmespath.search(query, response_data)
        if filtered_data is None:
            click.echo(f"No data matched the query: {query}")
            return

        # Display or save the result
        if display:
            click.echo(json.dumps(filtered_data, indent=4))

        if output:
            with open(output, 'w') as f:
                json.dump(filtered_data, f, indent=4)
            click.echo(f"Queried data from {url} and saved to {output}")

    except requests.HTTPError as http_err:
        click.echo(f"HTTP error occurred: {http_err}", err=True)
    except requests.RequestException as req_err:
        click.echo(f"Request error occurred: {req_err}", err=True)
    except json.JSONDecodeError as json_err:
        click.echo(f"Failed to decode JSON from scrape output: {json_err}", err=True)
    except jmespath.exceptions.JMESPathError as jmespath_err:
        click.echo(f"JMESPath query error: {jmespath_err}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
