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
    # CI usa cliente 1, Local usa cliente 3
    CUSTOMER_ID = os.getenv("TEST_CUSTOMER_ID", "1" if IS_CI else "3")
    PRODUCT_CODE = os.getenv("TEST_PRODUCT_CODE", "123")

    # --- Timeouts ---
    DEFAULT_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
    SHORT_TIMEOUT = int(os.getenv("TEST_SHORT_TIMEOUT", "5"))


# Instância global para uso nos testes
test_data = TestData()
