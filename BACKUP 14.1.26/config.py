import subprocess
from pathlib import Path
from appium.options.android import UiAutomator2Options

def get_connected_device_udid():
    print("-> Procurando por dispositivos Android conectados...")
    try:
        resultado = subprocess.check_output(['adb', 'devices'], text=True)
        linhas = resultado.strip().split('\n')
        dispositivos = [l.split('\t')[0] for l in linhas[1:] if l.strip() and l.split('\t')[1] == 'device']
        if len(dispositivos) == 1:
            print(f"   [✅ SUCESSO!] Dispositivo encontrado: {dispositivos[0]}")
            return dispositivos[0]
        elif len(dispositivos) == 0:
            raise RuntimeError("ERRO: Nenhum dispositivo Android foi encontrado.")
        else:
            raise RuntimeError(f"ERRO: Mais de um dispositivo conectado: {dispositivos}.")
    except FileNotFoundError:
        raise RuntimeError("ERRO: O comando 'adb' não foi encontrado. Verifique se o Android SDK está no PATH do sistema.")
    except Exception as e:
        raise RuntimeError(f"Falha ao detectar dispositivo: {e}")

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
    }
} 

def discover_target_app():
    print("-> Procurando por aplicativos de teste instalados no dispositivo...")
    try:
        resultado = subprocess.check_output(['adb', 'shell', 'pm', 'list', 'packages'], text=True)
        pacotes_instalados = [p.replace('package:', '') for p in resultado.strip().split('\n')]
        pacotes_conhecidos = [env_info for flavor_info in APP_TARGETS.values() for env_info in flavor_info.values()]
        apps_encontrados = [app_info for app_info in pacotes_conhecidos if app_info["package"] in pacotes_instalados]
        
        if len(apps_encontrados) == 1:
            app_encontrado = apps_encontrados[0]
            print(f"   [✅ SUCESSO!] App alvo detectado: {app_encontrado['package']}")
            return app_encontrado["package"], app_encontrado["activity"]
        elif len(apps_encontrados) == 0:
            raise RuntimeError("ERRO: Nenhum dos apps cadastrados em APP_TARGETS foi encontrado no dispositivo.")
        else:
            raise RuntimeError(f"ERRO: Múltiplos apps de teste encontrados: {[app['package'] for app in apps_encontrados]}. Desinstale os desnecessários.")
    except Exception as e:
        raise RuntimeError(f"Falha ao detectar o app alvo: {e}")

LOGS_DIR = Path("logs")
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"
REPORTS_DIR = LOGS_DIR / "reports"
APPIUM_SERVER_URL = "http://127.0.0.1:4723"
DEFAULT_WAIT = 30
RETRY_ATTEMPTS = 2

try:
    DEVICE_NAME = get_connected_device_udid()
    APP_PACKAGE, APP_ACTIVITY = discover_target_app()
except RuntimeError as e:
    print(f"\n[!!!] ERRO DE INICIALIZAÇÃO [!!!]\n{e}\n")
    exit(1)

def get_appium_options(limpar_dados_app: bool = False):
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = DEVICE_NAME
    options.app_package = APP_PACKAGE
    options.no_reset = not limpar_dados_app
    options.auto_grant_permissions = True
    options.set_capability("appWaitActivity", "*")
    options.set_capability("forceAppLaunch", True)
    return options