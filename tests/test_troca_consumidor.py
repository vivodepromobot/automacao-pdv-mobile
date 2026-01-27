"""
Test Troca Consumidor - Teste de troca/devolução para consumidor.
"""
import pytest
import allure
from pages.home_page import HomePage
from pages.troca_page import TrocaPage


@allure.epic("PDV Mobile")
@allure.feature("Trocas e Devoluções")
@allure.story("Troca para Consumidor")
class TestTrocaConsumidor:
    """Testes de troca para consumidor (com venda pos-troca)."""

    @allure.title("Troca Consumidor - Devolução com Venda Bônus")
    @allure.description("""
    Teste de troca/devolução para consumidor com venda pós-troca:
    1. Acessar menu Realizar Troca
    2. Selecionar vendedor
    3. Definir periodo e consultar notas
    4. Selecionar nota e item para devolução
    5. Confirmar troca (gera bônus)
    6. Adicionar novo produto
    7. Pagar com bônus da troca
    8. Finalizar venda

    Pré-requisito: Deve existir venda recente para consumidor
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("troca", "consumidor", "bonus", "devolução")
    def test_troca_consumidor_sucesso(self, driver_logado):
        """
        Cenario: Realizar troca de produto para consumidor
        Dado que estou logado no app
        Quando inicio uma troca
        E seleciono uma nota fiscal
        E marco um item para devolucao
        E realizo uma venda com o bonus da troca
        Entao a troca e venda sao realizadas com sucesso
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

        with allure.step("3. Executar fluxo de troca consumidor (com venda bônus)"):
            pagina_troca.executar_troca_consumidor()

        # Assert
        with allure.step("4. Validar venda realizada com sucesso"):
            pagina_troca.validar_venda_e_concluir()

        with allure.step("5. Verificar retorno à tela inicial"):
            assert pagina_inicial.tela_inicial_exibida(), "Nao voltou para tela inicial"
