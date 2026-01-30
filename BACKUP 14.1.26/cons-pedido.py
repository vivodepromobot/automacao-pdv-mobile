import traceback
from datetime import datetime
from appium import webdriver
from config import *
from framework import *

def run_test_consulta_pedido_venda():
    start_time = datetime.now()
    driver = None
    teste_passou = False
    erro_capturado = None
    # Centraliza o nome para relatórios e logs
    NOME_TESTE = "CONSULTA_PEDIDO_VENDA_CONSUMIDOR" 

    try:
        appium_options = get_appium_options(limpar_dados_app=False)
        driver = executar_passo(
            "Conectar ao servidor Appium e iniciar o app",
            lambda: webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=appium_options)
        )
        garantir_login(driver)
        
        # função para ativar a flag de buscar todos os pedidos
        executar_passo("Abrir Menu Lateral", lambda: driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Open navigation drawer").click())
        executar_passo("Clicar em Configurações", lambda: clicar_por_texto(driver, "Configurações"))
        executar_passo("Encontrar opção 'Buscar todos os pedidos'",lambda: scroll_ate_encontrar_texto(driver, "Buscar todos os pedidos")) 
        executar_passo("Garantir flag 'Buscar todos os pedidos' ATIVO", lambda: garantir_switch_ativo_por_texto(driver, "Buscar todos os pedidos"))
        executar_passo("Voltar para Home", lambda: driver.back())
        # venda via conslta pedido
        executar_passo("Clicar no botão 'Pedido Venda'", lambda: clicar_por_texto(driver, "Cons. Pedido"))   
        executar_passo("Clicar no primeiro pedido (Com Espera)",lambda: clicar_no_primeiro_da_lista_por_id(driver, "textView230"))  
        executar_passo("Clicar em 'Finalizar Pedido'", lambda: clicar_por_texto(driver, "Finalizar Pedido")) 
        executar_passo("Fechar Bônus (se aparecer)",lambda: clicar_em_id_se_existir(driver, "btn_mais_tarde", wait_time=3))  
        executar_passo("Botão finalizar", lambda: clicar_por_id(driver,"btnFinalizar"))
        executar_passo("Responder SIM para Imprimir Comprovante (aguardando até 20s)",lambda: clicar_em_id_se_existir(driver, "android:id/button2", wait_time=20))   
        executar_passo("Validar mensagem de sucesso ao fundo", lambda: find_element_by_text(driver, "Venda realizada com sucesso!"))
        executar_passo("Clicar em CONCLUIR VENDA", lambda: scroll_ate_encontrar_texto(driver, "CONCLUIR VENDA").click())
                            
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
    run_test_consulta_pedido_venda()