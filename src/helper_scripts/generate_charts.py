import os
import re
import matplotlib.pyplot as plt
import numpy as np

# Konfiguracja wyglądów wykresów
plt.style.use('ggplot')

def parse_results(filepath):
    """Odczytuje plik z wynikami i zwraca słownik z rankingiem oraz matchupami."""
    # Próbujemy otworzyć jako UTF-8 (dla pliku finałowego)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    # Jeśli wystąpi błąd kodowania (jak z PowerShell'a), używamy UTF-16
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='utf-16') as f:
            lines = f.readlines()

    ranking = []
    matchups = {}
    current_bot_matchups = None

    for line in lines:
        # 1. Parsowanie Rankingu Głównego
        # Szukamy linii typu: #1 | dqn_balanced | 87.5% | 100.0% | 75.0% | 700-100-0
        ranking_match = re.match(r'^#\d+\s+\|\s+(.*?)\s+\|\s+([\d.]+)%\s+\|\s+([\d.]+)%\s+\|\s+([\d.]+)%', line)
        if ranking_match:
            name = ranking_match.group(1).strip()
            wr_total = float(ranking_match.group(2))
            wr_left = float(ranking_match.group(3))
            wr_right = float(ranking_match.group(4))
            ranking.append((name, wr_total, wr_left, wr_right))
            continue

        # 2. Szukanie nagłówka szczegółowych wyników bota
        # Szukamy linii typu: [dqn_balanced] Winrate przeciwko:
        bot_match = re.match(r'^\[(.*?)\] Winrate przeciwko:', line)
        if bot_match:
            current_bot_matchups = bot_match.group(1).strip()
            matchups[current_bot_matchups] = []
            continue

        # 3. Parsowanie konkretnych walk
        # Szukamy linii typu:  - vs ppo_aggressive : 50.0% ...
        if current_bot_matchups:
            vs_match = re.match(r'^\s+-\s+vs\s+(.*?)\s+:\s+([\d.]+)%', line)
            if vs_match:
                opponent = vs_match.group(1).strip()
                wr_vs = float(vs_match.group(2))
                matchups[current_bot_matchups].append((opponent, wr_vs))

    # Sortowanie rankingu po ogólnym Winrate malejąco
    ranking.sort(key=lambda x: x[1], reverse=True)
    
    # Sortowanie matchupów po Winrate malejąco
    for bot in matchups:
        matchups[bot].sort(key=lambda x: x[1], reverse=True)

    return ranking, matchups

def plot_global_ranking(ranking, title, filename):
    """Generuje i zapisuje wykres słupkowy potrójny dla globalnego rankingu."""
    names = [x[0] for x in ranking]
    wr_total = [x[1] for x in ranking]
    wr_left = [x[2] for x in ranking]
    wr_right = [x[3] for x in ranking]

    x = np.arange(len(names))
    width = 0.25  # Szerokość pojedynczego słupka

    fig, ax = plt.subplots(figsize=(16, 8))
    
    rects1 = ax.bar(x - width, wr_total, width, label='Ogólny Winrate', color='#2ca02c') # Zielony
    rects2 = ax.bar(x, wr_left, width, label='WR (Lewa strona)', color='#1f77b4')        # Niebieski
    rects3 = ax.bar(x + width, wr_right, width, label='WR (Prawa strona)', color='#d62728')# Czerwony

    ax.set_ylabel('Winrate (%)', fontsize=12)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10)
    ax.legend(fontsize=12)
    ax.set_ylim(0, 110) # Żeby mieć miejsce na etykiety nad słupkami (do 100%)

    # Linie siatki dla czytelności
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)

    fig.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

def plot_private_matchups(matchups, top_n_names, title_prefix, output_dir):
    """Generuje prywatne wykresy dla wskazanej listy najlepszych botów."""
    for bot_name in top_n_names:
        if bot_name not in matchups:
            print(f"Ostrzeżenie: Brak szczegółowych danych dla {bot_name}")
            continue

        data = matchups[bot_name]
        opponents = [x[0] for x in data]
        winrates = [x[1] for x in data]

        fig, ax = plt.subplots(figsize=(14, 7))
        bars = ax.bar(opponents, winrates, color='#9467bd') # Fioletowy dla prywatnych

        ax.set_ylabel('Winrate (%)', fontsize=12)
        ax.set_title(f'{title_prefix}: {bot_name} vs Reszta', fontsize=16, fontweight='bold')
        ax.set_xticks(np.arange(len(opponents)))
        ax.set_xticklabels(opponents, rotation=45, ha='right', fontsize=10)
        ax.set_ylim(0, 110)

        # Dodanie procentów nad słupkami
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 punkty wyżej
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        fig.tight_layout()
        
        safe_name = bot_name.replace(' ', '_')
        safe_prefix = title_prefix.replace(' ', '_') # Np. RUNDA_1 lub WIELKI_FINAL
        plt.savefig(os.path.join(output_dir, f'{safe_prefix}_{safe_name}.png'), dpi=300)
        plt.close()

def main():
    OUTPUT_DIR = "wykresy_turniejowe"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generowanie wykresów...")

    # =========================================================
    # 1. PIERWSZY TURNIEJ
    # =========================================================
    file_first = "first_tournament_results.txt"
    if os.path.exists(file_first):
        print(f"Przetwarzanie {file_first}...")
        rank_1, matchups_1 = parse_results(file_first)
        
        # Główny wykres potrójny
        plot_global_ranking(rank_1, "RUNDA 1: Ranking Główny 9 Modeli", os.path.join(OUTPUT_DIR, "Runda1_Globalny.png"))
        
        # Prywatne wykresy dla TOP 3
        top_3_names = [rank_1[0][0], rank_1[1][0], rank_1[2][0]]
        plot_private_matchups(matchups_1, top_3_names, "RUNDA 1", OUTPUT_DIR)
    else:
        print(f"Brak pliku: {file_first}")

    # =========================================================
    # 2. WIELKI FINAŁ
    # =========================================================
    file_final = "final_tournament_results.txt"
    if os.path.exists(file_final):
        print(f"Przetwarzanie {file_final}...")
        rank_f, matchups_f = parse_results(file_final)
        
        # Główny wykres potrójny
        plot_global_ranking(rank_f, "WIELKI FINAŁ: Ranking Główny 21 Modeli", os.path.join(OUTPUT_DIR, "Final_Globalny.png"))
        
        # Prywatne wykresy dla TOP 6
        top_6_names = [rank_f[i][0] for i in range(min(6, len(rank_f)))]
        plot_private_matchups(matchups_f, top_6_names, "WIELKI FINAŁ", OUTPUT_DIR)
    else:
        print(f"Brak pliku: {file_final}")

    print(f"Gotowe! Wszystkie wykresy zostały wygenerowane i zapisane w folderze: '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()