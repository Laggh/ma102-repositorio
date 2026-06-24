import random
from judge import card_value

# Define a classe do jogador (Player): deve ser herdada para implementar a estratégia de jogo
class Player:
    def __init__(self, ra, name, image_path="img/none.jpg"):
        self._name = name
        self._cards = []
        self._position = 0
        self._image_path = image_path
        self._image = None
        self._ra = ra

    @property
    def name(self):
        return self._name

    @property
    def ra(self):
        return self._ra

    @property
    def image_path(self):
        return self._image_path

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def cards(self):
        return self._cards.copy()

    @cards.setter
    def cards(self, value):
        self._cards = value.copy()

    def remove_card(self, card):
        if card in self._cards:
            self._cards.remove(card)

    def __str__(self):
        return f"{self.name}({self.ra})"

    def play(self, top_card, play_hist, score_hist):
        # Lógica de jogar carta a ser implementada por classes herdeiras
        pass
        
    def respond(self, top_card, play_hist, score_hist):
        # Função para resposta a trucos ou aumentos
        return 1

# Define a classe do jogador tolo (DummyPlayer)
# Sempre faz opções válidas aleatórias
class DummyPlayer(Player):

    def play(self, top_card, play_hist, score_hist):
        # O DummyPlayer nunca truca e joga uma carta aleatória válida
        return 1, random.choice(self._cards)
        
        
    def respond(self, top_card, play_hist, score_hist):
        # Resposta aleatória válida
        return random.choice((0,1,2 if score_hist[-1][1]!=12 else 1))


# Define a classe do jogador ganancioso (GreedyPlayer)
# Joga sempre a melhor carta de primeira e pede truco se tiver uma manilha
# Sempre aumenta se possível o truco e aceita se não poder aumentar
class GreedyPlayer(Player):

    def play(self, top_card, play_hist, score_hist):
        best_card = self._cards[0]
        best_value = card_value(best_card, top_card)
        
        for card in self._cards:
            current_value = card_value(card, top_card)
            if current_value > best_value:
                best_card = card
                best_value = current_value
        
        team = (self.position, (self.position+2)%4)
        can_truco = True
        for play in play_hist[-1]:
            if play[2] in (3, 6, 9):
                can_truco = (play[0] not in team)
        if best_value >= 1000 and score_hist[-1][1] != 12 and can_truco:
            return 2, best_card
        return 1, best_card

    def respond(self, top_card, play_hist, score_hist):
        if score_hist[-1][1] != 12:
            return 2
        return 1
  
# Define a classe do jogador "cauteloso" (ReveseGreedyPlayer)
# Deixa as melhores cartas para serem jogadas no final a não ser que tenha perdido a primeira rodada, aí joga a melhor carta para tentar ganhar a segunda rodada
# Só aceita trucos se tiver pelo menos uma carta que é manilha e aceita com pelo menos um 3 
# Só envia truco na última rodada se tiver uma manilha ou 3
# Se ele receber um truco na última jogada possível, ou seja ninguém mais tem cartas para jogar, ele só aceita se seu time tiver um três ou manilha jogada
class ReverseGreedyPlayer(Player):
    
    def play(self, top_card, play_hist, score_hist):
        best_card = self._cards[0]
        best_value = card_value(best_card, top_card)
        worst_card = self._cards[0]
        worst_value = card_value(worst_card, top_card)
        
        for card in self._cards:
            val = card_value(card, top_card)
            if val > best_value:
                best_card, best_value = card, val
            if val < worst_value:
                worst_card, worst_value = card, val
        
        lost_first_round = False
        
        if len(self._cards) == 2:
            round1_plays = []
            for plays in play_hist[-1]:
                if plays[1] is not None:
                    round1_plays.append(plays)
            t0_max = 0
            t1_max = 0
            
            for p_idx, card, _ in round1_plays:
                val = card_value(card, top_card)
                if p_idx in (0, 2):
                    t0_max = max(t0_max, val)
                else:
                    t1_max = max(t1_max, val)
            
            my_team = (self.position, (self.position + 2) % 4)
            my_team_id = 0 if 0 in my_team else 1
            
            if my_team_id == 0:
                lost_first_round = (t1_max > t0_max)
            else:
                lost_first_round = (t0_max > t1_max)

        chosen_card = best_card if lost_first_round else worst_card
        chosen_value = best_value if lost_first_round else worst_value

        team = (self.position, (self.position+2)%4)
        can_truco = True
        if len(play_hist)>0:
            for play in play_hist[-1]:
                if play[2] in (3, 6, 9):
                    can_truco = (play[0] not in team)

        if len(self._cards) == 1 and (chosen_value >= 1000 or best_card[0] == '3') and can_truco:
            if score_hist[-1][1] != 12:
                return 2, chosen_card
        return 1, chosen_card

    def respond(self, top_card, play_hist, score_hist):
        if len(self.cards) != 0:
            best_card = self._cards[0]
            best_value = card_value(best_card, top_card)
            
            for card in self._cards[1:]:
                current_value = card_value(card, top_card)
                if current_value > best_value:
                    best_card = card
                    best_value = current_value
                    
            if score_hist[-1][1] != 12 and best_value >= 1000:
                return 2
            if best_card[0] == '3':
                return 1
        else:
            team = (self.position, (self.position + 2) % 4)

            recent_plays = play_hist[-1][::-1]
            
            cards_found = 0
            for play in recent_plays:
                p_id = play[0]
                card = play[1]
                if card is not None:
                    if p_id in team:
                        val = card_value(card, top_card)
                        if val >= 1000 or card[0] == '3':
                            return 1
                    if cards_found == 4:
                        break
                    cards_found += 1
        return 0
    
    