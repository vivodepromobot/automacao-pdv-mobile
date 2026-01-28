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
        time.sleep(1)  # Aguarda tela estabilizar

        # Tenta clicar diretamente sem scroll (botão sempre visível na home)
        # Primeiro tenta "Iniciar Venda" (devices: Stone, L400, etc)
        try:
            if self.texto_exibido(self.TXT_INICIAR_VENDA, timeout=3):
                logger.info("   [INFO] Encontrado 'Iniciar Venda' (versão device)")
                self.clicar_por_texto(self.TXT_INICIAR_VENDA)
                return
        except:
            pass

        # Depois tenta "Venda" (versão Playstore)
        try:
            if self.texto_exibido(self.TXT_VENDA, timeout=3):
                logger.info("   [INFO] Encontrado 'Venda' (versão Playstore)")
                self.clicar_por_texto(self.TXT_VENDA)
                return
        except:
            pass

        # Fallback: tenta qualquer um com um pouco mais de espera
        raise Exception(f"Não encontrou 'Venda' nem 'Iniciar Venda' na tela inicial")

    def iniciar_troca(self):
        """Inicia uma troca/devolução."""
        logger.info("-> Iniciando troca...")
        # Rola até encontrar o botão se necessário
        self.rolar_ate_texto(self.TXT_REALIZAR_TROCA, max_scrolls=5)
        time.sleep(0.5)
        self.clicar_por_texto(self.TXT_REALIZAR_TROCA)
        logger.info("-> Clicou em 'Realizar Troca'")

    def selecionar_vendedor(self, max_tentativas: int = 3):
        """
        Seleciona vendedor no diálogo.
        Se o diálogo não aparecer (algumas versões não exigem), continua o fluxo.
        """
        logger.info("-> Selecionando vendedor...")
        time.sleep(1)  # Aguarda diálogo aparecer

        for tentativa in range(max_tentativas):
            try:
                # Verifica se o diálogo do vendedor existe
                if self.elemento_existe(self.DIALOGO_VENDEDOR, tempo_espera=3):
                    self.clicar_por_id(self.DIALOGO_VENDEDOR)
                    logger.info("-> Vendedor selecionado!")
                    return
                else:
                    # Diálogo não apareceu - algumas versões não exigem seleção de vendedor
                    logger.info("-> Diálogo de vendedor não apareceu (versão pode não exigir)")
                    return
            except Exception as e:
                if tentativa < max_tentativas - 1:
                    logger.warning(f"   [RETRY] Tentativa {tentativa + 1}: {e}")
                    time.sleep(1)
                else:
                    # Se falhou todas as tentativas, assume que não precisa de vendedor
                    logger.warning("-> Não foi possível selecionar vendedor, continuando...")

    # --- Validações ---
    def tela_inicial_exibida(self, timeout: int = 10) -> bool:
        """Verifica se está na tela inicial."""
        return (
            self.texto_exibido(self.TXT_INICIAR_VENDA, timeout) or
            self.texto_exibido(self.TXT_VENDA, timeout)
        )
