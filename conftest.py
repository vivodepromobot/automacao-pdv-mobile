"""
Conftest - Fixtures compartilhadas para pytest.
Suporta execucao em multiplos dispositivos.
Configuracao avancada do Allure para relatorios detalhados.
"""
import pytest
import allure
import os
import json
from datetime import datetime
from pathlib import Path
from appium import webdriver

from config import (
    APPIUM_SERVER_URL,
    get_appium_options,
    SCREENSHOTS_DIR,
    APP_PACKAGE,
    logger
)
from pages.login_page import LoginPage
from pages.home_page import HomePage
from test_data import test_data


# Diretorio para resultados Allure
ALLURE_RESULTS_DIR = Path(__file__).parent / "allure-results"


# --- Opcoes de linha de comando para multiplos dispositivos ---
def pytest_addoption(parser):
    """Adiciona opcoes de linha de comando."""
    parser.addoption(
        "--device-id",
        action="store",
        default=None,
        help="ID do dispositivo (UDID) para rodar os testes"
    )
    parser.addoption(
        "--appium-port",
        action="store",
        default=4723,
        type=int,
        help="Porta do servidor Appium (default: 4723)"
    )


# --- Ordem dos testes (dependencias de dados) ---
# Troca precisa de venda IMEDIATAMENTE antes para pegar a nota certa
# A primeira nota da lista eh sempre a mais recente
ORDEM_TESTES = [
    # 1. Login primeiro
    "test_login_sucesso",
    "test_login_falha_senha_invalida",
    # 2. Venda Consumidor -> Troca Consumidor (em sequencia)
    "test_venda_consumidor_sucesso",
    "test_troca_consumidor_sucesso",
    # 3. Venda Cliente -> Troca Cliente (em sequencia)
    "test_venda_cliente_sucesso",
    "test_troca_cliente_sucesso",
    # 4. Outros testes
    "test_pedido_venda_sucesso",
]


def pytest_collection_modifyitems(session, config, items):
    """
    Hook para ordenar os testes baseado na lista ORDEM_TESTES.
    Testes nao listados rodam por ultimo na ordem original.
    """
    def obter_ordem(item):
        nome = item.name
        try:
            return ORDEM_TESTES.index(nome)
        except ValueError:
            # Teste nao esta na lista, vai pro final
            return len(ORDEM_TESTES) + 1

    items.sort(key=obter_ordem)

    # Log da ordem final
    logger.info("=" * 50)
    logger.info("ORDEM DE EXECUCAO DOS TESTES:")
    for i, item in enumerate(items, 1):
        logger.info(f"  {i}. {item.name}")
    logger.info("=" * 50)


# --- Hooks pytest ---
def pytest_configure(config):
    """Configurações iniciais do pytest."""
    # Cria diretórios necessários
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Cria arquivo de ambiente para o Allure
    _criar_ambiente_allure(config)


def _criar_ambiente_allure(config):
    """Cria arquivo environment.properties para o Allure."""
    try:
        import subprocess
        import platform

        # Obtém informações do dispositivo
        device_id = config.getoption("--device-id", default=None)
        appium_port = config.getoption("--appium-port", default=4723)

        # Informações do sistema
        env_info = {
            "Sistema Operacional": platform.system(),
            "Python": platform.python_version(),
            "App Package": APP_PACKAGE,
            "Servidor Appium": f"http://127.0.0.1:{appium_port}",
            "Device ID": device_id or "auto-detectar",
            "Data Execucao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Tenta obter info do dispositivo via ADB
        try:
            if device_id:
                cmd = ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model']
            else:
                cmd = ['adb', 'shell', 'getprop', 'ro.product.model']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                env_info["Modelo Dispositivo"] = result.stdout.strip()
        except:
            pass

        try:
            if device_id:
                cmd = ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release']
            else:
                cmd = ['adb', 'shell', 'getprop', 'ro.build.version.release']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                env_info["Android Version"] = result.stdout.strip()
        except:
            pass

        # Escreve arquivo environment.properties
        env_file = ALLURE_RESULTS_DIR / "environment.properties"
        with open(env_file, "w", encoding="utf-8") as f:
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")

        # Escreve arquivo categories.json para categorizar falhas
        categories = [
            {
                "name": "Falhas de Elemento",
                "matchedStatuses": ["failed"],
                "messageRegex": ".*nao encontrado.*|.*TimeoutException.*|.*NoSuchElementException.*"
            },
            {
                "name": "Falhas de Assertiva",
                "matchedStatuses": ["failed"],
                "messageRegex": ".*AssertionError.*|.*assert.*"
            },
            {
                "name": "Falhas de Conexao",
                "matchedStatuses": ["failed"],
                "messageRegex": ".*Connection.*|.*WebDriverException.*"
            },
            {
                "name": "Testes Ignorados",
                "matchedStatuses": ["skipped"]
            }
        ]
        categories_file = ALLURE_RESULTS_DIR / "categories.json"
        with open(categories_file, "w", encoding="utf-8") as f:
            json.dump(categories, f, indent=2)

    except Exception as e:
        logger.warning(f"Erro ao criar ambiente Allure: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook para capturar screenshots e logs em falhas."""
    outcome = yield
    report = outcome.get_result()

    # Captura screenshot em falhas durante execucao do teste
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("driver_logado")
        if driver:
            try:
                # Screenshot
                screenshot_name = f"FALHA_{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_path = SCREENSHOTS_DIR / screenshot_name
                driver.get_screenshot_as_file(str(screenshot_path))

                allure.attach.file(
                    str(screenshot_path),
                    name="Screenshot da Falha",
                    attachment_type=allure.attachment_type.PNG
                )
                logger.error(f"Screenshot salvo: {screenshot_path}")

                # Page Source (XML da tela)
                try:
                    page_source = driver.page_source
                    allure.attach(
                        page_source,
                        name="Page Source (XML)",
                        attachment_type=allure.attachment_type.XML
                    )
                except:
                    pass

            except Exception as e:
                logger.warning(f"Falha ao capturar screenshot: {e}")


# --- Fixtures ---
@pytest.fixture(scope="function")
def driver(request):
    """
    Fixture principal - Cria e gerencia o driver Appium.
    Suporta multiplos dispositivos via parametros de linha de comando.

    Uso:
        def test_exemplo(driver):
            driver.find_element(...)

    Linha de comando:
        pytest --device-id=XXXXX --appium-port=4723
    """
    # Parametros de linha de comando
    device_id = request.config.getoption("--device-id")
    appium_port = request.config.getoption("--appium-port")

    # Verifica se teste quer limpar dados do app
    param = getattr(request, "param", None)
    if isinstance(param, dict):
        limpar_dados = param.get("limpar_dados", False)
    else:
        limpar_dados = False

    logger.info("=" * 50)
    logger.info(f"INICIANDO TESTE: {request.node.name}")
    logger.info(f"Dispositivo: {device_id or 'auto-detectar'}")
    logger.info(f"Porta Appium: {appium_port}")
    logger.info(f"Limpar dados do app: {limpar_dados}")
    logger.info("=" * 50)

    # Monta URL do Appium
    appium_url = f"http://127.0.0.1:{appium_port}"

    # Obtem options com device_id especifico se fornecido
    options = get_appium_options(limpar_dados_app=limpar_dados, device_id=device_id)
    drv = webdriver.Remote(command_executor=appium_url, options=options)

    yield drv

    logger.info("Encerrando driver...")
    drv.quit()


@pytest.fixture(scope="function")
def driver_logado(driver):
    """
    Fixture que garante que o usuario esta logado.

    Uso:
        def test_venda(driver_logado):
            # Ja esta logado, pode comecar o teste
    """
    login_page = LoginPage(driver)
    home_page = HomePage(driver)

    # Usa garantir_login que lida com app ja configurado
    login_page.garantir_login(
        ip=test_data.SERVER_IP,
        porta=test_data.SERVER_PORT,
        empresa=test_data.COMPANY,
        usuario=test_data.USER,
        senha=test_data.PASSWORD
    )

    # Aguarda tela inicial carregar
    assert home_page.tela_inicial_exibida(timeout=30), "Falha ao fazer login"

    logger.info("Usuario logado com sucesso.")
    return driver


@pytest.fixture
def pagina_login(driver):
    """Fixture para LoginPage."""
    return LoginPage(driver)


@pytest.fixture
def pagina_inicial(driver):
    """Fixture para HomePage."""
    return HomePage(driver)
