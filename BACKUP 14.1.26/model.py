import traceback
from datetime import datetime
from appium import webdriver
from config import *
from framework import *

def run_test_modelo(): # 1. Alterar o nome da função
    start_time = datetime.now()
    driver = None
    teste_passou = False
    erro_capturado = None
    NOME_TESTE = "NOME_DO_TESTE_AQUI" # 2. Definir o nome amigável aqui

    try:
        appium_options = get_appium_options(limpar_dados_app=False)
        driver = executar_passo(
            "Conectar ao servidor Appium e iniciar o app",
            lambda: webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=appium_options)
        )
        garantir_login(driver)
        
        # --- SEUS PASSOS DE TESTE COMEÇAM AQUI ---
        
        # Exemplo: executar_passo("Passo 1", lambda: clicar_por_texto(driver, "Botão"))

        # --- SEUS PASSOS DE TESTE TERMINAM AQUI ---

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
    run_test_modelo() # 3. Alterar a chamada aqui