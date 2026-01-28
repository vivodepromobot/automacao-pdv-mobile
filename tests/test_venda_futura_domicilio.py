import pytest
import allure
from pages.home_page import HomePage
from pages.venda_futura_page import VendaFuturaPage

@allure.epic("PDV Mobile")
@allure.feature("Vendas")
@allure.story("Venda Futura")
class TestVendaFuturaDomicilio:
    
    @allure.title("Venda Futura - Entrega em Domicílio")
    @allure.description("""
    Teste de Venda Futura com fluxo de Entrega em Domicílio:
    1. Iniciar Venda Futura
    2. Selecionar Domicílio e confirmar Frete
    3. Fluxo padrão (Vendedor, Cliente, Produto, Pagamento)
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("venda_futura", "domicilio", "dinheiro")
    def test_venda_futura_domicilio_sucesso(self, driver_logado):
        """
        Cenário: Realizar venda futura para entrega em domicílio.
        """
        driver = driver_logado
        
        # Instancia as páginas (Reutilizando a existente!)
        home = HomePage(driver)
        venda_futura = VendaFuturaPage(driver)

        # 1. Início
        with allure.step("1. Iniciar Venda Futura"):
            venda_futura.clicar_venda_futura()

        # 2. Entrega (AQUI É A DIFERENÇA DO SEU LEGADO)
        with allure.step("2. Configurar Entrega em Domicílio"):
            venda_futura.selecionar_entrega_domicilio()
            # Nota: O método que criamos já clica no "Avançar" do Frete

        # 3. Fluxo Padrão (Reutilizando métodos que já funcionam)
        with allure.step("3. Vendedor e Cliente"):
            venda_futura.selecionar_vendedor()
            venda_futura.buscar_cliente_cpf("1")

        with allure.step("4. Adicionar Produto"):
            venda_futura.adicionar_produto(codigo="123", tamanho="36")
            venda_futura.clicar_avancar()

        with allure.step("5. Pagamento (A Vista/Dinheiro)"):
            venda_futura.selecionar_pagamento_avista()
            venda_futura.tratar_popup_bonus() # Lógica blindada do bônus
            venda_futura.selecionar_forma_dinheiro()

        with allure.step("6. Finalizar"):
            venda_futura.finalizar_venda()
            venda_futura.responder_impressao(imprimir=False)
            venda_futura.validar_sucesso_e_concluir()

        # Validação final
        assert home.tela_inicial_exibida(), "Não retornou para a Home"