"""
Test Troca Cliente - Teste de troca/devolução para cliente.
"""
import pytest
import allure
from pages.home_page import HomePage
from pages.troca_page import TrocaPage


@allure.epic("PDV Mobile")
@allure.feature("Trocas e Devoluções")
@allure.story("Troca para Cliente")
class TestTrocaCliente:
    """Testes de troca para cliente cadastrado."""

    @allure.title("Troca Cliente - Devolução de Produto")
    @allure.description("""
    Teste de troca/devolução para cliente cadastrado:
    1. Acessar menu Realizar Troca
    2. Selecionar vendedor
    3. Definir periodo de busca
    4. Consultar notas fiscais
    5. Selecionar nota e item para devolução
    6. Confirmar troca

    Pré-requisito: Deve existir venda recente para este cliente
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("troca", "cliente", "devolução")
    def test_troca_cliente_sucesso(self, driver_logado):
        """
        Cenário: Realizar troca de produto para cliente
        Dado que estou logado no app
        Quando inicio uma troca
        E seleciono uma nota fiscal
        E marco um item para devolução
        Então a troca é realizada com sucesso
        """
        driver = driver_logado

        # Arrange
        pagina_inicial = HomePage(driver)
        pagina_troca = TrocaPage(driver)

        # Act
        with allure.step("1. Acessar menu 'Realizar Troca'"):
            pagina_inicial.iniciar_troca()

        with allure.step("2. Selecionar vendedor"):
            pagina_inicial.selecionar_vendedor()

        with allure.step("3. Executar fluxo de troca (período, consulta, seleção)"):
            pagina_troca.executar_troca()

        # Assert
        with allure.step("4. Validar mensagem de sucesso"):
            pagina_troca.validar_e_fechar_sucesso()

        with allure.step("5. Voltar para tela inicial"):
            pagina_troca.voltar_tela(confirmar=True)

        with allure.step("6. Verificar retorno à tela inicial"):
            assert pagina_inicial.tela_inicial_exibida(), "Nao voltou para tela inicial"
