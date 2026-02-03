"""
Testes unitários para TrocaPage.
Utiliza mocks para evitar interação real com Appium/emulador.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestTrocaPageDefinirDataInicial:
    """Testes para o método definir_data_inicial."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_definir_data_inicial_com_data_fornecida(self, mock_time, mock_logger, mock_base_init):
        """
        Quando uma data é fornecida, deve usá-la.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page._app_package = "com.test.app"
        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()
        page.digitar_por_xpath = MagicMock()

        data = "15/06/2024"

        # Act
        page.definir_data_inicial(data)

        # Assert
        page.clicar_por_id.assert_called_once_with(TrocaPage.INPUT_DATA_INICIAL)
        # Verifica que a data fornecida foi usada
        call_args = page.digitar_por_xpath.call_args
        assert data in str(call_args)

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_definir_data_inicial_usa_data_atual_quando_nao_fornecida(self, mock_time, mock_logger, mock_base_init):
        """
        Quando nenhuma data é fornecida, deve usar a data atual.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page._app_package = "com.test.app"
        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()
        page.digitar_por_xpath = MagicMock()

        data_esperada = datetime.now().strftime('%d/%m/%Y')

        # Act
        page.definir_data_inicial()

        # Assert
        call_args = page.digitar_por_xpath.call_args
        assert data_esperada in str(call_args)


class TestTrocaPageClicarConsultar:
    """Testes para o método clicar_consultar."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    def test_clicar_consultar_rola_e_clica(self, mock_logger, mock_base_init):
        """
        Deve rolar até o botão e clicar.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()

        # Act
        page.clicar_consultar()

        # Assert
        page.rolar_ate_id.assert_called_once_with(TrocaPage.BTN_CONSULTAR, max_scrolls=10)
        page.clicar_por_id.assert_called_once_with(TrocaPage.BTN_CONSULTAR)


class TestTrocaPageSelecionarPrimeiraNota:
    """Testes para o método selecionar_primeira_nota."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_selecionar_primeira_nota_clica_no_primeiro_item(self, mock_time, mock_logger, mock_base_init):
        """
        Deve clicar no primeiro item da lista de notas.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.clicar_no_primeiro_da_lista_por_id = MagicMock()

        # Act
        page.selecionar_primeira_nota()

        # Assert
        page.clicar_no_primeiro_da_lista_por_id.assert_called_once_with(TrocaPage.ITEM_LISTA_NOTAS)


class TestTrocaPageSelecionarCliente:
    """Testes para o método selecionar_cliente."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    def test_selecionar_cliente_digita_pesquisa_e_confirma(self, mock_logger, mock_base_init):
        """
        Deve digitar identificador, pesquisar e confirmar.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.digitar_por_id = MagicMock()
        page.pressionar_pesquisar = MagicMock()
        page.clicar_por_id = MagicMock()

        identificador = "54321"

        # Act
        page.selecionar_cliente(identificador)

        # Assert
        page.digitar_por_id.assert_called_once_with(TrocaPage.EDT_BUSCA_CLIENTE, identificador)
        page.pressionar_pesquisar.assert_called_once()
        page.clicar_por_id.assert_called_once_with(TrocaPage.BTN_CONFIRMAR_CLIENTE)


class TestTrocaPageMarcarItemParaDevolucao:
    """Testes para o método marcar_item_para_devolucao."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_marcar_item_para_devolucao_clica_no_checkbox(self, mock_time, mock_logger, mock_base_init):
        """
        Deve clicar no checkbox do item.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.clicar_por_id = MagicMock()

        # Act
        page.marcar_item_para_devolucao()

        # Assert
        page.clicar_por_id.assert_called_once_with(TrocaPage.CHECKBOX_ITEM)


class TestTrocaPageConfirmarDialogos:
    """Testes para o método confirmar_dialogos."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_confirmar_dialogos_clica_nos_popups(self, mock_time, mock_logger, mock_base_init):
        """
        Deve clicar em ambos os popups de confirmação.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.clicar_se_existir = MagicMock(return_value=True)
        page.clicar_por_id = MagicMock()

        # Act
        page.confirmar_dialogos()

        # Assert
        page.clicar_se_existir.assert_called_once_with(TrocaPage.BTN_DIALOGO_OK, tempo_espera=5)
        page.clicar_por_id.assert_called_once_with(TrocaPage.BTN_DIALOGO_OK)


class TestTrocaPageTratarPopupBonus:
    """Testes para o método tratar_popup_bonus."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_tratar_popup_bonus_clica_quando_visivel(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o popup de bônus está visível, deve clicar em 'Mais tarde'.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.texto_exibido = MagicMock(return_value=True)
        page.clicar_por_id = MagicMock()

        # Act
        page.tratar_popup_bonus()

        # Assert
        page.clicar_por_id.assert_called_once_with(TrocaPage.BTN_MAIS_TARDE)

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_tratar_popup_bonus_ignora_quando_nao_visivel(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o popup não está visível, não deve clicar.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.texto_exibido = MagicMock(return_value=False)
        page.clicar_por_id = MagicMock()

        # Act
        page.tratar_popup_bonus()

        # Assert
        page.clicar_por_id.assert_not_called()


class TestTrocaPageSelecionarPagamentoBonus:
    """Testes para o método selecionar_pagamento_bonus."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.time')
    def test_selecionar_pagamento_bonus_ativa_switch_e_avanca(self, mock_time, mock_logger, mock_base_init):
        """
        Deve ativar o switch de bônus e clicar em avançar.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.clicar_por_id = MagicMock()

        # Act
        page.selecionar_pagamento_bonus()

        # Assert
        page.clicar_por_id.assert_any_call(TrocaPage.SWITCH_BONUS)
        page.clicar_por_id.assert_any_call(TrocaPage.BTN_AVANCAR)


class TestTrocaPageValidacoes:
    """Testes para métodos de validação."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    def test_sucesso_exibido_retorna_true(self, mock_logger, mock_base_init):
        """
        Deve retornar True quando 'Sucesso!' está visível.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.texto_exibido = MagicMock(return_value=True)

        # Act
        resultado = page.sucesso_exibido(timeout=10)

        # Assert
        assert resultado is True
        page.texto_exibido.assert_called_once_with("Sucesso!", 10)

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    def test_venda_sucesso_exibida_retorna_true(self, mock_logger, mock_base_init):
        """
        Deve retornar True quando mensagem de venda sucesso está visível.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.texto_exibido = MagicMock(return_value=True)

        # Act
        resultado = page.venda_sucesso_exibida(timeout=10)

        # Assert
        assert resultado is True
        page.texto_exibido.assert_called_once_with("Venda realizada com sucesso!", 10)

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    def test_validar_e_fechar_sucesso(self, mock_logger, mock_base_init):
        """
        Deve aguardar 'Sucesso!' e clicar em OK.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.aguardar_texto = MagicMock()
        page.clicar_por_id = MagicMock()

        # Act
        page.validar_e_fechar_sucesso()

        # Assert
        page.aguardar_texto.assert_called_once_with("Sucesso!")
        page.clicar_por_id.assert_called_once_with(TrocaPage.BTN_DIALOGO_OK)


class TestTrocaPageFluxoTroca:
    """Testes para o método executar_troca."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    def test_executar_troca_chama_metodos_na_ordem(self, mock_logger, mock_base_init):
        """
        Deve chamar todos os métodos do fluxo na ordem correta.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.definir_data_inicial = MagicMock()
        page.clicar_consultar = MagicMock()
        page.selecionar_primeira_nota = MagicMock()
        page.clicar_texto_se_existir = MagicMock(return_value=False)
        page.marcar_item_para_devolucao = MagicMock()
        page.clicar_devolver_itens = MagicMock()
        page.confirmar_dialogos = MagicMock()

        data = "01/01/2024"

        # Act
        page.executar_troca(data)

        # Assert
        page.definir_data_inicial.assert_called_once_with(data)
        page.clicar_consultar.assert_called_once()
        page.selecionar_primeira_nota.assert_called_once()
        page.marcar_item_para_devolucao.assert_called_once()
        page.clicar_devolver_itens.assert_called_once()
        page.confirmar_dialogos.assert_called_once()

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    def test_executar_troca_usa_data_padrao(self, mock_logger, mock_base_init):
        """
        Quando data não é fornecida, deve passar None.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.definir_data_inicial = MagicMock()
        page.clicar_consultar = MagicMock()
        page.selecionar_primeira_nota = MagicMock()
        page.clicar_texto_se_existir = MagicMock(return_value=False)
        page.marcar_item_para_devolucao = MagicMock()
        page.clicar_devolver_itens = MagicMock()
        page.confirmar_dialogos = MagicMock()

        # Act
        page.executar_troca()

        # Assert
        page.definir_data_inicial.assert_called_once_with(None)


class TestTrocaPageFluxoTrocaConsumidor:
    """Testes para o método executar_troca_consumidor."""

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.test_data')
    def test_executar_troca_consumidor_fluxo_completo(self, mock_test_data, mock_logger, mock_base_init):
        """
        Deve executar fluxo completo de troca consumidor.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        mock_test_data.CUSTOMER_ID = "1"
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.definir_data_inicial = MagicMock()
        page.clicar_consultar = MagicMock()
        page.selecionar_primeira_nota = MagicMock()
        page.clicar_texto_se_existir = MagicMock(return_value=False)
        page.selecionar_cliente = MagicMock()
        page.marcar_item_para_devolucao = MagicMock()
        page.clicar_devolver_itens = MagicMock()
        page.confirmar_dialogos = MagicMock()
        page.validar_e_fechar_sucesso = MagicMock()
        page.adicionar_produto = MagicMock()
        page.clicar_avancar = MagicMock()
        page.selecionar_pagamento_bonus = MagicMock()
        page.finalizar_venda = MagicMock()
        page.responder_impressao_nao = MagicMock()

        data = "10/10/2024"
        codigo = "999"

        # Act
        page.executar_troca_consumidor(data, codigo)

        # Assert
        page.definir_data_inicial.assert_called_once_with(data)
        page.clicar_consultar.assert_called_once()
        page.selecionar_primeira_nota.assert_called_once()
        page.marcar_item_para_devolucao.assert_called_once()
        page.clicar_devolver_itens.assert_called_once()
        page.confirmar_dialogos.assert_called_once()
        page.validar_e_fechar_sucesso.assert_called_once()
        page.adicionar_produto.assert_called_once_with(codigo)
        page.clicar_avancar.assert_called_once()
        page.selecionar_pagamento_bonus.assert_called_once()
        page.finalizar_venda.assert_called_once()
        page.responder_impressao_nao.assert_called_once()

    @patch('pages.troca_page.BasePage.__init__', return_value=None)
    @patch('pages.troca_page.logger')
    @patch('pages.troca_page.test_data')
    def test_executar_troca_consumidor_seleciona_cliente_quando_popup_sim(self, mock_test_data, mock_logger, mock_base_init):
        """
        Quando popup SIM aparece, deve selecionar cliente.
        """
        from pages.troca_page import TrocaPage

        # Arrange
        mock_test_data.CUSTOMER_ID = "42"
        page = TrocaPage.__new__(TrocaPage)
        page.driver = MagicMock()
        page.definir_data_inicial = MagicMock()
        page.clicar_consultar = MagicMock()
        page.selecionar_primeira_nota = MagicMock()
        page.clicar_texto_se_existir = MagicMock(return_value=True)  # Popup SIM aparece
        page.selecionar_cliente = MagicMock()
        page.marcar_item_para_devolucao = MagicMock()
        page.clicar_devolver_itens = MagicMock()
        page.confirmar_dialogos = MagicMock()
        page.validar_e_fechar_sucesso = MagicMock()
        page.adicionar_produto = MagicMock()
        page.clicar_avancar = MagicMock()
        page.selecionar_pagamento_bonus = MagicMock()
        page.finalizar_venda = MagicMock()
        page.responder_impressao_nao = MagicMock()

        # Act
        page.executar_troca_consumidor()

        # Assert - deve ter chamado selecionar_cliente
        page.selecionar_cliente.assert_called_once_with("42")
