### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    [NOME COMPLETO #01] 
# RA #01 (quem entregou o código):      [RA #01]
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]
from basic_players import Player

# Implemente neste arquivo seus jogadores para Truco

# Jogador que não faz nada. Substitua esta classe para criar as suas, devem herdar da classe Player
class NonePlayer(Player):
    # Se estiver dúvida sobre como começar olhe os players prontos em basic_players.py e o ReadMe
    def __init__(self):
        super().__init__(0, "Ninguém") # Nome do Jogador

    # Função para retornar o que você vai jogar em determinada mão
    def play(self, top_card, play_hist, score_hist):
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
