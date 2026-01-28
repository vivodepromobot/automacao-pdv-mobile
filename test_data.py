"""
Test Data - Dados de teste externalizados.
Permite configurar via variáveis de ambiente ou valores padrão.
"""
import os

# Detecta se está rodando em CI (GitHub Actions)
IS_CI = os.getenv("CI", "false").lower() == "true" or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"


class TestData:
    """Dados de configuração para os testes."""

    # --- Conexão ---
    SERVER_IP = os.getenv("TEST_SERVER_IP", "10.2.3.106")
    SERVER_PORT = os.getenv("TEST_SERVER_PORT", "55101")

    # --- Credenciais ---
    COMPANY = os.getenv("TEST_COMPANY", "382")
    USER = os.getenv("TEST_USER", "SERVER")
    PASSWORD = os.getenv("TEST_PASSWORD", "gabinete")

    # --- Dados de Venda ---
    # CI e Local usam cliente 3 (pode ser alterado independentemente)
    _CUSTOMER_ID_CI = "3"      # Cliente para GitHub Actions
    _CUSTOMER_ID_LOCAL = "3"   # Cliente para execução local
    CUSTOMER_ID = os.getenv("TEST_CUSTOMER_ID", _CUSTOMER_ID_CI if IS_CI else _CUSTOMER_ID_LOCAL)
    PRODUCT_CODE = os.getenv("TEST_PRODUCT_CODE", "123")

    # --- Timeouts ---
    DEFAULT_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
    SHORT_TIMEOUT = int(os.getenv("TEST_SHORT_TIMEOUT", "5"))


# Instância global para uso nos testes
test_data = TestData()
