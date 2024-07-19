import asyncio
import os
import sys

import psutil
import pyfiglet
from rich.console import Console

# Configuração do logger
from worker_automate_hub.utils.updater import check_for_update

from worker_automate_hub.api.client import get_new_task, notify_is_alive
from worker_automate_hub.config.settings import load_env_config
from worker_automate_hub.tasks.task_executor import perform_task
from worker_automate_hub.utils.logger import logger

console = Console()


async def check_and_execute_tasks():
    while True:
        try:
            run_count = 0
            first_run = run_count == 0
            if first_run:
                check_for_update()
            # Verificar e executar tarefas
            task = await get_new_task()
            if task == None:
                console.print("Processo não encontrado", style="red")
            else:
                if task["update"] == False:
                    logger.info(f"Executando a task: {task['task']['nomProcesso']}")
                    await perform_task(task["task"])
                else:
                    logger.info("\nSolicitando atualização...\n")
                    sys.exit(1)
            run_count += 1
            await asyncio.sleep(
                5
            )  # Esperar um pouco antes de verificar por novas tarefas

        except Exception as e:
            logger.error(f"Ocorreu um erro de execução: {e}")


async def notify_alive():
    env_config, _ = load_env_config()
    while True:
        try:
            logger.info("Notificando last alive...")
            await notify_is_alive()
            await asyncio.sleep(env_config["NOTIFY_ALIVE_INTERVAL"])
        except Exception as e:
            logger.error(f"Erro ao notificar que está ativo: {e}")
            await asyncio.sleep(
                env_config["NOTIFY_ALIVE_INTERVAL"]
            )  # Esperar um pouco antes de tentar novamente

def is_already_running(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Verifica se o processo atual é este script, mas não ele próprio
            if proc.info['pid'] != os.getpid() and script_name in proc.info['cmdline']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


async def main_process():
    env_config, worker_config = load_env_config()
    script_name = sys.argv[0]
    if is_already_running(script_name):
        console.print("O script já está em execução. Saindo...")
        sys.exit(0)

    # Exibir texto estilizado
    custom_font = "slant"  # Substitua pelo nome da fonte desejada
    ascii_banner = pyfiglet.figlet_format(f"Worker", font=custom_font)
    # console.clear()
    console.print(ascii_banner + f" versão: {env_config["VERSION"]}\n")
    logger.info(f"Worker em execução: {worker_config["NOME_ROBO"]}")
    console.print(f"Worker em execução: {worker_config["NOME_ROBO"]}\n", style="green")  # Mensagem de inicialização

    tasks = [check_and_execute_tasks(), notify_alive()]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main_process())
