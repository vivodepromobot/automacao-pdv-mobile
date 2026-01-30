"""
Test Consulta Pedido - Testes de consulta e finalização de pedidos.
"""
import pytest
import allure
from pages.home_page import HomePage
from pages.consulta_pedido_page import ConsultaPedidoPage


@allure.epic("PDV Mobile")
@allure.feature("Consulta de Pedidos")
@allure.story("Finalizar Pedido")
class TestConsultaPedido:
    """Testes de consulta e finalização de pedidos."""

    @allure.title("Consulta Pedido - Finalizar pedido consumidor")
    @allure.description("""
    Teste de consulta e finalização de pedido de consumidor:
    1. Configurar flag 'Buscar todos os pedidos'
    2. Acessar Cons. Pedido
    3. Selecionar primeiro pedido da lista
    4. Finalizar pedido
    5. Validar venda realizada com sucesso
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("consulta", "pedido", "consumidor", "finalizar")
    def test_consulta_pedido_consumidor_sucesso(self, driver_logado):
        """
        Cenario: Finalizar pedido de consumidor via consulta
        Dado que estou logado no app
        E configurei a flag de buscar todos os pedidos
        Quando acesso a consulta de pedidos
        E seleciono o primeiro pedido (consumidor)
        E finalizo o pedido
        Entao a venda e realizada com sucesso
        """
        driver = driver_logado

        # Arrange
        pagina_inicial = HomePage(driver)
        pagina_consulta = ConsultaPedidoPage(driver)

        # Act
        with allure.step("1. Configurar flag 'Buscar todos os pedidos'"):
            pagina_consulta.configurar_buscar_todos_pedidos()

        with allure.step("2. Executar consulta e finalização do pedido"):
            pagina_consulta.executar_consulta_e_finalizar_pedido()

        # Assert
        with allure.step("3. Validar sucesso e concluir"):
            pagina_consulta.validar_sucesso_e_concluir()

        with allure.step("4. Verificar retorno à tela inicial"):
            assert pagina_inicial.tela_inicial_exibida(), "Nao voltou para tela inicial"

    @allure.title("Consulta Pedido - Finalizar pedido cliente")
    @allure.description("""
    Teste de consulta e finalização de pedido de cliente:
    1. Acessar Cons. Pedido (flag já configurada)
    2. Selecionar primeiro pedido da lista
    3. Finalizar pedido
    4. Validar venda realizada com sucesso
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("consulta", "pedido", "cliente", "finalizar")
    def test_consulta_pedido_cliente_sucesso(self, driver_logado):
        """
        Cenario: Finalizar pedido de cliente via consulta
        Dado que estou logado no app
        E a flag de buscar todos os pedidos já está configurada
        Quando acesso a consulta de pedidos
        E seleciono o primeiro pedido (cliente)
        E finalizo o pedido
        Entao a venda e realizada com sucesso
        """
        driver = driver_logado

        # Arrange
        pagina_inicial = HomePage(driver)
        pagina_consulta = ConsultaPedidoPage(driver)

        # Act - Flag já deve estar ativa do teste anterior
        with allure.step("1. Executar consulta e finalização do pedido"):
            pagina_consulta.executar_consulta_e_finalizar_pedido()

        # Assert
        with allure.step("2. Validar sucesso e concluir"):
            pagina_consulta.validar_sucesso_e_concluir()

        with allure.step("3. Verificar retorno à tela inicial"):
            assert pagina_inicial.tela_inicial_exibida(), "Nao voltou para tela inicial"
