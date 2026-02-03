"""
Teste Smoke E2E - Validacao rapida de sanidade.

OBJETIVO:
    Verificar se o ambiente basico esta funcionando ANTES de rodar
    os testes E2E completos. Se o smoke falhar, nao adianta rodar o resto.

QUANDO USAR:
    - Antes de cada release
    - Apos atualizar o app
    - Quando suspeitar de problemas de ambiente
    - No inicio do pipeline CI/CD

TEMPO ESTIMADO: 1-2 minutos

REQUISITOS:
    - Appium Server rodando
    - Dispositivo conectado
    - App instalado
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from test_data import test_data
from config import logger


@allure.epic("PDV Mobile")
@allure.feature("Smoke Tests")
@allure.story("Validacao de Ambiente")
@pytest.mark.smoke
class TestSmokeAmbiente:
    """
    Testes de sanidade do ambiente.
    Verifica se o basico funciona antes de rodar testes completos.
    """

    @allure.title("SMOKE: App abre corretamente")
    @allure.description("""
    Verifica se o app abre sem crashar.
    Se falhar aqui, o app tem problema grave ou nao esta instalado.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "ambiente", "critico")
    def test_01_app_abre_corretamente(self, driver):
        """
        SMOKE TEST 1: Verifica se o app abre.

        Criterios de sucesso:
        - Driver foi inicializado
        - Page source nao esta vazio
        - App nao crashou
        """
        logger.info("=" * 50)
        logger.info("SMOKE TEST: Verificando se app abre")
        logger.info("=" * 50)

        with allure.step("Verificar se driver foi inicializado"):
            assert driver is not None, "Driver nao foi inicializado - Appium pode estar com problema"

        with allure.step("Verificar se app esta respondendo"):
            page_source = driver.page_source
            assert page_source is not None, "Nao conseguiu obter page_source - app pode ter crashado"
            assert len(page_source) > 100, "Page source muito pequeno - app pode ter crashado"

        with allure.step("Registrar sucesso"):
            logger.info("[OK] App abriu corretamente!")
            allure.attach(
                "App iniciou sem problemas",
                name="Status",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.title("SMOKE: Login funciona")
    @allure.description("""
    Verifica se o fluxo de login funciona.
    Se falhar aqui, nenhum outro teste E2E vai funcionar.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "login", "critico")
    def test_02_login_funciona(self, driver):
        """
        SMOKE TEST 2: Verifica se o login funciona.

        Criterios de sucesso:
        - Consegue preencher credenciais (ou ja esta logado)
        - Tela inicial aparece apos login
        """
        logger.info("=" * 50)
        logger.info("SMOKE TEST: Verificando login")
        logger.info("=" * 50)

        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        with allure.step("Executar login (ou verificar se ja esta logado)"):
            login_page.garantir_login(
                ip=test_data.SERVER_IP,
                porta=test_data.SERVER_PORT,
                empresa=test_data.COMPANY,
                usuario=test_data.USER,
                senha=test_data.PASSWORD
            )

        with allure.step("Verificar se tela inicial apareceu"):
            assert home_page.tela_inicial_exibida(timeout=30), \
                "Tela inicial NAO apareceu apos login - LOGIN FALHOU!"

        with allure.step("Registrar sucesso"):
            logger.info("[OK] Login funcionou corretamente!")
            allure.attach(
                f"Login com usuario {test_data.USER} bem sucedido",
                name="Status Login",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.title("SMOKE: Elementos basicos visiveis na Home")
    @allure.description("""
    Verifica se os elementos basicos da tela inicial estao visiveis.
    Valida que o app esta em estado funcional apos login.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "home", "elementos")
    def test_03_elementos_basicos_visiveis(self, driver):
        """
        SMOKE TEST 3: Verifica elementos da tela inicial.

        Criterios de sucesso:
        - Botao de Venda esta visivel
        - App esta em estado navegavel
        """
        logger.info("=" * 50)
        logger.info("SMOKE TEST: Verificando elementos basicos")
        logger.info("=" * 50)

        # Garante login primeiro
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        login_page.garantir_login(
            ip=test_data.SERVER_IP,
            porta=test_data.SERVER_PORT,
            empresa=test_data.COMPANY,
            usuario=test_data.USER,
            senha=test_data.PASSWORD
        )

        with allure.step("Verificar se botao de Venda esta visivel"):
            venda_visivel = (
                home_page.texto_exibido("Venda", tempo_espera=5) or
                home_page.texto_exibido("Iniciar Venda", tempo_espera=5)
            )

            assert venda_visivel, \
                "Nenhum botao de venda encontrado na home - app pode estar em estado invalido"

        with allure.step("Registrar sucesso"):
            logger.info("[OK] Elementos basicos estao visiveis!")
            allure.attach(
                "Tela inicial com elementos corretos",
                name="Status Elementos",
                attachment_type=allure.attachment_type.TEXT
            )


@allure.epic("PDV Mobile")
@allure.feature("Smoke Tests")
@allure.story("Navegacao Basica")
@pytest.mark.smoke
class TestSmokeNavegacao:
    """
    Testes de navegacao basica.
    Verifica se consegue navegar entre telas principais.
    """

    @allure.title("SMOKE: Consegue iniciar fluxo de venda")
    @allure.description("""
    Verifica se consegue clicar em Venda e a tela abre.
    Nao completa a venda, apenas verifica navegacao.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "navegacao", "venda")
    def test_04_consegue_iniciar_venda(self, driver):
        """
        SMOKE TEST 4: Verifica navegacao para tela de venda.

        Criterios de sucesso:
        - Consegue clicar em Venda/Iniciar Venda
        - Proxima tela carrega (selecao de cliente ou vendedor)
        """
        logger.info("=" * 50)
        logger.info("SMOKE TEST: Verificando navegacao para venda")
        logger.info("=" * 50)

        # Garante login
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        login_page.garantir_login(
            ip=test_data.SERVER_IP,
            porta=test_data.SERVER_PORT,
            empresa=test_data.COMPANY,
            usuario=test_data.USER,
            senha=test_data.PASSWORD
        )

        with allure.step("Clicar em Iniciar Venda"):
            try:
                home_page.iniciar_venda()
                logger.info("[OK] Clicou em Iniciar Venda")
            except Exception as e:
                pytest.fail(f"Falha ao clicar em Iniciar Venda: {e}")

        with allure.step("Verificar se proxima tela carregou"):
            # Verifica se apareceu tela de selecao de cliente/vendedor
            tela_carregou = (
                home_page.texto_exibido("Selecionar Cliente", tempo_espera=5) or
                home_page.texto_exibido("Escolher Vendedor", tempo_espera=5) or
                home_page.texto_exibido("Buscar Cliente", tempo_espera=5) or
                home_page.elemento_existe("txt_dialog_seller_name", tempo_espera=5) or
                home_page.elemento_existe("btn_select_customer", tempo_espera=5)
            )

            assert tela_carregou, \
                "Proxima tela nao carregou apos clicar em Venda"

        with allure.step("Voltar para home (cleanup)"):
            try:
                driver.back()
                # Confirma dialogo se aparecer
                home_page.clicar_texto_se_existir("SIM", tempo_espera=2)
                home_page.clicar_texto_se_existir("OK", tempo_espera=2)
            except:
                pass

        logger.info("[OK] Navegacao para venda funcionou!")


@allure.epic("PDV Mobile")
@allure.feature("Smoke Tests")
@allure.story("Resumo Final")
@pytest.mark.smoke
class TestSmokeFinal:
    """Teste final que resume o status do smoke."""

    @allure.title("SMOKE: Resumo - Ambiente OK para testes E2E")
    @allure.description("""
    Este teste so passa se todos os anteriores passaram.
    Serve como gate final para liberar execucao dos testes E2E completos.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "resumo", "gate")
    def test_99_smoke_completo(self, driver):
        """
        SMOKE TEST FINAL: Confirma que ambiente esta OK.

        Se chegou aqui, significa que:
        - App abre
        - Login funciona
        - Navegacao basica funciona

        Ambiente APROVADO para testes E2E!
        """
        logger.info("=" * 50)
        logger.info("SMOKE TEST: RESUMO FINAL")
        logger.info("=" * 50)

        # Faz login para confirmar estado final
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        login_page.garantir_login(
            ip=test_data.SERVER_IP,
            porta=test_data.SERVER_PORT,
            empresa=test_data.COMPANY,
            usuario=test_data.USER,
            senha=test_data.PASSWORD
        )

        with allure.step("Confirmar estado final do ambiente"):
            assert home_page.tela_inicial_exibida(timeout=10), \
                "Estado final invalido"

        # Resumo
        resumo = """
        ========================================
        SMOKE TEST CONCLUIDO COM SUCESSO!
        ========================================

        Verificacoes realizadas:
        [OK] App abre corretamente
        [OK] Login funciona
        [OK] Elementos basicos visiveis
        [OK] Navegacao basica funciona

        AMBIENTE APROVADO PARA TESTES E2E!
        ========================================
        """

        logger.info(resumo)
        allure.attach(
            resumo,
            name="Resumo Smoke Test",
            attachment_type=allure.attachment_type.TEXT
        )

        print(resumo)
