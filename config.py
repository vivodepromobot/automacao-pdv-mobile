import subprocess
import sys
import logging
from pathlib import Path
from appium.options.android import UiAutomator2Options

# Fix encoding para Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Diretórios
LOGS_DIR = Path("logs")
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"
REPORTS_DIR = LOGS_DIR / "reports"

# Cria diretórios se não existirem
LOGS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Logger configurado - pytest cuida do console (log_cli), nos so salvamos em arquivo
logger = logging.getLogger("appium_test")
logger.setLevel(logging.INFO)

# Handler para arquivo (console é gerenciado pelo pytest log_cli)
from datetime import datetime
log_filename = LOGS_DIR / f"teste_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))

# Adiciona handler (evita duplicação)
if not logger.handlers:
    logger.addHandler(file_handler)
    # Propaga para pytest capturar e mostrar no console com cores
    logger.propagate = True

def get_connected_device_udid(permitir_multiplos: bool = False):
    """
    Detecta dispositivos Android conectados.

    Args:
        permitir_multiplos: Se True, retorna o primeiro dispositivo mesmo com multiplos conectados.
    """
    print("-> Procurando por dispositivos Android conectados...")
    try:
        resultado = subprocess.check_output(['adb', 'devices'], text=True)
        linhas = resultado.strip().split('\n')
        dispositivos = [l.split('\t')[0] for l in linhas[1:] if l.strip() and '\tdevice' in l]

        if len(dispositivos) == 0:
            raise RuntimeError("ERRO: Nenhum dispositivo Android foi encontrado.")
        elif len(dispositivos) == 1:
            print(f"   [OK] Dispositivo encontrado: {dispositivos[0]}")
            return dispositivos[0]
        else:
            # Multiplos dispositivos
            if permitir_multiplos:
                print(f"   [OK] {len(dispositivos)} dispositivos encontrados. Usando: {dispositivos[0]}")
                return dispositivos[0]
            else:
                print(f"   [INFO] {len(dispositivos)} dispositivos conectados: {dispositivos}")
                print(f"   [INFO] Use --device-id para especificar ou parallel_runner.py para paralelo")
                return dispositivos[0]  # Retorna primeiro por padrao

    except FileNotFoundError:
        raise RuntimeError("ERRO: O comando 'adb' nao foi encontrado. Verifique se o Android SDK esta no PATH do sistema.")
    except Exception as e:
        raise RuntimeError(f"Falha ao detectar dispositivo: {e}")


def get_all_connected_devices():
    """Retorna lista de todos os dispositivos conectados."""
    try:
        resultado = subprocess.check_output(['adb', 'devices'], text=True)
        linhas = resultado.strip().split('\n')
        dispositivos = [l.split('\t')[0] for l in linhas[1:] if l.strip() and '\tdevice' in l]
        return dispositivos
    except:
        return []

APP_TARGETS = {
    "REDEL400": {
        "QA":   {"package": "com.serverinfo.bshoppdv.redel400.qa", "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"},
        "PROD": {"package": "com.serverinfo.bshoppdv.redel400",    "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"}
    },
    "CieloDX800": {
        "QA":   {"package": "com.serverinfo.bshoppdv.cielostore.qa", "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"},
        "PROD": {"package": "com.serverinfo.bshoppdv.cielostore",    "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"}
    },
    "Stone": {
        "QA":   {"package": "com.serverinfo.bshoppdv.stone.qa", "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"},
        "PROD": {"package": "com.serverinfo.bshoppdv.stone",    "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"}
    },
    "Playstore": {
        "QA":   {"package": "com.serverinfo.bshoppdv.playstore.qa", "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"},
        "PROD": {"package": "com.serverinfo.bshoppdv.playstore",    "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"}
    },"Pagseguro": {
        "QA":   {"package": "com.serverinfo.bshoppdv.pagseguro.qa", "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"},
        "PROD": {"package": "com.serverinfo.bshoppdv.pagseguro",    "activity": "com.serverinfo.bshoppdv.activities.LoginPDVActivity"}
    }
} 

def discover_target_app(device_id: str = None):
    """
    Detecta o app alvo instalado no dispositivo.

    Args:
        device_id: ID do dispositivo. Se None, usa o primeiro disponivel.
    """
    print(f"-> Procurando por aplicativos de teste no dispositivo {device_id or 'padrao'}...")
    try:
        # Monta comando adb com ou sem device_id
        if device_id:
            cmd = ['adb', '-s', device_id, 'shell', 'pm', 'list', 'packages']
        else:
            cmd = ['adb', 'shell', 'pm', 'list', 'packages']

        resultado = subprocess.check_output(cmd, text=True, timeout=30)
        pacotes_instalados = [p.replace('package:', '') for p in resultado.strip().split('\n')]
        pacotes_conhecidos = [env_info for flavor_info in APP_TARGETS.values() for env_info in flavor_info.values()]
        apps_encontrados = [app_info for app_info in pacotes_conhecidos if app_info["package"] in pacotes_instalados]

        if len(apps_encontrados) == 1:
            app_encontrado = apps_encontrados[0]
            print(f"   [OK] App alvo detectado: {app_encontrado['package']}")
            return app_encontrado["package"], app_encontrado["activity"]
        elif len(apps_encontrados) == 0:
            raise RuntimeError("ERRO: Nenhum dos apps cadastrados em APP_TARGETS foi encontrado no dispositivo.")
        else:
            # Com multiplos apps, usa o primeiro (QA tem prioridade)
            app_encontrado = apps_encontrados[0]
            print(f"   [INFO] Multiplos apps encontrados. Usando: {app_encontrado['package']}")
            return app_encontrado["package"], app_encontrado["activity"]
    except subprocess.TimeoutExpired:
        raise RuntimeError("ERRO: Timeout ao listar pacotes do dispositivo.")
    except Exception as e:
        raise RuntimeError(f"Falha ao detectar o app alvo: {e}")

APPIUM_SERVER_URL = "http://127.0.0.1:4723"
DEFAULT_WAIT = 30
RETRY_ATTEMPTS = 2

# Inicializacao - detecta devices conectados
# Quando ha multiplos devices, nao tenta detectar app automaticamente
# O app sera detectado em get_appium_options() com device_id especifico
try:
    dispositivos = get_all_connected_devices()
    if len(dispositivos) == 1:
        DEVICE_NAME = dispositivos[0]
        APP_PACKAGE, APP_ACTIVITY = discover_target_app(DEVICE_NAME)
    elif len(dispositivos) > 1:
        # Multiplos devices - nao detecta app aqui, sera feito por device
        print(f"[INFO] {len(dispositivos)} dispositivos conectados - deteccao de app sera por device")
        DEVICE_NAME = dispositivos[0]  # Primeiro como padrao
        APP_PACKAGE = None
        APP_ACTIVITY = None
    else:
        DEVICE_NAME = None
        APP_PACKAGE = None
        APP_ACTIVITY = None
except RuntimeError as e:
    print(f"\n[!!!] ERRO DE INICIALIZACAO [!!!]\n{e}\n")
    DEVICE_NAME = None
    APP_PACKAGE = None
    APP_ACTIVITY = None

def _calcular_porta_unica(device_id: str, base_port: int = 8200) -> int:
    """Calcula uma porta unica baseada no device_id para evitar conflitos."""
    # Usa hash do device_id para gerar um offset (0-99)
    offset = abs(hash(device_id)) % 100
    return base_port + offset


def get_appium_options(limpar_dados_app: bool = False, device_id: str = None):
    """
    Cria opcoes do Appium.

    Args:
        limpar_dados_app: Se True, limpa dados do app antes de iniciar.
        device_id: ID do dispositivo (UDID). Se None, usa o detectado automaticamente.
    """
    # Determina device a usar
    device_para_usar = device_id or DEVICE_NAME

    if not device_para_usar:
        raise RuntimeError("Nenhum dispositivo especificado e nenhum detectado automaticamente")

    # Log qual device sera usado
    print(f"[APPIUM] Configurando sessao para device: {device_para_usar}")

    # Detecta app no dispositivo especifico
    try:
        app_package, app_activity = discover_target_app(device_para_usar)
        print(f"[APPIUM] App detectado: {app_package}")
    except Exception as e:
        print(f"[AVISO] Falha ao detectar app no device {device_para_usar}: {e}")
        if APP_PACKAGE:
            app_package = APP_PACKAGE
            app_activity = APP_ACTIVITY
        else:
            raise RuntimeError(f"Nao foi possivel detectar o app no dispositivo {device_para_usar}")

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"

    # IMPORTANTE: udid DEVE ser definido para garantir device correto com multiplos devices
    options.set_capability("udid", device_para_usar)
    options.device_name = device_para_usar

    # IMPORTANTE: systemPort unico por device para evitar conflitos UiAutomator2
    system_port = _calcular_porta_unica(device_para_usar)
    options.set_capability("systemPort", system_port)
    print(f"[APPIUM] SystemPort para {device_para_usar}: {system_port}")

    options.app_package = app_package
    options.no_reset = not limpar_dados_app
    options.auto_grant_permissions = True
    options.set_capability("appWaitActivity", "*")
    options.set_capability("forceAppLaunch", True)

    # Timeout maior para conexao com device
    options.set_capability("newCommandTimeout", 300)
    options.set_capability("adbExecTimeout", 60000)

    return options