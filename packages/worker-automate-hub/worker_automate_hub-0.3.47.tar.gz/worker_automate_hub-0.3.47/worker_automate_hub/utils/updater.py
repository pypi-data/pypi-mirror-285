import importlib.metadata
import subprocess
import sys
import os
from pathlib import Path

import requests
import toml
from packaging import version
from rich.console import Console
from worker_automate_hub.utils.logger import logger

from worker_automate_hub.config.settings import get_package_version, load_env_config
from worker_automate_hub.core.so_manipulation import download_assets_and_extract_from_drive
# from worker_automate_hub.core.so_manipulation import download_assets_from_drive

console = Console()


def update_version_in_toml(file_path, new_version):
    try:
        # Abrir e carregar o arquivo TOML
        with open(file_path, "r") as file:
            config = toml.load(file)

        # Alterar a versão
        config["params"]["version"] = new_version

        # Salvar as alterações de volta no arquivo TOML
        with open(file_path, "w") as file:
            toml.dump(config, file)

        print(f"Versão atualizada para {new_version} no arquivo {file_path}")
    except Exception as e:
        print(f"Erro ao atualizar a versão: {e}")

def create_update_script(new_version):
    try:
        # Caminho da pasta worker-automate-hub na raiz do usuário
        user_root = os.path.expanduser('~')
        work_dir = os.path.join(user_root, 'worker-automate-hub')

        # Caminho do arquivo TOML
        toml_file_path = os.path.join(work_dir, 'settings.toml')

        # Comando para fechar a aplicação
        close_command = 'taskkill /F /IM worker.exe'

        # Comando para atualizar o pacote via pipx
        update_command = 'pipx upgrade worker-automate-hub'

        # Comando para atualizar a versão no arquivo TOML
        update_toml_command = f'python -c "import toml; config=toml.load(\'{toml_file_path}\'); config[\'params\'][\'version\'] = \'{new_version}\'; toml.dump(config, open(\'{toml_file_path}\', \'w\'))"'

        # Comando para reiniciar a aplicação
        restart_command = f'start cmd /K "cd /D {work_dir} && worker run"'

        # Caminho do arquivo de log
        log_file_path = os.path.join(work_dir, 'update.log')

        # Criando o conteúdo do script .bat
        script_content = f"""
        @echo off
        {close_command}
        {update_command}
        if %errorlevel% equ 0 (
            echo Update successful, updating version in TOML file...
            {update_toml_command}
            echo Version updated successfully, restarting the application...
            {restart_command}
        ) else (
            echo Update failed. > "{log_file_path}"
            echo Error code: %errorlevel% >> "{log_file_path}"
            echo See pipx output for more details. >> "{log_file_path}"
        )
        """

        # Caminho completo para o arquivo update.bat
        bat_file_path = os.path.join(work_dir, 'update.bat')

        # Escrevendo o conteúdo no arquivo update.bat
        with open(bat_file_path, 'w') as file:
            file.write(script_content.strip())

        console.print("\nArquivo de update criado com sucesso!\n", style="bold green")
        logger.info("Arquivo de update criado com sucesso!")
        return bat_file_path

    except Exception as e:
        console.print(f"\nErro ao criar o arquivo de update: {e}\n", style="bold red")
        logger.error(f"Erro ao criar o arquivo de update: {e}")


def run_update_script(bat_file_path):
    try:
        # Executando o script .bat
        subprocess.run([bat_file_path], check=True, shell=True)
        console.print("\nupdate.bat executado com sucesso!\n", style="bold green")
        logger.info("update.bat executado com sucesso!")
    except subprocess.CalledProcessError as e:
        console.print(f"\nErro ao executar o update.bat: {e}\n", style="bold red")
        logger.error(f"Erro ao executar o update.bat: {e}")

def get_installed_version(package_name):
    try:
        result = subprocess.run(['pipx', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if package_name in line:
                # Parse the version from the line, assuming the line format is 'package_name <version>'
                return line.split(' ')[5].replace(',', '')
    except subprocess.CalledProcessError as e:
        console.print(f"\nOcorreu um erro ao obter a versão do pacote instalada: {e}\n", style="bold red")
        logger.error(f"Ocorreu um erro ao obter a versão do pacote instalada: {e}")
    return None

def check_for_update():
    try:
        """Check if there is a new version of the package available on PyPI."""
        package_name = "worker-automate-hub"
        current_version = get_installed_version(package_name)

        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        latest_version = response.json()
        console.print("last: "+latest_version["info"]["version"])
        console.print("current: "+current_version)
        if version.parse(latest_version["info"]["version"]) > version.parse(current_version):
            console.print(
                f"Uma nova versão [bold cyan]({latest_version["info"]["version"]})[/bold cyan] está disponível. Atualizando..."
            )
            bat_file_path = create_update_script(latest_version["info"]["version"])
            run_update_script(bat_file_path)
        else:
            # Caminho da pasta worker-automate-hub na raiz do usuário
            user_root = os.path.expanduser('~')
            work_dir = os.path.join(user_root, 'worker-automate-hub')

            # Caminho do arquivo TOML
            toml_file_path = os.path.join(work_dir, 'settings.toml')
            update_version_in_toml(toml_file_path, current_version)
            console.print("\nVocê está usando a versão mais atualizada.\n", style="green")
    except Exception as e:
        console.print(f"\nErro ao verificar novas versões do pacote: {e}\n", style="bold red")
        logger.error(f"Erro ao verificar novas versões do pacote: {e}")