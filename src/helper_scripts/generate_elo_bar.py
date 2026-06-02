import os
import re
import matplotlib.pyplot as plt
import numpy as np

# Utrzymujemy ten sam styl co w poprzednich wykresach
plt.style.use('ggplot')

def generate_elo_bar_chart():
    filepath = "elo_ranking.txt"
    output_dir = "wykresy_turniejowe"
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(filepath):
        print(f"BŁĄD: Nie znaleziono pliku {filepath}. Upewnij się, że wygenerowałeś ranking Elo.")
        return

    bots = []
    elos = []

    print("Czytanie danych z rankingu Elo...")
    
    # 1. Parsowanie pliku
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # Szukamy linii typu: #1 | dqn_balanced | 1250.5
            match = re.match(r'^#\d+\s+\|\s+(.*?)\s+\|\s+([\d.]+)', line)
            if match:
                name = match.group(1).strip()
                score = float(match.group(2))
                bots.append(name)
                elos.append(score)

    if not bots:
        print("Nie znaleziono danych w pliku. Sprawdź format elo_ranking.txt.")
        return

    # 2. Rysowanie klasycznego wykresu słupkowego
    fig, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(bots))
    width = 0.6
    
    # Klasyczny, chłodny niebieski (ten sam co użyty do lewej strony w poprzednim skrypcie)
    bars = ax.bar(x, elos, width, color='#1f77b4') 

    ax.set_ylabel('Punktacja Elo', fontsize=12)
    ax.set_title('Oficjalny Ranking Elo (21 Modeli)', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(bots, rotation=45, ha='right', fontsize=10)
    
    # Ustawiamy dynamiczny limit osi Y (najwyższy wynik + 100 pkt luzu na napisy)
    ax.set_ylim(0, max(elos) + 100)

    # 3. Dodawanie dokładnych wyników nad słupkami
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 piksele nad słupkiem
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Siatka w tle
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    fig.tight_layout()
    
    # Zapis
    output_filename = os.path.join(output_dir, "Ranking_Elo_Slupkowy.png")
    plt.savefig(output_filename, dpi=300)
    plt.close()
    
    print(f"Sukces! Klasyczny niebieski wykres zapisany jako '{output_filename}'.")

if __name__ == "__main__":
    generate_elo_bar_chart()