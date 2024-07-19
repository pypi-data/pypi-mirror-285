import asyncio
import warnings
import time
from datetime import datetime
import pyperclip
import re

import pyautogui
from rich.console import Console
from pywinauto.application import Application

from worker_automate_hub.utils.logger import logger
from worker_automate_hub.utils.util import (
    kill_process,
    type_text_into_field,
    api_simplifica,
    find_element_center
)

from worker_automate_hub.utils.util import login_emsys

console = Console()

ASSETS_BASE_PATH = 'assets/descartes_images/'

async def descartes(task):
    #TODO depois tem q tirar o user do emsys q ta hard
    #prod
    # task["configEntrada"]["user"] = "rpa.woody"
    # task["configEntrada"]["pass"] = "rpa321"
    # dev
    task["configEntrada"]["user"] = "RPA.MARVIN"
    task["configEntrada"]["pass"] = "cba321"

    try:
        console.print(task)
        itens = task['configEntrada']['itens']

        #Abre um novo emsys
        await kill_process("EMSys")
        app = Application(backend='win32').start("C:\\Rezende\\EMSys3\\EMSys3.exe")
        warnings.filterwarnings("ignore", category=UserWarning, message="32-bit application should be automated using 32-bit Python")
        console.print("\nEMSys iniciando...", style="bold green")
        return_login = await login_emsys(task, app)
        
        if return_login['sucesso'] == True:
            type_text_into_field('Cadastro Pré Venda', app['TFrmMenuPrincipal']['Edit'], True, '50')
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('enter')
            console.print(f"\nPesquisa: 'Cadastro Pre Venda' realizada com sucesso", style="bold green")
        else:
            logger.info(f"\nError Message: {return_login["retorno"]}")
            console.print(f"\nError Message: {return_login["retorno"]}", style="bold red")
            return return_login

        time.sleep(7)

        #Pesquisa "cadastro pre-venda" só que no pyautogui
        # search_menu = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "search_menu.png", confidence=0.8, grayscale=True)
        # if search_menu is not None:
        #     print("Achou:"+ str(search_menu))
        #     pyautogui.click(pyautogui.center(search_menu))
        #     pyautogui.write('Cadastro Pre Venda')
        #     time.sleep(1)
        #     pyautogui.press('enter')
        #     time.sleep(1)
        #     pyautogui.press('enter')
        #     console.print(f"Pesquisa: 'Cadastro Pre Venda' realizada com sucesso", style="bold green")
        # else:
        #     logger.info(f"Error Message: Campo 'Menus de acesso' não encontrado")
        #     console.print(f"Error Message: Campo 'Menus de acesso' não encontrado", style="bold red")


        #Preenche data de validade
        field_validade = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_validade.png", confidence=0.8, grayscale=True)
        if field_validade is not None:
            pyautogui.click(pyautogui.center(field_validade))
            pyautogui.write(f'{datetime.now().strftime("%d/%m/%Y")}', interval=0.1)
            pyautogui.press('tab')
            console.print(f"\nValidade Digitada: '{datetime.now().strftime("%d/%m/%Y")}'", style="bold green")
            time.sleep(1)
        else:
            logger.info(f"\nError Message: Campo 'Validade' não encontrado")
            console.print(f"\nError Message: Campo 'Validade' não encontrado", style="bold red")

        #Condição da Pré-Venda
        condicao_field = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "condicao_pre_venda_descartes.png", confidence=0.8, grayscale=True)
        if condicao_field is not None:
            pyautogui.click(pyautogui.center(condicao_field))
            pyautogui.sleep(1)
            avista = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "a_vista_descartes.png", confidence=0.8, grayscale=True)
            pyautogui.click(pyautogui.center(avista))
            pyautogui.sleep(1)
            console.print(f"\nCondição 'A Vista' Selecionada", style="bold green")
        else:
            logger.info(f"\nError Message: Campo 'Condicao pre-venda' não encontrado")
            console.print(f"\nError Message: Campo 'Condicao pre-venda' não encontrado", style="bold red")

        #Preenche o campo do cliente com o número da filial
        cliente_field = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_cliente.png", confidence=0.8, grayscale=True)
        if cliente_field is not None:
            pyautogui.click(pyautogui.center(cliente_field))
            pyautogui.hotkey("ctrl", "a")
            pyautogui.hotkey("del")
            pyautogui.write(task['configEntrada']['filial'])
            pyautogui.hotkey("tab")
            console.print(f"\nCliente preenchido: '{task['configEntrada']['filial']}'", style="bold green")
            time.sleep(6)
        else:
            logger.info(f"\nError Message: Campo 'Cliente' não encontrado")
            console.print(f"\nError Message: Campo 'Cliente' não encontrado", style="bold red")

        #Clica em cancelar na Janela "Busca Representante"
        try:
            window_busca_representante = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "window_busca_representante.png", confidence=1, grayscale=True)
        except Exception as e:
            window_busca_representante = None 

        if window_busca_representante is not None:
            observacao = f"Posto {task['configEntrada']['filial']} - {task['configEntrada']['nomeEmpresa']} sem representante!"
            await api_simplifica(task['configEntrada']['urlRetorno'], "ERRO", observacao, task['configEntrada']['uuidSimplifica'], None)
            return {"sucesso": False, "retorno": observacao}
        
        time.sleep(2)

        #Aviso "Deseja alterar a condição de pagamento informada no cadastro do cliente?"
        try:
            payment_condition_warning = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "warning_change_payment_condition.png", confidence=0.95, grayscale=True)
        except:
           payment_condition_warning = None
        if payment_condition_warning is not None:
            button_no = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "warning_button_no.png", confidence=0.8, grayscale=True)
            pyautogui.click(pyautogui.center(button_no))
            console.print(f"\nClicou OK Mensagem 'Deseja alterar a condição de pagamento informada no cadastro do cliente?'", style="bold green")
            time.sleep(6)
        else:
            logger.info(f"\nError Message: Aviso de condição de pagamento não encontrado")
            console.print(f"\nError Message: Aviso de condição de pagamento não encontrado", style="bold red")


        #Seleciona 'Custo Médio' (Seleção do tipo de preço)
        try:
            custo_medio_select = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "select_custo_medio.png", confidence=0.8, grayscale=True)
        except Exception as e:
            custo_medio_select = None
        if custo_medio_select is not None:
            pyautogui.click(pyautogui.center(custo_medio_select))
            button_ok = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "select_ok_custo_medio.png", confidence=0.8, grayscale=True)
            pyautogui.click(pyautogui.center(button_ok))
            time.sleep(5)
            console.print(f"\nClicou OK 'Custo médio'", style="bold green")
        else:
            logger.info(f"\nError Message: Campo 'Custo Médio' não encontrado")
            console.print(f"\nError Message: Campo 'Custo Médio' não encontrado", style="bold red")

        #Clica em ok na mensagem "Existem Pré-Vendas em aberto para este cliente."
        try:
            existing_pre_venda = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "existing_pre_venda.png", confidence=0.8, grayscale=True)
        except:
            existing_pre_venda = None 
        if existing_pre_venda is not None:
            button_ok = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_ok.png", confidence=0.8, grayscale=True)
            pyautogui.click(pyautogui.center(button_ok))
            console.print(f"\nClicou OK 'Pre Venda Existente'", style="bold green")
            time.sleep(5)
        else:
            logger.info(f"\nError Message: Menssagem de prevenda existente não encontrada")
            console.print(f"\nError Message: Menssagem de prevenda existente não encontrada", style="bold yellow")
        
        #Seleciona 'Modelo' BAIXA DE EST.DECORRENTE DE PERDA, ROUBO OU DETERIORAÇÃO
        existing_field_modelo = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_modelo.png", confidence=0.8, grayscale=True)  
        if existing_field_modelo:
            pyautogui.click(existing_field_modelo.left + 100, existing_field_modelo.top)
            pyautogui.click(1700,800)
            pyautogui.write("B")
            time.sleep(2)
            pyautogui.hotkey('tab')
            console.print(f"\nSelecionou 'BAIXA DE EST.DECORRENTE DE PERDA, ROUBO OU DETERIORAÇÃO'", style="bold green")
        #Ultimo passo no menu capa

        #Abre Menu itens
        menu_itens = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "menu_itens.png", confidence=0.99, grayscale=True)
        if menu_itens is not None:
            pyautogui.click(pyautogui.center(menu_itens))
        
        time.sleep(2)

        #Loop de itens
        for item in itens:
            button_incluir = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_incluir.png", confidence=0.9, grayscale=True)
            pyautogui.click(pyautogui.center(button_incluir))
            time.sleep(5)
            console.print("\nClicou em 'Incluir'", style='bold green')            

            # Digita Almoxarifado
            button_almoxarifado = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_almoxarifado.png", confidence=0.99, grayscale=True)
            pyautogui.doubleClick(button_almoxarifado.left + 129, button_almoxarifado.top + 14)
            pyautogui.hotkey('del')
            pyautogui.write(task['configEntrada']['filial']+"99")
            pyautogui.hotkey('tab')
            time.sleep(3)
            console.print(f"\nDigitou almoxarifado {task['configEntrada']['filial']+"99"}", style='bold green')            

            # #Segue para o campo do item
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.write(item['codigoProduto'])
            pyautogui.hotkey('tab')
            time.sleep(5)
            console.print(f"\nDigitou codigo do produto {item['codigoProduto']}", style='bold green')            

            #Checa tela de pesquisa de item
            try:
                window_pesquisa_item = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "window_pesquisa_item.png", confidence=0.9, grayscale=True)
            except:
                window_pesquisa_item = None
            
            if window_pesquisa_item is not None:
                observacao = f"Item {item['codigoProduto']} não encontrado, verificar cadastro"
                await api_simplifica(task['configEntrada']['urlRetorno'], "ERRO", observacao, task['configEntrada']['uuidSimplifica'], None)
                return {"sucesso": False, "retorno": observacao}

            #Checa se existe alerta de item sem preço, se existir retorna erro(simplifica e bof)
            try:
                warning_price = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "warning_item_price.png", confidence=0.8, grayscale=False)
            except:
                warning_price = None
            if warning_price is not None:
                observacao = f"Item {item['codigoProduto']} não possui preço, verificar erro de estoque ou de bloqueio."
                await api_simplifica(task['configEntrada']['urlRetorno'], "ERRO", observacao, task['configEntrada']['uuidSimplifica'], None)
                return {"sucesso": False, "retorno": observacao}
            
            time.sleep(5)
            #Seleciona o Saldo Disponivel e verifica se ah possibilidade do descarte
            field_saldo_disponivel = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_saldo_disponivel.png", confidence=0.8, grayscale=True)
            if field_saldo_disponivel is not None:
                pyautogui.doubleClick(field_saldo_disponivel.left + 20, field_saldo_disponivel.top + 20)
                time.sleep(1)
                pyautogui.doubleClick(field_saldo_disponivel.left + 20, field_saldo_disponivel.top + 20)
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'c')
                amount_avaliable= ''
                amount_avaliable = pyperclip.paste()
                console.print(f"Saldo Disponivel: '{amount_avaliable}'", style="bold green")
                #Verifica se o saldo disponivel é valido para descartar
                if int(amount_avaliable) > 0 and int(amount_avaliable) >= int(item['qtd']): 
                    field_quantidade = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_quantidade.png", confidence=0.8, grayscale=True)
                    pyautogui.doubleClick(pyautogui.center(field_quantidade))
                    pyautogui.hotkey('del')
                    pyautogui.write(str(item['qtd']))
                    pyautogui.hotkey('tab')
                    time.sleep(2)
                else:
                    observacao = f"Saldo Disponivel: '{amount_avaliable}' menor que o valor que deveria ser descartado. Item: '{item['qtd']}'"
                    # if task['configEntrada']['precisaRetorno'] == True:
                    await api_simplifica(task['configEntrada']['urlRetorno'], "ERRO", observacao, task['configEntrada']['uuidSimplifica'], None)
                    console.print(observacao, style="bold red")
                    return {"sucesso": False, "retorno": observacao}

            #Clica em incluir para adicionar o item na nota
            button_incluir_item = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_incluir_item.png", confidence=0.8, grayscale=True)
            if button_incluir_item is not None:
                pyautogui.click(pyautogui.center(button_incluir_item))
                time.sleep(3)

            #Clica em cancelar para fechar a tela e abrir novamente caso houver mais itens
            button_cancela_item = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_cancela_item.png", confidence=0.8, grayscale=False)
            pyautogui.click(pyautogui.center(button_cancela_item))
            time.sleep(3)
        
        time.sleep(2)

        #Clica no botão "+" no canto superior esquerdo para lançar a pre-venda
        button_lanca_pre_venda = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_lanca_prevenda.png", confidence=0.8, grayscale=False)
        pyautogui.click(pyautogui.center(button_lanca_pre_venda))
        console.print("\nLancçou Pré-Venda", style="bold green")
        
        time.sleep(5)
        #Verifica mensagem de "Pré-Venda incluida com número: xxxxx"
        try:
            included_pre_venda = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "included_pre_venda.png", confidence=0.85, grayscale=False)
        except:
            observacao = f'Não achou mensagem pré-venda incluida'
            console.print(observacao,style='bold green')
            return {"sucesso": True, "retorno": observacao}
        
        #Clica no centro da mensagem e copia o texto para pegar o numero da pre-venda
        pyautogui.click(pyautogui.center(included_pre_venda))
        pyautogui.hotkey("ctrl", "c")
        pre_venda_message = ""
        pre_venda_message = pyperclip.paste()
        pre_venda_message = re.findall(r'\d+-\d+', pre_venda_message)
        console.print(f"Numero pré-venda: '{pre_venda_message[0]}'",style='bold green')

        #Clica no ok da mensagem
        button_ok = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_ok2.png", confidence=0.8, grayscale=True)
        pyautogui.click(pyautogui.center(button_ok))
        
        #Clica em Faturar
        button_faturar = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_faturar.png", confidence=0.8, grayscale=False)
        pyautogui.click(pyautogui.center(button_faturar))
        console.print(f"Clicou em: 'Faturar'",style='bold green')
         
        time.sleep(10)

        #Verifica se existe a mensagem de recalcular parcelas
        try:
            message_recalcular = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "message_recalcular_parcelas.png", confidence=0.85, grayscale=False)
        except:
            message_recalcular = None

        #Se existir clica em nao
        if message_recalcular is not None:
            button_no = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "warning_button_no.png", confidence=0.8, grayscale=True)
            pyautogui.click(pyautogui.center(button_no))
        else:
            logger.info(f"Mensagem de para recalcular parcelas da pre-venda nao existe")
            console.print(f"Mensagem de para recalcular parcelas da pre-venda nao existe", style="bold yellow")
        
        time.sleep(8)

        #Seleciona o modelo da nota (em teoria em prod nao precisa mas esta aqui por precaução) -- depreciado
        # pyautogui.hotkey("tab")
        # pyautogui.write("077")
        # time.sleep(5) 

        try:
            model_selected = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_model_select_model_077.png", confidence=0.95, grayscale=True)
            console.print("Modelo já selecionado", style="bold green")
        except:
            console.print("Modelo não está selecionado", style="bold yellow")
            model_selected = None
            
        if model_selected is None:
            console.print("Selecionando Modelo", style="bold green")
            try:
                field_modelo_faturamento = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_modelo_faturamento2.png", confidence=0.9, grayscale=True)
            except:      
                field_modelo_faturamento = None
            
            if field_modelo_faturamento is not None:
                pyautogui.click(field_modelo_faturamento.left, field_modelo_faturamento.top + 50)
                time.sleep(1)
                for _ in range(15):
                    pyautogui.keyDown('up')
                pyautogui.keyUp('up')
                               
            try:
                model_to_select = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "field_model_select_model_077.png", confidence=0.95, grayscale=True)
                pyautogui.click(pyautogui.center(model_to_select))
            except:
                observacao = {
                "Numero Pre Venda": pre_venda_message[0],
                "Numero da nota": ''
                }
                await api_simplifica(task['configEntrada']['urlRetorno'], "ERRO", observacao, task['configEntrada']['uuidSimplifica'], None)
                return {"sucesso": False, "retorno": "Falha ao selecionar modelo: Na tela de Faturamento Pré-Venda"}

        time.sleep(5)

        #Clicar no botao "OK" com um certo verde
        button_verde = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_ok_verde.png", confidence=0.99, grayscale=True)
        pyautogui.click(pyautogui.center(button_verde))

        time.sleep(5)

        #Aviso "Deseja faturar pré-venda?"
        try:
            faturar_pre_venda = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "faturar_pre_venda.png", confidence=0.9, grayscale=True)
        except:
            faturar_pre_venda = None

        if faturar_pre_venda is not None:
            button_yes = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "warning_button_yes.png", confidence=0.9, grayscale=True)
            pyautogui.click(pyautogui.center(button_yes))
        else:
            observacao = {
            "Numero Pre Venda": pre_venda_message[0],
            "Numero da nota": ''
            }
            await api_simplifica(task['configEntrada']['urlRetorno'], "ERRO", observacao, task['configEntrada']['uuidSimplifica'], None)
            return {"sucesso": False, "retorno": "Falha ao cliclar em: 'SIM' no aviso: 'Deseja realmente faturar esta Pré-Venda ?'"}

        time.sleep(7)

        #Mensagem de nota fiscal gerada com número
        nota_fical_gerada = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "message_nota_fiscal_gerada.png", confidence=0.99, grayscale=True)
        pyautogui.click(pyautogui.center(nota_fical_gerada))
        pyautogui.hotkey("ctrl", "c")
        nota_fiscal = pyperclip.paste()
        nota_fiscal = re.findall(r'\d+-?\d*', nota_fiscal)
        console.print(f"\nNumero NF: '{nota_fiscal[0]}'",style='bold green')

        time.sleep(7)

        #Transmitir a nota
        transmitir = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_transmitir.png", confidence=0.99, grayscale=True)
        pyautogui.click(pyautogui.center(transmitir))
        logger.error("\nNota Transmitida")
        console.print("\nNota Transmitida", style="bold green")
        
        time.sleep(7)
        #Fechar transmitir nota
        transmitir_fechar = pyautogui.locateOnScreen(ASSETS_BASE_PATH + "button_fechar_transmitir_nota.png", confidence=0.99, grayscale=True)
        pyautogui.click(pyautogui.center(transmitir_fechar))

        observacao = {
            "Numero Pre Venda": pre_venda_message[0],
            "Numero da nota": nota_fiscal[0]
        }

        await api_simplifica(task['configEntrada']['urlRetorno'], "SUCESSO", observacao, task['configEntrada']['uuidSimplifica'], nota_fiscal[0])
        return {"sucesso": True, "retorno": observacao}
    
    except Exception as ex:
        observacao = f"Erro Processo Descartes: {str(ex)}"
        logger.error(observacao)
        console.print(observacao, style="bold red")
        await api_simplifica(task['configEntrada']['urlRetorno'], "ERRO", observacao, task['configEntrada']['uuidSimplifica'], None)
        return {"sucesso": False, "retorno": observacao}