import importlib.metadata
import subprocess
import sys
from pathlib import Path

import requests
import toml
from packaging import version
from rich.console import Console

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


def update_package():
    """Update the current package to the latest version."""
    package_name = "worker-automate-hub"

    try:
        # Execute o comando pip para instalar a última versão do pacote
        subprocess.check_call(
            [sys.executable, "-m", "pipx", "upgrade", package_name]
        )
        # Caminho para o arquivo settings.toml
        home_dir = Path.home()
        config_file_path = home_dir / "worker-automate-hub" / "settings.toml"        
        config_path = home_dir / "worker-automate-hub"
        config_path.mkdir(exist_ok=True)        
        # download_assets_and_extract_from_drive()

        # Nova versão que você deseja definir
        nova_versao = get_package_version("worker-automate-hub")

        # Chamar a função para atualizar a versão
        update_version_in_toml(config_file_path, nova_versao)
        console.print("Package atualizado com sucesso!", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"Falha ao atualizar o package: {e}", style="bold red")
        sys.exit(1)


def check_for_update():
    """Check if there is a new version of the package available on PyPI."""
    package_name = "worker-automate-hub"
    current_version = importlib.metadata.version(package_name)

    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    latest_version = response.json()
    print("last: "+latest_version["info"]["version"])
    print("current: "+current_version)
    if version.parse(latest_version["info"]["version"]) > version.parse(current_version):
        console.print(
            f"Uma nova versão [bold cyan]({latest_version})[/bold cyan] está disponível. Atualizando..."
        )
        update_package()
    else:
        console.print("\nVocê está usando a versão mais atualizada.\n", style="green")
