"""
Test Venda Cliente - Teste de venda para cliente cadastrado.
"""
import pytest
import allure
from pages.home_page import HomePage
from pages.venda_page import VendaPage
from test_data import test_data


@allure.epic("PDV Mobile")
@allure.feature("Vendas")
@allure.story("Venda para Cliente")
class TestVendaCliente:
    """Testes de venda para cliente cadastrado."""

    @allure.title("Venda Cliente - Pagamento Dinheiro")
    @allure.description("""
    Teste de venda para cliente cadastrado:
    1. Acessar menu Iniciar Venda
    2. Selecionar vendedor
    3. Buscar e selecionar cliente cadastrado
    4. Adicionar produto ao carrinho
    5. Selecionar pagamento em dinheiro
    6. Finalizar venda
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("venda", "cliente", "dinheiro")
    def test_venda_cliente_sucesso(self, driver_logado):
        """
        Cenario: Realizar venda para cliente cadastrado
        Dado que estou logado no app
        Quando inicio uma venda
        E seleciono um cliente
        E adiciono um produto
        E finalizo com pagamento em dinheiro
        Entao a venda e realizada com sucesso
        """
        driver = driver_logado

        # Arrange
        pagina_inicial = HomePage(driver)
        pagina_venda = VendaPage(driver)

        # Act
        with allure.step("1. Acessar menu 'Iniciar Venda'"):
            pagina_inicial.iniciar_venda()

        with allure.step("2. Selecionar vendedor"):
            pagina_inicial.selecionar_vendedor()

        with allure.step("3. Executar fluxo de venda para cliente"):
            pagina_venda.executar_venda_cliente(id_cliente=test_data.CUSTOMER_ID, codigo_produto="123")

        # Assert
        with allure.step("4. Validar sucesso e concluir"):
            pagina_venda.validar_sucesso_e_concluir()

        with allure.step("5. Verificar retorno a tela inicial"):
            assert pagina_inicial.tela_inicial_exibida(), "Nao voltou para tela inicial"
