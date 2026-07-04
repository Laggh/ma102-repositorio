### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    [NOME COMPLETO #01] 
# RA #01 (quem entregou o código):      [RA #01]
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]
import os

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

PESO_MEDIA_CHANCE_PADRAO = 0.7
PESO_MEDIA_VALOR_PADRAO = 0.3

PESO_CHANCE_MANILHA = 0.5
PESO_VALOR_MANILHA = 0.5

BONUS_QTD_MANILHAS = 0.25
BONUS_MELHOR_MANILHA = 0.5

MULTIPLICADOR_MAO_MANILHA_3 = 1.1
MULTIPLICADOR_MAO_BASE_2 = 1.1

MULTIPLICADOR_VENCEU_PRIMEIRA_RODADA = 1.15
MULTIPLICADOR_PERDEU_PRIMEIRA_RODADA = 0.9

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
        return 1.0 + (valor_base - 1000) / 10.0
    return valor_base / 100.0


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

    # Função para retornar o que você vai jogar em determinada mão
    def play(self, top_card, play_hist, score_hist):
        #self.printState(top_card, play_hist, score_hist)

        play_hist_jogada = play_hist[-1] if play_hist else []

        cartas_possiveis_adversarios = gerar_baralho_completo()

        for carta in self._cards:
            if carta in cartas_possiveis_adversarios:
                cartas_possiveis_adversarios.remove(carta)

        if top_card in cartas_possiveis_adversarios:
            cartas_possiveis_adversarios.remove(top_card)

        for jogada in play_hist_jogada:
            if len(jogada) > 1:
                carta_jogada = jogada[1]
                if carta_jogada is not None and carta_jogada != ('?', '?') and carta_jogada in cartas_possiveis_adversarios:
                    cartas_possiveis_adversarios.remove(carta_jogada)

        # Jogadas que realmente colocaram carta na mesa nesta mão
        jogadas_com_carta = []
        for jogada in play_hist_jogada:
            if len(jogada) > 1 and jogada[1] is not None:
                jogadas_com_carta.append(jogada)

        # Posição atual na mesa: 1 = primeiro a jogar na rodada, 2 = segundo, etc.
        posicao_mesa = len(jogadas_com_carta) % 4 + 1

        # Cartas já jogadas na rodada atual (ignorando truco e pedidos de aumento)
        jogadas_da_rodada = jogadas_com_carta[-(len(jogadas_com_carta) % 4):] if len(jogadas_com_carta) % 4 else []

        # Carta mais forte que apareceu até agora na rodada atual
        cartas_visiveis = []
        for jogada in jogadas_da_rodada:
            if jogada[1] != ('?', '?'):
                cartas_visiveis.append(jogada[1])
        carta_mais_forte_rodada = max(
            cartas_visiveis,
            key=lambda carta: card_value(carta, top_card),
            default=None,
        )



        if self._cards:
            return 1, self._cards[0]
        return 1, None

    # Função para retornar o que você vai dar de resposta a trucos
    def respond(self,top_card,play_hist, score_hist):
        return 0


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