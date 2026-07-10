import random

RANK_ORDER = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
SUIT_ORDER = ['Diamonds', 'Spades', 'Hearts', 'Clubs']
SUIT_SYMBOL = {'Clubs': '♣', 'Hearts': '♥', 'Spades': '♠', 'Diamonds': '♦'}

# Gera o deck
def generate_deck():
    return [(rank, suit) for rank in RANK_ORDER for suit in SUIT_ORDER]

# Calcula o desempate de manilhas
def manilha_rank(vira_rank):
    index = RANK_ORDER.index(vira_rank)
    return RANK_ORDER[(index + 1) % len(RANK_ORDER)]

# Calcula o valor de uma carta dado o vira
def card_value(card, vira):
    if card is None: return 0
    if card == ('?', '?'): return 0
    rank, suit = card
    vira_rank = vira[0] if isinstance(vira, tuple) else vira
    m_rank = manilha_rank(vira_rank)
    if rank == m_rank:
        return 1000 + SUIT_ORDER.index(suit)
    return 100 + RANK_ORDER.index(rank)

class Judge:
    def __init__(self):
        self._match_score = [0, 0]
        self._ended = False
        self._play_hist = []
        self._score_hist = []
        
    def start_game(self, players, first):
        self._players = players
        self._current = first
        self._match_score = [0, 0]
        self._ended = False
        self._play_hist = []
        self._score_hist = []
        self.next_hand()

    # Distribui as cartas, define o vira e reseta as variáveis para a próxima mão
    def next_hand(self):
        self._deck = generate_deck()
        random.shuffle(self._deck)
        self._players_cards = []
        for i in range(4):
            hand = [self._deck.pop() for _ in range(3)]
            self._players_cards.append(hand)
            self._players[i].cards = hand
        
        self._vira = self._deck.pop()
        self._hand_value = 1
        self._proposed_value = 1
        self._round_wins = [0, 0]
        self._hand_ended = False
        
        self._score_hist.append([self._match_score.copy(), self._hand_value])
        self._play_hist.append([])
        
        self._round_cards = []
        self._last_truco_team = None
        self._show_round_result = False

    @property
    def ended(self): return self._ended
    @property
    def hand_ended(self): return self._hand_ended
    @property
    def board(self): return self._round_cards
    @property
    def vira(self): return self._vira
    @property
    def start(self): return self._vira
    @property
    def round_wins(self): return self._round_wins
    @property
    def match_score(self): return self._match_score
    @property
    def show_round_result(self): return self._show_round_result
    @property
    def hand_value(self): return self._hand_value

    # Limpa o resultado da rodada para a próxima rodada, mantendo as cartas na mesa até o final da mão
    def clear_round_result(self):
        self._show_round_result = False
        if self._hand_ended: return
        self._round_cards = []

    # Dá o índice do time do jogador(não de seu parceiro, time 0 ou 1)
    def _player_team(self, player_idx):
        return player_idx % 2

    # Pega a resposta a um truco, seis, nove, doze, desistência ou aceitação
    def response_truco(self, idx_player):
        player = self._players[idx_player]
        response = player.respond(self._vira, self._play_hist.copy(), self._score_hist.copy())
        return response

    # De fato simula a jogada de um jogador, incluindo a lógica de truco e resolução de rodadas e mãos
    def play(self):
        if self.ended or self.hand_ended:
            return
        player = self._players[self._current]
        my_hand = self._players_cards[self._current]
        my_team = self._player_team(self._current)
        
        decision, card = player.play(self._vira, self._play_hist.copy(), self._score_hist.copy())
        is_invalid = False
        # Decisão inexistente
        if decision not in (0, 1, 2):
            is_invalid = True
        # Garante que o truco poderia ter sido jogado
        elif decision == 2 and (self._last_truco_team == my_team or self._hand_value >= 12):
            is_invalid = True
        # Garante que a carta jogada estava na sua mão
        elif decision in (0, 1, 2) and card not in my_hand:
            is_invalid = True
            
        if is_invalid:
            # Print para mais fácil detecção de erro
            print(f"Foi feita uma jogada inválida, decisão = {decision}, carta = {card}, mão = {my_hand}, jogador = {player.name}, histórico = {self._play_hist[-1]}, vira = {self._vira}, valor = {self._hand_value}")
            # Se a jogada foi dada como inválida o que acontecerá é que você jogará a primeira carta da sua mão no modo normal
            decision = 1
            if my_hand:
                card = my_hand[0]
            else:
                card = None

        action_str = 'NORMAL'
        
        if decision == 2:
            # Dicionário para facilitar o cálculo do próximo valor do truco
            truco_values = {1: 3, 3: 6, 6: 9, 9: 12}
            self._proposed_value = truco_values.get(self._hand_value, 12)
            
            self._last_truco_team = my_team
            
            #  Definimos quem começa perguntando e quem responde
            asker = self._current
            responder = (self._current + 1) % 4
            asking_team = my_team
            
            #  Loop de negociação
            while True:
                # Registra o pedido no histórico com None para não passar informação extra
                self._play_hist[-1].append([asker, None, self._proposed_value])
                
                # O adversário responde
                response = self.response_truco(responder)
                
                if response == 0:  # CORREU
                    self._play_hist[-1].append([responder, None, 'CORREU'])
                    # Quem pediu o truco ganha a rodada
                    self._round_wins[asking_team] = 2
                    self._round_wins[1 - asking_team] = 0
                    self._resolve_hand()
                    return
                    
                # Se ACEITOU, ou se tentou AUMENTAR quando o valor já é 12 (considerado Aceitar)
                elif response == 1 or (response == 2 and self._proposed_value == 12):
                    self._hand_value = self._proposed_value
                    self._score_hist[-1][1] = self._hand_value
                    self._play_hist[-1].append([responder, None, 'ACEITOU'])
                    # Sai do loop, e o jogo de cartas continua normalmente com a carta de quem pediu truco pela prieira vez sendo jogada
                    break 
                    
                elif response == 2:  # AUMENTOU
                    # Ele aceita o valor atual antes de mandar de volta
                    self._hand_value = self._proposed_value
                    self._score_hist[-1][1] = self._hand_value
                    # Inverte os papéis das duplas para o próximo ciclo
                    self._last_truco_team = 1 - asking_team
                    asking_team = 1 - asking_team
                    
                    # Puxa o próximo valor (se era 3 vira 6, se era 6 vira 9 e se era 9 vira 12)
                    self._proposed_value = truco_values.get(self._proposed_value, 12)
                    
                    # Quem respondeu agora vira quem pergunta
                    asker, responder = responder, asker
            
            # Força a carta que acompanha o truco aceito a ter action_str 'NORMAL'
            action_str = 'NORMAL'

        # Aqui de fato a carta é removido da mão do jogador depois da negociação ou jogada normal
        player.remove_card(card)
        if card in my_hand:
            my_hand.remove(card)
            
        # Carta jogada escondida
        if decision == 0:
            hist_card = ('?', '?')
            table_card = None 
            action_str = 'ENCOBERTA' 
        else:
            hist_card = card
            table_card = card
            
        # Atualização do histórico e passa turno
        self._play_hist[-1].append([self._current, hist_card, action_str])
        self._round_cards.append((self._current, table_card))
        self._current = (self._current + 1) % 4
        
        # Isso quer dizer que os 4 jogadores já jogaram suas respectivas cartas
        if len(self._round_cards) == 4:
            self._resolve_round()

    # Determina o resultado de um round
    def _resolve_round(self):
        # Mapeia as cartas jogadas separando-as por time
        t0_cards = [(p, c) for p, c in self._round_cards if p % 2 == 0]
        t1_cards = [(p, c) for p, c in self._round_cards if p % 2 == 1]
        
        # Calcula o valor das cartas de cada time
        vals_t0 = [card_value(c, self._vira) for _, c in t0_cards]
        vals_t1 = [card_value(c, self._vira) for _, c in t1_cards]
        
        # Maior valor da dupla
        t0_max = max(vals_t0)
        t1_max = max(vals_t1)
        
        # Determina que time ganha pontos
        round_winner = -1
        if t0_max > t1_max:
            self._round_wins[0] += 1
            round_winner = 0
            self.last_round_winner = t0_cards[0][0] if vals_t0[0] > vals_t0[1] else t0_cards[1][0]
            
        elif t1_max > t0_max:
            self._round_wins[1] += 1
            round_winner = 1
            self.last_round_winner = t1_cards[0][0] if vals_t1[0] > vals_t1[1] else t1_cards[1][0]
            
        else:
            self._round_wins[0] += 1; self._round_wins[1] += 1
            round_winner = -1
            self.last_round_winner = self._round_cards[0][0]

        if getattr(self, '_first_round_winner', None) is None:
            self._first_round_winner = round_winner
        elif self._first_round_winner == -1: 
            self._first_round_winner = round_winner
            
        self.last_round_winner_card = next(c for p, c in self._round_cards if p == self.last_round_winner)
        self._current = self.last_round_winner
        self._show_round_result = True
        
        # Se posível, aqui é terminada a mão e lançada o resultado da mão
        if self._round_wins[0] >= 2 or self._round_wins[1] >= 2:
            self._resolve_hand()
            
    # Determina o ganhador de uma mão
    def _resolve_hand(self):
        #  Alguém ganhou de forma clara
        if self._round_wins[0] > self._round_wins[1]: 
            self._match_score[0] += self._hand_value
        elif self._round_wins[1] > self._round_wins[0]: 
            self._match_score[1] += self._hand_value
            
        # Empate nas rodadas (Placar 2x2)
        else:
            # Se alguém ganhou a 1ª (ou a 2ª caso a 1ª tenha empatado)
            if getattr(self, '_first_round_winner', -1) != -1:
                self._match_score[self._first_round_winner] += self._hand_value
                
            # Se TODAS as rodadas empataram (_first_round_winner continuou -1)
            else:
                # Se tudo empatar, ganha quem começou a mão
                primeiro_jogador_da_mao = self._play_hist[-1][0][0]
                time_vencedor = primeiro_jogador_da_mao % 2
                self._match_score[time_vencedor] += self._hand_value

        self._hand_ended = True
        if self._match_score[0] >= 12 or self._match_score[1] >= 12: 
            self._ended = True
    
    # Determina o vencedor de um jogo inteiro
    def winner(self):
        if self._ended: return 0 if self._match_score[0] > self._match_score[1] else 1
        return None