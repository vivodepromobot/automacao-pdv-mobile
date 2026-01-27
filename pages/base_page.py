"""
Base Page - Classe base para todos os Page Objects.
Contém métodos comuns de interação com elementos.
"""
import time
import subprocess
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from config import APP_PACKAGE, DEFAULT_WAIT, logger


class BasePage:
    """Classe base com métodos comuns para todas as páginas."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_WAIT)

    # --- Helpers de locators ---
    def _id_completo(self, element_id: str) -> str:
        """Retorna ID completo com package."""
        if ':id/' in element_id:
            return element_id
        return f"{APP_PACKAGE}:id/{element_id}"

    def _capturar_tela_atual(self) -> str:
        """Captura identificador da tela atual para comparação."""
        try:
            return self.driver.page_source[:500]
        except:
            return ""

    def _elemento_realmente_visivel(self, elemento) -> bool:
        """
        Verifica se elemento está REALMENTE visível e interativo.
        Não apenas presente no DOM, mas visível na tela.
        """
        try:
            if not elemento:
                return False

            # Verifica se está displayed
            if not elemento.is_displayed():
                return False

            # Verifica se está enabled
            if not elemento.is_enabled():
                return False

            # Verifica se tem tamanho (não é invisível)
            size = elemento.size
            if size['width'] <= 0 or size['height'] <= 0:
                return False

            # Verifica se está dentro da área visível da tela
            location = elemento.location
            window_size = self.driver.get_window_size()

            if location['y'] < 0 or location['y'] > window_size['height']:
                return False
            if location['x'] < 0 or location['x'] > window_size['width']:
                return False

            return True
        except StaleElementReferenceException:
            return False
        except Exception:
            return False

    # --- Encontrar elementos ---
    def encontrar_por_id(self, element_id: str, tempo_espera: int = None):
        """Encontra elemento por ID."""
        timeout = tempo_espera or DEFAULT_WAIT
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ID, self._id_completo(element_id)))
        )

    def encontrar_clicavel_por_id(self, element_id: str, tempo_espera: int = None):
        """Encontra elemento clicável por ID com validação rigorosa."""
        timeout = tempo_espera or DEFAULT_WAIT
        full_id = self._id_completo(element_id)

        # Primeiro aguarda estar clicável
        elemento = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((AppiumBy.ID, full_id))
        )

        # Validação extra: verifica se realmente está visível
        if not self._elemento_realmente_visivel(elemento):
            raise Exception(f"Elemento '{element_id}' encontrado mas NAO está visivel/clicavel na tela")

        return elemento

    def encontrar_por_texto(self, texto: str, tempo_espera: int = None):
        """Encontra elemento por texto visível."""
        timeout = tempo_espera or DEFAULT_WAIT
        locator = f'new UiSelector().textContains("{texto}")'
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, locator))
        )

    def encontrar_por_xpath(self, xpath: str, tempo_espera: int = None):
        """Encontra elemento por XPath."""
        timeout = tempo_espera or DEFAULT_WAIT
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )

    # --- Ações de clique ---
    def clicar_por_id(self, element_id: str, max_tentativas: int = 3):
        """
        Clica em elemento por ID com validação.
        Tenta múltiplas vezes se necessário.
        """
        for tentativa in range(max_tentativas):
            try:
                tela_antes = self._capturar_tela_atual()

                elemento = self.encontrar_clicavel_por_id(element_id, tempo_espera=5)
                logger.info(f"   [CLICK] Clicando em '{element_id}'...")
                elemento.click()
                time.sleep(0.3)

                # Verifica se a tela mudou (clique teve efeito)
                tela_depois = self._capturar_tela_atual()
                if tela_antes != tela_depois:
                    logger.info(f"   [OK] Clique em '{element_id}' confirmado (tela mudou)")
                    return True

                # Se tela não mudou, pode ser ok (ex: checkbox)
                logger.info(f"   [OK] Clique em '{element_id}' executado")
                return True

            except Exception as e:
                if tentativa < max_tentativas - 1:
                    logger.warning(f"   [RETRY] Tentativa {tentativa + 1} falhou: {e}. Tentando novamente...")
                    time.sleep(1)
                else:
                    logger.error(f"   [ERRO] Falha ao clicar em '{element_id}' apos {max_tentativas} tentativas: {e}")
                    raise Exception(f"Nao foi possivel clicar em '{element_id}': {e}")

    def clicar_no_primeiro_da_lista_por_id(self, element_id: str, tempo_espera: int = None):
        """Clica no primeiro elemento de uma lista com mesmo ID."""
        timeout = tempo_espera or DEFAULT_WAIT
        full_id = self._id_completo(element_id)

        logger.info(f"   [LISTA] Buscando elementos com ID '{element_id}'...")

        lista_de_elementos = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((AppiumBy.ID, full_id))
        )

        if not lista_de_elementos:
            raise Exception(f"Nenhum elemento encontrado com o ID '{element_id}'")

        # Encontra o primeiro elemento realmente visível
        for i, elemento in enumerate(lista_de_elementos):
            if self._elemento_realmente_visivel(elemento):
                logger.info(f"   [OK] Encontrado elemento visivel na posicao {i}. Clicando...")
                elemento.click()
                return

        raise Exception(f"Nenhum elemento com ID '{element_id}' esta visivel na tela")

    def clicar_por_texto(self, texto: str, tempo_espera: int = None):
        """Clica em elemento por texto."""
        logger.info(f"   [CLICK] Buscando texto '{texto}'...")
        elemento = self.encontrar_por_texto(texto, tempo_espera)

        if not self._elemento_realmente_visivel(elemento):
            raise Exception(f"Texto '{texto}' encontrado mas NAO esta visivel na tela")

        time.sleep(0.3)
        elemento.click()
        logger.info(f"   [OK] Clicado em '{texto}'")

    def clicar_se_existir(self, element_id: str, tempo_espera: int = 3) -> bool:
        """Clica se elemento existir e estiver visível, senão ignora."""
        try:
            elemento = WebDriverWait(self.driver, tempo_espera).until(
                EC.element_to_be_clickable((AppiumBy.ID, self._id_completo(element_id)))
            )

            if self._elemento_realmente_visivel(elemento):
                logger.info(f"   [CLICK] Elemento '{element_id}' encontrado. Clicando...")
                elemento.click()
                return True
            else:
                logger.info(f"   [SKIP] Elemento '{element_id}' existe mas nao esta visivel")
                return False
        except:
            logger.info(f"   [SKIP] Elemento '{element_id}' nao encontrado")
            return False

    def clicar_texto_se_existir(self, texto: str, tempo_espera: int = 3) -> bool:
        """Clica em texto se existir e estiver visível, senão ignora."""
        try:
            elemento = self.encontrar_por_texto(texto, tempo_espera)

            if self._elemento_realmente_visivel(elemento):
                logger.info(f"   [CLICK] Texto '{texto}' encontrado. Clicando...")
                elemento.click()
                return True
            else:
                logger.info(f"   [SKIP] Texto '{texto}' existe mas nao esta visivel")
                return False
        except:
            logger.info(f"   [SKIP] Texto '{texto}' nao encontrado")
            return False

    # --- Ações de digitação ---
    def digitar_por_id(self, element_id: str, texto: str):
        """Digita texto em campo por ID."""
        logger.info(f"   [DIGITAR] Campo '{element_id}' <- '{texto}'")
        campo = self.encontrar_clicavel_por_id(element_id)
        campo.clear()
        campo.send_keys(texto)

    def digitar_por_xpath(self, xpath: str, texto: str):
        """Digita texto em campo por XPath."""
        logger.info(f"   [DIGITAR] XPath <- '{texto}'")
        campo = self.encontrar_por_xpath(xpath)
        campo.clear()
        campo.send_keys(texto)

    # --- Ações de teclado ---
    def fechar_teclado(self, max_tentativas: int = 3) -> bool:
        """
        Fecha o teclado virtual usando múltiplas estratégias.
        Compatível com diferentes ROMs Android (Stone, Cielo, etc).
        """
        for tentativa in range(max_tentativas):
            try:
                if not self._teclado_visivel():
                    return True

                logger.info(f"   [TECLADO] Tentativa {tentativa + 1}/{max_tentativas} de fechar...")

                # Método 1: Appium hide_keyboard
                try:
                    self.driver.hide_keyboard()
                    time.sleep(0.5)
                    if not self._teclado_visivel():
                        logger.info("   [OK] Teclado fechado via hide_keyboard.")
                        return True
                except:
                    pass

                # Método 2: KEYCODE_BACK via ADB
                try:
                    subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'],
                                  timeout=3, capture_output=True)
                    time.sleep(0.5)
                    if not self._teclado_visivel():
                        logger.info("   [OK] Teclado fechado via KEYCODE_BACK.")
                        return True
                except:
                    pass

                # Método 3: KEYCODE_ESCAPE (algumas ROMs respondem melhor)
                try:
                    subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ESCAPE'],
                                  timeout=3, capture_output=True)
                    time.sleep(0.5)
                    if not self._teclado_visivel():
                        logger.info("   [OK] Teclado fechado via KEYCODE_ESCAPE.")
                        return True
                except:
                    pass

            except:
                pass

        return False

    def _teclado_visivel(self) -> bool:
        """Verifica se teclado está visível."""
        try:
            return self.driver.execute_script('mobile: isKeyboardShown')
        except:
            return False

    def pressionar_pesquisar(self):
        """Pressiona tecla de pesquisa do teclado."""
        self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})

    # --- Ações de scroll ---
    def realizar_scroll_para_baixo(self):
        """Realiza scroll para baixo."""
        size = self.driver.get_window_size()
        x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.2)

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(
            self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
        )
        actions.w3c_actions.pointer_action.move_to_location(x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.2)
        actions.w3c_actions.pointer_action.move_to_location(x, end_y)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def realizar_scroll_ignorando_teclado(self, direcao: str = 'baixo'):
        """
        Realiza scroll MESMO COM TECLADO ABERTO.
        Usa coordenadas na parte superior da tela para evitar o teclado.
        Universal - funciona em qualquer dispositivo.
        """
        try:
            size = self.driver.get_window_size()
            x = size['width'] // 2

            if direcao == 'baixo':
                # Área superior da tela (acima do teclado)
                # Usa 35% a 10% para garantir que funciona com teclado grande
                y_inicial = int(size['height'] * 0.35)
                y_final = int(size['height'] * 0.10)
            else:
                y_inicial = int(size['height'] * 0.10)
                y_final = int(size['height'] * 0.35)

            logger.info(f"   [SCROLL] {direcao} - De Y:{y_inicial} ate Y:{y_final}")

            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(
                self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
            )
            actions.w3c_actions.pointer_action.move_to_location(x, y_inicial)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.3)
            actions.w3c_actions.pointer_action.move_to_location(x, y_final)
            actions.w3c_actions.pointer_action.release()
            actions.perform()

            time.sleep(0.5)

        except Exception as e:
            logger.warning(f"   [!] Erro ao fazer scroll: {e}")

    def scroll_nativo_ate_id(self, element_id: str):
        """
        Usa UiScrollable nativo do Android para rolar até elemento.
        Mais confiável em qualquer dispositivo.
        """
        try:
            full_id = self._id_completo(element_id)
            locator = f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().resourceId("{full_id}"))'
            logger.info(f"   [SCROLL NATIVO] Buscando ID '{element_id}'...")
            elemento = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
            logger.info(f"   [OK] ID '{element_id}' encontrado via scroll nativo!")
            return elemento
        except Exception as e:
            logger.warning(f"   [!] Scroll nativo falhou: {e}")
            return None

    def scroll_nativo_ate_texto(self, texto: str):
        """
        Usa UiScrollable nativo do Android para rolar até texto.
        Mais confiável em qualquer dispositivo.
        """
        try:
            locator = f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("{texto}"))'
            logger.info(f"   [SCROLL NATIVO] Buscando texto '{texto}'...")
            elemento = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
            logger.info(f"   [OK] Texto '{texto}' encontrado via scroll nativo!")
            return elemento
        except Exception as e:
            logger.warning(f"   [!] Scroll nativo falhou: {e}")
            return None

    def rolar_ate_texto(self, texto: str, max_scrolls: int = 5):
        """
        Rola até encontrar texto.
        Usa scroll nativo do Android primeiro (mais confiável).
        """
        logger.info(f"   [BUSCA] Procurando texto '{texto}'...")

        # Primeiro tenta scroll nativo do Android
        elemento = self.scroll_nativo_ate_texto(texto)
        if elemento and self._elemento_realmente_visivel(elemento):
            return elemento

        # Fallback: scroll manual
        logger.info(f"   [FALLBACK] Tentando scroll manual...")
        for tentativa in range(max_scrolls):
            try:
                elemento = self.encontrar_por_texto(texto, tempo_espera=2)
                if self._elemento_realmente_visivel(elemento):
                    logger.info(f"   [OK] Texto '{texto}' encontrado e visivel!")
                    return elemento
            except:
                pass

            if tentativa < max_scrolls - 1:
                logger.info(f"   [SCROLL] Tentativa {tentativa + 1}: Texto nao visivel. Rolando...")
                self.realizar_scroll_para_baixo()
                time.sleep(0.5)

        raise Exception(f"Texto '{texto}' nao encontrado apos {max_scrolls} scrolls")

    def rolar_ate_texto_ignorando_teclado(self, texto: str, max_scrolls: int = 10):
        """
        Rola ate encontrar texto MESMO COM TECLADO ABERTO.
        Versao melhorada que funciona com teclado na tela.
        """
        logger.info(f"   [BUSCA] Procurando '{texto}' (pode ter teclado aberto)...")

        for tentativa in range(max_scrolls):
            try:
                elemento = self.encontrar_por_texto(texto, tempo_espera=2)
                if self._elemento_realmente_visivel(elemento):
                    logger.info(f"   [OK] Elemento '{texto}' encontrado e visivel!")
                    return elemento
            except:
                pass

            if tentativa < max_scrolls - 1:
                logger.info(f"   [SCROLL] Tentativa {tentativa + 1}: Elemento nao encontrado. Rolando...")
                self.realizar_scroll_ignorando_teclado(direcao='baixo')

        raise Exception(f"Texto '{texto}' nao encontrado apos {max_scrolls} scrolls")

    def rolar_ate_id(self, element_id: str, max_scrolls: int = 10):
        """
        Rola até encontrar elemento por ID.
        Funciona MESMO COM TECLADO ABERTO - não tenta fechar.
        Usa scroll nativo do Android primeiro (mais confiável).
        """
        logger.info(f"   [BUSCA] Procurando ID '{element_id}'...")

        # Primeiro tenta scroll nativo do Android (mais confiável)
        elemento = self.scroll_nativo_ate_id(element_id)
        if elemento and self._elemento_realmente_visivel(elemento):
            return elemento

        # Fallback: scroll manual
        logger.info(f"   [FALLBACK] Tentando scroll manual...")
        for tentativa in range(max_scrolls):
            try:
                elemento = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((AppiumBy.ID, self._id_completo(element_id)))
                )
                if self._elemento_realmente_visivel(elemento):
                    logger.info(f"   [OK] ID '{element_id}' encontrado e visivel!")
                    return elemento
            except:
                pass

            if tentativa < max_scrolls - 1:
                logger.info(f"   [SCROLL] Tentativa {tentativa + 1}: Rolando...")
                self.realizar_scroll_ignorando_teclado(direcao='baixo')

        raise Exception(f"ID '{element_id}' nao encontrado apos {max_scrolls} scrolls")

    # --- Navegação ---
    def voltar_tela(self, confirmar: bool = False) -> bool:
        """Volta para tela anterior."""
        # Tenta botões de navegação comuns
        botoes_voltar = [
            f"{APP_PACKAGE}:id/navigationBarBackground",
            f"{APP_PACKAGE}:id/toolbar_navigation",
            f"{APP_PACKAGE}:id/btn_back",
        ]

        for btn_id in botoes_voltar:
            try:
                elemento = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.ID, btn_id))
                )
                elemento.click()
                if confirmar:
                    self._confirmar_dialogo_sair()
                return True
            except:
                continue

        # Fallback: KEYCODE_BACK
        subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'],
                      timeout=3, capture_output=True)
        time.sleep(0.5)
        if confirmar:
            self._confirmar_dialogo_sair()
        return True

    def _confirmar_dialogo_sair(self):
        """Confirma diálogo de sair se aparecer."""
        time.sleep(0.5)
        botoes_confirmar = [
            ("android:id/button1", AppiumBy.ID),
            (f"{APP_PACKAGE}:id/md_buttonDefaultPositive", AppiumBy.ID),
        ]

        for locator, by in botoes_confirmar:
            try:
                elemento = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((by, locator))
                )
                elemento.click()
                return
            except:
                continue

    # --- Validações ---
    def texto_exibido(self, texto: str, tempo_espera: int = 5) -> bool:
        """Verifica se texto está visível na tela."""
        try:
            elemento = self.encontrar_por_texto(texto, tempo_espera)
            return self._elemento_realmente_visivel(elemento)
        except:
            return False

    def aguardar_texto(self, texto: str, tempo_espera: int = None):
        """Aguarda texto aparecer na tela."""
        return self.encontrar_por_texto(texto, tempo_espera)

    def elemento_existe(self, element_id: str, tempo_espera: int = 3) -> bool:
        """Verifica se elemento existe e está visível."""
        try:
            elemento = self.encontrar_por_id(element_id, tempo_espera)
            return self._elemento_realmente_visivel(elemento)
        except:
            return False
