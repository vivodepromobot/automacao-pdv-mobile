"""
Test Venda Futura - Teste de venda futura com retirada em loja.
"""
import pytest
import allure
from pages.home_page import HomePage
from pages.venda_futura_page import VendaFuturaPage


@allure.epic("PDV Mobile")
@allure.feature("Vendas")
@allure.story("Venda Futura")
class TestVendaFutura:
    """Testes de venda futura."""

    @allure.title("Venda Futura - Retirada em Loja")
    @allure.description("""
    Teste de venda futura com retirada em loja:
    1. Acessar menu Venda Futura
    2. Selecionar retirada em loja
    3. Selecionar vendedor
    4. Buscar cliente por CPF
    5. Adicionar produto com tamanho
    6. Selecionar pagamento a vista
    7. Finalizar venda
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("venda_futura", "retirada_loja", "dinheiro")
    def test_venda_futura_sucesso(self, driver_logado):
        """
        Cenario: Realizar venda futura com retirada em loja
        Dado que estou logado no app
        Quando inicio uma venda futura
        E seleciono retirada em loja
        E busco cliente por CPF
        E adiciono um produto com tamanho
        E seleciono pagamento a vista em dinheiro
        Entao a venda e realizada com sucesso
        """
        driver = driver_logado

        # Arrange
        pagina_inicial = HomePage(driver)
        pagina_venda_futura = VendaFuturaPage(driver)

        # Act
        with allure.step("1. Acessar menu 'Venda Futura'"):
            pagina_venda_futura.clicar_venda_futura()

        with allure.step("2. Executar fluxo de venda futura"):
            pagina_venda_futura.executar_venda_futura(
                cpf="1",
                codigo_produto="123",
                tamanho="36"
            )

        # Assert
        with allure.step("3. Validar sucesso e concluir"):
            pagina_venda_futura.validar_sucesso_e_concluir()

        with allure.step("4. Verificar retorno a tela inicial"):
            assert pagina_inicial.tela_inicial_exibida(), "Nao voltou para tela inicial"
