"""
Home Page - Page Object para tela inicial (pós-login).
"""
import time
from pages.base_page import BasePage
from config import logger


class HomePage(BasePage):
    """Page Object para tela inicial do app."""

    # --- Locators ---
    TXT_INICIAR_VENDA = "Iniciar Venda"
    TXT_REALIZAR_TROCA = "Realizar Troca"
    TXT_VENDA = "Venda"
    DIALOGO_VENDEDOR = "txt_dialog_seller_name"

    # --- Ações ---
    def iniciar_venda(self):
        """Inicia uma venda. Tenta 'Venda' (Playstore) ou 'Iniciar Venda' (devices)."""
        logger.info("-> Iniciando venda...")

        # Tenta primeiro "Venda" (versão Playstore)
        try:
            if self.texto_exibido(self.TXT_VENDA, timeout=3):
                logger.info("   [INFO] Encontrado botão 'Venda' (versão Playstore)")
                self.clicar_por_texto(self.TXT_VENDA)
                return
        except:
            pass

        # Tenta "Iniciar Venda" (versões de device)
        try:
            self.rolar_ate_texto(self.TXT_INICIAR_VENDA, max_scrolls=5)
            self.clicar_por_texto(self.TXT_INICIAR_VENDA)
            return
        except:
            pass

        # Última tentativa: rola e tenta "Venda" novamente
        try:
            self.rolar_ate_texto(self.TXT_VENDA, max_scrolls=5)
            self.clicar_por_texto(self.TXT_VENDA)
        except Exception as e:
            raise Exception(f"Não encontrou 'Venda' nem 'Iniciar Venda': {e}")

    def iniciar_troca(self):
        """Inicia uma troca/devolução."""
        logger.info("-> Iniciando troca...")
        # Rola até encontrar o botão se necessário
        self.rolar_ate_texto(self.TXT_REALIZAR_TROCA, max_scrolls=5)
        time.sleep(0.5)
        self.clicar_por_texto(self.TXT_REALIZAR_TROCA)
        logger.info("-> Clicou em 'Realizar Troca'")

    def selecionar_vendedor(self, max_tentativas: int = 3):
        """Seleciona vendedor no diálogo."""
        logger.info("-> Selecionando vendedor...")
        for tentativa in range(max_tentativas):
            try:
                self.clicar_por_id(self.DIALOGO_VENDEDOR)
                logger.info("-> Vendedor selecionado!")
                return
            except Exception as e:
                if tentativa < max_tentativas - 1:
                    logger.warning(f"   [RETRY] Tentativa {tentativa + 1}: {e}")
                    time.sleep(1)
                else:
                    raise Exception(f"Nao foi possivel selecionar vendedor: {e}")

    # --- Validações ---
    def tela_inicial_exibida(self, timeout: int = 10) -> bool:
        """Verifica se está na tela inicial."""
        return (
            self.texto_exibido(self.TXT_INICIAR_VENDA, timeout) or
            self.texto_exibido(self.TXT_VENDA, timeout)
        )
