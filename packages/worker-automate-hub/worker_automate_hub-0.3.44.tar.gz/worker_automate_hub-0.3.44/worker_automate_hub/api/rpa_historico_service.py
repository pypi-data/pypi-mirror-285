import aiohttp


from worker_automate_hub.models.dto.rpa_hitorico_dto import RpaHistoricoDTO
from worker_automate_hub.config.settings import load_env_config
from worker_automate_hub.utils.logger import logger


async def store(data: RpaHistoricoDTO) -> dict:    
    env_config, _ = load_env_config()
    
    headers_basic = {"Authorization": f"Basic {env_config["API_AUTHORIZATION"]}", "Content-Type": "application/json"}  
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            payload = data.model_dump_json()      

            async with session.post(
                f"{env_config["API_BASE_URL"]}/historico",
                data=payload,
                headers=headers_basic,
            ) as response:
                response_text = await response.text()
                logger.info(f"Resposta store: {response_text}")

                if response.status == 200:
                    try:
                        response_data = await response.json()
                        return {
                            "success": response_data,
                            "status_code": response.status,
                        }
                    except aiohttp.ContentTypeError:
                        return {
                            "error": "Resposta não é JSON",
                            "status_code": response.status,
                        }
                else:
                    return {"error": response_text, "status_code": response.status}
    except aiohttp.ClientError as e:
        logger.error(f"Erro de cliente aiohttp: {str(e)}")
        return {"error": str(e), "status_code": 500}
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return {"error": str(e), "status_code": 500}

async def update(data: RpaHistoricoDTO) -> dict:    
    env_config, _ = load_env_config()
    headers_basic = {"Authorization": f"Basic {env_config["API_AUTHORIZATION"]}", "Content-Type": "application/json"} 
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            payload = data.model_dump_json()

            async with session.put(
                f"{env_config["API_BASE_URL"]}/historico",
                data=payload,
                headers=headers_basic,
            ) as response:
                response_text = await response.text()
                logger.info(f"Resposta update: {response_text}")

                if response.status == 200:
                    try:
                        response_data = await response.json()
                        return {
                            "success": response_data,
                            "status_code": response.status,
                        }
                    except aiohttp.ContentTypeError:
                        return {
                            "error": "Resposta não é JSON",
                            "status_code": response.status,
                        }
                else:
                    return {"error": response_text, "status_code": response.status}
    except aiohttp.ClientError as e:
        logger.error(f"Erro de cliente aiohttp: {str(e)}")
        return {"error": str(e), "status_code": 500}
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return {"error": str(e), "status_code": 500}
