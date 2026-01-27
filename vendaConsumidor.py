import traceback
from datetime import datetime
from appium import webdriver
from config import *
from framework import *

def run_test_venda_consumidor():
    start_time = datetime.now()
    driver = None
    teste_passou = False
    erro_capturado = None

    try:
        appium_options = get_appium_options(limpar_dados_app=False)
        driver = executar_passo(
            "Conectar ao servidor Appium e iniciar o app",
            lambda: webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=appium_options)
        )
        garantir_login(driver)
        
        logger.info("--- INICIANDO PASSOS DO TESTE DE VENDA CONSUMIDOR ---")
        
      # --- INICIANDO PASSOS DO TESTE DE VENDA CONSUMIDOR ---
        
        executar_passo("Clicar no botão 'Iniciar Venda'", lambda: clicar_por_texto(driver, "Venda"))
        executar_passo("Selecionar Vendedor", lambda: clicar_por_id(driver, "txt_dialog_seller_name"))
        executar_passo("Tela selecionar cliente/ Clicar 'Iniciar Venda'", lambda: clicar_por_id(driver, "button30"))
        executar_passo("Adicionar produto", lambda: clicar_por_id(driver, "btn_adicionar_produtos"))
        executar_passo("Procurar produto '123'", lambda: digitar_texto_por_id(driver, "editText", "123"))
        executar_passo("Clicar no produto", lambda: clicar_por_id(driver, "imageView3"))
        executar_passo("Clicar no botão AVANÇAR", lambda: clicar_por_id_com_espera(driver, "btn_proximo"))
        time.sleep(3) # Pausa estratégica para estabilizar a transição de tela e evitar Timeout no próximo passo
        executar_passo("Atalho de pagamento", lambda: clicar_por_texto(driver, "DINHEIRO"))
        executar_passo("Clicar em Avançar com a forma selecionada", lambda: clicar_por_id(driver, "btn_proceed"))
        executar_passo("Botão finalizar", lambda: validar_texto_e_clicar_por_id(driver, "Finalizar", "btnFinalizar"))
        # RESOLUÇÃO: Espera até 20s pelo pop-up. Se aparecer em 1s, clica em 1s.
        executar_passo("Responder SIM para Imprimir Comprovante (aguardando até 20s)", 
                       lambda: clicar_em_id_se_existir(driver, "android:id/button2", wait_time=20))
        time.sleep(2) # Aguarda o fechamento do diálogo de impressão para liberar a camada de clique
        executar_passo("Validar mensagem de sucesso ao fundo", lambda: find_element_by_text(driver, "Venda realizada com sucesso!"))
        executar_passo("Clicar no botão CONCLUIR VENDA", lambda: clicar_por_id(driver, "btn_confirmar_venda"))
        
        teste_passou = True

    except Exception as e:
        erro_capturado = traceback.format_exc()
        logger.error(f"ERRO CRÍTICO DURANTE A EXECUÇÃO DO TESTE DE VENDA CONSUMIDOR: {e}")
        if driver: save_screenshot(driver, "CRITICO_VENDA_CONSUMIDOR")
    finally:
        end_time = datetime.now()
        status = "SUCESSO_VENDA_CONSUMIDOR" if teste_passou else "FALHA_VENDA_CONSUMIDOR"
        write_report(status, start_time, end_time, extra=erro_capturado)
        
        if driver:
            driver.quit()

if __name__ == "__main__":
    run_test_venda_consumidor()