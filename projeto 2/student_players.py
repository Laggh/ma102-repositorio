### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    [NOME COMPLETO #01] 
# RA #01 (quem entregou o código):      [RA #01]
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]
import os

from basic_players import Player


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



# Implemente neste arquivo seus jogadores para Truco

# Jogador que não faz nada. Substitua esta classe para criar as suas, devem herdar da classe Player
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
        self.printState(top_card, play_hist, score_hist)

        play_hist_jogada = play_hist[-1] if play_hist else []
        posicao_jogada = len(play_hist_jogada) % 4
        carta_forte = None
            


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
