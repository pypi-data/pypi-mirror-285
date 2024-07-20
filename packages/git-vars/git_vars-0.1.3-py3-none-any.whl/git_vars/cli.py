"""
Main section where parsing of the package 'gitlab-variables' is done.
This script provides a command-line interface (CLI) for managing GitLab environment variables.
It utilizes Click for command-line argument parsing and asyncio for asynchronous operations.
"""

import click
import asyncio
from .utils import handle_error
from .push import push_vars
from .pull import pull_vars

@click.group()
@click.version_option(version="0.1", prog_name="git-vars")
def cli():
    """GitLab environment variable management pip package"""

@cli.command()
@click.option('-t', '--access-token', help="GitLab access token")
@click.option('-r', '--repository-url', help="GitLab repository url")
@click.option('-s', '--scope', type=click.Choice(['project', 'group', 'instance']), default='project',
              help="Scope of environment variables: project | group | instance (default: project)")
@click.option('-o', '--output-file', help="output path")
def pull(access_token, repository_url, scope, output_file):
    """Pull GitLab repo environment variables to file"""
    # Create a dictionary to store command-line arguments
    vars_dict = {
        'access_token': access_token,
        'repository_url': repository_url,
        'scope': scope,
        'output_file': output_file
    }
    try:
        asyncio.run(pull_vars(vars_dict))
    except Exception as err:
        handle_error(err)

@cli.command()
@click.option('-t', '--access-token', help="GitLab access token")
@click.option('-r', '--repository-url', help="GitLab repository url")
@click.option('-s', '--scope', type=click.Choice(['project', 'group', 'instance']), default='project',
              help="Scope of environment variables: project | group | instance (default: project)")
@click.option('-e', '--env-vars', help="Environment variables file")
def push(access_token, repository_url, scope, env_vars):
    """Push GitLab repo environment variables to file"""
    # Create a dictionary to store command-line arguments
    vars_dict = {
        'access_token': access_token,
        'repository_url': repository_url,
        'scope': scope,
        'env_vars': env_vars
    }
    try:
        asyncio.run(push_vars(vars_dict))
    except Exception as err:
        handle_error(err)

def main():
    cli()

if __name__ == "__main__":
    main()
