import os
import click
from colorama import init, Fore
import tempfile
import requests
from checkpadis.github_utils import download_file_from_github, execute_temp_file

init(autoreset=True)

url = "https://api.github.com/user/orgs"
 
def verify_org_membership(token, org_name="IngSoft-PADIS-2024-1"):
   
    headers = {'Authorization': f'token {token}'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        orgs = response.json()
        for org in orgs:
            if org['login'] == org_name:
                return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def construct_github_url(org_name, repo_path):
    base_url = "https://api.github.com/repos"
    return f"{base_url}/{org_name}/{repo_path}/contents/temp_script.py"

@click.command()
@click.argument('file_path')
@click.argument('pokemon_name')
@click.argument('repo_path')
def checkpadis(file_path, pokemon_name, repo_path):
    token = click.prompt('Please enter your GitHub token', hide_input=True)

    if not verify_org_membership(token):
        click.echo(Fore.RED + "The provided token does not have access to the required organization.")
        return

    github_url = construct_github_url("IngSoft-PADIS-2024-1", repo_path)

    if os.path.exists(file_path):
        click.echo(Fore.GREEN + f"The file '{file_path}' exists.")
        pokemon_data = get_pokemon_data(pokemon_name)
        click.echo(pokemon_data)

        with tempfile.TemporaryDirectory() as temp_dir:
            click.echo(Fore.YELLOW + f"Downloading file from GitHub: {github_url}")
            downloaded_file = download_file_from_github(github_url, temp_dir, token)

            if downloaded_file:
                click.echo(Fore.GREEN + f"File downloaded successfully.")
                execute_temp_file(downloaded_file)
            else:
                click.echo(Fore.RED + "Failed to download the file.")
    else:
        click.echo(Fore.RED + f"The file '{file_path}' does not exist.")

def get_pokemon_data(pokemon_name):
    url = "https://pokeapi.co/api/v2/pokemon/"
    try:
        response = requests.get(url + pokemon_name)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: Received status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

if __name__ == '__main__':
    checkpadis()
