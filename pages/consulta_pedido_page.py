"""
Consulta Pedido Page - Page Object para tela de consulta de pedidos.
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config import logger


class ConsultaPedidoPage(BasePage):
    """Page Object para tela de consulta de pedidos."""

    # --- Locators ---
    # Menu lateral
    ACCESSIBILITY_MENU = "Open navigation drawer"

    # Lista de pedidos
    TXT_ITEM_PEDIDO = "textView230"

    # Botões
    BTN_FINALIZAR = "btnFinalizar"
    BTN_MAIS_TARDE = "btn_mais_tarde"
    BTN_IMPRIMIR_NAO = "android:id/button2"
    BTN_CONFIRMAR_VENDA = "btn_confirmar_venda"

    # --- Ações de Configuração ---
    def abrir_menu_lateral(self):
        """Abre o menu lateral (navigation drawer)."""
        logger.info("-> Abrindo menu lateral...")
        try:
            menu = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, self.ACCESSIBILITY_MENU)
            menu.click()
            time.sleep(1)
            logger.info("   [OK] Menu lateral aberto")
        except Exception as e:
            logger.warning(f"   [!] Erro ao abrir menu: {e}")
            raise

    def acessar_configuracoes(self):
        """Acessa tela de configurações."""
        logger.info("-> Acessando Configurações...")
        self.clicar_por_texto("Configurações")
        time.sleep(1)

    def garantir_flag_buscar_todos_pedidos(self):
        """Garante que a flag 'Buscar todos os pedidos' está ativa."""
        logger.info("-> Verificando flag 'Buscar todos os pedidos'...")

        # Rola até encontrar o texto
        self.rolar_ate_texto("Buscar todos os pedidos")

        # Encontra o switch associado
        try:
            # Busca o texto e depois o switch próximo
            elementos = self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("Buscar todos os pedidos")'
            )

            if elementos:
                # Pega o parent e busca o switch
                parent = elementos[0]
                # Tenta encontrar switch no mesmo container
                switches = self.driver.find_elements(
                    AppiumBy.CLASS_NAME, "android.widget.Switch"
                )

                for switch in switches:
                    try:
                        # Verifica se o switch está na mesma linha (próximo ao texto)
                        if switch.is_displayed():
                            checked = switch.get_attribute("checked")
                            if checked == "false":
                                logger.info("   [INFO] Flag desativada, ativando...")
                                switch.click()
                                time.sleep(0.5)
                            else:
                                logger.info("   [OK] Flag já está ativa")
                            return True
                    except:
                        continue

            # Fallback: clica no texto para alternar
            logger.info("   [FALLBACK] Clicando no texto para alternar...")
            self.clicar_por_texto("Buscar todos os pedidos")
            time.sleep(0.5)
            return True

        except Exception as e:
            logger.warning(f"   [!] Erro ao configurar flag: {e}")
            return False

    def voltar_para_home(self):
        """Volta para a tela inicial."""
        logger.info("-> Voltando para Home...")
        self.driver.back()
        time.sleep(1)

    def configurar_buscar_todos_pedidos(self):
        """Fluxo completo para configurar flag de buscar todos os pedidos."""
        logger.info("--- [CONFIG] Configurando busca de pedidos ---")
        self.abrir_menu_lateral()
        self.acessar_configuracoes()
        self.garantir_flag_buscar_todos_pedidos()
        self.voltar_para_home()
        logger.info("--- [CONFIG] Configuração concluída ---")

    # --- Ações de Consulta ---
    def acessar_consulta_pedido(self):
        """Acessa a tela de consulta de pedidos."""
        logger.info("-> Acessando 'Cons. Pedido'...")
        self.rolar_ate_texto("Cons. Pedido")
        self.clicar_por_texto("Cons. Pedido")
        time.sleep(2)

    def selecionar_primeiro_pedido(self):
        """Seleciona o primeiro pedido da lista."""
        logger.info("-> Selecionando primeiro pedido da lista...")
        time.sleep(2)  # Aguarda lista carregar

        try:
            # Tenta clicar no primeiro item da lista
            elementos = self.driver.find_elements(
                AppiumBy.ID, f"{self.app_package}:id/{self.TXT_ITEM_PEDIDO}"
            )

            if elementos:
                elementos[0].click()
                logger.info("   [OK] Primeiro pedido selecionado")
                return True
            else:
                logger.warning("   [!] Nenhum pedido encontrado na lista")
                return False

        except Exception as e:
            logger.warning(f"   [!] Erro ao selecionar pedido: {e}")
            return False

    def clicar_finalizar_pedido(self):
        """Clica em 'Finalizar Pedido'."""
        logger.info("-> Clicando em 'Finalizar Pedido'...")
        self.rolar_ate_texto("Finalizar Pedido")
        self.clicar_por_texto("Finalizar Pedido")
        time.sleep(2)

    def tratar_popup_bonus(self):
        """Trata popup de bônus se aparecer."""
        logger.info("-> Verificando popup de bônus...")
        if self.clicar_se_existir(self.BTN_MAIS_TARDE, tempo_espera=3):
            logger.info("   [OK] Popup de bônus fechado")
            time.sleep(1)
        else:
            logger.info("   [INFO] Nenhum popup de bônus")

    def finalizar_venda(self):
        """Finaliza a venda do pedido."""
        logger.info("-> Finalizando venda...")
        self.tratar_popup_bonus()
        self.rolar_ate_id(self.BTN_FINALIZAR)
        self.clicar_por_id(self.BTN_FINALIZAR)

    def responder_impressao(self, imprimir: bool = False):
        """Responde ao diálogo de impressão."""
        logger.info(f"-> Respondendo impressão: {'SIM' if imprimir else 'NÃO'}")
        self.clicar_se_existir(self.BTN_IMPRIMIR_NAO, tempo_espera=20)
        time.sleep(2)

    def concluir_venda(self):
        """Clica em CONCLUIR VENDA."""
        logger.info("-> Concluindo venda...")
        self.rolar_ate_texto("CONCLUIR VENDA")
        self.clicar_por_texto("CONCLUIR VENDA")

    def executar_consulta_e_finalizar_pedido(self):
        """Executa fluxo completo de consulta e finalização de pedido."""
        logger.info("--- [FLUXO] Iniciando consulta e finalização de pedido ---")

        self.acessar_consulta_pedido()
        self.selecionar_primeiro_pedido()
        self.clicar_finalizar_pedido()
        self.finalizar_venda()
        self.responder_impressao(imprimir=False)

        logger.info("--- [FLUXO] Consulta e finalização executadas ---")

    # --- Validações ---
    def venda_sucesso_exibida(self, timeout: int = 10) -> bool:
        """Verifica se mensagem de sucesso apareceu."""
        return self.texto_exibido("Venda realizada com sucesso!", timeout)

    def validar_sucesso_e_concluir(self):
        """Valida sucesso e conclui venda."""
        self.aguardar_texto("Venda realizada com sucesso!")
        self.concluir_venda()
