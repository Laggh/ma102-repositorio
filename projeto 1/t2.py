"""Torneio de debug para avaliar estratégias com escolha do tipo de regra.

Este script é uma variante de `tournament.py` que permite fixar o tipo
da regra secreta por meio de `input()`, facilitando testes e depuração.
"""

from importlib import reload
from pathlib import Path

import player
from game import direction, guess_rule, verify_player_guess

try:
    from tqdm import tqdm
except ImportError:
    print("Tqdm não foi instalado. Instale com: python -m pip install tqdm")
    raise SystemExit(1)


OUTPUT_DIR = Path(__file__).resolve().parent / "out"


def prompt_text(message, default):
    """Lê texto do usuário com valor padrão."""
    raw_value = input(f"{message} [{default}]: ").strip()
    return raw_value or default


def prompt_int(message, default):
    """Lê um inteiro do usuário com valor padrão e validação simples."""
    while True:
        raw_value = input(f"{message} [{default}]: ").strip()
        if not raw_value:
            return default
        try:
            value = int(raw_value)
        except ValueError:
            print("Digite um número inteiro válido.")
            continue
        if value <= 0:
            print("Digite um número maior que zero.")
            continue
        return value


def get_debug_config():
    """Solicita a configuração de debug via input()."""
    print("\nConfiguração do torneio de debug")
    print("Tipos disponíveis: random, mod, pot, int")
    rule_type = prompt_text("Tipo da regra", "random").lower()
    while rule_type not in {"random", "mod", "pot", "int"}:
        print("Tipo inválido. Use random, mod, pot ou int.")
        rule_type = prompt_text("Tipo da regra", "random").lower()

    max_games = prompt_int("Quantidade de partidas", 1000)
    max_attempts = prompt_int("Máximo de tentativas por partida", 1000)
    
    save_mode = prompt_text("Salvar apenas erros? (s/n)", "n").lower()
    save_only_errors = save_mode in {"s", "sim", "yes", "y"}

    return rule_type, max_games, max_attempts, save_only_errors


def choose_rule(rule_type="random"):
    """Escolhe uma regra aleatória ou fixa pelo tipo pedido."""
    import random

    if rule_type == "random":
        rule_type = random.choice(["mod", "pot", "int"])

    if rule_type == "mod":
        k = random.randint(2, 100)
        r = random.randint(0, k - 1)
        return lambda n: n % k == r, f"n % {k} == {r}", {"type": rule_type, "k": k, "r": r}
    if rule_type == "pot":
        p = random.randint(2, 10)
        return lambda n: round(n ** (1 / p)) ** p == n, f"n é potência perfeita de ordem {p}", {"type": rule_type, "p": p}

    a = random.randint(1, 100_000)
    b = random.randint(a, min(100_000, a + 100))
    return lambda n: a <= n <= b, f"n está entre {a} e {b}, inclusive", {"type": rule_type, "a": a, "b": b}


def generate_numbers(rule):
    """Gera e retorna a lista de números que satisfazem a regra."""
    return [n for n in range(1, 100_001) if rule(n)]


def results_from_list(values):
    """Retorna média, mediana, desvio padrão, mínimo e máximo de uma lista."""
    ordered = sorted(values)
    n = len(ordered)
    mean = sum(ordered) / n
    median = ordered[n // 2] if n % 2 == 1 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    std = (sum((x - mean) ** 2 for x in ordered) / n) ** 0.5
    return mean, median, std, ordered[0], ordered[-1]


def format_guess_entry(guess):
    """Formata um chute para gravação no arquivo de log."""
    if guess[0] == "NUMBER":
        if len(guess) >= 3 and guess[2]:
            return f"NUMBER {guess[1]}*"
        return f"NUMBER {guess[1]}"

    rule_type, p1, p2 = guess[1]
    return f"RULE {rule_type} {p1} {p2}"


def write_game_log(game_index, rule_description, guess_log, win, error_message=None, save_only_errors=False):
    """Salva os chutes de uma partida em um arquivo de texto.
    
    Se save_only_errors for True, apenas salva partidas perdidas ou com erro.
    """
    if save_only_errors and win:
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "c" if win else "e"
    file_path = OUTPUT_DIR / f"partida_{game_index:04d}_{suffix}.txt"
    with file_path.open("w", encoding="utf-8") as file:
        file.write(f"REGRA: {rule_description}\n")
        for step, guess in enumerate(guess_log, start=1):
            file.write(f"{step:04d}. {format_guess_entry(guess)}\n")
        if error_message is not None:
            file.write(f"ERRO: {error_message}\n")


def clean_output_dir():
    """Remove arquivos antigos da pasta de saída antes de gerar novos logs."""
    if not OUTPUT_DIR.exists():
        return

    for path in OUTPUT_DIR.iterdir():
        if path.is_file():
            path.unlink()


def play_one_game(max_attempts, rule_type, game_index=None):
    """Simula uma partida e retorna estatísticas da partida."""
    rule, rule_description, rule_info = choose_rule(rule_type)
    if game_index is not None:
        print(f"Iniciando partida {game_index}: {rule_description}")
    else:
        print(f"Iniciando partida: {rule_description}")
    numbers = generate_numbers(rule)

    reload(player)
    number_guesses = []
    rule_guesses = []
    guess_log = []
    attempts = 0

    try:
        while attempts < max_attempts:
            attempts += 1
            guess = verify_player_guess(player.player(number_guesses, rule_guesses))

            if guess[0] == "NUMBER":
                n = guess[1]
                d = direction(n, numbers)
                hit = n in numbers
                number_guesses.append([n, d, hit])
                guess_log.append(["NUMBER", n, hit])
                continue

            rule_type_guess, p1, p2 = guess[1]
            if rule_type_guess == "mod":
                guessed_rule = {"type": "mod", "k": p1, "r": p2}
            elif rule_type_guess == "pot":
                guessed_rule = {"type": "pot", "p": p1}
            else:
                guessed_rule = {"type": "int", "a": p1, "b": p2}

            rule_guesses.append([rule_type_guess, p1, p2])
            guess_log.append(guess)
            if guess_rule(guessed_rule, rule_info):
                return {
                    "win": True,
                    "attempts": attempts,
                    "number_guesses": len(number_guesses),
                    "rule_description": rule_description,
                    "guess_log": guess_log,
                }
    except Exception as error:
        if game_index is not None:
            write_game_log(game_index, rule_description, guess_log, False, error_message=str(error))
        raise

    return {
        "win": False,
        "attempts": max_attempts,
        "number_guesses": len(number_guesses),
        "rule_description": rule_description,
        "guess_log": guess_log,
    }


def main():
    """Executa o torneio e imprime métricas agregadas."""
    rule_type, max_games, max_attempts, save_only_errors = get_debug_config()
    clean_output_dir()

    attempts = []
    number_guess_counts = []
    wins = 0

    for game_index in tqdm(range(1, max_games + 1)):
        result = play_one_game(max_attempts=max_attempts, rule_type=rule_type, game_index=game_index)
        attempts.append(result["attempts"])
        number_guess_counts.append(result["number_guesses"])
        write_game_log(game_index, result["rule_description"], result["guess_log"], result["win"], save_only_errors=save_only_errors)
        if result["win"]:
            wins += 1

    fails = max_games - wins
    success_rate = (wins / max_games * 100) if max_games else 0

    attempts_stats = results_from_list(attempts)
    number_stats = results_from_list(number_guess_counts)

    print("\nTorneio de debug finalizado!\n")
    print(f"Tipo de regra: {rule_type}")
    print(f"Total de partidas simuladas: {max_games}")
    print(f"Máximo de tentativas por jogo: {max_attempts}")
    print(f"Partidas vencidas: {wins}")
    print(f"Partidas sem acerto: {fails}")
    print(f"Taxa de acerto: {success_rate:.2f}%")

    print("\nTentativas por partida:")
    print(f"Média: {attempts_stats[0]:.3f}")
    print(f"Mediana: {attempts_stats[1]:.3f}")
    print(f"Desvio padrão: {attempts_stats[2]:.3f}")
    print(f"Mínimo: {attempts_stats[3]}")
    print(f"Máximo: {attempts_stats[4]}")

    print("\nChutes de número por partida:")
    print(f"Média: {number_stats[0]:.3f}")
    print(f"Mediana: {number_stats[1]:.3f}")
    print(f"Desvio padrão: {number_stats[2]:.3f}")
    print(f"Mínimo: {number_stats[3]}")
    print(f"Máximo: {number_stats[4]}")


if __name__ == "__main__":
    main()