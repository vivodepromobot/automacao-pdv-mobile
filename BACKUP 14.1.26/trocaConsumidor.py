import traceback
from datetime import datetime
from appium import webdriver
from config import *
from framework import *

def run_test_troca_consumidor():
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

        logger.info("--- INICIANDO PASSOS DO TESTE DE TROCA ---")
        
        executar_passo("Clicar no botão 'Realizar Troca'", 
                       lambda: clicar_por_texto(driver, "Realizar Troca"))
        
        executar_passo("Selecionar Vendedor",
                        lambda: clicar_por_id(driver, "txt_dialog_seller_name"))
        
        executar_passo("Fechar teclado com Back", lambda: fechar_teclado_back(driver))
        
        executar_passo("Rolar até encontrar o texto 'Período'",
                       lambda: scroll_ate_encontrar_texto(driver, "Período", max_scrolls=10))
        
        executar_passo("Clicar no campo 'Data inicial' para dar foco",
                       lambda: clicar_por_id(driver, "textInputLayout4"))

        data_atual = datetime.now().strftime('%d/%m/%Y')
        xpath_campo_data = f"//*[@resource-id='{APP_PACKAGE}:id/textInputLayout4']//android.widget.EditText"
        executar_passo(f"Inserir data atual ({data_atual})",
                       lambda: digitar_texto_por_xpath(driver, xpath_campo_data, data_atual))
        
        executar_passo("Fechar teclado com Back", lambda: fechar_teclado_back(driver))
        
        executar_passo("Rolar até encontrar o texto 'Consultar'",
                       lambda: scroll_ate_encontrar_texto(driver, "CONSULTAR", max_scrolls=10))
        executar_passo("Clicar no consultar",
                       lambda: clicar_por_id(driver, "button9"))

        executar_passo("Clicar no primeiro item da lista de notas",
               lambda: clicar_no_primeiro_da_lista_por_id(driver, "textView100"))

        popup_apareceu = clicar_em_texto_se_existir(driver, "SIM")
        
        if popup_apareceu:
            selecionar_cliente(driver, "1")
        
        executar_passo("Marcar item",
                       lambda: clicar_por_id(driver, "checkBox"))
        
        executar_passo("Clicar em 'Devolver Itens'",
                       lambda: clicar_por_id(driver, "button12"))
        
        executar_passo("Clicar no OK do pop-up de ATENÇÃO (se aparecer)", lambda: clicar_em_id_se_existir(driver, "md_buttonDefaultPositive", wait_time=5))
        
        executar_passo("Clicar no OK do pop-up de confirmação",
                       lambda: clicar_por_id(driver, "md_buttonDefaultPositive"))
        
        
        executar_passo("Validar Sucesso e fechar pop-up final",
                       lambda: validar_texto_e_clicar_por_id(driver, "Sucesso!", "md_buttonDefaultPositive"))
        
        executar_passo("Adicionar produto", lambda: clicar_por_id(driver, "btn_adicionar_produtos"))
        executar_passo("Procurar produto '123'", lambda: digitar_texto_por_id(driver, "editText", "123"))
        executar_passo("Clicar no produto", lambda: clicar_por_id(driver, "imageView3"))
        executar_passo("Clicar no botão AVANÇAR", lambda: clicar_por_id_com_espera(driver, "btn_proximo"))
        time.sleep(3) # Pausa estratégica para estabilizar a transição de tela e evitar Timeout no próximo passo
        executar_passo("Atalho de pagamento", lambda: clicar_por_id(driver, "switch_bonus"))
        executar_passo("Avançar →",lambda: clicar_por_id(driver, "btn_proceed"))
        executar_passo("Scroll", lambda: scroll_ate_encontrar_texto(driver, "Finalizar"))
        executar_passo("Finalizar", lambda: clicar_por_id(driver, "btnFinalizar"))
        
        executar_passo("Responder para Imprimir Comprovante (aguardando até 20s)", 
                       lambda: clicar_em_id_se_existir(driver, "android:id/button2", wait_time=20))
        time.sleep(2) # Aguarda o fechamento do diálogo de impressão para liberar a camada de clique
        executar_passo("Validar mensagem de sucesso ao fundo", lambda: find_element_by_text(driver, "Venda realizada com sucesso!"))
        executar_passo("Clicar no botão CONCLUIR VENDA", lambda: clicar_por_id(driver, "btn_confirmar_venda"))

        teste_passou = True

    except Exception as e:
        erro_capturado = traceback.format_exc()
        logger.error(f"ERRO CRÍTICO DURANTE A EXECUÇÃO DO TESTE DE TROCA: {e}")
        if driver: save_screenshot(driver, "CRITICO_TROCA")
    finally:
        end_time = datetime.now()
        status = "SUCESSO_TROCA" if teste_passou else "FALHA_TROCA"
        write_report(status, 
                     start_time, 
                     end_time, 
                     extra=erro_capturado)
        
        if driver:
            logger.info("Encerrando a sessão do driver...")
            driver.quit()
            logger.info("Sessão encerrada.")

if __name__ == "__main__":
    run_test_troca_consumidor()