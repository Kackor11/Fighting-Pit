import re
import random

def calculate_elo():
    filepath = "final_tournament_results.txt"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='utf-16') as f:
            lines = f.readlines()

    bots = set()
    matches = []
    seen_pairs = set()
    current_bot = None

    # 1. Parsowanie pliku i ekstrakcja pojedynczych walk
    for line in lines:
        bot_match = re.match(r'^\[(.*?)\] Winrate przeciwko:', line)
        if bot_match:
            current_bot = bot_match.group(1).strip()
            bots.add(current_bot)
            continue

        if current_bot:
            vs_match = re.match(r'^\s+-\s+vs\s+(.*?)\s+:\s+[\d.]+%\s+\(W:\s*(\d+)\s+L:\s*(\d+)\s+D:\s*(\d+)\s*\)', line)
            if vs_match:
                opponent = vs_match.group(1).strip()
                wins = int(vs_match.group(2))
                losses = int(vs_match.group(3))
                draws = int(vs_match.group(4))
                
                bots.add(opponent)

                # Unikamy podwójnego zliczania tej samej pary
                pair = tuple(sorted([current_bot, opponent]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    
                    # Wynik 1.0 dla wygranej, 0.0 dla przegranej, 0.5 dla remisu
                    for _ in range(wins):
                        matches.append((current_bot, opponent, 1.0))
                    for _ in range(losses):
                        matches.append((current_bot, opponent, 0.0))
                    for _ in range(draws):
                        matches.append((current_bot, opponent, 0.5))

    print(f"Pomyślnie wczytano {len(bots)} botów i {len(matches)} unikalnych walk.")

    # 2. Inicjalizacja systemu Elo
    elo_ratings = {bot: 1000.0 for bot in bots} # Każdy startuje z poziomu 1000
    K_FACTOR = 32 # Standardowy współczynnik dla dynamicznych zmian

    # 3. Tasowanie walk (symulacja naturalnego turnieju w czasie)
    random.seed(42) # Ustawienie ziarna, aby wyniki były zawsze powtarzalne
    random.shuffle(matches)

    # 4. Matematyka Elo - przeliczanie każdej walki
    for player_a, player_b, score_a in matches:
        rating_a = elo_ratings[player_a]
        rating_b = elo_ratings[player_b]

        # Oczekiwane prawdopodobieństwo wygranej
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

        # Punktacja dla Gracza B
        score_b = 1.0 - score_a

        # Aktualizacja ratingu
        elo_ratings[player_a] = rating_a + K_FACTOR * (score_a - expected_a)
        elo_ratings[player_b] = rating_b + K_FACTOR * (score_b - expected_b)

    # 5. Przygotowanie i wyświetlenie ostatecznego rankingu
    ranking = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "="*70)
    print(f"{'OFICJALNY RANKING ELO (Początkowe = 1000)':^70}")
    print("="*70)
    print(f"{'POZYCJA':<8} | {'BOT NAME':<30} | {'ELO SCORE':<10}")
    print("-" * 70)
    
    with open("elo_ranking.txt", "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write(f"{'OFICJALNY RANKING ELO (Początkowe = 1000)':^70}\n")
        f.write("="*70 + "\n")
        f.write(f"{'POZYCJA':<8} | {'BOT NAME':<30} | {'ELO SCORE':<10}\n")
        f.write("-" * 70 + "\n")
        
        for i, (name, score) in enumerate(ranking):
            row = f"#{i+1:<6} | {name:<30} | {score:>7.1f}"
            print(row)
            f.write(row + "\n")

if __name__ == "__main__":
    calculate_elo()