"""
Troca Page - Page Object para tela de troca/devolução.
"""
import time
from datetime import datetime
from pages.base_page import BasePage
from config import logger
from test_data import test_data


class TrocaPage(BasePage):
    """Page Object para tela de troca/devolução."""

    # --- Locators ---
    INPUT_DATA_INICIAL = "textInputLayout4"
    BTN_CONSULTAR = "button9"
    ITEM_LISTA_NOTAS = "textView100"
    CHECKBOX_ITEM = "checkBox"
    BTN_DEVOLVER = "button12"
    BTN_DIALOGO_OK = "md_buttonDefaultPositive"

    # Venda pós-troca (consumidor)
    BTN_ADICIONAR_PRODUTOS = "btn_adicionar_produtos"
    EDT_BUSCA_PRODUTO = "editText"
    IMG_PRODUTO = "imageView3"
    BTN_PROXIMO = "btn_proximo"
    BTN_AVANCAR = "btn_proceed"
    SWITCH_BONUS = "switch_bonus"
    BTN_FINALIZAR = "btnFinalizar"
    BTN_CONFIRMAR_VENDA = "btn_confirmar_venda"
    BTN_IMPRIMIR_NAO = "android:id/button2"

    # Busca cliente
    EDT_BUSCA_CLIENTE = "search_src_text"
    BTN_CONFIRMAR_CLIENTE = "button3"

    # Popup de bonus
    BTN_MAIS_TARDE = "btn_mais_tarde"
    TXT_BONUS_DISPONIVEL = "BÔNUS DISPONÍVEL"

    # --- Ações ---
    def definir_data_inicial(self, data: str = None):
        """Define data inicial para consulta."""
        if data is None:
            data = datetime.now().strftime('%d/%m/%Y')

        logger.info(f"-> Definindo data inicial: {data}")

        # Rola até encontrar o campo de período (não tenta fechar teclado)
        self.rolar_ate_id(self.INPUT_DATA_INICIAL, max_scrolls=10)

        self.clicar_por_id(self.INPUT_DATA_INICIAL)
        xpath = f"//*[@resource-id='{self.app_package}:id/{self.INPUT_DATA_INICIAL}']//android.widget.EditText"
        self.digitar_por_xpath(xpath, data)
        time.sleep(0.5)

    def clicar_consultar(self):
        """Clica no botão consultar."""
        # Rola até encontrar o botão consultar por ID (funciona com teclado aberto)
        self.rolar_ate_id(self.BTN_CONSULTAR, max_scrolls=10)
        self.clicar_por_id(self.BTN_CONSULTAR)

    def selecionar_primeira_nota(self):
        """Seleciona primeira nota da lista."""
        logger.info("-> Selecionando primeira nota da lista...")
        time.sleep(1)
        self.clicar_no_primeiro_da_lista_por_id(self.ITEM_LISTA_NOTAS)

    def selecionar_cliente(self, identificador: str):
        """Seleciona cliente pelo identificador."""
        logger.info(f"-> Selecionando cliente: {identificador}")
        self.digitar_por_id(self.EDT_BUSCA_CLIENTE, identificador)
        self.pressionar_pesquisar()
        self.clicar_por_id(self.BTN_CONFIRMAR_CLIENTE)

    def marcar_item_para_devolucao(self):
        """Marca item para devolução. Checkbox está no início da tela."""
        logger.info("-> Marcando item para devolução...")
        time.sleep(2)  # Aguarda tela carregar completamente
        self.clicar_por_id(self.CHECKBOX_ITEM)

    def clicar_devolver_itens(self):
        """Clica em devolver itens."""
        self.clicar_por_id(self.BTN_DEVOLVER)

    def confirmar_dialogos(self):
        """Confirma diálogos de atenção e confirmação."""
        # Popup de atenção (opcional) - espera 5 segundos como no legado
        self.clicar_se_existir(self.BTN_DIALOGO_OK, tempo_espera=5)
        time.sleep(0.5)
        # Popup de confirmação
        self.clicar_por_id(self.BTN_DIALOGO_OK)

    def adicionar_produto(self, codigo: str = "123"):
        """Adiciona produto pelo código."""
        logger.info(f"-> Adicionando produto: {codigo}")
        self.clicar_por_id(self.BTN_ADICIONAR_PRODUTOS)
        self.digitar_por_id(self.EDT_BUSCA_PRODUTO, codigo)
        self.clicar_por_id(self.IMG_PRODUTO)

    def clicar_avancar(self):
        """Clica no botão avançar."""
        logger.info("-> Clicando em Avançar...")
        elemento = self.encontrar_clicavel_por_id(self.BTN_PROXIMO)
        time.sleep(1.5)
        elemento.click()

    def selecionar_pagamento_bonus(self):
        """Seleciona pagamento via bônus da troca."""
        logger.info("-> Selecionando pagamento: BÔNUS")
        time.sleep(3)
        self.clicar_por_id(self.SWITCH_BONUS)
        self.clicar_por_id(self.BTN_AVANCAR)

    def tratar_popup_bonus(self):
        """Trata popup de BÔNUS DISPONÍVEL se aparecer."""
        if self.texto_exibido(self.TXT_BONUS_DISPONIVEL, tempo_espera=3):
            logger.info("-> Popup BÔNUS DISPONÍVEL detectado. Clicando em 'Mais tarde'...")
            self.clicar_por_id(self.BTN_MAIS_TARDE)
            time.sleep(1)

    def finalizar_venda(self):
        """Finaliza a venda pós-troca."""
        logger.info("-> Finalizando venda...")
        self.tratar_popup_bonus()  # Trata popup de bonus se aparecer
        self.rolar_ate_texto("Finalizar", max_scrolls=5)
        self.clicar_por_id(self.BTN_FINALIZAR)

    def responder_impressao_nao(self):
        """Responde NÃO ao diálogo de impressão."""
        logger.info("-> Respondendo impressão: NÃO")
        self.clicar_se_existir(self.BTN_IMPRIMIR_NAO, tempo_espera=20)
        time.sleep(2)

    def concluir_venda(self):
        """Clica em concluir venda após sucesso."""
        logger.info("-> Concluindo venda...")
        self.clicar_por_id(self.BTN_CONFIRMAR_VENDA)

    def executar_troca(self, data: str = None):
        """Executa fluxo completo de troca (cliente)."""
        logger.info("--- [FLUXO] Iniciando troca ---")

        # Rolagem por ID é feita dentro de definir_data_inicial e clicar_consultar
        self.definir_data_inicial(data)
        self.clicar_consultar()
        self.selecionar_primeira_nota()
        # Confirma popup se aparecer
        self.clicar_texto_se_existir("SIM", tempo_espera=3)
        self.marcar_item_para_devolucao()
        self.clicar_devolver_itens()
        self.confirmar_dialogos()

        # Valida sucesso e volta para tela inicial
        self.validar_e_fechar_sucesso()
        time.sleep(1)
        self.voltar_tela(confirmar=True)

        logger.info("--- [FLUXO] Troca concluída ---")

    def executar_troca_consumidor(self, data: str = None, codigo_produto: str = "123"):
        """Executa fluxo completo de troca para consumidor (com venda pós-troca)."""
        logger.info("--- [FLUXO] Iniciando troca consumidor ---")

        # Rolagem por ID é feita dentro de definir_data_inicial e clicar_consultar
        self.definir_data_inicial(data)
        self.clicar_consultar()
        self.selecionar_primeira_nota()

        # Se aparecer popup de SIM, precisa selecionar cliente
        if self.clicar_texto_se_existir("SIM", tempo_espera=3):
            self.selecionar_cliente(test_data.CUSTOMER_ID)

        self.marcar_item_para_devolucao()
        self.clicar_devolver_itens()
        self.confirmar_dialogos()

        # Valida sucesso da troca
        self.validar_e_fechar_sucesso()

        # Venda pós-troca
        self.adicionar_produto(codigo_produto)
        self.clicar_avancar()
        self.selecionar_pagamento_bonus()
        self.finalizar_venda()
        self.responder_impressao_nao()

        logger.info("--- [FLUXO] Troca consumidor concluída ---")

    # --- Validações ---
    def sucesso_exibido(self, timeout: int = 10) -> bool:
        """Verifica se mensagem de sucesso apareceu."""
        return self.texto_exibido("Sucesso!", timeout)

    def validar_e_fechar_sucesso(self):
        """Valida sucesso e fecha popup."""
        self.aguardar_texto("Sucesso!")
        self.clicar_por_id(self.BTN_DIALOGO_OK)

    def venda_sucesso_exibida(self, timeout: int = 10) -> bool:
        """Verifica se mensagem de sucesso da venda apareceu."""
        return self.texto_exibido("Venda realizada com sucesso!", timeout)

    def validar_venda_e_concluir(self):
        """Valida sucesso da venda e conclui."""
        self.aguardar_texto("Venda realizada com sucesso!")
        self.concluir_venda()
