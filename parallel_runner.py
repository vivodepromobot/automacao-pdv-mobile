"""
Runner para execucao paralela em multiplos dispositivos.
Detecta dispositivos conectados, inicia Appium e roda testes em paralelo.
"""
import subprocess
import sys
import time
import argparse
import socket
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


# Lista para guardar processos Appium iniciados
processos_appium = []


def porta_em_uso(porta: int) -> bool:
    """Verifica se uma porta esta em uso (Appium rodando)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        resultado = sock.connect_ex(('127.0.0.1', porta))
        sock.close()
        return resultado == 0  # 0 = porta em uso
    except:
        return False


def iniciar_servidor_appium(porta: int) -> subprocess.Popen:
    """Inicia servidor Appium em uma porta especifica."""
    if porta_em_uso(porta):
        print(f"[APPIUM] Porta {porta} ja esta em uso (Appium rodando)")
        return None

    print(f"[APPIUM] Iniciando servidor na porta {porta}...")

    # Windows: cria nova janela de console
    if sys.platform == 'win32':
        processo = subprocess.Popen(
            f'appium -p {porta} --relaxed-security',
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        processo = subprocess.Popen(
            ['appium', '-p', str(porta), '--relaxed-security'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # Aguarda servidor iniciar (max 30 segundos)
    for i in range(30):
        time.sleep(1)
        if porta_em_uso(porta):
            print(f"[APPIUM] Servidor na porta {porta} pronto!")
            processos_appium.append(processo)
            return processo

    print(f"[ERRO] Timeout ao iniciar Appium na porta {porta}")
    return None


def parar_servidores_appium():
    """Para todos os servidores Appium iniciados."""
    for processo in processos_appium:
        try:
            processo.terminate()
            processo.wait(timeout=5)
        except:
            processo.kill()
    processos_appium.clear()


def obter_dispositivos_conectados():
    """Retorna lista de dispositivos conectados via ADB."""
    try:
        resultado = subprocess.run(
            ['adb', 'devices'],
            capture_output=True,
            text=True,
            timeout=10
        )

        dispositivos = []
        linhas = resultado.stdout.strip().split('\n')[1:]

        for linha in linhas:
            if '\tdevice' in linha:
                device_id = linha.split('\t')[0]
                dispositivos.append(device_id)

        return dispositivos
    except Exception as e:
        print(f"[ERRO] Falha ao detectar dispositivos: {e}")
        return []


def obter_info_dispositivo(device_id: str) -> dict:
    """Retorna informacoes do dispositivo."""
    try:
        modelo = subprocess.run(
            ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()

        versao = subprocess.run(
            ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()

        return {
            'id': device_id,
            'modelo': modelo or 'Desconhecido',
            'versao': versao or '?'
        }
    except:
        return {'id': device_id, 'modelo': 'Desconhecido', 'versao': '?'}


def rodar_testes_dispositivo(device_id: str, porta: int, testes: str = None,
                              html_report: bool = True) -> dict:
    """Roda testes em um dispositivo especifico."""
    info = obter_info_dispositivo(device_id)
    print(f"\n{'='*60}")
    print(f"[DEVICE] {info['modelo']} (Android {info['versao']})")
    print(f"[DEVICE] ID: {device_id}")
    print(f"[DEVICE] Porta Appium: {porta}")
    print(f"{'='*60}\n")

    # Monta comando pytest
    cmd = [
        sys.executable, '-m', 'pytest',
        testes if testes else 'tests/',
        '-v',
        f'--device-id={device_id}',
        f'--appium-port={porta}',
    ]

    if html_report:
        report_name = f"logs/reports/relatorio_{device_id.replace(':', '_')}.html"
        cmd.extend(['--html', report_name, '--self-contained-html'])

    # Executa
    inicio = time.time()
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    duracao = time.time() - inicio

    sucesso = resultado.returncode == 0

    return {
        'device_id': device_id,
        'modelo': info['modelo'],
        'porta': porta,
        'sucesso': sucesso,
        'duracao': duracao,
        'output': resultado.stdout,
        'erro': resultado.stderr
    }


def listar_dispositivos():
    """Lista dispositivos conectados."""
    dispositivos = obter_dispositivos_conectados()

    if not dispositivos:
        print("\n[AVISO] Nenhum dispositivo conectado!")
        print("Conecte dispositivos via USB ou inicie emuladores.\n")
        return

    print(f"\n{'='*60}")
    print(f" DISPOSITIVOS CONECTADOS: {len(dispositivos)}")
    print(f"{'='*60}\n")

    for i, device_id in enumerate(dispositivos, 1):
        info = obter_info_dispositivo(device_id)
        print(f"  {i}. {info['modelo']}")
        print(f"     ID: {device_id}")
        print(f"     Android: {info['versao']}")
        print()


def rodar_paralelo(testes: str = None, max_workers: int = None):
    """Roda testes em todos os dispositivos em paralelo."""
    dispositivos = obter_dispositivos_conectados()

    if not dispositivos:
        print("\n[ERRO] Nenhum dispositivo conectado!")
        return False

    print(f"\n{'='*60}")
    print(f" EXECUCAO PARALELA - {len(dispositivos)} DISPOSITIVOS")
    print(f"{'='*60}\n")

    porta_base = 4723

    # Prepara configuracao e inicia Appium para cada dispositivo
    configs = []
    print("[INFO] Preparando servidores Appium...\n")

    for i, device_id in enumerate(dispositivos):
        porta = porta_base + (i * 2)  # 4723, 4725, 4727...
        info = obter_info_dispositivo(device_id)
        print(f"  [{i+1}] {info['modelo']} -> Porta {porta}")

        # Inicia Appium se necessario
        iniciar_servidor_appium(porta)
        configs.append((device_id, porta))

    print(f"\n[INFO] Iniciando testes em paralelo...\n")
    time.sleep(2)  # Pequena pausa para estabilizar

    # Executa em paralelo
    workers = max_workers or len(dispositivos)
    resultados = []

    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(rodar_testes_dispositivo, device_id, porta, testes): device_id
                for device_id, porta in configs
            }

            for future in as_completed(futures):
                device_id = futures[future]
                try:
                    resultado = future.result()
                    resultados.append(resultado)
                    status = "[OK]" if resultado['sucesso'] else "[X]"
                    print(f"{status} {resultado['modelo']} finalizado")
                except Exception as e:
                    print(f"[ERRO] Falha no dispositivo {device_id}: {e}")
                    resultados.append({
                        'device_id': device_id,
                        'sucesso': False,
                        'erro': str(e)
                    })
    finally:
        # Para servidores Appium ao finalizar
        print("\n[INFO] Finalizando servidores Appium...")
        parar_servidores_appium()

    # Resumo
    print(f"\n{'='*60}")
    print(f" RESUMO DA EXECUCAO PARALELA")
    print(f"{'='*60}\n")

    total_sucesso = 0
    for r in resultados:
        status = "PASSOU" if r.get('sucesso') else "FALHOU"
        emoji = "[OK]" if r.get('sucesso') else "[X]"
        duracao = r.get('duracao', 0)

        print(f"  {emoji} {r.get('modelo', r['device_id'])}")
        print(f"      Status: {status}")
        print(f"      Duracao: {duracao:.1f}s")

        if not r.get('sucesso') and r.get('erro'):
            # Mostra ultimas linhas do erro
            erro_linhas = r['erro'].strip().split('\n')[-5:]
            for linha in erro_linhas:
                print(f"      {linha}")
        print()

        if r.get('sucesso'):
            total_sucesso += 1

    print(f"{'='*60}")
    print(f" RESULTADO: {total_sucesso}/{len(resultados)} dispositivos passaram")
    print(f"{'='*60}\n")

    return all(r.get('sucesso') for r in resultados)


def rodar_sequencial(dispositivo_index: int = None, testes: str = None):
    """Roda testes em um dispositivo especifico."""
    dispositivos = obter_dispositivos_conectados()

    if not dispositivos:
        print("\n[ERRO] Nenhum dispositivo conectado!")
        return

    # Seleciona dispositivo
    if dispositivo_index is not None:
        if dispositivo_index < 1 or dispositivo_index > len(dispositivos):
            print(f"[ERRO] Indice invalido. Escolha entre 1 e {len(dispositivos)}")
            return
        device_id = dispositivos[dispositivo_index - 1]
    else:
        device_id = dispositivos[0]

    porta = 4723

    # Inicia Appium se necessario
    print(f"\n[INFO] Verificando Appium na porta {porta}...")
    iniciar_servidor_appium(porta)
    time.sleep(2)

    try:
        resultado = rodar_testes_dispositivo(device_id, porta, testes)

        if resultado['sucesso']:
            print("\n[OK] Testes concluidos com sucesso!")
        else:
            print("\n[X] Alguns testes falharam.")
            if resultado.get('output'):
                print(resultado['output'][-2000:])  # Ultimos 2000 chars
    finally:
        parar_servidores_appium()


def rodar_sequencial_todos(testes: str = None):
    """
    Roda testes em TODOS os dispositivos, um por vez (sequencial).
    Mostra logs em tempo real. Ideal para evitar conflitos no servidor.
    """
    dispositivos = obter_dispositivos_conectados()

    if not dispositivos:
        print("\n[ERRO] Nenhum dispositivo conectado!")
        return False

    print(f"\n{'='*60}")
    print(f" EXECUCAO SEQUENCIAL - {len(dispositivos)} DISPOSITIVOS")
    print(f" (Um device por vez, logs em tempo real)")
    print(f"{'='*60}\n")

    porta = 4723
    resultados = []

    # Inicia Appium uma vez
    print(f"[INFO] Verificando Appium na porta {porta}...")
    iniciar_servidor_appium(porta)
    time.sleep(2)

    try:
        for i, device_id in enumerate(dispositivos, 1):
            info = obter_info_dispositivo(device_id)

            print(f"\n{'='*60}")
            print(f" [{i}/{len(dispositivos)}] {info['modelo']} (Android {info['versao']})")
            print(f" ID: {device_id}")
            print(f"{'='*60}\n")

            # Monta comando pytest - SEM capture para ver logs em tempo real
            cmd = [
                sys.executable, '-m', 'pytest',
                testes if testes else 'tests/',
                '-v', '-s',
                '--tb=short',
                f'--device-id={device_id}',
                f'--appium-port={porta}',
                '--html', f"logs/reports/relatorio_{info['modelo'].replace(' ', '_')}.html",
                '--self-contained-html'
            ]

            inicio = time.time()
            # Executa SEM capture - mostra output em tempo real
            resultado_proc = subprocess.run(cmd)
            duracao = time.time() - inicio

            sucesso = resultado_proc.returncode == 0
            resultados.append({
                'device_id': device_id,
                'modelo': info['modelo'],
                'sucesso': sucesso,
                'duracao': duracao
            })

            status = "[OK]" if sucesso else "[X]"
            print(f"\n{status} {info['modelo']} finalizado em {duracao:.1f}s")

            # Pausa entre dispositivos para limpar sessões
            if i < len(dispositivos):
                print(f"\n[INFO] Aguardando 8s para limpar sessoes antes do proximo dispositivo...")
                time.sleep(8)

    finally:
        parar_servidores_appium()

    # Resumo final
    print(f"\n{'='*60}")
    print(f" RESUMO FINAL")
    print(f"{'='*60}\n")

    total_sucesso = 0
    for r in resultados:
        status = "[OK]" if r['sucesso'] else "[X]"
        print(f"  {status} {r['modelo']}: {'PASSOU' if r['sucesso'] else 'FALHOU'} ({r['duracao']:.1f}s)")
        if r['sucesso']:
            total_sucesso += 1

    print(f"\n{'='*60}")
    print(f" RESULTADO: {total_sucesso}/{len(resultados)} dispositivos passaram")
    print(f"{'='*60}\n")

    return all(r['sucesso'] for r in resultados)


def main():
    parser = argparse.ArgumentParser(
        description='Runner para execucao em multiplos dispositivos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python parallel_runner.py --list                    # Lista dispositivos
  python parallel_runner.py --seq                     # Roda em todos (sequencial, RECOMENDADO)
  python parallel_runner.py --all                     # Roda em todos (paralelo, pode conflitar)
  python parallel_runner.py --device 1                # Roda no dispositivo 1
  python parallel_runner.py --device 2 --test tests/test_venda_cliente.py

RECOMENDADO: Use --seq para rodar em todos os devices um por vez.
Isso evita conflitos no servidor e mostra logs em tempo real.
        """
    )

    parser.add_argument('--list', '-l', action='store_true',
                        help='Lista dispositivos conectados')
    parser.add_argument('--seq', '-s', action='store_true',
                        help='Roda em todos os dispositivos SEQUENCIALMENTE (recomendado)')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Roda em todos os dispositivos em PARALELO (pode conflitar)')
    parser.add_argument('--device', '-d', type=int,
                        help='Roda no dispositivo especifico (numero)')
    parser.add_argument('--test', '-t', type=str,
                        help='Testes especificos (ex: tests/test_venda.py)')
    parser.add_argument('--workers', '-w', type=int,
                        help='Numero maximo de workers paralelos')

    args = parser.parse_args()

    if args.list:
        listar_dispositivos()
    elif args.seq:
        sucesso = rodar_sequencial_todos(args.test)
        sys.exit(0 if sucesso else 1)
    elif args.all:
        sucesso = rodar_paralelo(args.test, args.workers)
        sys.exit(0 if sucesso else 1)
    elif args.device:
        rodar_sequencial(args.device, args.test)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
