import os
import json
import random
import subprocess
import re
import time
import sys

ARQUIVO_PESOS = "pesos.json"
ARQUIVO_LOG = "historico_treinamento.txt"
NOME_BOT = "algum nome"

# --- VARIÁVEIS DE CONFIGURAÇÃO ---
JOGOS_NO_NORMAL = 500
JOGOS_PARA_CONFIRMAR = 1000
QNT_PARA_SALVAR = 100
VARIAVEIS_MUDADAS_AO_MESMO_TEMPO = 1

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
}

def carregar_pesos():
    with open(ARQUIVO_PESOS, "r", encoding="utf-8") as f:
        return json.load(f)


def obter_valor_peso(entrada):
    if isinstance(entrada, list) or isinstance(entrada, tuple):
        return entrada[0]
    return entrada


def obter_limites_peso(nome_peso, entrada):
    if isinstance(entrada, list) or isinstance(entrada, tuple):
        return entrada[1], entrada[2]
    return LIMITES_PADRAO[nome_peso]

def salvar_pesos(pesos):
    with open(ARQUIVO_PESOS, "w", encoding="utf-8") as f:
        json.dump(pesos, f, indent=2)

def avaliar_bot(num_jogos):
    """Roda o main.py e retorna a porcentagem de vitórias em JOGOS."""
    comando_teste = [sys.executable, "main.py", "-n", str(num_jogos), "-s", "0"]
    resultado = subprocess.run(comando_teste, capture_output=True, text=True, encoding='latin-1', errors='replace')
    saida = resultado.stdout
    
    if not saida:
        print("Erro: Nenhuma saída capturada do terminal.")
        return 0.0
    
    # Captura tanto as vitórias quanto as derrotas na string de JOGOS
    padrao = rf"{NOME_BOT} - CONFRONTOS\[.*?\] - JOGOS\[(\d+) Vit.rias, (\d+) Derrotas"
    match = re.search(padrao, saida)
    
    if match:
        vitorias = int(match.group(1))
        derrotas = int(match.group(2))
        total_jogos = vitorias + derrotas
        
        if total_jogos == 0:
            return 0.0
            
        porcentagem = (vitorias / total_jogos) * 100
        return round(porcentagem, 2)
    else:
        print(f"Erro ao extrair resultados do bot '{NOME_BOT}'. Verifique o terminal.")
        return 0.0

def mutar_pesos(pesos, taxa_mutacao=0.01, qtd_variaveis=1):
    """Escolhe N pesos aleatórios e altera ligeiramente."""
    novos_pesos = json.loads(json.dumps(pesos)) # Deep copy
    
    chaves = [k for k in novos_pesos.keys() if k != "NOME_DO_PESO"]
    
    # Garante que não vai tentar mudar mais variáveis do que existem no JSON
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
        novo_valor = atual + alteracao
        
        # Clampa o valor
        novo_valor = max(minimo, min(maximo, novo_valor))
        novos_pesos[chave_escolhida] = round(novo_valor, 4)
        
        log_mudancas.append(f"{chave_escolhida}: {atual:.4f} -> {novo_valor:.4f}")
    
    return novos_pesos, log_mudancas

def formatar_log(porcentagem, pesos):
    """Gera a string no formato: XXXX% Vitorias - peso1,peso2,peso3..."""
    valores = [str(obter_valor_peso(pesos[k])) for k in pesos.keys() if k != "NOME_DO_PESO"]
    return f"{porcentagem:.2f}% Vitorias - " + ",".join(valores)

def main():
    print("Iniciando treinamento de Hill Climbing...")
    pesos_atuais = carregar_pesos()
    
    print("Avaliando peso inicial (Baseline com 1000 jogos)...")
    melhor_porcentagem = avaliar_bot(1000)
    print(f"Baseline: {melhor_porcentagem}% de vitórias.\n")
    
    iteracao = 1
    
    while True:
        # 1. Altera ligeiramente os parametros
        pesos_mutados, log_mudancas = mutar_pesos(
            pesos_atuais, 
            taxa_mutacao=0.01, 
            qtd_variaveis=VARIAVEIS_MUDADAS_AO_MESMO_TEMPO
        )
        salvar_pesos(pesos_mutados)
        
        # 2. Testa com a quantidade de jogos normal
        porcentagem_atual = avaliar_bot(JOGOS_NO_NORMAL)
        
        mudancas_str = " | ".join(log_mudancas)
        
        # 3. Se a amostra curta melhorar, confirma com 1000 jogos antes de aceitar
        if porcentagem_atual > melhor_porcentagem:
            print(f"[Iter {iteracao}] PROVISÓRIO | {porcentagem_atual}% vitórias em {JOGOS_NO_NORMAL} jogos | Confirmando com {JOGOS_PARA_CONFIRMAR} jogos...")
            porcentagem_confirmada = avaliar_bot(JOGOS_PARA_CONFIRMAR)

            if porcentagem_confirmada > melhor_porcentagem:
                print(f"[Iter {iteracao}] SUCESSO | {porcentagem_confirmada}% vitórias confirmadas | {mudancas_str}")
                melhor_porcentagem = porcentagem_confirmada
                pesos_atuais = pesos_mutados
            else:
                print(f"[Iter {iteracao}] FALHA   | {porcentagem_confirmada}% vitórias confirmadas | Revertendo: {mudancas_str}")
                salvar_pesos(pesos_atuais)
        else:
            print(f"[Iter {iteracao}] FALHA   | {porcentagem_atual}% vitórias | Revertendo: {mudancas_str}")
            # 4. Se diminuir, volta pro antes
            salvar_pesos(pesos_atuais) 
            
        # 5. Salva no arquivo com base na variável QNT_PARA_SALVAR
        if iteracao % QNT_PARA_SALVAR == 0:
            linha_log = formatar_log(melhor_porcentagem, pesos_atuais)
            print(f"\n--- SALVANDO CHECKPOINT ITERAÇÃO {iteracao} ---")
            print(linha_log + "\n")
            with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
                f.write(f"Iteracao {iteracao} | {linha_log}\n")
                
        iteracao += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTreinamento interrompido pelo usuário.")