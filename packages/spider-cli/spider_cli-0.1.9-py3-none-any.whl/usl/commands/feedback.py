import click
import requests
import json

@click.command(name='feedback')
@click.option('-n', '--name', prompt='Your name', help='The name of the feedback submitter.')
@click.option('-e', '--email', prompt='Your email', help='The email of the feedback submitter.')
@click.option('-f', '--feedback', prompt='Your feedback', help='The feedback to submit.')
def feedback(name, email, feedback):
    """Submit feedback to the MinakiLabs Spider Project."""
    url = "http://127.0.0.1:8004/submit-feedback/"
    headers = {"Content-Type": "application/json"}
    data = {
        "name": name,
        "email": email,
        "feedback": feedback
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        click.echo("Thank you for your feedback!")
    except requests.RequestException as e:
        click.echo(f"Failed to submit feedback: {e}", err=True)
