import time
import traceback
from datetime import datetime
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from config import *
from conftest import driver
from framework import * # Garanta que framework.py está na mesma pasta

def run_test_vendafutura():
    start_time = datetime.now()
    driver = None
    teste_passou = False
    erro_capturado = None
    NOME_TESTE = "VENDA_FUTURA"

    try:
        print(f"=== INICIANDO TESTE: {NOME_TESTE} ===")
        
        # 1. Conexão
        appium_options = get_appium_options(limpar_dados_app=False)
        driver = executar_passo(
            "Conectar ao servidor Appium e iniciar o app",
            lambda: webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=appium_options)
        )
        
        # 2. Login (se precisar)
        garantir_login(driver)
        
        # --- SEU FLUXO DE VENDA FUTURA ---
        
        executar_passo("Clicar no botão 'Venda Futura'", lambda: clicar_por_texto(driver, "Venda Futura"))
        
        executar_passo("Selecione 'Retirada em loja'", lambda: clicar_por_id(driver, "btn_venda_futura_loja"))
        
        executar_passo("Tipo de entrega, Avançar", lambda: clicar_por_texto(driver, "Avançar"))
        
        executar_passo("Selecionar Vendedor", lambda: clicar_por_id(driver, "txt_dialog_seller_name"))
        
        # Ajuste: Busca de Cliente
        executar_passo("Clicar no botão 'Buscar Cliente' (CPF)", lambda: clicar_por_id(driver, "edtCpf"))

        # Inserir "1" no campo CPF
        executar_passo("Digitar CPF '1'", lambda: digitar_texto_por_id(driver, "edtCpf", "1"))

        # Clicar no botão 30
        executar_passo("Clicar no botão confirmar", lambda: clicar_por_id(driver, "button30"))
        
        
        executar_passo("Adicionar produto", lambda: clicar_por_id(driver, "btn_adicionar_produtos"))
        
        executar_passo("Procurar produto '123'", lambda: digitar_texto_por_id(driver, "editText", "123"))

        executar_passo("Clicar no produto", lambda: clicar_por_id(driver, "imageView3"))

        executar_passo("selecionar tamanho", lambda: clicar_por_texto(driver, "36"))
        

        executar_passo("Clicar no botão AVANÇAR", lambda: clicar_por_id_com_espera(driver, "btn_proximo"))
        
        time.sleep(3) # Pausa estratégica
        
        executar_passo("Pagamento personalizado (Título)", lambda: clicar_por_id(driver, "txt_payment_title"))
        
        executar_passo("Selecionar Movimento: A VISTA", 
               lambda: driver.find_elements(AppiumBy.ID, "com.serverinfo.bshoppdv.redel400:id/txt_option_title")[0].click())

        time.sleep(1) # Segurança para a animação

        # 2. Seleciona o segundo (Plano de Venda)
        # AQUI ESTÁ O TRUQUE: Usamos [1] para pegar o segundo elemento da lista
        executar_passo("Selecionar Plano: A Vista", 
               lambda: driver.find_elements(AppiumBy.ID, "com.serverinfo.bshoppdv.redel400:id/txt_option_title")[1].click())
        
        # 3. Agora o botão Avançar deve estar liberado
        executar_passo("Botão Avançar (Pagamento)", 
               lambda: clicar_por_id(driver, "btn_proceed"))
        # --- LÓGICA DO BÔNUS ---
        # --- LÓGICA DO BÔNUS (CORRIGIDA) ---
        print("   [AGUARDANDO] Esperando transição de tela...")
        time.sleep(3) # Dá tempo do popup animar ou da tela mudar
        
        try:
            # Verifica se o BOTÃO 'Mais Tarde' existe (é mais seguro que buscar texto)
            # Usamos find_elements (plural) para não quebrar se não existir
            btn_bonus = driver.find_elements(AppiumBy.ID, "com.serverinfo.bshoppdv.redel400:id/btn_mais_tarde")
            
            if len(btn_bonus) > 0:
                print("   ⚠️ Popup de Bônus detectado! Clicando em 'Mais tarde'...")
                btn_bonus[0].click()
                time.sleep(2) # Espera o popup fechar
            else:
                print("   ℹ️ Nenhum popup apareceu. Seguindo...")
                
        except Exception as e:
            print(f"   [IGNORADO] Erro leve ao checar bônus: {e}")
        # ----------------------------------------
        # -----------------------

        executar_passo("Clicar em ícone Pagamentos", lambda: validar_texto_e_clicar_por_id(driver, "Pagamentos", "imageView19"))
        
        executar_passo("Selecionar forma 'DINHEIRO'", lambda: clicar_por_texto(driver, "DINHEIRO"))
        
        executar_passo("Clicar em PAGAR", lambda: clicar_por_id(driver, "btn_pagar"))
        
        executar_passo("Finalizar venda", lambda: clicar_por_id(driver, "btnFinalizar"))
        
        # Resposta da Impressão (timeout longo 20s)
        executar_passo("Responder NÃO para impressão", 
                       lambda: clicar_em_id_se_existir(driver, "android:id/button2", wait_time=20))
        
        time.sleep(2)
        
        executar_passo("Validar mensagem de sucesso", lambda: find_element_by_text(driver, "Venda realizada com sucesso!"))
        
        executar_passo("Clicar em CONCLUIR VENDA", lambda: clicar_por_id(driver, "btn_confirmar_venda"))

        teste_passou = True
        print(f"\n=== SUCESSO: {NOME_TESTE} PASSOU! ===")

    except Exception as e:
        erro_capturado = traceback.format_exc()
        logger.error(f"ERRO CRÍTICO DURANTE {NOME_TESTE}: {e}")
        print(f"\n❌ FALHA: {e}")
        if driver: save_screenshot(driver, f"CRITICO_{NOME_TESTE}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    run_test_vendafutura()