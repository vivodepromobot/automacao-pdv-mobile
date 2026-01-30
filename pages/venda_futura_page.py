"""
Venda Futura Page - Page Object para tela de venda futura.
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config import logger


class VendaFuturaPage(BasePage):
    """Page Object para tela de venda futura."""

    # --- Locators ---
    BTN_VENDA_FUTURA_LOJA = "btn_venda_futura_loja"
    BTN_VENDA_FUTURA_DOMICILIO = "btn_venda_futura_domicilio"
    TXT_VENDEDOR = "txt_dialog_seller_name"
    EDT_CPF = "edtCpf"
    BTN_CONFIRMAR_CPF = "button30"
    BTN_ADICIONAR_PRODUTOS = "btn_adicionar_produtos"
    EDT_BUSCA_PRODUTO = "editText"
    IMG_PRODUTO = "imageView3"
    BTN_PROXIMO = "btn_proximo"
    BTN_AVANCAR = "btn_proceed"
    TXT_PAGAMENTO_TITULO = "txt_payment_title"
    TXT_OPCAO_TITULO = "txt_option_title"
    IMG_PAGAMENTOS = "imageView19"
    BTN_PAGAR = "btn_pagar"
    BTN_FINALIZAR = "btnFinalizar"
    BTN_CONFIRMAR_VENDA = "btn_confirmar_venda"
    BTN_IMPRIMIR_NAO = "android:id/button2"
    BTN_MAIS_TARDE = "btn_mais_tarde"

    # --- Ações ---
    def clicar_venda_futura(self):
        """Clica no botão Venda Futura na tela inicial."""
        logger.info("-> Clicando em 'Venda Futura'...")
        self.clicar_por_texto("Venda Futura")

    def selecionar_retirada_loja(self):
        """Seleciona opção 'Retirada em loja'."""
        logger.info("-> Selecionando 'Retirada em loja'...")
        # Scroll até o botão (telas pequenas)
        self.rolar_ate_id(self.BTN_VENDA_FUTURA_LOJA)
        self.clicar_por_id(self.BTN_VENDA_FUTURA_LOJA)

    def selecionar_entrega_domicilio(self):
        """Seleciona opção 'Entrega em Domicílio' e avança Frete."""
        logger.info("-> Selecionando 'Entrega em Domicílio'...")
        # Scroll até o botão (telas pequenas)
        self.rolar_ate_id(self.BTN_VENDA_FUTURA_DOMICILIO)
        self.clicar_por_id(self.BTN_VENDA_FUTURA_DOMICILIO)

        # O script legado mostra que tem um "Avançar" logo depois (Frete)
        logger.info("-> Confirmando Frete (Avançar)...")
        self.rolar_ate_texto("Avançar")
        self.clicar_por_texto("Avançar")


    def avancar_tipo_entrega(self):
        """Avança na tela de tipo de entrega."""
        logger.info("-> Avançando tipo de entrega...")
        self.rolar_ate_texto("Avançar")
        self.clicar_por_texto("Avançar")

    def selecionar_vendedor(self):
        """Seleciona o vendedor."""
        logger.info("-> Selecionando vendedor...")
        self.clicar_por_id(self.TXT_VENDEDOR)

    def buscar_cliente_cpf(self, cpf: str = "1"):
        """Busca cliente pelo CPF."""
        logger.info(f"-> Buscando cliente CPF: {cpf}")
        self.clicar_por_id(self.EDT_CPF)
        self.digitar_por_id(self.EDT_CPF, cpf)
        self.clicar_por_id(self.BTN_CONFIRMAR_CPF)

    def adicionar_produto(self, codigo: str = "123", tamanho: str = "36"):
        """Adiciona produto com tamanho específico."""
        logger.info(f"-> Adicionando produto: {codigo}, tamanho: {tamanho}")
        self.rolar_ate_id(self.BTN_ADICIONAR_PRODUTOS)
        self.clicar_por_id(self.BTN_ADICIONAR_PRODUTOS)
        self.digitar_por_id(self.EDT_BUSCA_PRODUTO, codigo)
        self.clicar_por_id(self.IMG_PRODUTO)
        self.rolar_ate_texto(tamanho)
        self.clicar_por_texto(tamanho)

    def clicar_avancar(self):
        """Clica no botão avançar."""
        logger.info("-> Clicando em Avançar...")
        self.rolar_ate_id(self.BTN_PROXIMO)
        elemento = self.encontrar_clicavel_por_id(self.BTN_PROXIMO)
        time.sleep(1.5)
        elemento.click()

    def selecionar_pagamento_avista(self):
        """Seleciona pagamento à vista (movimento e plano)."""
        logger.info("-> Selecionando pagamento à vista...")
        time.sleep(3)

        # Clica em pagamento personalizado
        self.rolar_ate_id(self.TXT_PAGAMENTO_TITULO)
        self.clicar_por_id(self.TXT_PAGAMENTO_TITULO)

        # Seleciona movimento: A VISTA (primeiro elemento)
        elementos = self.driver.find_elements(
            AppiumBy.ID, f"{self.app_package}:id/{self.TXT_OPCAO_TITULO}"
        )
        if len(elementos) > 0:
            elementos[0].click()
            logger.info("   [OK] Movimento A VISTA selecionado")

        time.sleep(1)

        # Seleciona plano: A Vista (segundo elemento)
        elementos = self.driver.find_elements(
            AppiumBy.ID, f"{self.app_package}:id/{self.TXT_OPCAO_TITULO}"
        )
        if len(elementos) > 1:
            elementos[1].click()
            logger.info("   [OK] Plano A Vista selecionado")

        # Avança
        self.rolar_ate_id(self.BTN_AVANCAR)
        self.clicar_por_id(self.BTN_AVANCAR)

    def tratar_popup_bonus(self):
        """Trata popup de bônus se aparecer."""
        logger.info("-> Verificando popup de bônus...")
        time.sleep(3)

        if self.clicar_se_existir(self.BTN_MAIS_TARDE, tempo_espera=2):
            logger.info("   [OK] Popup de bônus fechado")
            time.sleep(2)
        else:
            logger.info("   [INFO] Nenhum popup de bônus")

    def selecionar_forma_dinheiro(self):
        """Seleciona forma de pagamento DINHEIRO."""
        logger.info("-> Selecionando forma DINHEIRO...")
        self.rolar_ate_id(self.IMG_PAGAMENTOS)
        self.clicar_por_id(self.IMG_PAGAMENTOS)
        self.rolar_ate_texto("DINHEIRO")
        self.clicar_por_texto("DINHEIRO")
        self.rolar_ate_id(self.BTN_PAGAR)
        self.clicar_por_id(self.BTN_PAGAR)

    def finalizar_venda(self):
        """Finaliza a venda."""
        logger.info("-> Finalizando venda...")
        self.rolar_ate_id(self.BTN_FINALIZAR)
        self.clicar_por_id(self.BTN_FINALIZAR)

    def responder_impressao(self, imprimir: bool = False):
        """Responde ao diálogo de impressão."""
        logger.info(f"-> Respondendo impressão: {'SIM' if imprimir else 'NÃO'}")
        self.clicar_se_existir(self.BTN_IMPRIMIR_NAO, tempo_espera=20)
        time.sleep(2)

    def concluir_venda(self):
        """Clica em concluir venda após sucesso."""
        logger.info("-> Concluindo venda...")
        self.rolar_ate_id(self.BTN_CONFIRMAR_VENDA)
        self.clicar_por_id(self.BTN_CONFIRMAR_VENDA)

    def executar_venda_futura(self, cpf: str = "1", codigo_produto: str = "123", tamanho: str = "36"):
        """Executa fluxo completo de venda futura com retirada em loja."""
        logger.info("--- [FLUXO] Iniciando venda futura (retirada loja) ---")

        self.selecionar_retirada_loja()
        self.avancar_tipo_entrega()
        self.selecionar_vendedor()
        self.buscar_cliente_cpf(cpf)
        self.adicionar_produto(codigo_produto, tamanho)
        self.clicar_avancar()
        self.selecionar_pagamento_avista()
        self.tratar_popup_bonus()
        self.selecionar_forma_dinheiro()
        self.finalizar_venda()
        self.responder_impressao(imprimir=False)

        logger.info("--- [FLUXO] Venda futura (retirada loja) executada ---")

    def executar_venda_futura_domicilio(self, cpf: str = "1", codigo_produto: str = "123", tamanho: str = "36"):
        """Executa fluxo completo de venda futura com entrega em domicílio."""
        logger.info("--- [FLUXO] Iniciando venda futura (domicílio) ---")

        self.selecionar_entrega_domicilio()  # Já inclui avançar frete
        self.selecionar_vendedor()
        self.buscar_cliente_cpf(cpf)
        self.adicionar_produto(codigo_produto, tamanho)
        self.clicar_avancar()
        self.selecionar_pagamento_avista()
        self.tratar_popup_bonus()
        self.selecionar_forma_dinheiro()
        self.finalizar_venda()
        self.responder_impressao(imprimir=False)

        logger.info("--- [FLUXO] Venda futura (domicílio) executada ---")

    # --- Validações ---
    def venda_sucesso_exibida(self, timeout: int = 10) -> bool:
        """Verifica se mensagem de sucesso apareceu."""
        return self.texto_exibido("Venda realizada com sucesso!", timeout)

    def validar_sucesso_e_concluir(self):
        """Valida sucesso e conclui venda."""
        self.aguardar_texto("Venda realizada com sucesso!")
        self.concluir_venda()
