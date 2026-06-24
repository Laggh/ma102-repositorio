import pygame
import random
import sys
from drawer import draw_game, draw_match, draw_podium, init_drawer, pause
from judge import Judge
from basic_players import GreedyPlayer, DummyPlayer, ReverseGreedyPlayer
from student_players import pair_name, create_pair

# Classe que gerencia as estatísticas de desempenho de cada dupla no torneio
class Score:
    def __init__(self, pair_name):
        self._pair_name = pair_name
        self._game = [0, 0]
        self._match = [0, 0]

    @property
    def pair_name(self): return self._pair_name
    
    @property
    def sorting_attribute(self): return self._match + self._game

    # Atualiza o saldo de jogos ganhos e perdidos
    def _update_score(self, wins=0, losses=0):
        self._game[0] += wins
        self._game[1] += losses

    # Registra uma vitória na série de confrontos
    def new_match_win(self, wins=1, losses=0):
        self._match[0] += 1
        self._update_score(wins, losses)

    # Registra uma derrota na série de confrontos
    def new_match_losse(self, wins=0, losses=1):
        self._match[1] += 1
        self._update_score(wins, losses)

    def __str__(self):
        return (f"{self._pair_name} - CONFRONTOS[{self._match[0]} Vitórias, {self._match[1]} Derrotas] "
                f"- JOGOS[{self._game[0]} Vitórias, {self._game[1]} Derrotas]")


PAIRS = {
    'Dummy': (DummyPlayer(1, "Patrick Star", "img/Patrick_Star.jpeg"), DummyPlayer(2, "Philip Fry", "img/Philip_Fry.jpg")),
    'Greedy': (GreedyPlayer(3, "Scrooge McDuck", "img/Scrooge_McDuck.jpg"), GreedyPlayer(4, "Mr Burns", "img/Mr_Burns.jpg")),
    'Mixed': (DummyPlayer(5, "Mr Krabs", "img/Mr_Krabs.jpeg"), GreedyPlayer(6, "Mr Burns", "img/Mr_Burns.jpg")),
    'ReverseGreedy': (ReverseGreedyPlayer(7, "sbarK rM",  "img/Mr_KrabsR.png"), ReverseGreedyPlayer(8, "snruB yremogtnoM",  "img/Mr_BurnsR.png")),
    'Mixed2': (ReverseGreedyPlayer(9, "kcuDcM egoorcS", "img/Scrooge_McduckR.png"), GreedyPlayer(10, "Montgomery Burns", "img/Mr_Burns.jpg")),
    pair_name(): create_pair() # Adiciona a sua própria dupla
}

# Gerencia um único jogo de Truco até que uma dupla chegue a 12 pontos
def play_game(judge, players, speed, first, team_names):
    judge.start_game(players, first) # Inicializa o jogo
    
    # Renderiza o estado inicial da mesa se o modo visual estiver ativo
    if speed > 0:
        draw_game(judge.start, judge.board, players, judge.round_wins, team_names, judge.match_score, None, judge._current, players[judge._current].name, judge._hand_value)
        pygame.display.flip()
        pause(500, speed)
    
    # Loop principal da partida: continua enquanto ninguém atingir 12 pontos
    while not judge.ended:
        if judge.hand_ended:
            judge.next_hand()
        
        hist_index_before = len(judge._play_hist[-1])
        display_hand_value = judge._hand_value
        
        judge.play()
        
        new_history = judge._play_hist[-1][hist_index_before:]
        
        temp_board = judge.board.copy()
        
        card_played = any(card_info is not None for _, card_info, _ in new_history)
        waiting_card = None
        

        if card_played and len(temp_board) > 0:
            waiting_card = temp_board.pop()
        
        proposed_value = display_hand_value

        for play in new_history:
            player_idx, card_info, action = play
            p_name = players[player_idx].name
            msg = None

            if isinstance(action, int):
                terms = {3: "TRUCO!", 6: "SEIS!", 9: "NOVE!", 12: "DOZE!"}
                msg = f"{p_name}: {terms.get(action, 'AUMENTOU!')}"
                proposed_value = action
                
            elif action == 'CORREU':
                msg = f"{p_name} CORREU!"
            elif action == 'ACEITOU':
                msg = f"{p_name} ACEITOU!"
                display_hand_value = proposed_value

            if msg and speed > 0:
                draw_game(judge.start, temp_board, players, judge.round_wins, team_names, 
                            judge.match_score, (None, None, msg), player_idx, 
                            p_name, hand_value=display_hand_value)
                pygame.display.flip()
                pause(1000, speed)
                
            if card_info is not None and waiting_card is not None:
                temp_board.append(waiting_card)
                if speed > 0:
                    draw_game(judge.start, temp_board, players, judge.round_wins, team_names, 
                              judge.match_score, None, player_idx, 
                              p_name, hand_value=display_hand_value)
                    pygame.display.flip()
                    pause(400, speed)

        round_result = None
        if judge.show_round_result:
            round_result = (judge.last_round_winner, judge.last_round_winner_card, players[judge.last_round_winner].name)
        
        if speed > 0:
            draw_game(judge.start, judge.board, players, judge.round_wins, team_names, judge.match_score, 
                      round_result, judge._current, players[judge._current].name, hand_value=judge._hand_value)
            pygame.display.flip()
        
        if judge.show_round_result:
            if speed > 0:
                pause(1200, speed)
            judge.clear_round_result() 
        else:
            if speed > 0:
                pause(600, speed)
            
        if speed > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
    return judge.winner()

# Gerencia um confronto que pode consistir em vários jogos de 12 pontos
def run_match(judge, pair1, pair2, number, speed, team_names):
    players = [pair1[0], pair2[0], pair1[1], pair2[1]]
    for i in range(len(players)):
        players[i].position = i 
    
    wins = [0] * 2
    first = random.randint(0, 3) 
    
    # Loop da série de jogos
    for i in range(number):
        print(f"-- Iniciando jogo (até 12 pontos): {i+1}")
        winner = play_game(judge, players, speed, first, team_names)
        
        if winner is not None:
            idx_dupla = winner % 2
            wins[idx_dupla] += 1
            p1 = players[idx_dupla].name
            p2 = players[idx_dupla + 2].name
            print(f"-- Fim do jogo {i+1}. Vencedores: {p1} e {p2}!")
        
        # O próximo jogador à esquerda começa distribuindo na próxima partida
        first = (first + 1) % 4
        
    return wins


# Função principal que organiza o torneio "Todos contra Todos"
def run_tournament(number, speed, waiting):
    if speed > 0:
        init_drawer()
        pygame.init()
        for pair in PAIRS.values():
            for player in pair:
                try:
                    image = pygame.image.load(player.image_path)
                    image = pygame.transform.scale(image, (100, 100))
                    player.image = image
                except: pass

    judge = Judge()
    scores = [Score(key) for key in PAIRS]
        
    # Sistema de rodízio: cada dupla joga contra todas as outras
    for i in range(len(scores)):
        for j in range(i + 1, len(scores)):
            p1_n, p2_n = scores[i].pair_name, scores[j].pair_name
            
            if speed > 0:
                draw_match([p1_n, p2_n], PAIRS)
                pygame.display.flip()
                pygame.time.wait(2000) 
                pause(waiting, speed)
            
            print(f"\nCONFRONTO DE {number} JOGOS ENTRE: {p1_n} E {p2_n}.")
            wins = run_match(judge, PAIRS[p1_n], PAIRS[p2_n], number, speed, (p1_n, p2_n))
            
            print(f"RESULTADO DO CONFRONTO: {p1_n} fez {wins[0]} vitórias, e {p2_n} fez {wins[1]} vitórias.")
            
            if speed > 0:
                draw_match([p1_n, p2_n], PAIRS, start=False, lossers=[wins[0] < wins[1], wins[0] > wins[1]])
                pygame.display.flip()
                pygame.time.wait(1500)
            
            if wins[0] > wins[1]:
                scores[i].new_match_win(wins=wins[0], losses=wins[1])
                scores[j].new_match_losse(wins=wins[1], losses=wins[0])
            else:
                scores[i].new_match_losse(wins=wins[0], losses=wins[1])
                scores[j].new_match_win(wins=wins[1], losses=wins[0])
                
    scores = sorted(scores, key=lambda x: x.sorting_attribute, reverse=True)
    
    if speed > 0:
        draw_podium(scores, PAIRS)
        pygame.display.flip()
    
    print("\n" + "="*50)
    print("CLASSIFICAÇÃO FINAL:")
    print("="*50)
    for i in range(len(scores)):
        p_info = PAIRS[scores[i].pair_name]
        print(f"{i+1}º Lugar - {scores[i].pair_name} ({p_info[0].name} e {p_info[1].name})")
        print(f"   {scores[i]}")
        
    if speed > 0:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
    else:
        pygame.quit()
        print("\nTorneio finalizado via Terminal.")