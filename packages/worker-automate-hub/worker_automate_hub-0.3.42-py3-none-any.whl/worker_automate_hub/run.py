import asyncio

# import os
import subprocess

# from utils import updater


async def run_application():
    try:
        while True:
            print('Iniciando a aplicação...')
            process = subprocess.Popen(
                ['python', 'worker_automate_hub/main_process.py']
            )
            process.wait()

            # Verificar se a aplicação terminou solicitando uma atualização
            needs_update = process.returncode == 1
            if needs_update:
                print('Aplicando atualização...')
                # await updater.update_application(
                #     "https://drive.google.com/file/d/1teLQg7b0d_676ETChn9OO3EnsYIn49vn/view?usp=sharing"
                # )
                asyncio.wait(5)
                print('Atualização concluída. Reiniciando a aplicação...')
            else:
                break  # Se não foi uma atualização, sair do loop
    except asyncio.CancelledError:
        print('Aplicação encerrada pelo usuário.')


if __name__ == '__main__':
    asyncio.run(run_application())
