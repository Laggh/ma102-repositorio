### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    [NOME COMPLETO #01] 
# RA #01 (quem entregou o código):      [RA #01]
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]
import os
import json

from basic_players import Player
from judge import card_value, generate_deck
# card_value(card, vira) -> int do valor

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

def carregar_pesos():
    caminho_pesos = os.path.join(os.path.dirname(__file__), "pesos.json")
    with open(caminho_pesos, encoding="utf-8") as arquivo_pesos:
        return json.load(arquivo_pesos)


PESOS = carregar_pesos()

# Pesos da avaliacao geral da mao. (somam 1.0)
PESO_MEDIA_CHANCE_PADRAO = PESOS["PESO_MEDIA_CHANCE_PADRAO"]
PESO_MEDIA_VALOR_PADRAO = PESOS["PESO_MEDIA_VALOR_PADRAO"]

# Pesos da avaliacao quando a mao tem manilha. (somam 1.0)
PESO_CHANCE_MANILHA = PESOS["PESO_CHANCE_MANILHA"]
PESO_VALOR_MANILHA = PESOS["PESO_VALOR_MANILHA"]

# Pesos de bonus para a avaliacao da mao quando tem manilha
BONUS_QTD_MANILHAS = PESOS["BONUS_QTD_MANILHAS"]
BONUS_MELHOR_MANILHA = PESOS["BONUS_MELHOR_MANILHA"]

# Ajustes por quantidade de cartas na mao.
MULTIPLICADOR_MAO_MANILHA_3 = PESOS["MULTIPLICADOR_MAO_MANILHA_3"]
MULTIPLICADOR_MAO_BASE_2 = PESOS["MULTIPLICADOR_MAO_BASE_2"]
MULTIPLICADOR_VENCEU_PRIMEIRA_RODADA = PESOS["MULTIPLICADOR_VENCEU_PRIMEIRA_RODADA"]
MULTIPLICADOR_PERDEU_PRIMEIRA_RODADA = PESOS["MULTIPLICADOR_PERDEU_PRIMEIRA_RODADA"]

RDD2_LIMIAR_SUBSTITUIR_CARTA = PESOS["RDD2_LIMIAR_SUBSTITUIR_CARTA"]
RDD2_LIMIAR_PEDIR_TRUCO = PESOS["RDD2_LIMIAR_PEDIR_TRUCO"]

# Terceira rodada: a decisão principal é se a única carta vale um truco.
RDD3_LIMIAR_PEDIR_TRUCO = PESOS["RDD3_LIMIAR_PEDIR_TRUCO"]

# Resposta a truco: quando correr, aceitar ou aumentar.
RESP_LIMIAR_CORRER = PESOS["RESP_LIMIAR_CORRER"]
RESP_LIMIAR_AUMENTAR = PESOS["RESP_LIMIAR_AUMENTAR"]

# Escala interna de avaliação das cartas.
VALOR_MANILHA_BASE = PESOS["VALOR_MANILHA_BASE"]
VALOR_MANILHA_DIVISOR = PESOS["VALOR_MANILHA_DIVISOR"]
VALOR_COMUM_DIVISOR = PESOS["VALOR_COMUM_DIVISOR"]

# gera como coleção pra ser mais facil de achar
def gerar_baralho_completo():
    baralho = []
    for carta in generate_deck():
        baralho.append(carta)
    return baralho

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
class NonePlayer(Player):
    # Se estiver dúvida sobre como começar olhe os players prontos em basic_players.py e o ReadMe
    def __init__(self):
        super().__init__(0, "Ninguém") # Nome do Jogador 
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

    def printState(self, top_card, play_hist, score_hist):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("TopCard:", top_card)
        print("PlayHist:")
        for i in range(len(play_hist)):
            print(f"\t {i+1}: {play_hist[i]}")
        
        print("ScoreHist:")
        for i in range(len(score_hist)):
            print(f"\t {i+1}: {score_hist[i]}")

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
        # 1: Joga mais forte
        if self.posicao_mesa == 1:
            return 1, self.carta_maior

        # 2: Tenta ganhar, se não consegue descarta
        if self.posicao_mesa == 2:
            if self.carta_mais_forte_rodada is not None and self.valor_maior is not None:
                if self.valor_maior > card_value(self.carta_mais_forte_rodada, top_card):
                    return 1, self.carta_maior
            return 1, self.carta_menor

        # 3: Tenta ganhar, se não consegue descarta
        # Pode descartar se o aliado estiver ganhando
        if self.posicao_mesa == 3:
            if self.aliado_esta_ganhando:
                return 1, self.carta_menor

            if self.carta_mais_forte_rodada is not None and self.valor_maior is not None:
                if self.valor_maior > card_value(self.carta_mais_forte_rodada, top_card):
                    return 1, self.carta_maior
            return 1, self.carta_menor

        # 4: Tenta ganhar, se não consegue descarta
        # Pode descartar se o aliado estiver ganhando
        if self.posicao_mesa == 4:
            if self.carta_mais_forte_rodada is not None and self.valor_maior is not None:
                if self.valor_maior > card_value(self.carta_mais_forte_rodada, top_card):
                    return 1, self.carta_maior
            return 1, self.carta_menor

        return 1, self.carta_menor

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
            avaliacao_mao = avaliar_mao(
                self._cards,
                top_card,
                self.cartas_possiveis_adversarios,
                venceu_primeira_rodada=self.venceu_primeira_rodada,
            )

            if avaliacao_mao >= RDD2_LIMIAR_PEDIR_TRUCO and self.posicao_mesa == 1:
                return 2, self.carta_maior

            return 1, self.carta_maior

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
        chance_carta_maior = chance_carta_ser_mais_forte(
            self.cartas_possiveis_adversarios,
            self.carta_maior,
            top_card,
        )

        # Se a carta da terceira rodada estiver muito forte, vale tentar aumentar o valor da mão.
        if chance_carta_maior >= RDD3_LIMIAR_PEDIR_TRUCO and self.ultimo_time_truco != (self.position % 2) and self.valor_mao_atual < 12:
            return 2, self.carta_maior

        # Caso contrário, só joga a carta e tenta fechar a mão sem arriscar demais.
        return 1, self.carta_maior

    def responderTruco(self, top_card):
        avaliacao_mao = avaliar_mao(
            self._cards,
            top_card,
            self.cartas_possiveis_adversarios,
            venceu_primeira_rodada=self.venceu_primeira_rodada,
        )

        # para o caso de já estar em 12
        # counterar o bot greedy, chato dms
        if self.valor_mao_atual >= 12:
            return 1

        if avaliacao_mao < RESP_LIMIAR_CORRER:
            return 0

        if avaliacao_mao >= RESP_LIMIAR_AUMENTAR:
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
    return "algum nome"  # Defina aqui o nome da sua dupla


# Função que cria a dupla:
def create_pair():
    return (NonePlayer(), NonePlayer())  # Defina aqui a dupla de jogadores. Deve ser uma tupla com dois jogadores.


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