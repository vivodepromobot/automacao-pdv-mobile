import os
import sys
import time
import traceback
import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
import subprocess

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder

from config import *

# --- ESTRUTURA DE LOGS E UTILITÁRIOS ---
for d in (LOGS_DIR, SCREENSHOTS_DIR, REPORTS_DIR): d.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger("appium_test")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    fh = logging.FileHandler(REPORTS_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", "w", "utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_screenshot(driver, name):
    filename = SCREENSHOTS_DIR / f"{name}_{timestamp()}.png"
    try:
        driver.get_screenshot_as_file(str(filename))
        logger.info(f"[📸 EVIDÊNCIA] Screenshot salvo em: {filename}")
    except Exception as e: 
        logger.warning(f"[⚠️] Falha ao tirar screenshot: {e}")
    
def write_report(status, start_time, end_time, extra=None):
    path = REPORTS_DIR / f"log_teste_{status}_{timestamp()}.txt"
    duracao_teste = "N/A"
    if start_time and end_time: 
        duracao_teste = f"{(end_time - start_time).total_seconds():.2f} segundos"
    with path.open("w", encoding="utf-8") as f:
        f.write("="*51+"\n        RELATÓRIO DE EXECUÇÃO DE TESTE\n"+"="*51+"\n\n")
        f.write(f"Data/Hora: {timestamp()}\nResultado Final: {status}\nDuração Total do Teste: {duracao_teste}\n\n--- Log completo ---\n")
        try:
            fh.flush()
            with (REPORTS_DIR / Path(fh.baseFilename).name).open("r", "utf-8") as mainlog: 
                f.write(mainlog.read())
        except Exception: 
            pass
        if extra: 
            f.write(f"\n--- Detalhes do erro ---\n{extra}")
    logger.info(f"[📄 LOG] Relatório de teste salvo em: {path}")
    logger.info(f"[⏱️ TEMPO] Duração do teste: {duracao_teste}")

def executar_passo(desc, func):
    logger.info(f"-> PASSO: {desc} ...")
    try:
        res = func()
        logger.info("   [✅ SUCESSO]")
        return res
    except Exception: 
        logger.exception("   [❌ FALHA] Exceção no passo.")
        raise

def realizar_scroll_para_baixo(driver):
    tamanho_tela = driver.get_window_size()
    largura, altura = tamanho_tela['width'], tamanho_tela['height']
    start_x, start_y, end_y = largura // 2, int(altura * 0.8), int(altura * 0.2)
    actions = ActionChains(driver)
    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
    actions.w3c_actions.pointer_action.move_to_location(start_x, start_y).pointer_down().pause(0.2).move_to_location(start_x, end_y).release()
    actions.perform()

def find_clickable_by_id(driver, id, wait=DEFAULT_WAIT): 
    full_id = f"{APP_PACKAGE}:id/{id}"
    return WebDriverWait(driver, wait).until(EC.element_to_be_clickable((AppiumBy.ID, full_id)))

def find_element_by_text(driver, text, wait=DEFAULT_WAIT): 
    locator = f'new UiSelector().textContains("{text}")'
    return WebDriverWait(driver, wait).until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, locator)))

def find_element_by_xpath(driver, xpath, wait=DEFAULT_WAIT): 
    return WebDriverWait(driver, wait).until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))

def scroll_ate_encontrar_texto(driver, texto_a_procurar, max_scrolls=5):
    for _ in range(max_scrolls):
        try:
            return find_element_by_text(driver, texto_a_procurar, wait=2)
        except Exception:
            realizar_scroll_para_baixo(driver)
            time.sleep(1)
    raise Exception(f"Não foi possível encontrar o elemento com o texto '{texto_a_procurar}' após {max_scrolls} tentativas.")

def fechar_teclado_back(driver):
    try:
        subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'], check=True, timeout=3, capture_output=True)
        time.sleep(0.8)
    except Exception:
        driver.back()

def clicar_por_id(driver, id): 
    find_clickable_by_id(driver, id).click()

def clicar_por_texto(driver, text, wait=DEFAULT_WAIT): 
    elemento = find_element_by_text(driver, text, wait=wait)
    time.sleep(1)
    
    elemento.click()

def digitar_texto_por_id(driver, id, texto):
    campo = find_clickable_by_id(driver, id)
    campo.clear()
    campo.send_keys(texto)

def digitar_texto_por_xpath(driver, xpath, texto):
    campo = find_element_by_xpath(driver, xpath)
    campo.clear()
    campo.send_keys(texto)

def clicar_no_primeiro_da_lista_por_id(driver, element_id: str):
    full_id = f"{APP_PACKAGE}:id/{element_id}"
    lista_de_elementos = WebDriverWait(driver, DEFAULT_WAIT).until(EC.presence_of_all_elements_located((AppiumBy.ID, full_id)))
    if not lista_de_elementos: 
        raise Exception(f"Nenhum elemento encontrado com o ID '{element_id}'")
    lista_de_elementos[0].click()

def clicar_em_texto_se_existir(driver, texto_a_clicar: str, wait_time: int = 5) -> bool:
    try:
        elemento = find_element_by_text(driver, texto_a_clicar, wait=wait_time)
        elemento.click()
        return True
    except Exception:
        return False
    
def clicar_ate_mudar_tela(driver, id_clicar, texto_esperado_nova_tela, tentativas=3):
    """Clica no elemento e verifica se a tela mudou procurando um texto específico."""
    for i in range(tentativas):
        try:
            clicar_por_id(driver, id_clicar)
            # Tenta verificar se o próximo elemento já apareceu (wait curto)
            find_element_by_text(driver, texto_esperado_nova_tela, wait=5)
            logger.info(f"   [✅] Tela mudou com sucesso na tentativa {i+1}")
            return True
        except Exception:
            logger.warning(f"   [⚠️] Tentativa {i+1} de clique falhou em mudar a tela. Reentando...")
            time.sleep(1)
    raise Exception(f"Falha ao mudar de tela após clicar em {id_clicar}")   

def clicar_em_id_se_existir(driver, id_elemento: str, wait_time: int = 3) -> bool:
    """Tenta clicar em um ID. Se não encontrar em 'wait_time' segundos, ignora sem dar erro."""
    try:
        # Usa uma espera curta para não travar o teste
        elemento = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((AppiumBy.ID, id_elemento))
        )
        elemento.click()
        logger.info(f"   [ℹ️] Elemento '{id_elemento}' encontrado e clicado.")
        return True
    except Exception:
        # Se o botão não aparecer, apenas avisa no log e retorna False
        logger.info(f"   [ℹ️] Elemento '{id_elemento}' não apareceu. Pulando...")
        return False 

def clicar_por_id_com_espera(driver, id_elemento, wait=DEFAULT_WAIT, tentativas=3):
    
    for i in range(tentativas):
        try:
            # Localiza o elemento garantindo que ele está pronto para interação
            elemento = find_clickable_by_id(driver, id_elemento, wait=wait)
            
            # Pausa de 1.5s: Dá tempo para o app terminar cálculos de carrinho/estoque
            time.sleep(1.5)
            
            elemento.click()
            logger.info(f"   [✅] Clique no ID '{id_elemento}' realizado na tentativa {i+1}.")
            return True
        except Exception as e:
            if i == tentativas - 1:
                logger.error(f"   [❌] Falha definitiva ao clicar no ID '{id_elemento}' após {tentativas} tentativas.")
                raise e
            logger.warning(f"   [⚠️] Tentativa {i+1} de clique falhou. Reentando...")
            time.sleep(1) 

def garantir_switch_ativo_por_texto(driver, texto_label):
    """
    Rola até encontrar o texto e garante que o switch ao lado dele esteja ATIVO (True).
    """
    # 1. Rola a tela até achar o texto
    scroll_ate_encontrar_texto(driver, texto_label)
    
    # 2. Busca o Switch "irmão" (Correção: Subindo 2 níveis)
    # Explicação: Texto -> Pai (Caixa de Texto) -> Avô (Linha inteira) -> Busca Switch
    xpath_switch = f"//*[@text='{texto_label}']/../..//*[@resource-id='android:id/switch_widget']"
    
    # Tenta encontrar o elemento
    try:
        switch = find_element_by_xpath(driver, xpath_switch)
    except:
        # Fallback: Se 2 níveis não funcionar, tenta 1 nível (para telas diferentes)
        logger.info("   [DEBUG] XPath de 2 níveis falhou, tentando 1 nível...")
        xpath_switch = f"//*[@text='{texto_label}']/..//*[@resource-id='android:id/switch_widget']"
        switch = find_element_by_xpath(driver, xpath_switch)

    # 3. Verifica o estado e clica se necessário
    if switch.get_attribute("checked") == "false":
        logger.info(f"   [ACTION] Switch '{texto_label}' estava desligado. Ativando...")
        switch.click()
        time.sleep(1) # Espera animação
    else:
        logger.info(f"   [OK] Switch '{texto_label}' já estava ativo.")   

def pressionar_tecla_pesquisar_teclado(driver):
    driver.execute_script('mobile: performEditorAction', {'action': 'search'})

def validar_texto_e_clicar_por_id(driver, texto, id, wait=DEFAULT_WAIT):
    find_element_by_text(driver, texto, wait=wait)
    clicar_por_id(driver, id)

import time # Você precisará importar a biblioteca 'time' no início do seu arquivo

def garantir_login(driver):
    logger.info("--- [PRÉ-CONDIÇÃO] Verificando se o usuário já está logado ---")

    tempo_maximo_total = 5
    tempo_inicial = time.time()
    usuario_logado = False

    # Este loop vai rodar por no máximo 5 segundos
    while time.time() - tempo_inicial < tempo_maximo_total:
        try:
            # 1. Tenta achar "Iniciar Venda" sem esperar (wait=0).
            #    Isso apenas verifica se o elemento JÁ ESTÁ na tela.
            find_element_by_text(driver, "Iniciar Venda", wait=0)
            logger.info("   [✅ SUCESSO] Usuário já está logado (encontrado 'Iniciar Venda').")
            usuario_logado = True
            break  # Encontrou, então quebra o loop e sai.

        except Exception:
            # 2. Se não achou o primeiro, imediatamente tenta achar "Venda", também sem esperar.
            try:
                find_element_by_text(driver, "Venda", wait=0)
                logger.info("   [✅ SUCESSO] Usuário já está logado (encontrado 'Venda').")
                usuario_logado = True
                break  # Encontrou, então quebra o loop e sai.
            except Exception:
                # 3. Se não encontrou nenhum dos dois, faz uma pequena pausa
                #    e o loop tentará novamente na próxima iteração.
                time.sleep(0.5)  # Pausa de meio segundo para não sobrecarregar o processador

    # 4. Depois que o loop terminar (seja por encontrar o elemento ou por estourar o tempo)
    #    verificamos se o usuário foi de fato logado.
    if not usuario_logado:
        logger.info(f"   [⚠️ AVISO] Nenhum elemento encontrado após {tempo_maximo_total} segundos. Executando o fluxo de login...")
        realizar_login_completo(driver)

def realizar_login_completo(driver):
    logger.info("--- [FLUXO] Executando o processo de login completo ---")
    executar_passo("Clicar no botão 'PRÓXIMO' da tela 1", lambda: clicar_em_texto_se_existir(driver, "btn_next_intro"))
    executar_passo("Clicar no botão 'PRÓXIMO' da tela 2", lambda: clicar_em_texto_se_existir(driver, "btn_done_intro"))
    executar_passo("Clicar em 'CONFIGURAR CONEXAO'", lambda: clicar_por_id(driver, "btn_config_connection"))
    executar_passo("Digitar o IP", lambda: digitar_texto_por_id(driver, "edt_config_conn_ip_server", "10.2.3.106"))
    executar_passo("Digitar a Porta", lambda: digitar_texto_por_id(driver, "edt_config_conn_gateway_server", "55101"))
    executar_passo("Clicar no botão 'SALVAR' da conexão", lambda: clicar_por_id(driver, "md_buttonDefaultPositive"))
    executar_passo("Digitar a Empresa", lambda: digitar_texto_por_id(driver, "edt_company_login", "382"))
    executar_passo("Digitar o Usuário", lambda: digitar_texto_por_id(driver, "edt_user_login", "SERVER"))
    executar_passo("Digitar a Senha", lambda: digitar_texto_por_id(driver, "edt_password_login", "gabinete"))
    executar_passo("Clicar no botão 'ENTRAR'", lambda: clicar_por_id(driver, "btn_enter_login"))
    logger.info("--- [FLUXO] Processo de login concluído ---")

    


def selecionar_cliente(driver, identificador_cliente: str):
    logger.info(f"--- [FLUXO] Iniciando a seleção do cliente: {identificador_cliente} ---")
    
    executar_passo(f"Digitar '{identificador_cliente}' no campo de busca",
                   lambda: digitar_texto_por_id(driver, "search_src_text", identificador_cliente))

    executar_passo("Acionar a pesquisa pelo teclado",
                   lambda: pressionar_tecla_pesquisar_teclado(driver))

    executar_passo("Confirmar a seleção do cliente",
                   lambda: clicar_por_id(driver, "button3"))

    logger.info("--- [FLUXO] Seleção de cliente concluída ---")