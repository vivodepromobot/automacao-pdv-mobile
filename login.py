# Arquivo: login.py

import traceback
from datetime import datetime
from appium import webdriver
from config import *
from framework import *

def run_test_login():
    start_time = datetime.now()
    driver = None
    teste_passou = False
    erro_capturado = None

    try:
        appium_options = get_appium_options(limpar_dados_app=True)
        driver = executar_passo(
            "Conectar ao servidor Appium e iniciar o app",
            lambda: webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=appium_options)
        )
        realizar_login_completo(driver)
        
        logger.info("-> Validando se o login foi bem-sucedido...")
        executar_passo("Verificar se o texto 'Iniciar Venda' está visível",
                       lambda: find_element_by_text(driver, "Iniciar Venda"))
        
        teste_passou = True

    except Exception as e:
        erro_capturado = traceback.format_exc()
        logger.error(f"ERRO CRÍTICO DURANTE O TESTE DE LOGIN: {e}")
        if driver: save_screenshot(driver, "CRITICO_LOGIN")
    finally:
        end_time = datetime.now()
        status = "SUCESSO_LOGIN" if teste_passou else "FALHA_LOGIN"
        write_report(status, start_time, end_time, extra=erro_capturado)
        
        if driver:
            logger.info("Encerrando a sessão do driver...")
            driver.quit()
            logger.info("Sessão encerrada.")

if __name__ == "__main__":
    run_test_login()