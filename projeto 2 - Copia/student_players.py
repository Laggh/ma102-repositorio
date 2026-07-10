### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01: Renan Andrade dos Santos
# RA #01: 321330      
# Nome #02: Igor Henrique de Abreu
# RA #02 183538

from basic_players import Player
from judge import card_value, generate_deck
import os

cardValueHash = {
    "4": 0,
    "5": 1,
    "6": 2,
    "7": 3,
    "Q": 4,
    "J": 5,
    "K": 6,
    "A": 7,
    "2": 8,
    "3": 9,
    "MANILHA": 10,
}
nextCardValueHash = {
    "4": "5",
    "5": "6",
    "6": "7",
    "7": "Q",
    "Q": "J",
    "J": "K",
    "K": "A",
    "A": "2",
    "2": "3",
    "3": "4",
}
suitValueHash = {
    "Diamonds": 0,
    "Clubs": 1,
    "Hearts": 2,
    "Spades": 3,
}
"""
==============================================================================
ALGORITMO DE TREINAMENTO (Hill Climbing)

Os pesos abaixo foram otimizados usando uma tecnica de Inteligencia Artificial 
chamada Hill Climbing que aleatoriamente altera os pesos e vê se o bot melhora ou piora
Se melhora ele mantem, se não ele discarta, eu deixei rodando algumas horas e as vezes
manualmente mudando os valores

Referência: https://www.youtube.com/watch?v=oSdPmxRCWws
Hill Climbing Algorithm & Artificial Intelligence - Computerphile

para treinar eu usei esse codigo, qualquer pergunta/duvida pode mandar no comentario do classrom

import os, json, random, subprocess, re, sys

ARQUIVO_PESOS = "pesos.json"
ARQUIVO_LOG = "historico_treinamento.txt"
NOME_BOT = "algum nome"

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
    "RDD1_VALOR_MINIMO_MEDIANA": (100.0, 110.0),
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
    comando_teste = [sys.executable, "main.py", "-n", str(num_jogos), "-s", "0"]
    resultado = subprocess.run(comando_teste, capture_output=True, text=True, encoding='latin-1', errors='replace')
    saida = resultado.stdout
    if not saida:
        return 0.0
    padrao = rf"{NOME_BOT} - CONFRONTOS\[.*?\] - JOGOS\[(\d+) Vit.rias, (\d+) Derrotas"
    match = re.search(padrao, saida)
    if match:
        vitorias = int(match.group(1))
        derrotas = int(match.group(2))
        total_jogos = vitorias + derrotas
        if total_jogos == 0:
            return 0.0
        return round((vitorias / total_jogos) * 100, 2)
    return 0.0

def mutar_pesos(pesos, taxa_mutacao=0.01, qtd_variaveis=1):
    novos_pesos = json.loads(json.dumps(pesos))
    chaves = [k for k in novos_pesos.keys() if k != "NOME_DO_PESO"]
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

def main():
    print("Iniciando treinamento de Hill Climbing...")
    pesos_atuais = carregar_pesos()
    melhor_porcentagem = avaliar_bot(1000)
    print(f"Baseline: {melhor_porcentagem}% de vitorias.\n")
    iteracao = 1
    while True:
        pesos_mutados, log_mudancas = mutar_pesos(pesos_atuais, taxa_mutacao=0.01, qtd_variaveis=VARIAVEIS_MUDADAS_AO_MESMO_TEMPO)
        salvar_pesos(pesos_mutados)
        porcentagem_atual = avaliar_bot(JOGOS_NO_NORMAL)
        mudancas_str = " | ".join(log_mudancas)
        if porcentagem_atual > melhor_porcentagem:
            porcentagem_confirmada = avaliar_bot(JOGOS_PARA_CONFIRMAR)
            if porcentagem_confirmada > melhor_porcentagem:
                print(f"[Iter {iteracao}] SUCESSO | {porcentagem_confirmada}% confirmados | {mudancas_str}")
                melhor_porcentagem = porcentagem_confirmada
                pesos_atuais = pesos_mutados
            else:
                print(f"[Iter {iteracao}] FALHA   | {porcentagem_confirmada}% confirmados | Revertendo: {mudancas_str}")
                salvar_pesos(pesos_atuais)
        else:
            print(f"[Iter {iteracao}] FALHA   | {porcentagem_atual}% | Revertendo: {mudancas_str}")
            salvar_pesos(pesos_atuais)
        if iteracao % QNT_PARA_SALVAR == 0:
            with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
                f.write(f"Iteracao {iteracao} | {melhor_porcentagem:.2f}% Vitorias\n")
        iteracao += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTreinamento interrompido pelo usuario.")
"""
# Pesos da avaliacao geral da mao. (somam 1.0)
PESO_MEDIA_CHANCE_PADRAO = 0.7
PESO_MEDIA_VALOR_PADRAO= 0.3

# Pesos da avaliacao quando a mao tem manilha. (somam 1.0)
PESO_CHANCE_MANILHA = 0.5
PESO_VALOR_MANILHA = 0.5

# Pesos de bonus para a avaliacao da mao quando tem manilha
BONUS_QTD_MANILHAS = 0.25
BONUS_MELHOR_MANILHA = 0.5

# Ajustes por quantidade de cartas na mao.
MULTIPLICADOR_MAO_MANILHA_3 = 1.1
MULTIPLICADOR_MAO_BASE_2 = 1.1
MULTIPLICADOR_VENCEU_PRIMEIRA_RODADA = 1.15
MULTIPLICADOR_PERDEU_PRIMEIRA_RODADA = 0.9

RDD2_LIMIAR_SUBSTITUIR_CARTA = 0.1
RDD2_LIMIAR_PEDIR_TRUCO = 1.55

# Terceira rodada: a decisão principal é se a única carta vale um truco.
RDD3_LIMIAR_PEDIR_TRUCO = 0.8

# Resposta a truco: quando correr, aceitar ou aumentar.
RESP_LIMIAR_CORRER   = 0.75
RESP_LIMIAR_AUMENTAR = 1.55

# Escala interna de avaliação das cartas.
VALOR_MANILHA_BASE = 1.0
VALOR_MANILHA_DIVISOR = 10.0
VALOR_COMUM_DIVISOR = 100.0

# Valor mínimo da carta mediana para ser jogada na primeira rodada (sendo o mão).
# 104 = 100 + RANK_ORDER.index('Q'), ou seja, equivale a um 'Q' no mínimo.
RDD1_VALOR_MINIMO_MEDIANA = 104.0

# gera como coleção pra ser mais facil de achar
def gerar_baralho_completo():
    baralho = []
    for carta in generate_deck():
        baralho.append(carta)
    return baralho
    #67


def chance_carta_ser_mais_forte(cartas_possiveis_adversarios, carta_especifica, top_card):
    if not cartas_possiveis_adversarios or carta_especifica is None:
        return 0.0

    valor_carta_especifica = card_value(carta_especifica, top_card)
    cartas_vencidas = 0

    for carta_adversaria in cartas_possiveis_adversarios:
        if card_value(carta_adversaria, top_card) < valor_carta_especifica:
            cartas_vencidas += 1

    return cartas_vencidas / len(cartas_possiveis_adversarios)


def _valor_carta_para_avaliacao(carta, top_card):
    if carta is None:
        return 0.0

    valor_base = card_value(carta, top_card)
    if valor_base >= 1000:
        return VALOR_MANILHA_BASE + (valor_base - 1000) / VALOR_MANILHA_DIVISOR
    return valor_base / VALOR_COMUM_DIVISOR


def avaliar_mao_padrao(mao, top_card, cartas_possiveis_adversarios):
    if not mao:
        return 0.0

    soma_chances = 0.0
    soma_valores = 0.0

    for carta in mao:
        soma_chances += chance_carta_ser_mais_forte(cartas_possiveis_adversarios, carta, top_card)
        soma_valores += _valor_carta_para_avaliacao(carta, top_card)

    media_chance = soma_chances / len(mao)
    media_valor = soma_valores / len(mao)
    return (media_chance * PESO_MEDIA_CHANCE_PADRAO) + (media_valor * PESO_MEDIA_VALOR_PADRAO)


def avaliar_mao_manilha(mao, top_card, cartas_possiveis_adversarios):
    total = 0.0
    qtd_manilhas = 0
    melhor_manilha = 0.0

    for carta in mao:
        chance = chance_carta_ser_mais_forte(cartas_possiveis_adversarios, carta, top_card)
        valor = _valor_carta_para_avaliacao(carta, top_card)
        total += (chance * PESO_CHANCE_MANILHA) + (valor * PESO_VALOR_MANILHA)

        if card_value(carta, top_card) >= 1000:
            qtd_manilhas += 1
            if chance > melhor_manilha:
                melhor_manilha = chance

    media = total / len(mao)
    bonus_manilhas = qtd_manilhas * BONUS_QTD_MANILHAS
    bonus_melhor_manilha = melhor_manilha * BONUS_MELHOR_MANILHA
    return media + bonus_manilhas + bonus_melhor_manilha


def avaliar_mao1(mao, top_card, cartas_possiveis_adversarios):
    return avaliar_mao_padrao(mao, top_card, cartas_possiveis_adversarios)


def avaliar_mao2(mao, top_card, cartas_possiveis_adversarios, venceu_primeira_rodada=None):
    if not mao:
        return 0.0

    if any(card_value(carta, top_card) >= 1000 for carta in mao):
        valor_avaliado = avaliar_mao_manilha(mao, top_card, cartas_possiveis_adversarios)
    else:
        valor_avaliado = avaliar_mao_padrao(mao, top_card, cartas_possiveis_adversarios) * MULTIPLICADOR_MAO_BASE_2

    if venceu_primeira_rodada is True:
        return valor_avaliado * MULTIPLICADOR_VENCEU_PRIMEIRA_RODADA
    if venceu_primeira_rodada is False:
        return valor_avaliado * MULTIPLICADOR_PERDEU_PRIMEIRA_RODADA

    return valor_avaliado


def avaliar_mao3(mao, top_card, cartas_possiveis_adversarios):
    if not mao:
        return 0.0

    # Se tiver manilha
    if any(card_value(carta, top_card) >= 1000 for carta in mao):
        return avaliar_mao_manilha(mao, top_card, cartas_possiveis_adversarios) * MULTIPLICADOR_MAO_MANILHA_3

    return avaliar_mao_padrao(mao, top_card, cartas_possiveis_adversarios)


def avaliar_mao(mao, top_card, cartas_possiveis_adversarios, venceu_primeira_rodada=None):
    quantidade_cartas = len(mao)

    if quantidade_cartas == 3:
        return avaliar_mao3(mao, top_card, cartas_possiveis_adversarios)
    if quantidade_cartas == 2:
        return avaliar_mao2(mao, top_card, cartas_possiveis_adversarios, venceu_primeira_rodada=venceu_primeira_rodada)
    if quantidade_cartas == 1:
        return avaliar_mao1(mao, top_card, cartas_possiveis_adversarios)

    return avaliar_mao_padrao(mao, top_card, cartas_possiveis_adversarios)


# A estrategia é a seguinte:
# Em toda situação calcular a chance de ganhar a mão,
# Tentar garantir a primeira mão, para "controlar" o jogo
# ir com tudo se perder a primeira mão

# se tiver manilha, deixar pro final 
class botComPesos(Player):
    # Se estiver dúvida sobre como começar olhe os players prontos em basic_players.py e o ReadMe
    def __init__(self,ra,nome,image):
        super().__init__(ra, nome,image) # Nome do Jogador 
        self.play_hist_jogada = []
        self.cartas_possiveis_adversarios = []
        self.jogadas_com_carta = []
        self.rodada_atual = 1
        self.posicao_mesa = 1
        self.jogadas_da_rodada = []
        self.carta_mais_forte_rodada = None
        self.time_carta_mais_forte_rodada = None
        self.carta_maior = None
        self.carta_menor = None
        self.valor_maior = None
        self.valor_menor = None
        self.aliado_esta_ganhando = False
        self.venceu_primeira_rodada = None
        self.valor_mao_atual = 1
        self.ultimo_time_truco = None

    # Printa todo o estado para debug
    def printState(self, top_card, play_hist, score_hist):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("TopCard:", top_card)
        print("PlayHist:")
        for i in range(len(play_hist)):
            print(f"\t {i+1}: {play_hist[i]}")
        
        print("ScoreHist:")
        for i in range(len(score_hist)):
            print(f"\t {i+1}: {score_hist[i]}")
    
    # (card, top_card) -> int: Valor da carta considerando a carta virada (top_card)
    def getCardValue(self, card, top_card):
        topRank, topSuit = top_card
        rank, suit = card

        manilha = nextCardValueHash[topRank]
        # Se for manilha então o naipe importa senão nem é adicionado na conta
        if rank == manilha:
            return cardValueHash["MANILHA"] + suitValueHash[suit]
        
        return cardValueHash[rank]

    
    def _jogadas_com_carta(self, play_hist_jogada):
        jogadas_com_carta = []
        for jogada in play_hist_jogada:
            if len(jogada) > 1 and jogada[1] is not None:
                jogadas_com_carta.append(jogada)
        return jogadas_com_carta

    # Interpreta todo o estado do jogo e coloca no `self`
    def entenderJogo(self, top_card, play_hist, score_hist):
        self.play_hist_jogada = play_hist[-1] if play_hist else []
        self.valor_mao_atual = score_hist[-1][1] if score_hist else 1

        self.cartas_possiveis_adversarios = gerar_baralho_completo()

        for carta in self._cards:
            if carta in self.cartas_possiveis_adversarios:
                self.cartas_possiveis_adversarios.remove(carta)

        if top_card in self.cartas_possiveis_adversarios:
            self.cartas_possiveis_adversarios.remove(top_card)

        for jogada in self.play_hist_jogada:
            if len(jogada) > 1:
                carta_jogada = jogada[1]
                if carta_jogada is not None and carta_jogada != ('?', '?') and carta_jogada in self.cartas_possiveis_adversarios:
                    self.cartas_possiveis_adversarios.remove(carta_jogada)

        self.ultimo_time_truco = None
        for jogada in self.play_hist_jogada:
            if len(jogada) > 2 and isinstance(jogada[2], int):
                self.ultimo_time_truco = jogada[0] % 2

        self.jogadas_com_carta = self._jogadas_com_carta(self.play_hist_jogada)
        self.rodada_atual = len(self.jogadas_com_carta) // 4 + 1
        self.posicao_mesa = len(self.jogadas_com_carta) % 4 + 1

        self.jogadas_da_rodada = []
        if len(self.jogadas_com_carta) % 4:
            self.jogadas_da_rodada = self.jogadas_com_carta[-(len(self.jogadas_com_carta) % 4):]

        self.carta_mais_forte_rodada = None
        self.time_carta_mais_forte_rodada = None
        cartas_visiveis = []
        for jogada in self.jogadas_da_rodada:
            if jogada[1] != ('?', '?'):
                cartas_visiveis.append(jogada[1])
        if cartas_visiveis:
            maior_valor_rodada = None
            for jogada in self.jogadas_da_rodada:
                if jogada[1] == ('?', '?'):
                    continue
                valor_jogada = card_value(jogada[1], top_card)
                if self.carta_mais_forte_rodada is None or valor_jogada > maior_valor_rodada:
                    self.carta_mais_forte_rodada = jogada[1]
                    self.time_carta_mais_forte_rodada = jogada[0] % 2
                    maior_valor_rodada = valor_jogada

        self.carta_maior = None
        self.carta_menor = None
        self.valor_maior = None
        self.valor_menor = None

        for carta in self._cards:
            valor = card_value(carta, top_card)
            if self.carta_maior is None or valor > self.valor_maior:
                self.carta_maior = carta
                self.valor_maior = valor
            if self.carta_menor is None or valor < self.valor_menor:
                self.carta_menor = carta
                self.valor_menor = valor

        self.aliado_esta_ganhando = False
        if self.posicao_mesa == 3 and len(self.jogadas_da_rodada) >= 2:
            meu_time = self.position % 2
            carta_aliado = None
            carta_adversario = None

            for jogada in self.jogadas_da_rodada:
                if jogada[0] % 2 == meu_time:
                    carta_aliado = jogada[1]
                else:
                    carta_adversario = jogada[1]

            if carta_aliado is not None and carta_adversario is not None:
                self.aliado_esta_ganhando = card_value(carta_aliado, top_card) >= card_value(carta_adversario, top_card)

        self.venceu_primeira_rodada = None
        if len(self.jogadas_com_carta) >= 4:
            primeira_rodada = self.jogadas_com_carta[:4]
            melhor_time = None
            melhor_valor = None

            for jogada in primeira_rodada:
                valor_jogada = card_value(jogada[1], top_card)
                time_jogada = jogada[0] % 2
                if melhor_valor is None or valor_jogada > melhor_valor:
                    melhor_valor = valor_jogada
                    melhor_time = time_jogada

            if melhor_time is not None:
                self.venceu_primeira_rodada = (melhor_time == (self.position % 2))


    def jogarRodada1(self, top_card):
        # Lógica de pedir truco na primeira rodada
        decision = 1 #1 normal, 2 truco
        manilhas = []
        for c in self._cards:
            if card_value(c, top_card) >= 1000:
                manilhas.append(c)

        has_manilha = False
        if len(manilhas) >= 1:
            has_manilha = True

        has_three_or_another_manilha = False
        if len(manilhas) >= 2:
            has_three_or_another_manilha = True
        elif len(manilhas) == 1:
            for c in self._cards:
                if c != manilhas[0]:
                    if c[0] == '3':
                        has_three_or_another_manilha = True

        if self.pode_pedir_truco():
            if has_manilha:
                if has_three_or_another_manilha:
                    decision = 2

        # 1: Sendo o mão, joga a sua carta mediana (do meio) caso ela seja minimamente forte
        if self.posicao_mesa == 1:
            sorted_cards = sorted(self._cards, key=lambda c: card_value(c, top_card))
            if len(sorted_cards) == 3:
                mid_card = sorted_cards[1]
                if card_value(mid_card, top_card) >= RDD1_VALOR_MINIMO_MEDIANA:
                    return decision, mid_card
            return decision, self.carta_maior

        # 2: Tenta ganhar, se não consegue descarta
        if self.posicao_mesa == 2:
            if self.carta_mais_forte_rodada is not None and self.valor_maior is not None:
                if self.valor_maior > card_value(self.carta_mais_forte_rodada, top_card):
                    return decision, self.carta_maior
            return decision, self.carta_menor

        # 3: Tenta ganhar, se não consegue descarta
        # Pode descartar se o aliado estiver ganhando
        if self.posicao_mesa == 3:
            if self.aliado_esta_ganhando:
                return decision, self.carta_menor

            if self.carta_mais_forte_rodada is not None and self.valor_maior is not None:
                if self.valor_maior > card_value(self.carta_mais_forte_rodada, top_card):
                    return decision, self.carta_maior
            return decision, self.carta_menor

        # 4: Tenta ganhar, se não consegue descarta
        # Pode descartar se o aliado estiver ganhando
        if self.posicao_mesa == 4:
            if self.carta_mais_forte_rodada is not None and self.valor_maior is not None:
                if self.valor_maior > card_value(self.carta_mais_forte_rodada, top_card):
                    return decision, self.carta_maior
            return decision, self.carta_menor

        return decision, self.carta_menor

    def jogarRodada2(self, top_card):
        chance_carta_maior = chance_carta_ser_mais_forte(
            self.cartas_possiveis_adversarios,
            self.carta_maior,
            top_card,
        )
        chance_carta_menor = chance_carta_ser_mais_forte(
            self.cartas_possiveis_adversarios,
            self.carta_menor,
            top_card,
        )

        # Venceu: pensa sobre trucar e joga forte
        # porem não tenta tão forte pq tem a terceira
        if self.venceu_primeira_rodada:
            decision = 1
            if self.pode_pedir_truco():
                is_three_or_manilha = False
                if self.carta_maior[0] == '3':
                    is_three_or_manilha = True
                elif card_value(self.carta_maior, top_card) >= 1000:
                    is_three_or_manilha = True

                if is_three_or_manilha:
                    decision = 2
            return decision, self.carta_maior

        # Perdeu: tenta ganhar de qualquer jeito
        # não tem outra chance alem dessa, então joga a melhor carta
        if self.carta_mais_forte_rodada is not None and self.time_carta_mais_forte_rodada == (self.position % 2):
            chance_carta_mais_forte = chance_carta_ser_mais_forte(
                self.cartas_possiveis_adversarios,
                self.carta_mais_forte_rodada,
                top_card,
            )
            if chance_carta_maior - chance_carta_mais_forte > RDD2_LIMIAR_SUBSTITUIR_CARTA:
                return 1, self.carta_maior
            return 1, self.carta_menor

        if chance_carta_maior >= chance_carta_menor:
            return 1, self.carta_maior
        return 1, self.carta_menor

    def jogarRodada3(self, top_card):
        decision = 1
        if self.venceu_primeira_rodada:
            if self.pode_pedir_truco():
                is_three_or_manilha = False
                if self.carta_maior[0] == '3':
                    is_three_or_manilha = True
                elif card_value(self.carta_maior, top_card) >= 1000:
                    is_three_or_manilha = True

                if is_three_or_manilha:
                    decision = 2
        return decision, self.carta_maior

    def responderTruco(self, top_card):
        if self.valor_mao_atual >= 12:
            return 1

        if self.valor_maior is None:
            return 0

        meu_time = self.position % 2

        # 1. Verificar se a vitória da rodada está garantida ou muito provável
        vitoria_garantida = False

        # Se o parceiro jogou o Zap (1003)
        if self.time_carta_mais_forte_rodada == meu_time:
            if self.carta_mais_forte_rodada is not None:
                if card_value(self.carta_mais_forte_rodada, top_card) == 1003:
                    vitoria_garantida = True

        # Se somos os últimos a jogar
        if self.posicao_mesa == 4:
            if self.time_carta_mais_forte_rodada == meu_time:
                vitoria_garantida = True
            else:
                if self.carta_mais_forte_rodada is not None:
                    if self.valor_maior > card_value(self.carta_mais_forte_rodada, top_card):
                        vitoria_garantida = True

        if vitoria_garantida:
            if self.valor_maior >= 1000:
                if self.valor_mao_atual < 9:
                    return 2
            return 1

        # 2. Se o parceiro tem qualquer manilha na mesa e ainda faltam adversários jogarem, aceitamos por segurança
        if self.time_carta_mais_forte_rodada == meu_time:
            if self.carta_mais_forte_rodada is not None:
                if card_value(self.carta_mais_forte_rodada, top_card) >= 1000:
                    return 1

        # 3. Regra geral de aceitação por valor de carta
        if self.rodada_atual == 1:
            valor_necessario_para_aceitar = 109 # Pelo menos um 3 (109) ou Manilha (>=1000)
        else:
            if self.venceu_primeira_rodada is True:
                valor_necessario_para_aceitar = 107 # Permite aceitar com 'A' (107) ou '2' (108)
            else:
                valor_necessario_para_aceitar = 109

        if self.valor_maior < valor_necessario_para_aceitar:
            return 0

        # Se você tem Manilha, aumente (Retruco), a não ser que já esteja valendo 9 ou 12.
        if self.valor_maior >= 1000:
            if self.valor_mao_atual < 9:
                return 2

        return 1

    def pode_pedir_truco(self):
        if self.valor_mao_atual >= 12:
            return False

        if self.ultimo_time_truco == (self.position % 2):
            return False

        return True

    # Função para retornar o que você vai jogar em determinada mão
    def play(self, top_card, play_hist, score_hist):
        #self.printState(top_card, play_hist, score_hist)

        self.entenderJogo(top_card, play_hist, score_hist)

        if self.rodada_atual == 1:
            return self.jogarRodada1(top_card)
        
        if self.rodada_atual == 2:
            decision, card = self.jogarRodada2(top_card)
            if decision == 2 and not self.pode_pedir_truco():
                return 1, card
            return decision, card
        
        if self.rodada_atual == 3:
            decision, card = self.jogarRodada3(top_card)
            if decision == 2 and not self.pode_pedir_truco():
                return 1, card
            return decision, card
        


        if self._cards:
            return 1, self._cards[0]
        return 1, None

    # Função para retornar o que você vai dar de resposta a trucos
    def respond(self,top_card,play_hist, score_hist):
        self.entenderJogo(top_card, play_hist, score_hist)
        return self.responderTruco(top_card)


# Função que define o nome da dupla:
def pair_name():
    return "K-tarrados" 


# Função que cria a dupla:
def create_pair():
    return (botComPesos(321330,"Renan Andrade dos Santos", "img/hellnah.jpg"), botComPesos(183538,"Igor Henrique de Abreu","img/walterWhiteOculos.jpg"))  # Defina aqui a dupla de jogadores. Deve ser uma tupla com dois jogadores.


if __name__ == "__main__":
    baralho_completo = gerar_baralho_completo()
    aux = []

    for carta in baralho_completo:
        cartas_restantes = []
        removida = False
        for carta_restante in baralho_completo:
            if not removida and carta_restante == carta:
                removida = True
                continue
            cartas_restantes.append(carta_restante)

        chance = chance_carta_ser_mais_forte(cartas_restantes, carta, ('4', 'Diamonds'))
        aux.append((carta, chance))

    aux.sort(key=lambda x: x[1], reverse=True)
    print("Cartas ordenadas por chance de serem mais fortes que as outras cartas:")
    for carta, chance in aux:
        print(f"Carta: {carta}, Chance: {chance:.2%}")