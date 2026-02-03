"""
Testes unitários para VendaFuturaPage.
Utiliza mocks para evitar interação real com Appium/emulador.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestVendaFuturaPageSelecionarRetiradaLoja:
    """Testes para o método selecionar_retirada_loja."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_selecionar_retirada_loja_rola_e_clica(self, mock_logger, mock_base_init):
        """
        Deve rolar até o botão e clicar.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()

        # Act
        page.selecionar_retirada_loja()

        # Assert
        page.rolar_ate_id.assert_called_once_with(VendaFuturaPage.BTN_VENDA_FUTURA_LOJA)
        page.clicar_por_id.assert_called_once_with(VendaFuturaPage.BTN_VENDA_FUTURA_LOJA)


class TestVendaFuturaPageSelecionarEntregaDomicilio:
    """Testes para o método selecionar_entrega_domicilio."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_selecionar_entrega_domicilio_rola_clica_e_avanca_frete(self, mock_logger, mock_base_init):
        """
        Deve rolar, clicar no botão e avançar frete.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()
        page.rolar_ate_texto = MagicMock()
        page.clicar_por_texto = MagicMock()

        # Act
        page.selecionar_entrega_domicilio()

        # Assert
        page.rolar_ate_id.assert_called_once_with(VendaFuturaPage.BTN_VENDA_FUTURA_DOMICILIO)
        page.clicar_por_id.assert_called_once_with(VendaFuturaPage.BTN_VENDA_FUTURA_DOMICILIO)
        page.rolar_ate_texto.assert_called_once_with("Avançar")
        page.clicar_por_texto.assert_called_once_with("Avançar")


class TestVendaFuturaPageBuscarClienteCpf:
    """Testes para o método buscar_cliente_cpf."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_buscar_cliente_cpf_clica_digita_e_confirma(self, mock_logger, mock_base_init):
        """
        Deve clicar no campo, digitar CPF e confirmar.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.clicar_por_id = MagicMock()
        page.digitar_por_id = MagicMock()

        cpf = "12345678901"

        # Act
        page.buscar_cliente_cpf(cpf)

        # Assert
        page.clicar_por_id.assert_any_call(VendaFuturaPage.EDT_CPF)
        page.digitar_por_id.assert_called_once_with(VendaFuturaPage.EDT_CPF, cpf)
        page.clicar_por_id.assert_any_call(VendaFuturaPage.BTN_CONFIRMAR_CPF)

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_buscar_cliente_cpf_usa_valor_padrao(self, mock_logger, mock_base_init):
        """
        Deve usar CPF padrão '1' quando não especificado.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.clicar_por_id = MagicMock()
        page.digitar_por_id = MagicMock()

        # Act
        page.buscar_cliente_cpf()

        # Assert
        page.digitar_por_id.assert_called_once_with(VendaFuturaPage.EDT_CPF, "1")


class TestVendaFuturaPageAdicionarProduto:
    """Testes para o método adicionar_produto."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_adicionar_produto_com_tamanho(self, mock_logger, mock_base_init):
        """
        Deve adicionar produto e selecionar tamanho.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()
        page.digitar_por_id = MagicMock()
        page.rolar_ate_texto = MagicMock()
        page.clicar_por_texto = MagicMock()

        codigo = "456"
        tamanho = "38"

        # Act
        page.adicionar_produto(codigo, tamanho)

        # Assert
        page.rolar_ate_id.assert_any_call(VendaFuturaPage.BTN_ADICIONAR_PRODUTOS)
        page.clicar_por_id.assert_any_call(VendaFuturaPage.BTN_ADICIONAR_PRODUTOS)
        page.digitar_por_id.assert_called_once_with(VendaFuturaPage.EDT_BUSCA_PRODUTO, codigo)
        page.clicar_por_id.assert_any_call(VendaFuturaPage.IMG_PRODUTO)
        page.rolar_ate_texto.assert_called_once_with(tamanho)
        page.clicar_por_texto.assert_called_once_with(tamanho)


class TestVendaFuturaPageSelecionarPagamentoAvista:
    """Testes para o método selecionar_pagamento_avista."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    @patch('pages.venda_futura_page.time')
    def test_selecionar_pagamento_avista_seleciona_movimento_e_plano(self, mock_time, mock_logger, mock_base_init):
        """
        Deve selecionar movimento e plano A VISTA.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page._app_package = "com.test.app"

        mock_elemento1 = MagicMock()
        mock_elemento2 = MagicMock()

        # Primeira chamada retorna 1 elemento, segunda retorna 2
        page.driver.find_elements.side_effect = [
            [mock_elemento1],
            [mock_elemento1, mock_elemento2]
        ]

        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()

        # Act
        page.selecionar_pagamento_avista()

        # Assert
        mock_elemento1.click.assert_called()  # Movimento A VISTA
        mock_elemento2.click.assert_called_once()  # Plano A Vista
        page.clicar_por_id.assert_any_call(VendaFuturaPage.BTN_AVANCAR)


class TestVendaFuturaPageTratarPopupBonus:
    """Testes para o método tratar_popup_bonus."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    @patch('pages.venda_futura_page.time')
    def test_tratar_popup_bonus_clica_quando_existe(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o popup existe, deve clicar em 'Mais tarde'.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.clicar_se_existir = MagicMock(return_value=True)

        # Act
        page.tratar_popup_bonus()

        # Assert
        page.clicar_se_existir.assert_called_once_with(VendaFuturaPage.BTN_MAIS_TARDE, tempo_espera=2)

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    @patch('pages.venda_futura_page.time')
    def test_tratar_popup_bonus_ignora_quando_nao_existe(self, mock_time, mock_logger, mock_base_init):
        """
        Quando o popup não existe, deve apenas logar.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.clicar_se_existir = MagicMock(return_value=False)

        # Act - não deve lançar exceção
        page.tratar_popup_bonus()

        # Assert
        page.clicar_se_existir.assert_called_once()


class TestVendaFuturaPageSelecionarFormaDinheiro:
    """Testes para o método selecionar_forma_dinheiro."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_selecionar_forma_dinheiro_rola_e_clica(self, mock_logger, mock_base_init):
        """
        Deve selecionar forma DINHEIRO e clicar em Pagar.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.rolar_ate_id = MagicMock()
        page.clicar_por_id = MagicMock()
        page.rolar_ate_texto = MagicMock()
        page.clicar_por_texto = MagicMock()

        # Act
        page.selecionar_forma_dinheiro()

        # Assert
        page.rolar_ate_id.assert_any_call(VendaFuturaPage.IMG_PAGAMENTOS)
        page.clicar_por_id.assert_any_call(VendaFuturaPage.IMG_PAGAMENTOS)
        page.rolar_ate_texto.assert_called_once_with("DINHEIRO")
        page.clicar_por_texto.assert_called_once_with("DINHEIRO")
        page.clicar_por_id.assert_any_call(VendaFuturaPage.BTN_PAGAR)


class TestVendaFuturaPageValidacoes:
    """Testes para métodos de validação."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_venda_sucesso_exibida_retorna_true(self, mock_logger, mock_base_init):
        """
        Deve retornar True quando mensagem de sucesso está visível.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.texto_exibido = MagicMock(return_value=True)

        # Act
        resultado = page.venda_sucesso_exibida(timeout=10)

        # Assert
        assert resultado is True
        page.texto_exibido.assert_called_once_with("Venda realizada com sucesso!", 10)

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_validar_sucesso_e_concluir(self, mock_logger, mock_base_init):
        """
        Deve aguardar texto e chamar concluir_venda.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.aguardar_texto = MagicMock()
        page.concluir_venda = MagicMock()

        # Act
        page.validar_sucesso_e_concluir()

        # Assert
        page.aguardar_texto.assert_called_once_with("Venda realizada com sucesso!")
        page.concluir_venda.assert_called_once()


class TestVendaFuturaPageFluxoRetiradaLoja:
    """Testes para o método executar_venda_futura."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_executar_venda_futura_chama_metodos_na_ordem(self, mock_logger, mock_base_init):
        """
        Deve chamar todos os métodos do fluxo na ordem correta.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.selecionar_retirada_loja = MagicMock()
        page.avancar_tipo_entrega = MagicMock()
        page.selecionar_vendedor = MagicMock()
        page.buscar_cliente_cpf = MagicMock()
        page.adicionar_produto = MagicMock()
        page.clicar_avancar = MagicMock()
        page.selecionar_pagamento_avista = MagicMock()
        page.tratar_popup_bonus = MagicMock()
        page.selecionar_forma_dinheiro = MagicMock()
        page.finalizar_venda = MagicMock()
        page.responder_impressao = MagicMock()

        cpf = "98765"
        codigo = "111"
        tamanho = "40"

        # Act
        page.executar_venda_futura(cpf, codigo, tamanho)

        # Assert
        page.selecionar_retirada_loja.assert_called_once()
        page.avancar_tipo_entrega.assert_called_once()
        page.selecionar_vendedor.assert_called_once()
        page.buscar_cliente_cpf.assert_called_once_with(cpf)
        page.adicionar_produto.assert_called_once_with(codigo, tamanho)
        page.clicar_avancar.assert_called_once()
        page.selecionar_pagamento_avista.assert_called_once()
        page.tratar_popup_bonus.assert_called_once()
        page.selecionar_forma_dinheiro.assert_called_once()
        page.finalizar_venda.assert_called_once()
        page.responder_impressao.assert_called_once_with(imprimir=False)


class TestVendaFuturaPageFluxoDomicilio:
    """Testes para o método executar_venda_futura_domicilio."""

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_executar_venda_futura_domicilio_chama_metodos_na_ordem(self, mock_logger, mock_base_init):
        """
        Deve chamar todos os métodos do fluxo domicílio na ordem correta.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.selecionar_entrega_domicilio = MagicMock()
        page.selecionar_vendedor = MagicMock()
        page.buscar_cliente_cpf = MagicMock()
        page.adicionar_produto = MagicMock()
        page.clicar_avancar = MagicMock()
        page.selecionar_pagamento_avista = MagicMock()
        page.tratar_popup_bonus = MagicMock()
        page.selecionar_forma_dinheiro = MagicMock()
        page.finalizar_venda = MagicMock()
        page.responder_impressao = MagicMock()

        cpf = "12345"
        codigo = "222"
        tamanho = "42"

        # Act
        page.executar_venda_futura_domicilio(cpf, codigo, tamanho)

        # Assert
        page.selecionar_entrega_domicilio.assert_called_once()
        page.selecionar_vendedor.assert_called_once()
        page.buscar_cliente_cpf.assert_called_once_with(cpf)
        page.adicionar_produto.assert_called_once_with(codigo, tamanho)
        page.clicar_avancar.assert_called_once()
        page.selecionar_pagamento_avista.assert_called_once()
        page.tratar_popup_bonus.assert_called_once()
        page.selecionar_forma_dinheiro.assert_called_once()
        page.finalizar_venda.assert_called_once()
        page.responder_impressao.assert_called_once_with(imprimir=False)

    @patch('pages.venda_futura_page.BasePage.__init__', return_value=None)
    @patch('pages.venda_futura_page.logger')
    def test_executar_venda_futura_domicilio_usa_valores_padrao(self, mock_logger, mock_base_init):
        """
        Deve usar valores padrão quando não especificados.
        """
        from pages.venda_futura_page import VendaFuturaPage

        # Arrange
        page = VendaFuturaPage.__new__(VendaFuturaPage)
        page.driver = MagicMock()
        page.selecionar_entrega_domicilio = MagicMock()
        page.selecionar_vendedor = MagicMock()
        page.buscar_cliente_cpf = MagicMock()
        page.adicionar_produto = MagicMock()
        page.clicar_avancar = MagicMock()
        page.selecionar_pagamento_avista = MagicMock()
        page.tratar_popup_bonus = MagicMock()
        page.selecionar_forma_dinheiro = MagicMock()
        page.finalizar_venda = MagicMock()
        page.responder_impressao = MagicMock()

        # Act
        page.executar_venda_futura_domicilio()

        # Assert - verifica valores padrão
        page.buscar_cliente_cpf.assert_called_once_with("1")
        page.adicionar_produto.assert_called_once_with("123", "36")
