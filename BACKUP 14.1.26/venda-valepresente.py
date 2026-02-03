import traceback
from datetime import datetime
from appium import webdriver
from config import *
from framework import *

def run_test_venda_valepresente(): 
    start_time = datetime.now()
    driver = None
    teste_passou = False
    erro_capturado = None
    NOME_TESTE = "Venda Vale Presente" 

    try:
        appium_options = get_appium_options(limpar_dados_app=False)
        driver = executar_passo(
            "Conectar ao servidor Appium e iniciar o app",
            lambda: webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=appium_options)
        )
        garantir_login(driver)
        
        executar_passo("Navegar para a tela de Vale Presente",lambda: clicar_por_texto (driver, "Vale Presente"))
        executar_passo("Selecionar Vendedor", lambda: clicar_por_id(driver, "txt_dialog_seller_name"))
        executar_passo("Clicar na label Cliente'",lambda: clicar_por_id(driver, "textView192"))
        executar_passo("Buscar cliente '1'", lambda: digitar_texto_por_id(driver, "search_src_text", "1"))
        executar_passo("Selecionar o cliente", lambda: clicar_por_id(driver, "rcv_search_customer"))
        executar_passo("Clicar em selecionar cliente", lambda: clicar_por_id(driver, "button3"))
        executar_passo("Inserir Valor no Campo",lambda: digitar_texto_por_id(driver, "textInputEditText", "15")) 

               


                                

            
        

        teste_passou = True
    except Exception as e:
        erro_capturado = traceback.format_exc()
        logger.error(f"ERRO CRÍTICO DURANTE {NOME_TESTE}: {e}")
        if driver: save_screenshot(driver, f"CRITICO_{NOME_TESTE}")
    finally:
        end_time = datetime.now()
        status = f"SUCESSO_{NOME_TESTE} ✅" if teste_passou else f"FALHA_{NOME_TESTE} ❌"
        write_report(status, start_time, end_time, extra=erro_capturado)
        
        if driver:
            driver.quit()

if __name__ == "__main__":
    run_test_venda_valepresente() #