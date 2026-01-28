"""
Venda Page - Page Object para tela de venda.
"""
import time
from pages.base_page import BasePage
from config import logger


class VendaPage(BasePage):
    """Page Object para tela de venda."""

    # --- Locators ---
    BTN_BUSCAR_CLIENTE = "btn_select_customer"
    BTN_INICIAR_VENDA_SEM_CLIENTE = "button30"  # Versão Playstore
    BTN_ADICIONAR_PRODUTOS = "btn_adicionar_produtos"
    EDT_BUSCA_PRODUTO = "editText"
    IMG_PRODUTO = "imageView3"
    BTN_PROXIMO = "btn_proximo"
    BTN_AVANCAR = "btn_proceed"
    BTN_FINALIZAR = "btnFinalizar"
    BTN_CONFIRMAR_VENDA = "btn_confirmar_venda"
    BTN_IMPRIMIR_SIM = "android:id/button1"
    BTN_IMPRIMIR_NAO = "android:id/button2"

    # Busca cliente
    EDT_BUSCA_CLIENTE = "search_src_text"
    BTN_CONFIRMAR_CLIENTE = "button3"

    # Tela "Selecionar Cliente" (versão L400/Stone)
    TELA_SELECIONAR_CLIENTE = "Selecionar Cliente"
    TXT_INICIAR_VENDA_BTN = "INICIAR VENDA"

    # Popup de bonus
    BTN_MAIS_TARDE = "btn_mais_tarde"
    TXT_BONUS_DISPONIVEL = "BÔNUS DISPONÍVEL"

    # --- Ações ---
    def clicar_buscar_cliente(self):
        """Clica no botão buscar cliente."""
        logger.info("-> Clicando em Buscar Cliente...")
        time.sleep(1)

        # Versão L400/Stone: Tela "Selecionar Cliente" com botão "Buscar Cliente" por texto
        if self.texto_exibido(self.TELA_SELECIONAR_CLIENTE, tempo_espera=3):
            logger.info("   [OK] Tela 'Selecionar Cliente' detectada")
            if self.texto_exibido("Buscar Cliente", tempo_espera=2):
                self.clicar_por_texto("Buscar Cliente")
                logger.info("   [OK] Clicou em 'Buscar Cliente'")
                return

        # Versão Playstore: ID btn_select_customer
        logger.info("   [INFO] Tentando versão Playstore (ID)...")
        self.clicar_por_id(self.BTN_BUSCAR_CLIENTE)

    def iniciar_venda_sem_cliente(self):
        """Inicia venda sem selecionar cliente (consumidor)."""
        logger.info("-> Iniciando venda sem cliente...")
        time.sleep(1)  # Aguarda tela estabilizar

        # Versão L400/Stone: Tela "Selecionar Cliente" com botão "INICIAR VENDA"
        if self.texto_exibido(self.TELA_SELECIONAR_CLIENTE, tempo_espera=3):
            logger.info("   [OK] Tela 'Selecionar Cliente' detectada (versão L400/Stone)")
            if self.texto_exibido(self.TXT_INICIAR_VENDA_BTN, tempo_espera=3):
                self.clicar_por_texto(self.TXT_INICIAR_VENDA_BTN)
                logger.info("   [OK] Clicou em 'INICIAR VENDA'")
                return

        # Versão Playstore: botão button30
        logger.info("   [INFO] Tentando versão Playstore (button30)...")
        self.clicar_por_id(self.BTN_INICIAR_VENDA_SEM_CLIENTE)

    def selecionar_cliente(self, identificador: str):
        """Seleciona cliente pelo identificador."""
        logger.info(f"-> Selecionando cliente: {identificador}")
        self.digitar_por_id(self.EDT_BUSCA_CLIENTE, identificador)
        self.pressionar_pesquisar()
        self.clicar_por_id(self.BTN_CONFIRMAR_CLIENTE)

    def adicionar_produto(self, codigo: str = "123"):
        """Adiciona produto pelo código."""
        logger.info(f"-> Adicionando produto: {codigo}")
        self.clicar_por_id(self.BTN_ADICIONAR_PRODUTOS)
        self.digitar_por_id(self.EDT_BUSCA_PRODUTO, codigo)
        self.clicar_por_id(self.IMG_PRODUTO)

    def clicar_avancar(self):
        """Clica no botão avançar."""
        logger.info("-> Clicando em Avançar...")
        # Espera extra para estabilizar transição
        elemento = self.encontrar_clicavel_por_id(self.BTN_PROXIMO)
        time.sleep(1.5)
        elemento.click()

    def selecionar_pagamento_dinheiro(self):
        """Seleciona forma de pagamento dinheiro."""
        logger.info("-> Selecionando pagamento: DINHEIRO")
        time.sleep(3)  # Pausa para estabilizar tela de pagamento
        self.clicar_por_texto("DINHEIRO")
        self.clicar_por_id(self.BTN_AVANCAR)

    def tratar_popup_bonus(self):
        """Trata popup de BÔNUS DISPONÍVEL se aparecer."""
        if self.texto_exibido(self.TXT_BONUS_DISPONIVEL, tempo_espera=3):
            logger.info("-> Popup BÔNUS DISPONÍVEL detectado. Clicando em 'Mais tarde'...")
            self.clicar_por_id(self.BTN_MAIS_TARDE)
            time.sleep(1)

    def finalizar_venda(self):
        """Finaliza a venda."""
        logger.info("-> Finalizando venda...")
        self.tratar_popup_bonus()  # Trata popup de bonus se aparecer
        self.aguardar_texto("Finalizar")
        self.clicar_por_id(self.BTN_FINALIZAR)

    def responder_impressao(self, imprimir: bool = False):
        """Responde ao diálogo de impressão."""
        logger.info(f"-> Respondendo impressão: {'SIM' if imprimir else 'NÃO'}")
        btn = self.BTN_IMPRIMIR_SIM if imprimir else self.BTN_IMPRIMIR_NAO
        self.clicar_se_existir(btn, tempo_espera=20)
        time.sleep(2)  # Aguarda fechamento do diálogo

    def concluir_venda(self):
        """Clica em concluir venda após sucesso."""
        logger.info("-> Concluindo venda...")
        self.clicar_por_id(self.BTN_CONFIRMAR_VENDA)

    def executar_venda_cliente(self, id_cliente: str = "1", codigo_produto: str = "123"):
        """Executa fluxo completo de venda para cliente."""
        logger.info("--- [FLUXO] Iniciando venda para cliente ---")

        self.clicar_buscar_cliente()
        self.selecionar_cliente(id_cliente)
        self.adicionar_produto(codigo_produto)
        self.clicar_avancar()
        self.selecionar_pagamento_dinheiro()
        self.finalizar_venda()
        self.responder_impressao(imprimir=True)

        logger.info("--- [FLUXO] Venda para cliente concluída ---")

    def executar_venda_consumidor(self, codigo_produto: str = "123"):
        """Executa fluxo completo de venda para consumidor (sem cliente)."""
        logger.info("--- [FLUXO] Iniciando venda consumidor ---")

        self.iniciar_venda_sem_cliente()
        self.adicionar_produto(codigo_produto)
        self.clicar_avancar()
        self.selecionar_pagamento_dinheiro()
        self.finalizar_venda()
        self.responder_impressao(imprimir=False)

        logger.info("--- [FLUXO] Venda consumidor concluída ---")

    # --- Validações ---
    def venda_sucesso_exibida(self, timeout: int = 10) -> bool:
        """Verifica se mensagem de sucesso apareceu."""
        return self.texto_exibido("Venda realizada com sucesso!", timeout)

    def validar_sucesso_e_concluir(self):
        """Valida sucesso e conclui venda."""
        self.aguardar_texto("Venda realizada com sucesso!")
        self.concluir_venda()
