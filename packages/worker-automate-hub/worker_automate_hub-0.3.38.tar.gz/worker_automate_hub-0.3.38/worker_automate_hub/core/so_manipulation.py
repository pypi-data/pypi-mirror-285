import json
import os
import io
import requests
import zipfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import toml
from pathlib3x import Path
from rich.console import Console
from worker_automate_hub.config.settings import get_package_version, load_env_config
from worker_automate_hub.utils.logger import logger

console = Console()


def write_env_config(env_dict: dict, google_credentials: dict):
    try:
        print("env: ", env_dict)
        home_dir = Path(os.path.expanduser("~"))
        config_path = home_dir / "worker-automate-hub"
        config_path.mkdir(exist_ok=True)        
        assets_path = config_path / "assets"
        logs_path = config_path / "logs"
        assets_path.mkdir(exist_ok=True)
        logs_path.mkdir(exist_ok=True)

        config_file_path = config_path / "settings.toml"
        config_data = {
            "name": "WORKER",
            "params": {
                "api_base_url": env_dict["API_BASE_URL"],
                "api_auth": env_dict["API_AUTHORIZATION"],
                "notify_alive_interval": env_dict["NOTIFY_ALIVE_INTERVAL"],
                "version": get_package_version("worker-automate-hub"),
                "log_level": env_dict["LOG_LEVEL"],
                "drive_url": env_dict["DRIVE_URL"]
            },
            "google_credentials": google_credentials["content"]
        }
        
        with open(config_file_path, "w") as config_file:
            toml.dump(config_data, config_file)
            console.print(f"\nArquivo de configuração criado em: {config_file_path}\n", style="green")

        logger.info(f"Arquivo de configuração do ambiente criado em {config_path}")
        return {
            "Message": f"Arquivo de configuração do ambiente criado em {config_path}",
            "Status": True,
        }
    except Exception as e:
        logger.error(f"Erro ao criar o arquivo de configuração do ambiente. Comando retornou: {e}")
        return {
            "Message": f"Erro ao criar o arquivo de configuração do ambiente.\n Comando retornou: {e}",
            "Status": False,
        }


def add_worker_config(worker):
    try:
        home_dir = Path(os.path.expanduser("~"))
        config_file_path = home_dir / "worker-automate-hub" / "settings.toml"

        if not config_file_path.exists():
            raise FileNotFoundError(f"O arquivo de configuração não foi encontrado em: {config_file_path}")

        with open(config_file_path, "r") as config_file:
            config_data = toml.load(config_file)

        config_data["id"] = {
            "worker_uuid": worker["uuidRobo"],
            "worker_name": worker["nomRobo"],
        }

        with open(config_file_path, "w") as config_file:
            toml.dump(config_data, config_file)

        console.print(f"\nInformações do worker adicionadas ao arquivo de configuração em {config_file_path}\n", style="green")
        console.print("\nConfiguração finalizada com sucesso!\n", style="bold green")
        return {
            "Message": f"Informações do worker adicionadas ao arquivo de configuração em {config_file_path}",
            "Status": True,
        }
    except Exception as e:
        return {
            "Message": f"Erro ao adicionar informações do worker ao arquivo de configuração.\n Comando retornou: {e}",
            "Status": False,
        }

def list_files_in_folder(folder_id, service):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, pageSize=1000, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])
    print("items: ", items)
    return items

def download_file(file_id, file_name, output_folder, service):
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(output_folder, file_name)
    
    with io.FileIO(file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Downloading {file_name}, {int(status.progress() * 100)}% complete.")

def download_assets_and_extract_from_drive():
    try:
        console.print("\nIniciando download dos assets...\n", style="bold green")
        env_config, creds_loaded = load_env_config()
        creds_loaded = json.loads(creds_loaded)["web"]   
        folder_url = env_config["DRIVE_URL"]
        home_dir = Path.home()
        config_path = home_dir / "worker-automate-hub"
        config_path.mkdir(exist_ok=True)               
        output_folder = config_path / "assets"
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

        credentials = service_account.Credentials.from_service_account_file(
        f"{config_path}\\credentials.json", scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        folder_id = folder_url.split('/')[-1].replace("?usp=drive_link", "")
        files = list_files_in_folder(folder_id, service)
        
        for file in files:
            file_id = file['id']
            file_name = file['name']
            
            download_file(file_id, file_name, output_folder, service)
            
            file_path = os.path.join(output_folder, file_name)
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_folder)
                os.remove(file_path)  # Remove the zip file after extraction

        console.print("\nAssets baixados com sucesso!\n", style="bold green")
    except Exception as e:
        logger.error(f"Erro ao baixar os assets: {e}")
        console.print(f"\nErro ao baixar os assets: {e} \n", style="bold red")
        