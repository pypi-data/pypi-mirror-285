import asyncio
import importlib.metadata
import os
import sys

import psutil
from rich.console import Console
from typer import Context, Exit, Option, Typer

from worker_automate_hub.api.client import get_workers, load_environments
from worker_automate_hub.utils.updater import check_for_update
import inquirer
from inquirer.themes import GreenPassion

from worker_automate_hub.core.so_manipulation import add_worker_config, download_assets_and_extract_from_drive, write_env_config
from .worker import run_worker

console = Console()
app = Typer()

HELP_MESSAGE = """
[b]Worker[/] - Grupo Argenta

Forma de uso: [b]worker [SUBCOMANDO] [ARGUMENTOS][/]

Existem 3 subcomandos disponíveis para essa aplicação

- [b]run[/]: Inicializa o Worker na máquina atual e começa a solicitar trabalho para o orquestrador.
- [b]validate[/]: Verifica se o Worker atual está configurado corretamente e pronto para ser inicializado.
- [b]assets[/]: Realiza a limpeza e depois download na pasta assets de todos arquivos utilizado pelo worker durante execução.

[b]Exemplos de uso:[/]
 [b][blue]RUN[/][/]
    [green][b]worker[/][/] [b]run[/]

 [b][blue]UPDATE[/][/]
    [green][b]worker[/][/] [b]update[/]

 [b][blue]VALIDATE[/][/]
    [green][b]worker[/][/] [b]validate[/]

---

[b]Help:[/]
 [b]Para mais informações[/]
    [green][b]worker[/][/] --help

 [b]Para ver a versão instalada[/]
    [green][b]worker[/][/] --version

 [b]Para gerar o arquivo de configuração[/]
    [green][b]worker[/][/] --configure

 [b]Para informações detalhadas
    [blue][link=https://github.com/SIM-Rede/worker-automate-hub]Repo no GIT Argenta[/][/] | [blue][link=https://pypi.org/project/worker-automate-hub/]Publicação no PyPI[/][/]
"""


def function_help(flag: bool):
    if flag:
        console.print(
            importlib.metadata.version("worker-automate-hub"),
            style="bold blue",
        )
        raise Exit(code=0)


def function_configure(flag: bool):

    if flag:
        console.clear()
        environment_names = [            
            "local",
            "qa",
            "main",
        ]
        q =[
            inquirer.Text("vault_token", "Por favor digite o token do Vault"),
            inquirer.List("env_list", "Selecione o ambiente", environment_names)]
        r = inquirer.prompt(q, theme=GreenPassion())

        env_sel, credentials = load_environments(r["env_list"], r["vault_token"])
        write_env_config(env_sel, credentials)
        workers = asyncio.run(get_workers())
        
        if workers == None:
            console.print("\nNenhum worker encontrado.\n", style="yellow")
            raise Exit(code=0)
        else:
        
            nomes_workers = [worker["nomRobo"] for worker in workers]
            q2 = [inquirer.List("worker_list", "Selecione um Worker", choices=nomes_workers)]
            r2 = inquirer.prompt(q2, theme=GreenPassion())
            worker_sel = next(worker for worker in workers if worker["nomRobo"] == r2["worker_list"])
            add_worker_config(worker_sel)
            # download_assets_and_extract_from_drive()

            raise Exit(code=0)


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    version: bool = Option(False, callback=function_help, is_flag=True),
    configure: bool = Option(False, callback=function_configure, is_flag=True)    
):
    if ctx.invoked_subcommand:
        return
    console.print(HELP_MESSAGE)

def is_already_running(script_name):
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                # Verifica se o processo atual é este script, mas não ele próprio
                if proc.info['pid'] != os.getpid() and cmdline and script_name in cmdline:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    except Exception as e:
        console.print(f"\nErro ao verificar se o processo já está em execução: {e}\n", style="bold red")        


@app.command()
def run():
    script_name = sys.argv[0]
    if is_already_running(script_name):
        console.print("O script já está em execução. Saindo...")
        sys.exit(0)
    else:
        asyncio.run(run_worker())


@app.command()
def update():
    check_for_update()
