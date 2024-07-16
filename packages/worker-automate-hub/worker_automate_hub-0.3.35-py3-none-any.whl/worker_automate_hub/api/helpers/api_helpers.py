from rich.console import Console

from worker_automate_hub.utils.logger import logger
from worker_automate_hub.utils.updater import check_for_update

console = Console()


async def handle_api_response(response, last_alive=False):

    status = response.status
    match status:
        case 200:
            if last_alive:
                console.print(
                    "\n[Worker last alive] Informado salvo com sucesso.\n",
                    style="bold green",
                )
            else:
                data = await response.json()
                return {"data": data, "update": False}
        case 204:
            console.print("204 - Nenhum processo encontrado", style="yellow")
            logger.info("204 - Nenhum processo encontrado")
        case 300:
            console.print("300 - Necessário atualização!", style="blue")
            logger.info("300 - Necessário atualização!")
            check_for_update()
        case 401:
            console.print("401 - Acesso não autorizado!", style="red")
            logger.error("401 - Acesso não autorizado!")
        case 404:
            console.print("404 - Nenhum processo disponível!", style="yellow")
            logger.error("404 - Nenhum processo disponível!")
        case 500:
            console.print("500 - Erro interno da API!", style="red")
            logger.error("500 - Erro interno da API!")
        case _:
            logger.error(f"Status não tratado: {status}")
    return None
