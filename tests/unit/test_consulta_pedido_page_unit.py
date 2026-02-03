"""
Testes unitários para ConsultaPedidoPage.
Utiliza mocks para evitar interação real com Appium/emulador.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestConsultaPedidoPageAbrirMenuLateral:
    """Testes para o método abrir_menu_lateral."""

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_abrir_menu_lateral_sucesso(self, mock_time, mock_logger, mock_base_init):
        """
        Deve encontrar e clicar no menu lateral por accessibility ID.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        mock_menu = MagicMock()
        page.driver = MagicMock()
        page.driver.find_element.return_value = mock_menu

        # Act
        page.abrir_menu_lateral()

        # Assert
        mock_menu.click.assert_called_once()

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_abrir_menu_lateral_lanca_excecao_quando_falha(self, mock_time, mock_logger, mock_base_init):
        """
        Deve lançar exceção quando não encontra o menu.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page.driver.find_element.side_effect = Exception("Elemento não encontrado")

        # Act & Assert
        with pytest.raises(Exception):
            page.abrir_menu_lateral()


class TestConsultaPedidoPageGarantirFlagBuscarTodosPedidos:
    """Testes para o método garantir_flag_buscar_todos_pedidos."""

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_garantir_flag_ativa_switch_quando_desativado(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o switch está desativado (checked=false),
        deve clicar para ativar.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()

        mock_switch = MagicMock()
        mock_switch.is_displayed.return_value = True
        mock_switch.get_attribute.return_value = "false"

        page.driver.find_elements.side_effect = [
            [MagicMock()],  # elementos do texto
            [mock_switch]   # switches
        ]

        page.rolar_ate_texto = MagicMock()
        page.clicar_por_texto = MagicMock()

        # Act
        resultado = page.garantir_flag_buscar_todos_pedidos()

        # Assert
        assert resultado is True
        mock_switch.click.assert_called_once()

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_garantir_flag_nao_clica_quando_ja_ativado(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o switch já está ativado (checked=true),
        não deve clicar.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()

        mock_switch = MagicMock()
        mock_switch.is_displayed.return_value = True
        mock_switch.get_attribute.return_value = "true"

        page.driver.find_elements.side_effect = [
            [MagicMock()],  # elementos do texto
            [mock_switch]   # switches
        ]

        page.rolar_ate_texto = MagicMock()
        page.clicar_por_texto = MagicMock()

        # Act
        resultado = page.garantir_flag_buscar_todos_pedidos()

        # Assert
        assert resultado is True
        mock_switch.click.assert_not_called()


class TestConsultaPedidoPageSelecionarPrimeiroPedido:
    """Testes para o método selecionar_primeiro_pedido."""

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_selecionar_primeiro_pedido_quando_lista_tem_elementos(self, mock_time, mock_logger, mock_base_init):
        """
        Quando há pedidos na lista, deve clicar no primeiro.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page._app_package = "com.test.app"

        mock_elemento = MagicMock()
        page.driver.find_elements.return_value = [mock_elemento, MagicMock()]

        # Act
        resultado = page.selecionar_primeiro_pedido()

        # Assert
        assert resultado is True
        mock_elemento.click.assert_called_once()

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_selecionar_primeiro_pedido_retorna_false_quando_lista_vazia(self, mock_time, mock_logger, mock_base_init):
        """
        Quando não há pedidos na lista, deve retornar False.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page._app_package = "com.test.app"
        page.driver.find_elements.return_value = []

        # Act
        resultado = page.selecionar_primeiro_pedido()

        # Assert
        assert resultado is False


class TestConsultaPedidoPageTratarPopupBonus:
    """Testes para o método tratar_popup_bonus."""

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_tratar_popup_bonus_clica_quando_existe(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o popup de bônus existe, deve clicar em 'Mais tarde'.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page.clicar_se_existir = MagicMock(return_value=True)

        # Act
        page.tratar_popup_bonus()

        # Assert
        page.clicar_se_existir.assert_called_once_with(ConsultaPedidoPage.BTN_MAIS_TARDE, tempo_espera=3)

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_tratar_popup_bonus_ignora_quando_nao_existe(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o popup de bônus não existe, deve ignorar.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page.clicar_se_existir = MagicMock(return_value=False)

        # Act - não deve lançar exceção
        page.tratar_popup_bonus()

        # Assert
        page.clicar_se_existir.assert_called_once()


class TestConsultaPedidoPageResponderImpressao:
    """Testes para o método responder_impressao."""

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_responder_impressao_clica_nao(self, mock_time, mock_logger, mock_base_init):
        """
        Deve clicar em NÃO no diálogo de impressão.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page.clicar_se_existir = MagicMock()

        # Act
        page.responder_impressao(imprimir=False)

        # Assert
        page.clicar_se_existir.assert_called_once_with(ConsultaPedidoPage.BTN_IMPRIMIR_NAO, tempo_espera=20)


class TestConsultaPedidoPageValidacoes:
    """Testes para métodos de validação."""

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    def test_venda_sucesso_exibida_retorna_true(self, mock_logger, mock_base_init):
        """
        Deve retornar True quando mensagem de sucesso está visível.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page.texto_exibido = MagicMock(return_value=True)

        # Act
        resultado = page.venda_sucesso_exibida(timeout=10)

        # Assert
        assert resultado is True
        page.texto_exibido.assert_called_once_with("Venda realizada com sucesso!", 10)

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    def test_venda_sucesso_exibida_retorna_false(self, mock_logger, mock_base_init):
        """
        Deve retornar False quando mensagem de sucesso não está visível.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page.texto_exibido = MagicMock(return_value=False)

        # Act
        resultado = page.venda_sucesso_exibida(timeout=10)

        # Assert
        assert resultado is False


class TestConsultaPedidoPageFluxoCompleto:
    """Testes para o método executar_consulta_e_finalizar_pedido."""

    @patch('pages.consulta_pedido_page.BasePage.__init__', return_value=None)
    @patch('pages.consulta_pedido_page.logger')
    @patch('pages.consulta_pedido_page.time')
    def test_executar_consulta_e_finalizar_pedido_chama_metodos_na_ordem(self, mock_time, mock_logger, mock_base_init):
        """
        Deve chamar todos os métodos do fluxo na ordem correta.
        """
        from pages.consulta_pedido_page import ConsultaPedidoPage

        # Arrange
        page = ConsultaPedidoPage.__new__(ConsultaPedidoPage)
        page.driver = MagicMock()
        page.acessar_consulta_pedido = MagicMock()
        page.selecionar_primeiro_pedido = MagicMock()
        page.clicar_finalizar_pedido = MagicMock()
        page.finalizar_venda = MagicMock()
        page.responder_impressao = MagicMock()

        # Act
        page.executar_consulta_e_finalizar_pedido()

        # Assert - verifica ordem de chamada
        page.acessar_consulta_pedido.assert_called_once()
        page.selecionar_primeiro_pedido.assert_called_once()
        page.clicar_finalizar_pedido.assert_called_once()
        page.finalizar_venda.assert_called_once()
        page.responder_impressao.assert_called_once_with(imprimir=False)
