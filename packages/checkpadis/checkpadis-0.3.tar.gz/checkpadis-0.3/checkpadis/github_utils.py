import os
import requests
import sys
import importlib.util
import click
import base64
from colorama import Fore

def download_file_from_github(url, temp_dir, token):
    local_filename = os.path.join(temp_dir, 'temp_script.py')
    headers = {'Authorization': f'token {token}'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.json()['content']
        file_content = base64.b64decode(content)
        with open(local_filename, 'wb') as f:
            f.write(file_content)
        return local_filename
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
 


def execute_temp_file(local_filename):
    import sys
    import importlib.util
    import click
    from colorama import Fore

    # añade el archivo descargado al path de importación de python
    temp_dir = os.path.dirname(local_filename)
    sys.path.insert(0, temp_dir)

    try:
        with open(local_filename, 'r') as f:
            print(f.read())

        # importamos el modulo temp_script
        module_name = 'temp_script'
        spec = importlib.util.spec_from_file_location(module_name, local_filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'ping'):
            click.echo(Fore.BLUE + "Executing 'ping' function:")
            result = module.ping()
            click.echo(result)
        else:
            click.echo(Fore.RED + "The function 'ping' was not found in the downloaded file.")
    finally:
        # limpiamos el path de importación
        sys.path.pop(0)
