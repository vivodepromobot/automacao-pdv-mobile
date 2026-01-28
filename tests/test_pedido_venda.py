"""
Test Pedido Venda - Teste de pedido de venda.
"""
import pytest
import allure
from pages.home_page import HomePage
from pages.pedido_page import PedidoPage
from test_data import test_data


@allure.epic("PDV Mobile")
@allure.feature("Pedido de Venda")
@allure.story("Gerar Pedido")
class TestPedidoVenda:
    """Testes de pedido de venda."""

    @allure.title("Gerar pedido de venda com pagamento em dinheiro")
    @allure.description("""
    Teste completo do fluxo de pedido de venda:
    1. Acessar menu Pedido Venda
    2. Selecionar vendedor
    3. Buscar e selecionar cliente
    4. Adicionar produto ao pedido
    5. Selecionar pagamento em dinheiro
    6. Finalizar e confirmar pedido
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("pedido", "venda", "dinheiro")
    def test_pedido_venda_sucesso(self, driver_logado):
        """
        Cenario: Realizar pedido de venda
        Dado que estou logado no app
        Quando inicio um pedido de venda
        E seleciono um cliente
        E adiciono um produto
        E finalizo com pagamento em dinheiro
        Entao o pedido e gerado com sucesso
        """
        driver = driver_logado

        # Arrange
        pagina_inicial = HomePage(driver)
        pagina_pedido = PedidoPage(driver)

        # Act
        with allure.step("1. Acessar menu 'Pedido Venda'"):
            pagina_inicial.rolar_ate_texto("Pedido Venda", max_scrolls=3)
            pagina_inicial.clicar_por_texto("Pedido Venda")

        with allure.step("2. Selecionar vendedor"):
            pagina_inicial.selecionar_vendedor()

        with allure.step("3. Buscar e selecionar cliente"):
            pagina_pedido.clicar_buscar_cliente()
            pagina_pedido.selecionar_cliente(test_data.CUSTOMER_ID)

        with allure.step("4. Adicionar produto ao pedido"):
            pagina_pedido.adicionar_produto("123")

        with allure.step("5. Avançar para pagamento"):
            pagina_pedido.clicar_avancar()

        with allure.step("6. Selecionar pagamento DINHEIRO"):
            pagina_pedido.selecionar_pagamento_dinheiro()

        with allure.step("7. Finalizar pedido"):
            pagina_pedido.finalizar_pedido()

        # Assert - validação já acontece dentro de confirmar_pedido_gerado
        with allure.step("8. Confirmar pedido gerado com sucesso"):
            pagina_pedido.confirmar_pedido_gerado()

        with allure.step("9. Verificar retorno à tela inicial"):
            assert pagina_inicial.tela_inicial_exibida(), "Nao voltou para tela inicial"
