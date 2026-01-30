"""
Pedido Page - Page Object para tela de pedido de venda.
"""
import time
from pages.base_page import BasePage
from config import logger


class PedidoPage(BasePage):
    """Page Object para tela de pedido de venda."""

    # --- Locators ---
    BTN_BUSCAR_CLIENTE = "btn_select_customer"
    BTN_ADICIONAR_PRODUTOS = "btn_adicionar_produtos"
    EDT_BUSCA_PRODUTO = "editText"
    IMG_PRODUTO = "imageView3"
    BTN_PROXIMO = "btn_proximo"
    BTN_AVANCAR = "btn_proceed"
    BTN_FINALIZAR = "btnFinalizar"
    BTN_PEDIDO_GERADO = "button17"

    # Busca cliente
    EDT_BUSCA_CLIENTE = "search_src_text"
    BTN_CONFIRMAR_CLIENTE = "button3"
    BTN_INICIAR_VENDA = "button30"  # Botão para consumidor (sem cliente)
    TXT_VENDEDOR = "txt_dialog_seller_name"

    # Popup de bonus
    BTN_MAIS_TARDE = "btn_mais_tarde"
    TXT_BONUS_DISPONIVEL = "BÔNUS DISPONÍVEL"

    # --- Ações ---
    def selecionar_vendedor(self):
        """Seleciona o vendedor."""
        logger.info("-> Selecionando vendedor...")
        self.clicar_por_id(self.TXT_VENDEDOR)

    def clicar_buscar_cliente(self):
        """Clica no botão buscar cliente."""
        logger.info("-> Clicando em Buscar Cliente...")
        self.clicar_por_id(self.BTN_BUSCAR_CLIENTE)

    def iniciar_como_consumidor(self):
        """Inicia pedido sem selecionar cliente (consumidor final).

        Após selecionar vendedor, clica direto em 'Iniciar Venda' (button30).
        """
        logger.info("-> Iniciando como consumidor (sem cliente)...")
        # Clica direto no botão Iniciar Venda (sem buscar cliente)
        self.rolar_ate_id(self.BTN_INICIAR_VENDA)
        self.clicar_por_id(self.BTN_INICIAR_VENDA)

    def selecionar_cliente(self, identificador: str):
        """Seleciona cliente pelo identificador."""
        logger.info(f"-> Selecionando cliente: {identificador}")
        self.digitar_por_id(self.EDT_BUSCA_CLIENTE, identificador)
        self.pressionar_pesquisar()
        self.clicar_por_id(self.BTN_CONFIRMAR_CLIENTE)

    def adicionar_produto(self, codigo: str = "123"):
        """Adiciona produto pelo código."""
        logger.info(f"-> Adicionando produto: {codigo}")
        time.sleep(2)  # Aguarda tela carregar após selecionar cliente

        # Tenta encontrar o botão, pode precisar de scroll em algumas telas
        try:
            self.clicar_por_id(self.BTN_ADICIONAR_PRODUTOS)
        except:
            # Se não encontrou, tenta scroll
            logger.info("   [DEBUG] Botão não visível, tentando scroll...")
            self.rolar_ate_id(self.BTN_ADICIONAR_PRODUTOS, max_scrolls=3)
            self.clicar_por_id(self.BTN_ADICIONAR_PRODUTOS)

        self.digitar_por_id(self.EDT_BUSCA_PRODUTO, codigo)
        self.clicar_por_id(self.IMG_PRODUTO)

    def clicar_avancar(self):
        """Clica no botão avançar."""
        logger.info("-> Clicando em Avançar...")
        self.rolar_ate_id(self.BTN_PROXIMO)
        elemento = self.encontrar_clicavel_por_id(self.BTN_PROXIMO)
        time.sleep(1.5)
        elemento.click()

    def selecionar_pagamento_dinheiro(self):
        """Seleciona forma de pagamento dinheiro."""
        logger.info("-> Selecionando pagamento: DINHEIRO")
        time.sleep(3)
        self.rolar_ate_texto("DINHEIRO")
        self.clicar_por_texto("DINHEIRO")
        self.rolar_ate_id(self.BTN_AVANCAR)
        self.clicar_por_id(self.BTN_AVANCAR)

    def tratar_popup_bonus(self):
        """Trata popup de BÔNUS DISPONÍVEL se aparecer."""
        if self.texto_exibido(self.TXT_BONUS_DISPONIVEL, tempo_espera=3):
            logger.info("-> Popup BÔNUS DISPONÍVEL detectado. Clicando em 'Mais tarde'...")
            self.clicar_por_id(self.BTN_MAIS_TARDE)
            time.sleep(1)

    def finalizar_pedido(self):
        """Finaliza o pedido."""
        logger.info("-> Finalizando pedido...")
        self.tratar_popup_bonus()  # Trata popup de bonus se aparecer
        self.rolar_ate_texto("Finalizar")
        self.rolar_ate_id(self.BTN_FINALIZAR)
        self.clicar_por_id(self.BTN_FINALIZAR)

    def confirmar_pedido_gerado(self):
        """Confirma o pedido gerado."""
        logger.info("-> Confirmando pedido gerado...")
        self.aguardar_texto("Pedido gerado com sucesso!")
        self.rolar_ate_id(self.BTN_PEDIDO_GERADO)
        self.clicar_por_id(self.BTN_PEDIDO_GERADO)

    def executar_pedido_venda_consumidor(self, codigo_produto: str = "123"):
        """Executa fluxo completo de pedido de venda para consumidor (sem cliente)."""
        logger.info("--- [FLUXO] Iniciando pedido de venda (CONSUMIDOR) ---")

        self.selecionar_vendedor()
        self.iniciar_como_consumidor()
        self.adicionar_produto(codigo_produto)
        self.clicar_avancar()
        self.selecionar_pagamento_dinheiro()
        self.finalizar_pedido()
        self.confirmar_pedido_gerado()

        logger.info("--- [FLUXO] Pedido de venda (CONSUMIDOR) concluído ---")

    def executar_pedido_venda_cliente(self, id_cliente: str = "1", codigo_produto: str = "123"):
        """Executa fluxo completo de pedido de venda para cliente cadastrado."""
        logger.info("--- [FLUXO] Iniciando pedido de venda (CLIENTE) ---")

        self.selecionar_vendedor()
        self.clicar_buscar_cliente()
        self.selecionar_cliente(id_cliente)
        self.adicionar_produto(codigo_produto)
        self.clicar_avancar()
        self.selecionar_pagamento_dinheiro()
        self.finalizar_pedido()
        self.confirmar_pedido_gerado()

        logger.info("--- [FLUXO] Pedido de venda (CLIENTE) concluído ---")

    def executar_pedido_venda(self, id_cliente: str = "1", codigo_produto: str = "123"):
        """Executa fluxo completo de pedido de venda (mantido para compatibilidade)."""
        self.executar_pedido_venda_cliente(id_cliente, codigo_produto)

    # --- Validações ---
    def pedido_sucesso_exibido(self, timeout: int = 10) -> bool:
        """Verifica se mensagem de sucesso apareceu."""
        return self.texto_exibido("Pedido gerado com sucesso!", timeout)
