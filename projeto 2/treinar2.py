import json
import os
import queue
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

from student_players import pair_name

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_PESOS = BASE_DIR / "pesos.json"
ARQUIVO_LOG = BASE_DIR / "historico_treinamento.txt"
NOME_BOT = pair_name()

# --- VARIAVEIS DE CONFIGURACAO ---
JOGOS_NO_NORMAL = 5000
JOGOS_PARA_CONFIRMAR = 10000
QNT_PARA_SALVAR = 100
VARIAVEIS_MUDADAS_AO_MESMO_TEMPO = 1
QUANTIA_THREADS = max(2, (os.cpu_count() or 2) // 2)

# Configuração para ponderar o peso de um bot específico na avaliação
BOT_ALVO = None        # Ex: "ReverseGreedy" (None para avaliar contra todos igualmente)
PESO_BOT_ALVO = 1.0    # Ex: 5.0 (multiplica vitórias/derrotas deste bot por este peso)

LIMITES_PADRAO = {
    "PESO_MEDIA_CHANCE_PADRAO": (0.0, 1.0),
    "PESO_MEDIA_VALOR_PADRAO": (0.0, 1.0),
    "PESO_CHANCE_MANILHA": (0.0, 1.0),
    "PESO_VALOR_MANILHA": (0.0, 1.0),
    "BONUS_QTD_MANILHAS": (0.0, 1.0),
    "BONUS_MELHOR_MANILHA": (0.0, 1.0),
    "MULTIPLICADOR_MAO_MANILHA_3": (0.0, 2.0),
    "MULTIPLICADOR_MAO_BASE_2": (0.0, 2.0),
    "MULTIPLICADOR_VENCEU_PRIMEIRA_RODADA": (0.0, 2.0),
    "MULTIPLICADOR_PERDEU_PRIMEIRA_RODADA": (0.0, 2.0),
    "RDD2_LIMIAR_SUBSTITUIR_CARTA": (0.0, 1.0),
    "RDD2_LIMIAR_PEDIR_TRUCO": (0.0, 3.0),
    "RDD3_LIMIAR_PEDIR_TRUCO": (0.0, 1.0),
    "RESP_LIMIAR_CORRER": (0.0, 1.0),
    "RESP_LIMIAR_AUMENTAR": (0.0, 3.0),
    "VALOR_MANILHA_BASE": (0.0, 2.0),
    "VALOR_MANILHA_DIVISOR": (1.0, 100.0),
    "VALOR_COMUM_DIVISOR": (1.0, 1000.0),
    "RDD1_VALOR_MINIMO_MEDIANA": (100.0, 110.0),
}


@dataclass
class TarefaAvaliacao:
    indice: int
    pesos: dict
    mudancas: list[str]
    baseline: float


def carregar_pesos(caminho=ARQUIVO_PESOS):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_pesos(pesos, caminho=ARQUIVO_PESOS):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(pesos, arquivo, indent=2)


def obter_valor_peso(entrada):
    if isinstance(entrada, (list, tuple)):
        return entrada[0]
    return entrada


def obter_limites_peso(nome_peso, entrada):
    if isinstance(entrada, (list, tuple)):
        return entrada[1], entrada[2]
    return LIMITES_PADRAO[nome_peso]


def mutar_pesos(pesos, taxa_mutacao=0.01, qtd_variaveis=1):
    """Escolhe N pesos aleatorios e altera levemente."""
    novos_pesos = json.loads(json.dumps(pesos))
    chaves = [chave for chave in novos_pesos.keys() if chave != "NOME_DO_PESO"]

    qtd_real = min(qtd_variaveis, len(chaves))
    chaves_escolhidas = random.sample(chaves, qtd_real)
    log_mudancas = []

    for chave_escolhida in chaves_escolhidas:
        entrada_atual = novos_pesos[chave_escolhida]
        atual = obter_valor_peso(entrada_atual)
        minimo, maximo = obter_limites_peso(chave_escolhida, entrada_atual)

        range_peso = maximo - minimo
        if range_peso == 0:
            range_peso = 1.0

        alteracao = (random.random() * 2 - 1) * (range_peso * taxa_mutacao)
        novo_valor = max(minimo, min(maximo, atual + alteracao))
        novos_pesos[chave_escolhida] = round(novo_valor, 4)
        log_mudancas.append(f"{chave_escolhida}: {atual:.4f} -> {novo_valor:.4f}")

    return novos_pesos, log_mudancas


def formatar_log(porcentagem, pesos):
    valores = [str(obter_valor_peso(pesos[chave])) for chave in pesos.keys() if chave != "NOME_DO_PESO"]
    return f"{porcentagem:.2f}% Vitorias - " + ",".join(valores)


def copiar_arquivos_execucao(diretorio_destino):
    arquivos = [
        "main.py",
        "tournament.py",
        "drawer.py",
        "judge.py",
        "basic_players.py",
        "student_players.py",
    ]

    for nome_arquivo in arquivos:
        origem = BASE_DIR / nome_arquivo
        if origem.exists():
            shutil.copy2(origem, diretorio_destino / nome_arquivo)

    for nome_pasta in ["fonts", "img"]:
        origem_pasta = BASE_DIR / nome_pasta
        destino_pasta = diretorio_destino / nome_pasta
        if origem_pasta.exists() and not destino_pasta.exists():
            shutil.copytree(origem_pasta, destino_pasta)


def extrair_porcentagem(saida):
    if not saida:
        return 0.0

    confrontos = re.findall(
        r"RESULTADO DO CONFRONTO: (.*?) fez (\d+) vit.rias, e (.*?) fez (\d+) vit.rias\.",
        saida
    )

    if confrontos:
        soma_vitorias = 0.0
        soma_derrotas = 0.0
        for time1, vits1_str, time2, vits2_str in confrontos:
            vits1 = int(vits1_str)
            vits2 = int(vits2_str)

            if time1 == NOME_BOT or time2 == NOME_BOT:
                if time1 == NOME_BOT:
                    oponente = time2
                    vits = vits1
                    ders = vits2
                else:
                    oponente = time1
                    vits = vits2
                    ders = vits1

                peso = 1.0
                if BOT_ALVO is not None:
                    if oponente == BOT_ALVO:
                        peso = PESO_BOT_ALVO

                soma_vitorias += vits * peso
                soma_derrotas += ders * peso

        total_jogos = soma_vitorias + soma_derrotas
        if total_jogos > 0:
            return round((soma_vitorias / total_jogos) * 100, 2)

    padrao = rf"{re.escape(NOME_BOT)} - CONFRONTOS\[.*?\] - JOGOS\[(\d+) Vit.rias, (\d+) Derrotas"
    match = re.search(padrao, saida)
    if not match:
        return 0.0

    vitorias = int(match.group(1))
    derrotas = int(match.group(2))
    total_jogos = vitorias + derrotas
    if total_jogos == 0:
        return 0.0

    return round((vitorias / total_jogos) * 100, 2)


def avaliar_bot(num_jogos, diretorio_execucao):
    comando_teste = [sys.executable, "main.py", "-n", str(num_jogos), "-s", "0"]
    resultado = subprocess.run(
        comando_teste,
        capture_output=True,
        text=True,
        encoding="latin-1",
        errors="replace",
        cwd=str(diretorio_execucao),
    )
    return extrair_porcentagem(resultado.stdout)


def criar_ambiente_worker(indice_worker):
    temp_dir = tempfile.TemporaryDirectory(prefix=f"treino_truco_worker_{indice_worker}_")
    diretorio = Path(temp_dir.name)
    copiar_arquivos_execucao(diretorio)
    return temp_dir, diretorio


def worker_loop(indice_worker, fila_tarefas, fila_resultados, evento_parar):
    temp_dir, diretorio_worker = criar_ambiente_worker(indice_worker)

    try:
        while not evento_parar.is_set():
            tarefa = fila_tarefas.get()
            if tarefa is None:
                fila_tarefas.task_done()
                break

            salvar_pesos(tarefa.pesos, diretorio_worker / "pesos.json")

            porcentagem_curta = avaliar_bot(JOGOS_NO_NORMAL, diretorio_worker)
            passou_teste_1 = porcentagem_curta > tarefa.baseline

            porcentagem_confirmada = None
            passou_teste_2 = False
            if passou_teste_1:
                porcentagem_confirmada = avaliar_bot(JOGOS_PARA_CONFIRMAR, diretorio_worker)
                passou_teste_2 = porcentagem_confirmada > tarefa.baseline

            fila_resultados.put(
                {
                    "indice": tarefa.indice,
                    "pesos": tarefa.pesos,
                    "mudancas": tarefa.mudancas,
                    "porcentagem_curta": porcentagem_curta,
                    "porcentagem_confirmada": porcentagem_confirmada,
                    "passou_teste_1": passou_teste_1,
                    "passou_teste_2": passou_teste_2,
                }
            )
            fila_tarefas.task_done()
    finally:
        temp_dir.cleanup()


def criar_tarefa(indice, pesos_base, baseline):
    pesos_mutados, log_mudancas = mutar_pesos(
        pesos_base,
        taxa_mutacao=0.01,
        qtd_variaveis=VARIAVEIS_MUDADAS_AO_MESMO_TEMPO,
    )
    return TarefaAvaliacao(
        indice=indice,
        pesos=pesos_mutados,
        mudancas=log_mudancas,
        baseline=baseline,
    )


def main():
    print("Iniciando treinamento paralelo de Hill Climbing...")
    print(f"Usando {QUANTIA_THREADS} threads em paralelo.")

    pesos_atuais = carregar_pesos()
    print("Avaliando peso inicial (Baseline com 1000 jogos)...")
    melhor_porcentagem = avaliar_bot(1000, BASE_DIR)
    print(f"Baseline: {melhor_porcentagem}% de vitórias.\n")

    fila_tarefas = queue.Queue()
    fila_resultados = queue.Queue()
    evento_parar = threading.Event()

    workers = []
    for indice_worker in range(QUANTIA_THREADS):
        thread = threading.Thread(
            target=worker_loop,
            args=(indice_worker, fila_tarefas, fila_resultados, evento_parar),
            daemon=True,
        )
        thread.start()
        workers.append(thread)

    proxima_iteracao = 1
    iteracao = 1

    try:
        for _ in range(QUANTIA_THREADS):
            fila_tarefas.put(criar_tarefa(proxima_iteracao, pesos_atuais, melhor_porcentagem))
            proxima_iteracao += 1

        while True:
            resultado = fila_resultados.get()

            if resultado["passou_teste_1"] and resultado["passou_teste_2"] and resultado["porcentagem_confirmada"] > melhor_porcentagem:
                print(
                    f"[Iter {iteracao}] SUCESSO | {resultado['porcentagem_curta']}% em {JOGOS_NO_NORMAL} jogos | "
                    f"{resultado['porcentagem_confirmada']}% confirmados em {JOGOS_PARA_CONFIRMAR} jogos | "
                    f"{' | '.join(resultado['mudancas'])}"
                )
                melhor_porcentagem = resultado["porcentagem_confirmada"]
                pesos_atuais = resultado["pesos"]
                salvar_pesos(pesos_atuais)
            else:
                if resultado["porcentagem_confirmada"] is None:
                    print(
                        f"[Iter {iteracao}] FALHA   | {resultado['porcentagem_curta']}% em {JOGOS_NO_NORMAL} jogos | "
                        f"Revertendo: {' | '.join(resultado['mudancas'])}"
                    )
                else:
                    print(
                        f"[Iter {iteracao}] FALHA   | {resultado['porcentagem_curta']}% em {JOGOS_NO_NORMAL} jogos | "
                        f"{resultado['porcentagem_confirmada']}% confirmados em {JOGOS_PARA_CONFIRMAR} jogos | "
                        f"Revertendo: {' | '.join(resultado['mudancas'])}"
                    )
                salvar_pesos(pesos_atuais)

            if iteracao % QNT_PARA_SALVAR == 0:
                linha_log = formatar_log(melhor_porcentagem, pesos_atuais)
                print(f"\n--- SALVANDO CHECKPOINT ITERACAO {iteracao} ---")
                print(linha_log + "\n")
                with open(ARQUIVO_LOG, "a", encoding="utf-8") as arquivo_log:
                    arquivo_log.write(f"Iteracao {iteracao} | {linha_log}\n")

            fila_tarefas.put(criar_tarefa(proxima_iteracao, pesos_atuais, melhor_porcentagem))
            proxima_iteracao += 1
            iteracao += 1
    except KeyboardInterrupt:
        print("\nTreinamento interrompido pelo usuario.")
    finally:
        evento_parar.set()
        for _ in workers:
            fila_tarefas.put(None)
        for thread in workers:
            thread.join(timeout=5)


if __name__ == "__main__":
    main()