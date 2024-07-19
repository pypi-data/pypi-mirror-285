from datetime import datetime
from pytz import timezone
from rich.console import Console

from worker_automate_hub.api.client import get_processo
from worker_automate_hub.api.rpa_historico_service import store, update
from worker_automate_hub.models.dto.rpa_hitorico_dto import RpaHistoricoDTO, RpaHistoricoStatusEnum
from worker_automate_hub.tasks.task_definitions import task_definitions
from worker_automate_hub.utils.logger import logger

console = Console()


async def perform_task(task):
    console.print(
        f"\nProcesso a ser executado: {task['nomProcesso']}\n", style="green"
    )
    logger.info(f"Processo a ser executado: {task['nomProcesso']}")
    task_uuid = task["uuidProcesso"]
    processo = await get_processo(task_uuid)       
    historico = await _store_historico(task, processo)
    try:
        if task_uuid in task_definitions:            
            result = await task_definitions[task_uuid](task)
            await _update_historico(historico["success"]["uuidHistorico"], task, result["sucesso"], result, processo)
            return result
        else:
            console.print(f"Processo não encontrado: {task_uuid}", style="yellow")
            logger.error(f"Processo não encontrado: {task_uuid}")
            await _update_historico(historico["success"]["uuidHistorico"], task, False, {"sucesso": False, "retorno": f"Processo não encontrado: {task_uuid}"}, processo)
            return None
    except Exception as e:
        console.print(f"Erro ao performar o processo: {e}\n", style="red")
        logger.error(f"Erro ao performar o processo: {e}")
        await _update_historico(historico["success"]["uuidHistorico"], task, False, {"sucesso": False, "retorno": f"Erro ao performar o processo: {e}"}, processo)

async def _store_historico(task: dict, processo: dict):
    try:
        from worker_automate_hub.config.settings import load_worker_config
        worker_config = load_worker_config()
        tz = timezone("America/Sao_Paulo")
        start_time = datetime.now(tz).isoformat()

        # Armazenar início da operação no histórico
        start_data = RpaHistoricoDTO(
            uuidProcesso=task["uuidProcesso"],
            uuidRobo=worker_config["UUID_ROBO"],
            prioridade=processo["prioridade"],
            desStatus=RpaHistoricoStatusEnum.Processando,
            configEntrada=task["configEntrada"],
            datInicioExecucao=start_time,
            datEntradaFila=task["datEntradaFila"]
        )
        
        store_response = await store(start_data)
        console.print(f"\nHistorico salvo: {store_response}")
        return store_response
    except Exception as e:
        console.print(f"Erro ao salvar o histórico do processo: {e}\n", style="red")
        logger.error(f"Erro ao salvar o histórico do processo: {e}")

async def _update_historico(historico_uuid: str, task: dict, sucesso: bool, retorno_processo: dict, processo: dict):  
    try: 
        from worker_automate_hub.config.settings import load_worker_config
        worker_config = load_worker_config()
        tz = timezone("America/Sao_Paulo")
        des_status = (
                        RpaHistoricoStatusEnum.Sucesso
                        if sucesso
                        else RpaHistoricoStatusEnum.Falha
                    )
        end_time = datetime.now(tz).isoformat()

        # Armazenar fim da operação no histórico
        end_data = RpaHistoricoDTO(
            uuidHistorico=historico_uuid,
            uuidProcesso=task["uuidProcesso"],
            uuidRobo=worker_config["UUID_ROBO"],
            prioridade=processo["prioridade"],
            desStatus=des_status,
            configEntrada=task["configEntrada"],
            retorno=retorno_processo,
            datFimExecucao=end_time,
        )

        
        update_response = await update(end_data)
        console.print(f"\nHistorico atualizado: {update_response}")
        return update_response
    
    except Exception as e:
        console.print(f"Erro ao atualizar o histórico do processo: {e}\n", style="red")
        logger.error(f"Erro ao atualizar o histórico do processo: {e}")