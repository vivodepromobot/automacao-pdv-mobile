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
    
    # Cores ANSI para o CONSOLE
    VERDE = "\033[1;92m"   
    VERMELHO = "\033[1;91m" 
    RESET = "\033[0m"
    NEGRITO = "\033[1m"

    # ASCII ART para o ARQUIVO (sem cores ANSI)
    ascii_sucesso = """
====================================================================
 ███████╗██╗   ██╗ ██████╗███████╗███████╗███████╗ ██████╗
 ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔═══██╗
 ███████╗██║   ██║██║     █████╗  ███████╗███████╗██║   ██║
 ╚════██║██║   ██║██║     ██╔══╝  ╚════██║╚════██║██║   ██║
 ███████║╚██████╔╝╚██████╗███████╗███████╗███████║╚██████╔╝
 ╚══════╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝ ╚═════╝
"""
    
    ascii_falha = """
====================================================================
 ███████╗ █████╗ ██╗     ██╗  ██╗  █████╗
 ██╔════╝██╔══██╗██║     ██║  ██║ ██╔══██╗
 █████╗  ███████║██║     ███████║ ███████║
 ██╔══╝  ██╔══██║██║     ██╔══██║ ██╔══██║
 ██║     ██║  ██║███████╗██║  ██║ ██║  ██║
 ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═╝  ╚═╝
"""

    # Salva o arquivo físico de texto COM ASCII ART
    with path.open("w", encoding="utf-8") as f:
        f.write("="*51+"\n        RELATÓRIO DE EXECUÇÃO DE TESTE\n"+"="*51+"\n\n")
        f.write(f"Data/Hora: {timestamp()}\nResultado Final: {status}\nDuração Total do Teste: {duracao_teste}\n\n")
        
        # ADICIONA O ASCII ART NO ARQUIVO
        if "SUCESSO" in status:
            f.write(ascii_sucesso)
            f.write(f"\n   >> TESTE CONCLUÍDO COM ÊXITO: {status}\n")
        else:
            f.write(ascii_falha)
            f.write(f"\n   >> ATENÇÃO: O TESTE FALHOU: {status}\n")
        
        f.write(f"   >> Duração: {duracao_teste}\n")
        f.write(f"   >> Relatório: {path.name}\n")
        f.write("="*68+"\n\n")
        
        f.write("--- Log completo ---\n")
        try:
            fh.flush()
            with (REPORTS_DIR / Path(fh.baseFilename).name).open("r", "utf-8") as mainlog: 
                f.write(mainlog.read())
        except Exception: 
            pass
        if extra: 
            f.write(f"\n--- Detalhes do erro ---\n{extra}")

    # --- MENSAGEM FINAL NO CONSOLE (COLORIDA E FORTE) ---
    if "SUCESSO" in status:
        print(f"\n{VERDE}{'='*68}")
        print(" ███████╗██╗   ██╗ ██████╗███████╗███████╗███████╗ ██████╗")
        print(" ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔═══██╗")
        print(" ███████╗██║   ██║██║     █████╗  ███████╗███████╗██║   ██║")
        print(" ╚════██║██║   ██║██║     ██╔══╝  ╚════██║╚════██║██║   ██║")
        print(" ███████║╚██████╔╝╚██████╗███████╗███████╗███████║╚██████╔╝")
        print(" ╚══════╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝ ╚═════╝")
        print(f"\n   >> {NEGRITO}TESTE CONCLUÍDO COM ÊXITO: {status}{RESET}{VERDE}")
        print(f"   >> Duração: {duracao_teste}")
        print(f"   >> Relatório: {path.name}")
        print(f"{'='*68}{RESET}\n")
    else:
        print(f"\n{VERMELHO}{'='*60}")
        print(" ███████╗ █████╗ ██╗     ██╗  ██╗  █████╗")
        print(" ██╔════╝██╔══██╗██║     ██║  ██║ ██╔══██╗")
        print(" █████╗  ███████║██║     ███████║ ███████║")
        print(" ██╔══╝  ██╔══██║██║     ██╔══██║ ██╔══██║")
        print(" ██║     ██║  ██║███████╗██║  ██║ ██║  ██║")
        print(" ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═╝  ╚═╝")
        print(f"\n   >> {NEGRITO}ATENÇÃO: O TESTE FALHOU: {status}{RESET}{VERMELHO}")
        print(f"   >> Duração: {duracao_teste}")
        print(f"   >> Relatório: {path.name}")
        print(f"{'='*60}{RESET}\n")

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

def fechar_teclado_forcado(driver, max_tentativas=3):
    """
    Fecha o teclado virtual usando múltiplas estratégias.
    Compatível com diferentes ROMs Android (Stone, Cielo, etc).

    Args:
        driver: WebDriver do Appium
        max_tentativas: Número máximo de tentativas (default: 3)

    Returns:
        bool: True se fechou com sucesso, False caso contrário
    """
    for tentativa in range(max_tentativas):
        try:
            # Verifica se o teclado está aberto antes de tentar fechar
            try:
                teclado_aberto = driver.execute_script('mobile: isKeyboardShown')
                if not teclado_aberto:
                    logger.info("   [ℹ️] Teclado já está fechado.")
                    return True
            except:
                pass  # Continua tentando fechar mesmo sem conseguir verificar

            logger.info(f"   [ℹ️] Tentativa {tentativa + 1}/{max_tentativas} de fechar teclado...")

            # Método 1: Appium hide_keyboard (mais seguro)
            try:
                driver.hide_keyboard()
                time.sleep(0.5)
                if _teclado_fechou(driver):
                    logger.info("   [OK] Teclado fechado via hide_keyboard.")
                    return True
            except:
                pass

            # Método 2: KEYCODE_BACK via ADB
            try:
                subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'],
                             timeout=3, capture_output=True)
                time.sleep(0.5)
                if _teclado_fechou(driver):
                    logger.info("   [OK] Teclado fechado via KEYCODE_BACK.")
                    return True
            except:
                pass

            # Método 3: KEYCODE_ESCAPE (algumas ROMs respondem melhor)
            try:
                subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ESCAPE'],
                             timeout=3, capture_output=True)
                time.sleep(0.5)
                if _teclado_fechou(driver):
                    logger.info("   [OK] Teclado fechado via KEYCODE_ESCAPE.")
                    return True
            except:
                pass

        except Exception as e:
            logger.warning(f"   [!] Erro na tentativa {tentativa + 1}: {e}")

    logger.warning("   [!] Nao foi possivel fechar o teclado. Continuando...")
    return False


def _teclado_fechou(driver):
    """Verifica se o teclado foi fechado. Função auxiliar interna."""
    try:
        return not driver.execute_script('mobile: isKeyboardShown')
    except:
        return True  # Assume que fechou se não conseguir verificar

def realizar_scroll_ignorando_teclado(driver, direcao='baixo', distancia_percentual=0.6):
    """
    Realiza scroll MESMO COM TECLADO ABERTO.
    Usa coordenadas mais altas para não pegar o teclado.
    
    Args:
        direcao: 'baixo' ou 'cima'
        distancia_percentual: quanto da tela rolar (0.6 = 60%)
    """
    try:
        tamanho_tela = driver.get_window_size()
        largura = tamanho_tela['width']
        altura = tamanho_tela['height']
        
        # Define coordenadas X (centro da tela)
        x = largura // 2
        
        if direcao == 'baixo':
            # Começa mais acima para não pegar o teclado
            # O teclado geralmente ocupa 40-50% da parte inferior
            y_inicial = int(altura * 0.45)  # Começa em 45% da altura
            y_final = int(altura * 0.15)     # Termina em 15% da altura
        else:  # cima
            y_inicial = int(altura * 0.15)
            y_final = int(altura * 0.45)
        
        logger.info(f"   [📜] Scrolling {direcao} - De Y:{y_inicial} até Y:{y_final}")
        
        # Executa o scroll
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(x, y_inicial)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.2)
        actions.w3c_actions.pointer_action.move_to_location(x, y_final)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
        
        time.sleep(0.8)
        logger.info("   [✅] Scroll executado (ignorando teclado).")
        
    except Exception as e:
        logger.warning(f"   [⚠️] Erro ao fazer scroll: {e}")

def scroll_ate_encontrar_texto_ignorando_teclado(driver, texto_a_procurar, max_scrolls=10):
    """
    Rola a tela até encontrar o texto MESMO COM TECLADO ABERTO.
    Versão melhorada que funciona com teclado na tela.
    """
    logger.info(f"   [🔍] Procurando por '{texto_a_procurar}' (pode ter teclado aberto)...")
    
    for tentativa in range(max_scrolls):
        try:
            # Tenta encontrar o elemento (wait curto)
            elemento = find_element_by_text(driver, texto_a_procurar, wait=2)
            logger.info(f"   [✅] Elemento '{texto_a_procurar}' encontrado!")
            return elemento
        except Exception:
            if tentativa < max_scrolls - 1:
                logger.info(f"   [📜] Tentativa {tentativa + 1}: Elemento não encontrado. Rolando...")
                realizar_scroll_ignorando_teclado(driver, direcao='baixo')
            else:
                logger.error(f"   [❌] Elemento '{texto_a_procurar}' não encontrado após {max_scrolls} scrolls.")
    
    raise Exception(f"Não foi possível encontrar '{texto_a_procurar}' após {max_scrolls} tentativas.")

def fechar_teclado_back(driver):
    """
    Fecha o teclado com validação de mudança de tela.
    Detecta se o Back causou navegação indesejada.
    """
    try:
        # Captura elementos da tela atual para comparar depois
        elementos_antes = _capturar_ids_tela(driver)

        # Tenta hide_keyboard primeiro (mais seguro)
        try:
            driver.hide_keyboard()
            time.sleep(0.5)
            if _teclado_fechou(driver):
                logger.info("   [OK] Teclado fechado via hide_keyboard.")
                return True
        except:
            pass

        # Usa KEYCODE_BACK via ADB
        logger.info("   [i] Tentando fechar teclado com Back...")
        subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'],
                      timeout=3, capture_output=True)
        time.sleep(0.8)

        # Valida se ainda está na mesma tela
        elementos_depois = _capturar_ids_tela(driver)
        if elementos_antes and elementos_depois:
            comuns = set(elementos_antes) & set(elementos_depois)
            if len(comuns) < len(elementos_antes) * 0.3:
                logger.warning("   [!] Back causou navegacao. Tela pode ter mudado.")
                return False

        logger.info("   [OK] Teclado fechado via Back.")
        return True

    except Exception as e:
        logger.warning(f"   [!] Erro ao fechar teclado: {e}")
        return False


def _capturar_ids_tela(driver, limite=5):
    """Captura IDs de elementos da tela atual para comparação."""
    try:
        elementos = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id]")[:limite]
        return [el.get_attribute('resource-id') for el in elementos]
    except:
        return []


def voltar_tela(driver, confirmar=False):
    """
    Volta para a tela anterior. Compatível com POS (Stone, Cielo, Pagseguro) e celulares Android.

    Args:
        driver: WebDriver do Appium
        confirmar: Se True, tenta confirmar diálogo de "deseja sair?" após voltar

    Returns:
        bool: True se conseguiu voltar, False caso contrário
    """
    logger.info("   [<-] Voltando tela...")

    # Lista de estratégias para voltar (ordem de prioridade)
    estrategias = [
        # 1. Botão de navegação do app (toolbar/actionbar)
        ("ID", f"{APP_PACKAGE}:id/navigationBarBackground"),
        ("ID", f"{APP_PACKAGE}:id/toolbar_navigation"),
        ("ID", f"{APP_PACKAGE}:id/btn_back"),
        ("ID", f"{APP_PACKAGE}:id/backButton"),
        # 2. Content description comum
        ("ACCESSIBILITY", "Navigate up"),
        ("ACCESSIBILITY", "Voltar"),
        ("ACCESSIBILITY", "Back"),
        # 3. XPath para botões de voltar genéricos
        ("XPATH", "//android.widget.ImageButton[@content-desc='Navigate up']"),
        ("XPATH", "//android.widget.ImageButton[contains(@content-desc,'oltar')]"),
    ]

    # Tenta cada estratégia de UI primeiro
    for tipo, locator in estrategias:
        try:
            if tipo == "ID":
                elemento = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.ID, locator))
                )
            elif tipo == "ACCESSIBILITY":
                elemento = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, locator))
                )
            elif tipo == "XPATH":
                elemento = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, locator))
                )

            elemento.click()
            logger.info(f"   [OK] Voltou via {tipo}: {locator.split('/')[-1]}")

            if confirmar:
                _confirmar_dialogo_sair(driver)
            return True

        except:
            continue

    # Fallback: KEYCODE_BACK via ADB (funciona em qualquer dispositivo)
    try:
        logger.info("   [i] Usando KEYCODE_BACK via ADB...")
        subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'],
                      timeout=3, capture_output=True)
        time.sleep(0.5)
        logger.info("   [OK] Voltou via KEYCODE_BACK.")

        if confirmar:
            _confirmar_dialogo_sair(driver)
        return True

    except Exception as e:
        logger.error(f"   [X] Falha ao voltar tela: {e}")
        return False


def _confirmar_dialogo_sair(driver):
    """Confirma diálogo de 'Deseja sair?' se aparecer."""
    time.sleep(0.5)

    # Tenta confirmar por diferentes botões comuns
    botoes_confirmar = [
        ("android:id/button1", "ID"),           # Botão padrão Android "OK/Sim"
        (f"{APP_PACKAGE}:id/md_buttonDefaultPositive", "ID"),  # Material Dialog
        ("SIM", "TEXT"),
        ("OK", "TEXT"),
        ("Confirmar", "TEXT"),
    ]

    for locator, tipo in botoes_confirmar:
        try:
            if tipo == "ID":
                elemento = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.ID, locator))
                )
            else:  # TEXT
                elemento = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().textContains("{locator}")'))
                )

            elemento.click()
            logger.info(f"   [OK] Dialogo confirmado via: {locator}")
            return True
        except:
            continue

    return False


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

def pressionar_tecla_pesquisar_teclado(driver):
    driver.execute_script('mobile: performEditorAction', {'action': 'search'})

def validar_texto_e_clicar_por_id(driver, texto, id, wait=DEFAULT_WAIT):
    find_element_by_text(driver, texto, wait=wait)
    clicar_por_id(driver, id)

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