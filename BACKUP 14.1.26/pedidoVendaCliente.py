import traceback
from datetime import datetime
from appium import webdriver
from config import *
from framework import *

def run_test_pedido_venda_cliente():
    start_time = datetime.now()
    driver = None
    teste_passou = False
    erro_capturado = None
    # Centraliza o nome para relatórios e logs
    NOME_TESTE = "PEDIDO_VENDA_CLIENTE" 

    try:
        appium_options = get_appium_options(limpar_dados_app=False)
        driver = executar_passo(
            "Conectar ao servidor Appium e iniciar o app",
            lambda: webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=appium_options)
        )
        garantir_login(driver)
        
        # --- INÍCIO DO FLUXO DE PEDIDO ---
        executar_passo("Clicar no botão 'Pedido Venda'", lambda: clicar_por_texto(driver, "Pedido Venda"))
        executar_passo("Selecionar Vendedor", lambda: clicar_por_id(driver, "txt_dialog_seller_name"))
        executar_passo("Clicar no botão 'Buscar Cliente'", lambda: clicar_por_id(driver, "btn_select_customer"))
        
        # Volta a usar a função que funcionava (assumindo que ela existe no framework ou foi definida antes)
        # Se ela não existir no framework, avise que eu coloco o bloco explicito aqui de novo
        selecionar_cliente(driver, "1")
        
        executar_passo("Adicionar produto", lambda: clicar_por_id(driver, "btn_adicionar_produtos"))
        executar_passo("Procurar produto '123'", lambda: digitar_texto_por_id(driver, "editText", "123"))
        executar_passo("Clicar no produto", lambda: clicar_por_id(driver, "imageView3"))
        
        # Uso da função robusta para evitar clique fantasma no AVANÇAR
        executar_passo("Clicar no botão AVANÇAR", lambda: clicar_por_id_com_espera(driver, "btn_proximo"))
        time.sleep(3) # Pausa estratégica para estabilizar a transição de tela
        executar_passo("Atalho de pagamento", lambda: clicar_por_texto(driver, "DINHEIRO"))
        executar_passo("Clicar em Avançar com a forma selecionada", lambda: clicar_por_id(driver, "btn_proceed"))
    
        executar_passo("Fechar Bônus (se aparecer)", 
               lambda: clicar_em_id_se_existir(driver, "btn_mais_tarde"))
        
        executar_passo("Botão finalizar", lambda: validar_texto_e_clicar_por_id(driver, "Finalizar", "btnFinalizar"))
        executar_passo("Validar mensagem de sucesso ao fundo", lambda: find_element_by_text(driver, "Pedido gerado com sucesso!"))
        executar_passo("Clicar no botão CONCLUIR VENDA", lambda: clicar_por_id(driver, "button17"))
       
       
       
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
    run_test_pedido_venda_cliente()