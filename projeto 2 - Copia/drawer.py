import pygame
import os # Para a fonte usada
from judge import card_value

WIDTH, HEIGHT = 1200, 800

SCREEN = None
CARD_FONT = None
SMALL_FONT = None
ROUND_FONT = None
RESULT_FONT = None

WHITE = (255, 255, 255)
LIGHT_GRAY = (211, 211, 211)
BLUE_IC = (11, 149, 222)  
ORANGE_IC = (255, 115, 1) 
BLACK = (0, 0, 0)
CARD_BG = (245, 245, 240)
CARD_BACK = (70, 70, 90)

CARD_WIDTH = 80
CARD_HEIGHT = 110
CARD_GAP = 14

SUIT_SYMBOL = {
    'Clubs': '♣',
    'Hearts': '♥',
    'Spades': '♠',
    'Diamonds': '♦'
}

# Iniciar variáveis globais
def init_drawer():
    global SCREEN, CARD_FONT, SMALL_FONT, ROUND_FONT, RESULT_FONT
    
    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Truco")
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR, "fonts", "dejavu-sans.condensed.ttf")

    try:
        CARD_FONT = pygame.font.Font(font_path, 30)
        SMALL_FONT = pygame.font.Font(font_path, 20)
    except FileNotFoundError:
        print(f"Erro: A fonte não foi encontrada em {font_path}. Usando fonte padrão.")
        CARD_FONT = pygame.font.SysFont("sans-serif", 30)
        SMALL_FONT = pygame.font.SysFont("sans-serif", 20)
    
    ROUND_FONT = pygame.font.SysFont(None, 28)
    RESULT_FONT = pygame.font.SysFont(None, 34)

# Função para controlar a velocidade das animações e pausas no Pygame
def pause(tempo_base_ms, multiplicador_velocidade):
    if multiplicador_velocidade <= 0:
        return 
    tempo_real = tempo_base_ms / multiplicador_velocidade
    if tempo_real > 0:
        pygame.time.wait(int(tempo_real))
        
# Retorna a representação em string do número e naipe de uma carta
def card_text(card):
    if card is None:
        return ""
    rank, suit = card
    symbol = SUIT_SYMBOL.get(suit, suit[0])
    return f"{rank}{symbol}"

# Desenha uma carta específica nas coordenadas fornecidas, virada para cima ou para baixo
def draw_card(x, y, card, face_up=True):
    # Se a carta é None (encoberta) ou face_up é False, usa o fundo de carta virada
    is_hidden = (card is None) or not face_up
    color = CARD_BACK if is_hidden else CARD_BG
    
    pygame.draw.rect(SCREEN, color, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=12)
    pygame.draw.rect(SCREEN, ORANGE_IC, (x, y, CARD_WIDTH, CARD_HEIGHT), 3, border_radius=12)
    
    if not is_hidden:
        rank, suit = card
        symbol = SUIT_SYMBOL.get(suit, suit[0])
        text_color = (200, 0, 0) if suit in ('Hearts', 'Diamonds') else BLACK
        
        rank_text = CARD_FONT.render(rank, True, text_color)
        SCREEN.blit(rank_text, (x + 8, y + 8))
        
        suit_text = CARD_FONT.render(symbol, True, text_color)
        SCREEN.blit(suit_text, suit_text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2)))
        
        small_text = SMALL_FONT.render(suit[0], True, text_color)
        SCREEN.blit(small_text, (x + CARD_WIDTH - small_text.get_width() - 8, y + CARD_HEIGHT - small_text.get_height() - 8))
        
    elif card is None:
        question_font = pygame.font.SysFont(None, 70, bold=True)
        q_surface = question_font.render("?", True, WHITE)
        q_surface.set_alpha(100)
        
        q_rect = q_surface.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
        SCREEN.blit(q_surface, q_rect)
        
# Escreve o valor da mão no canto inferior direito
def draw_hand_value(value):
    text_str = f"Valor da Mão: {value}"
    text_surface = RESULT_FONT.render(text_str, True, ORANGE_IC)
    text_rect = text_surface.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
    SCREEN.blit(text_surface, text_rect)
    
# Renderiza a mesa completa, incluindo vira, placares, cartas jogadas e janela de resultado
def draw_board(vira, round_cards, round_wins=None, team_names=None, match_score=None, round_result=None, current_player=None, current_player_name=None, hand_value=None):
    SCREEN.fill(LIGHT_GRAY)
    
    if vira is not None:
        draw_card(WIDTH // 2 - CARD_WIDTH // 2, HEIGHT // 2 - CARD_HEIGHT // 2, vira)
    
    if round_wins is not None:
        if team_names is not None:
            left_name, right_name = team_names
        else:
            left_name, right_name = "Time 1", "Time 2"
            
        title_text = SMALL_FONT.render("Pontuação Rodada Atual", True, WHITE)
        left_text = ROUND_FONT.render(f"{left_name}: {round_wins[0]}", True, WHITE)
        right_text = ROUND_FONT.render(f"{right_name}: {round_wins[1]}", True, WHITE)
        
        width = max(title_text.get_width(), left_text.get_width() + right_text.get_width() + 20) + 40
        height = title_text.get_height() + max(left_text.get_height(), right_text.get_height()) + 20
        
        bg_rect = pygame.Rect(WIDTH - width - 20, 12, width, height)
        box_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 0, 180), box_surface.get_rect(), border_radius=12)
        pygame.draw.rect(box_surface, WHITE, box_surface.get_rect(), 2, border_radius=12)
        SCREEN.blit(box_surface, bg_rect.topleft)
        
        SCREEN.blit(title_text, (bg_rect.centerx - title_text.get_width() // 2, bg_rect.top + 8))
        SCREEN.blit(left_text, (bg_rect.left + 12, bg_rect.top + title_text.get_height() + 12))
        SCREEN.blit(right_text, (bg_rect.right - right_text.get_width() - 12, bg_rect.top + title_text.get_height() + 12))

    if match_score is not None:
        if team_names is not None:
            left_name, right_name = team_names
        else:
            left_name, right_name = "Time 1", "Time 2"
            
        title_text = SMALL_FONT.render("Pontuação Jogo Atual", True, WHITE)
        left_text = ROUND_FONT.render(f"{left_name}: {match_score[0]}", True, WHITE)
        right_text = ROUND_FONT.render(f"{right_name}: {match_score[1]}", True, WHITE)
        
        width = max(title_text.get_width(), left_text.get_width() + right_text.get_width() + 20) + 40
        height = title_text.get_height() + max(left_text.get_height(), right_text.get_height()) + 20
        
        bg_rect = pygame.Rect(20, 12, width, height)
        box_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 0, 180), box_surface.get_rect(), border_radius=12)
        pygame.draw.rect(box_surface, WHITE, box_surface.get_rect(), 2, border_radius=12)
        SCREEN.blit(box_surface, bg_rect.topleft)
        
        SCREEN.blit(title_text, (bg_rect.centerx - title_text.get_width() // 2, bg_rect.top + 8))
        SCREEN.blit(left_text, (bg_rect.left + 12, bg_rect.top + title_text.get_height() + 12))
        SCREEN.blit(right_text, (bg_rect.right - right_text.get_width() - 12, bg_rect.top + title_text.get_height() + 12))

    # Lógica para destacar os empates da rodada
    strongest_positions = []
    if round_cards and vira is not None:
        valid_cards = [(pos, card) for pos, card in round_cards if card is not None]
        if valid_cards:
            max_value = max(card_value(card, vira) for pos, card in valid_cards)
            strongest_positions = [pos for pos, card in valid_cards if card_value(card, vira) == max_value]
    
    CX = WIDTH // 2 - CARD_WIDTH // 2
    CY = HEIGHT // 2 - CARD_HEIGHT // 2
    OFFSET_Y = 130
    OFFSET_X = 140
    draw_hand_value(hand_value)
    for pos, card in round_cards:
        if pos == 0:
            x, y = CX, CY - OFFSET_Y
        elif pos == 1:
            x, y = CX - OFFSET_X, CY
        elif pos == 2:
            x, y = CX, CY + OFFSET_Y
        else:
            x, y = CX + OFFSET_X, CY
            
        draw_card(x, y, card)
        if pos in strongest_positions:
            pygame.draw.rect(SCREEN, (255, 215, 0), (x - 5, y - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 4)

    if round_result is not None:
        winner, winning_card, winner_name = round_result
        
        display_text = winner_name if winning_card is None else f"{winner_name} ganhou com:"
        title_surface = RESULT_FONT.render(display_text, True, WHITE)
        
        box_width = max(title_surface.get_width(), CARD_WIDTH if winning_card else 0) + 80
        box_height = title_surface.get_height() + (CARD_HEIGHT + 30 if winning_card else 0) + 70
        
        box_rect = pygame.Rect(WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2, box_width, box_height)
        
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 0, 200), box_surface.get_rect(), border_radius=16)
        pygame.draw.rect(box_surface, WHITE, box_surface.get_rect(), 3, border_radius=16)
        SCREEN.blit(box_surface, box_rect.topleft)
        
        text_y = box_rect.top + 40 if winning_card else box_rect.centery - title_surface.get_height() // 2
        SCREEN.blit(title_surface, title_surface.get_rect(center=(box_rect.centerx, text_y)))
        
        if winning_card is not None:
            card_x = box_rect.centerx - CARD_WIDTH // 2
            card_y = box_rect.top + title_surface.get_height() + 50
            draw_card(card_x, card_y, winning_card)
            
HAND_W_OFFSET = int(CARD_WIDTH * 1.5 + CARD_GAP)
HAND_H_OFFSET = int(CARD_HEIGHT * 1.5 + CARD_GAP)
MARGIN = 90

PLAYER_POS = {
    0: ((WIDTH // 2 - HAND_W_OFFSET, MARGIN), (1, 0)),
    1: ((MARGIN, HEIGHT // 2 - HAND_H_OFFSET), (0, 1)),
    2: ((WIDTH // 2 - HAND_W_OFFSET, HEIGHT - CARD_HEIGHT - MARGIN), (1, 0)),
    3: ((WIDTH - CARD_WIDTH - MARGIN, HEIGHT // 2 - HAND_H_OFFSET), (0, 1))
}

square_surface = pygame.Surface((100, 100), pygame.SRCALPHA)

# Desenha o avatar e as cartas de um único jogador
def draw_player(number, image, cards, is_current=False):
    x = PLAYER_POS[number][0][0]
    y = PLAYER_POS[number][0][1]
    dx = PLAYER_POS[number][1][0]
    dy = PLAYER_POS[number][1][1]
    
    square_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(square_surface, (255, 255, 255, 128), (0, 0, 100, 100))
    square_surface.blit(image, (0, 0))
    
    img_x, img_y = x - dx * 110, y - dy * 110
    SCREEN.blit(square_surface, (img_x, img_y))
    pygame.draw.rect(SCREEN, BLACK, (img_x, img_y, 100, 100), 1) 
    
    if is_current:
        pygame.draw.circle(SCREEN, WHITE, (img_x + 50, img_y + 50), 55, 4)
        
    for card in cards:
        draw_card(x, y, card)
        x += dx * (CARD_WIDTH + CARD_GAP)
        y += dy * (CARD_HEIGHT + CARD_GAP)

# Itera sobre todos os jogadores desenhando as informações e apontando o turno atual
def draw_players(players, current_player=None):
    for player in players:
        draw_player(player.position, player.image, player.cards, player.position == current_player)

# Gerencia o redesenho da tela a cada rodada, com delay dinâmico
def draw_game(start, board, players, round_wins=None, team_names=None, match_score=None, round_result=None, current_player=None, current_player_name=None, delay_ms=1200, hand_value=1):
    active_player = None if round_result is not None else current_player

    if round_result is not None:
        draw_board(start, board, round_wins, team_names, match_score, None, current_player, current_player_name, hand_value)
        draw_players(players, active_player) 
        pygame.display.flip()
        
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < delay_ms:
            pygame.event.pump()
        
    draw_board(start, board, round_wins, team_names, match_score, round_result, current_player, current_player_name, hand_value)
    draw_players(players, active_player)
    pygame.display.flip()

# Desenha uma dupla (duas imagens e nome) para a tela de versus
def draw_match_pair(pair_name, pair, x, losse=False):
    font = pygame.font.Font(None, 75)
    text_surface = font.render(pair_name, True, WHITE)
    vs_rect = text_surface.get_rect(center=(x, HEIGHT // 2 - 80))
    SCREEN.blit(text_surface, vs_rect)
    
    img_gap = 20
    img1_x = x - 100 - (img_gap // 2)
    img2_x = x + (img_gap // 2)
    img_y = HEIGHT // 2 - 10
    
    square_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(square_surface, (255, 255, 255, 128), (0, 0, 100, 100))
    square_surface.blit(pair[0].image, (0, 0))
    SCREEN.blit(square_surface, (img1_x, img_y))
    pygame.draw.rect(SCREEN, BLACK, (img1_x, img_y, 100, 100), 1)
    
    square_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(square_surface, (255, 255, 255, 128), (0, 0, 100, 100))
    square_surface.blit(pair[1].image, (0, 0))
    SCREEN.blit(square_surface, (img2_x, img_y))
    pygame.draw.rect(SCREEN, BLACK, (img2_x, img_y, 100, 100), 1)
    
    if losse:
        font = pygame.font.Font(None, 400)
        text_surface = font.render("X", True, ORANGE_IC)
        vs_rect = text_surface.get_rect(center=(x, HEIGHT // 2 + 40))
        SCREEN.blit(text_surface, vs_rect)

# Desenha a tela de apresentação antes de começar uma série de partidas entre duas duplas
def draw_match(pair_names, pairs, start=True, lossers=[]):
    SCREEN.fill(BLUE_IC)
    bolt_points = [
        (WIDTH // 2, HEIGHT // 4),
        (WIDTH // 2 + 30, HEIGHT // 3),
        (WIDTH // 2 - 20, HEIGHT // 2),
        (WIDTH // 2 + 20, 2 * HEIGHT // 3),
        (WIDTH // 2 - 10, 3 * HEIGHT // 4),
        (WIDTH // 2, HEIGHT * 3 // 4 + 30),
    ]
    pygame.draw.lines(SCREEN, WHITE, False, bolt_points, 10)
    font = pygame.font.Font(None, 200)
    text_surface = font.render("VS", True, ORANGE_IC)
    vs_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    SCREEN.blit(text_surface, vs_rect)
    font = pygame.font.Font(None, 100)
    if start:
        text_surface = font.render("Início", True, WHITE)
        draw_match_pair(pair_names[0], pairs[pair_names[0]], WIDTH // 4)
        draw_match_pair(pair_names[1], pairs[pair_names[1]], 3 * WIDTH // 4)
    else:
        text_surface = font.render("Fim", True, WHITE)
        draw_match_pair(pair_names[0], pairs[pair_names[0]], WIDTH // 4, lossers[0])
        draw_match_pair(pair_names[1], pairs[pair_names[1]], 3 * WIDTH // 4, lossers[1])
    vs_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 8))
    SCREEN.blit(text_surface, vs_rect)
    pygame.display.flip()

# Exibe as imagens e o nome de uma dupla em uma determinada posição do pódio
def draw_double(name, pair, podium_rect):
    font = pygame.font.Font(None, 42)
    text_surface = font.render(name, True, WHITE)
    text_rect = text_surface.get_rect(center=(podium_rect.centerx, podium_rect.centery))
    SCREEN.blit(text_surface, text_rect)
    
    img1_x, img1_y = podium_rect.left - 110, podium_rect.centery - 50
    img2_x, img2_y = podium_rect.right + 10, podium_rect.centery - 50
    
    SCREEN.blit(pair[0].image, (img1_x, img1_y))
    pygame.draw.rect(SCREEN, BLACK, (img1_x, img1_y, 100, 100), 1)
    
    SCREEN.blit(pair[1].image, (img2_x, img2_y))
    pygame.draw.rect(SCREEN, BLACK, (img2_x, img2_y, 100, 100), 1)

# Monta o visual final do encerramento do campeonato mostrando as pontuações e pódio
def draw_podium(scores, pairs):
    SCREEN.fill(BLUE_IC)
    first_place = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 6)
    second_place = pygame.Rect(WIDTH // 4 + 50, HEIGHT // 4 + HEIGHT // 6 + 50, WIDTH // 2 - 100, HEIGHT // 6)
    third_place = pygame.Rect(WIDTH // 4 + 100, HEIGHT // 4 + HEIGHT // 6 + HEIGHT // 6 + 100, WIDTH // 2 - 200, HEIGHT // 6)
    pygame.draw.rect(SCREEN, (255, 215, 0), first_place)
    pygame.draw.rect(SCREEN, (192, 192, 192), second_place)
    pygame.draw.rect(SCREEN, (205, 127, 50), third_place)
    if len(scores) > 0:
        draw_double("1ro - " + scores[0].pair_name, pairs[scores[0].pair_name], first_place)
    if len(scores) > 1:
        draw_double("2do - " + scores[1].pair_name, pairs[scores[1].pair_name], second_place)
    if len(scores) > 2:
        draw_double("3ro - " + scores[2].pair_name, pairs[scores[2].pair_name], third_place)
    pygame.display.flip()