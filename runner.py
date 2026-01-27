#!/usr/bin/env python
"""
Runner - CLI profissional para executar testes Appium.

Uso:
    python runner.py                    # Menu interativo
    python runner.py --list             # Lista testes disponíveis
    python runner.py --test login       # Roda teste específico
    python runner.py --all              # Roda todos os testes
    python runner.py --test troca --allure  # Com relatório Allure
"""
import os
import sys
import time
import argparse
import subprocess
import socket
from pathlib import Path
from datetime import datetime

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


# Configurações
APPIUM_PORT = 4723
APPIUM_CMD = r"D:\nvm\v22.19.0\appium.cmd"
PROJECT_DIR = Path(__file__).parent
ALLURE_RESULTS_DIR = PROJECT_DIR / "allure-results"
ALLURE_REPORT_DIR = PROJECT_DIR / "allure-report"


def print_banner():
    """Exibe banner do sistema."""
    banner = f"""
{Colors.CYAN}+================================================================+
|                                                                |
|   {Colors.BOLD}AUTOMACAO DE TESTES - PDV MOBILE{Colors.RESET}{Colors.CYAN}                          |
|                                                                |
|   Framework: Pytest + Appium + Allure                          |
|   Versao: 2.0.0                                                |
|                                                                |
+================================================================+{Colors.RESET}
"""
    print(banner)


def is_port_open(port: int) -> bool:
    """Verifica se porta está em uso (Appium rodando)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0
    finally:
        sock.close()


def start_appium_server() -> subprocess.Popen:
    """Inicia servidor Appium em background."""
    if is_port_open(APPIUM_PORT):
        print(f"{Colors.GREEN}✓ Servidor Appium já está rodando na porta {APPIUM_PORT}{Colors.RESET}")
        return None

    print(f"{Colors.YELLOW}⏳ Iniciando servidor Appium...{Colors.RESET}")

    # Verifica se Appium está instalado
    if not Path(APPIUM_CMD).exists():
        print(f"{Colors.RED}✗ Appium não encontrado em: {APPIUM_CMD}{Colors.RESET}")
        print(f"  Execute: npm install -g appium")
        sys.exit(1)

    # Inicia Appium em background
    process = subprocess.Popen(
        [APPIUM_CMD],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )

    # Aguarda servidor iniciar
    for i in range(30):
        if is_port_open(APPIUM_PORT):
            print(f"{Colors.GREEN}✓ Servidor Appium iniciado com sucesso!{Colors.RESET}")
            return process
        time.sleep(1)
        print(f"  Aguardando... ({i+1}s)", end='\r')

    print(f"\n{Colors.RED}✗ Timeout ao iniciar Appium{Colors.RESET}")
    process.kill()
    sys.exit(1)


def check_device() -> bool:
    """Verifica se há dispositivo Android conectado."""
    try:
        result = subprocess.run(
            ['adb', 'devices'],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.strip().split('\n')[1:]
        devices = [l for l in lines if l.strip() and 'device' in l]

        if not devices:
            print(f"{Colors.RED}✗ Nenhum dispositivo Android conectado{Colors.RESET}")
            print(f"  Conecte um dispositivo ou inicie um emulador")
            return False

        print(f"{Colors.GREEN}✓ Dispositivo encontrado: {devices[0].split()[0]}{Colors.RESET}")
        return True

    except Exception as e:
        print(f"{Colors.RED}✗ Erro ao verificar dispositivos: {e}{Colors.RESET}")
        return False


def get_available_tests() -> dict:
    """Retorna dicionário de testes disponíveis."""
    tests_dir = PROJECT_DIR / "tests"
    tests = {}

    # Testes pytest (novos)
    for test_file in tests_dir.glob("test_*.py"):
        name = test_file.stem.replace("test_", "")
        tests[name] = {
            "file": str(test_file),
            "type": "pytest",
            "description": f"Teste de {name.replace('_', ' ').title()}"
        }

    # Testes legados (scripts antigos)
    legacy_tests = {
        "login_legacy": ("login.py", "Login (script legado)"),
        "venda_consumidor": ("vendaConsumidor.py", "Venda Consumidor (script legado)"),
        "venda_cliente": ("vendaCliente.py", "Venda Cliente (script legado)"),
        "troca_consumidor": ("trocaConsumidor.py", "Troca Consumidor (script legado)"),
        "troca_cliente_legacy": ("trocaCliente.py", "Troca Cliente (script legado)"),
        "pedido_venda": ("pedidoVenda.py", "Pedido de Venda (script legado)"),
    }

    for name, (file, desc) in legacy_tests.items():
        filepath = PROJECT_DIR / file
        if filepath.exists():
            tests[name] = {
                "file": str(filepath),
                "type": "legacy",
                "description": desc
            }

    return tests


def list_tests():
    """Lista todos os testes disponíveis."""
    tests = get_available_tests()

    print(f"\n{Colors.BOLD}📋 TESTES DISPONÍVEIS:{Colors.RESET}\n")

    pytest_tests = {k: v for k, v in tests.items() if v["type"] == "pytest"}
    legacy_tests = {k: v for k, v in tests.items() if v["type"] == "legacy"}

    if pytest_tests:
        print(f"{Colors.CYAN}  Pytest (recomendado):{Colors.RESET}")
        for name, info in pytest_tests.items():
            print(f"    • {name:<20} - {info['description']}")

    if legacy_tests:
        print(f"\n{Colors.YELLOW}  Scripts Legados:{Colors.RESET}")
        for name, info in legacy_tests.items():
            print(f"    • {name:<20} - {info['description']}")

    print(f"\n{Colors.BOLD}Uso:{Colors.RESET}")
    print(f"  python runner.py --test <nome>")
    print(f"  python runner.py --test <nome> --allure")
    print(f"  python runner.py --all")
    print()


def run_pytest(test_path: str, use_allure: bool = False, verbose: bool = True):
    """Executa teste com pytest."""
    cmd = ["pytest", test_path, "-v"]

    if use_allure:
        ALLURE_RESULTS_DIR.mkdir(exist_ok=True)
        cmd.extend(["--alluredir", str(ALLURE_RESULTS_DIR)])

    if verbose:
        cmd.append("-s")

    print(f"\n{Colors.CYAN}▶ Executando: {' '.join(cmd)}{Colors.RESET}\n")

    result = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    return result.returncode


def run_legacy(test_path: str):
    """Executa script legado."""
    print(f"\n{Colors.YELLOW}▶ Executando script legado: {test_path}{Colors.RESET}\n")

    result = subprocess.run(
        [sys.executable, test_path],
        cwd=str(PROJECT_DIR)
    )
    return result.returncode


def run_test(test_name: str, use_allure: bool = False):
    """Executa um teste específico."""
    tests = get_available_tests()

    if test_name not in tests:
        print(f"{Colors.RED}✗ Teste '{test_name}' não encontrado{Colors.RESET}")
        list_tests()
        return 1

    test_info = tests[test_name]

    if test_info["type"] == "pytest":
        return run_pytest(test_info["file"], use_allure)
    else:
        return run_legacy(test_info["file"])


def run_all_tests(use_allure: bool = False):
    """Executa todos os testes pytest."""
    tests_dir = PROJECT_DIR / "tests"
    return run_pytest(str(tests_dir), use_allure)


def allure_instalado() -> bool:
    """Verifica se Allure CLI está instalado."""
    try:
        result = subprocess.run(
            ["allure", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def open_allure_report():
    """Gera e abre relatório Allure."""
    if not ALLURE_RESULTS_DIR.exists():
        print(f"{Colors.RED}✗ Nenhum resultado Allure encontrado{Colors.RESET}")
        print(f"  Execute testes com --allure primeiro")
        return

    # Verifica se Allure está instalado
    if not allure_instalado():
        print(f"{Colors.RED}✗ Allure CLI não está instalado ou não está no PATH{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Para instalar o Allure:{Colors.RESET}")
        print(f"  1. Via npm:   npm install -g allure-commandline")
        print(f"  2. Via scoop: scoop install allure")
        print(f"\n{Colors.CYAN}Alternativa - usar 'allure serve' direto:{Colors.RESET}")
        print(f"  allure serve {ALLURE_RESULTS_DIR}")
        return

    print(f"\n{Colors.CYAN}📊 Gerando relatório Allure...{Colors.RESET}")

    # Gera relatório
    result = subprocess.run([
        "allure", "generate",
        str(ALLURE_RESULTS_DIR),
        "-o", str(ALLURE_REPORT_DIR),
        "--clean"
    ])

    if result.returncode != 0:
        print(f"{Colors.RED}✗ Erro ao gerar relatório Allure{Colors.RESET}")
        return

    # Abre no navegador
    print(f"{Colors.GREEN}✓ Abrindo relatório no navegador...{Colors.RESET}")
    subprocess.Popen(["allure", "open", str(ALLURE_REPORT_DIR)])


def interactive_menu():
    """Menu interativo para seleção de testes."""
    tests = get_available_tests()
    test_list = list(tests.items())

    while True:
        print(f"\n{Colors.BOLD}═══════════════════════════════════════════════════{Colors.RESET}")
        print(f"{Colors.BOLD}           SELECIONE O TESTE PARA EXECUTAR{Colors.RESET}")
        print(f"{Colors.BOLD}═══════════════════════════════════════════════════{Colors.RESET}\n")

        for i, (name, info) in enumerate(test_list, 1):
            tipo = f"{Colors.CYAN}[pytest]{Colors.RESET}" if info["type"] == "pytest" else f"{Colors.YELLOW}[legacy]{Colors.RESET}"
            print(f"  {i}. {info['description']:<35} {tipo}")

        print(f"\n  {len(test_list) + 1}. {Colors.GREEN}Executar TODOS os testes pytest{Colors.RESET}")
        print(f"  {len(test_list) + 2}. {Colors.BLUE}Abrir relatório Allure{Colors.RESET}")
        print(f"  0. Sair\n")

        try:
            choice = input(f"{Colors.BOLD}Digite o número do teste: {Colors.RESET}").strip()

            if choice == "0":
                print(f"\n{Colors.GREEN}Até logo!{Colors.RESET}\n")
                break

            choice = int(choice)

            if 1 <= choice <= len(test_list):
                test_name = test_list[choice - 1][0]
                use_allure = input("Gerar relatório Allure? (s/N): ").lower() == 's'
                run_test(test_name, use_allure)

            elif choice == len(test_list) + 1:
                use_allure = input("Gerar relatório Allure? (s/N): ").lower() == 's'
                run_all_tests(use_allure)

            elif choice == len(test_list) + 2:
                open_allure_report()

            else:
                print(f"{Colors.RED}Opção inválida{Colors.RESET}")

            input(f"\n{Colors.CYAN}Pressione Enter para continuar...{Colors.RESET}")

        except ValueError:
            print(f"{Colors.RED}Digite um número válido{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}Até logo!{Colors.RESET}\n")
            break


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="CLI para execução de testes Appium",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python runner.py                     Menu interativo
  python runner.py --list              Lista testes disponíveis
  python runner.py --test login        Executa teste de login
  python runner.py --test troca_cliente --allure  Com relatório Allure
  python runner.py --all               Executa todos os testes
  python runner.py --report            Abre relatório Allure
        """
    )

    parser.add_argument("--list", "-l", action="store_true", help="Lista testes disponíveis")
    parser.add_argument("--test", "-t", type=str, help="Nome do teste para executar")
    parser.add_argument("--all", "-a", action="store_true", help="Executa todos os testes pytest")
    parser.add_argument("--allure", action="store_true", help="Gera relatório Allure")
    parser.add_argument("--report", "-r", action="store_true", help="Abre relatório Allure")
    parser.add_argument("--no-appium", action="store_true", help="Não inicia Appium automaticamente")

    args = parser.parse_args()

    print_banner()

    # Verifica pré-requisitos
    if not args.list and not args.report:
        if not check_device():
            sys.exit(1)

        if not args.no_appium:
            appium_process = start_appium_server()

    # Executa ação solicitada
    try:
        if args.list:
            list_tests()

        elif args.report:
            open_allure_report()

        elif args.test:
            exit_code = run_test(args.test, args.allure)
            # Se usou allure e foi bem sucedido, tenta abrir o relatório
            if args.allure and exit_code == 0:
                if allure_instalado():
                    open_allure_report()
                else:
                    print(f"\n{Colors.YELLOW}📊 Resultados Allure salvos em: {ALLURE_RESULTS_DIR}{Colors.RESET}")
                    print(f"   Para visualizar: allure serve {ALLURE_RESULTS_DIR}")
            sys.exit(exit_code)

        elif args.all:
            exit_code = run_all_tests(args.allure)
            # Se usou allure e foi bem sucedido, tenta abrir o relatório
            if args.allure and exit_code == 0:
                if allure_instalado():
                    open_allure_report()
                else:
                    print(f"\n{Colors.YELLOW}📊 Resultados Allure salvos em: {ALLURE_RESULTS_DIR}{Colors.RESET}")
                    print(f"   Para visualizar, instale o Allure CLI:")
                    print(f"   npm install -g allure-commandline")
                    print(f"   Depois execute: allure serve {ALLURE_RESULTS_DIR}")
            sys.exit(exit_code)

        else:
            interactive_menu()

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrompido pelo usuário{Colors.RESET}")
        sys.exit(130)


if __name__ == "__main__":
    main()
