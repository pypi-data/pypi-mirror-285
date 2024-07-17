import asyncio
import sys

import pyfiglet
from rich.console import Console

# Configuração do logger
from worker_automate_hub.utils.updater import check_for_update

from worker_automate_hub.api.client import get_new_task, notify_is_alive
from worker_automate_hub.config.settings import NOTIFY_ALIVE_INTERVAL, VERSION
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
    while True:
        try:
            logger.info("Notificando last alive...")
            await notify_is_alive()
            await asyncio.sleep(NOTIFY_ALIVE_INTERVAL)
        except Exception as e:
            logger.error(f"Erro ao notificar que está ativo: {e}")
            await asyncio.sleep(
                NOTIFY_ALIVE_INTERVAL
            )  # Esperar um pouco antes de tentar novamente


async def main_process():
    # Exibir texto estilizado
    custom_font = "slant"  # Substitua pelo nome da fonte desejada
    ascii_banner = pyfiglet.figlet_format(f"Worker", font=custom_font)
    console.clear()
    console.print(ascii_banner + f" versão: {VERSION}\n")
    logger.info("Worker em execução.")
    console.print("Worker em execução.\n", style="green")  # Mensagem de inicialização

    tasks = [check_and_execute_tasks(), notify_alive()]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main_process())
