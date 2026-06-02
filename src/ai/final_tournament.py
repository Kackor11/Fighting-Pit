import os
import itertools
import numpy as np
from tqdm import tqdm
from stable_baselines3 import PPO, DQN, A2C
from src.core.engine import CombatEngine

# ============================================================================
# KONFIGURACJA TURNIEJU
# ============================================================================
# Definiujemy wszystkie foldery, z których chcemy pobrać gladiatorów
MODEL_DIRS = [
    "src/ai/models_vs_dqn_balanced",
    "src/ai/models_vs_dqn_defensive",
    "src/ai/models_vs_ppo_aggressive",
    "src/ai/top_models_round_1"
]

OUTPUT_FILE = "final_tournament_results.txt"
MATCHES_PER_SIDE = 10  # Optymalna wartość dla środowiska deterministycznego
MAX_TICKS = 60 * 60    # 60 sekund

def load_model(file_path, file_name):
    """Dynamicznie ładuje model, rozpoznając algorytm po przedrostku nazwy."""
    name_lower = file_name.lower()
    # Szukamy głównego członu, ignorując resztę nazwy np. dqn_aggr_vs_dqn_b
    if name_lower.startswith("ppo"): return PPO.load(file_path)
    if name_lower.startswith("dqn"): return DQN.load(file_path)
    if name_lower.startswith("a2c"): return A2C.load(file_path)
    raise ValueError(f"Nieznany algorytm bazowy w nazwie pliku: {file_name}")

def get_observation(engine, is_left_side):
    """Buduje symetryczny wektor 7-elementowy w zależności od strony areny."""
    if is_left_side:
        dist_x = engine.boss_pos[0] - engine.player_pos[0]
        dist_y = abs(engine.boss_pos[1] - engine.player_pos[1])
        return np.array([
            engine.player_pos[1], engine.player_hp, engine.player_cooldown, engine.player_facing,
            dist_x, dist_y, engine.boss_hp
        ], dtype=np.float32)
    else:
        dist_x = engine.player_pos[0] - engine.boss_pos[0]
        dist_y = abs(engine.player_pos[1] - engine.boss_pos[1])
        return np.array([
            engine.boss_pos[1], engine.boss_hp, engine.boss_cooldown, engine.boss_facing,
            dist_x, dist_y, engine.player_hp
        ], dtype=np.float32)

def run_headless_match(model_left, model_right):
    """Symuluje jedną walkę bez GUI i zwraca zwycięzcę."""
    engine = CombatEngine()
    
    for _ in range(MAX_TICKS):
        if engine.player_hp <= 0 or engine.boss_hp <= 0:
            break
            
        obs_left = get_observation(engine, is_left_side=True)
        action_left, _ = model_left.predict(obs_left, deterministic=True)
        
        obs_right = get_observation(engine, is_left_side=False)
        action_right, _ = model_right.predict(obs_right, deterministic=True)
        
        engine.update_physics(int(action_left), int(action_right))

    if engine.player_hp <= 0 and engine.boss_hp <= 0: return "DRAW"
    elif engine.boss_hp <= 0: return "LEFT"
    elif engine.player_hp <= 0: return "RIGHT"
    else:
        if engine.player_hp > engine.boss_hp: return "LEFT"
        elif engine.boss_hp > engine.player_hp: return "RIGHT"
        else: return "DRAW"

def main():
    print("="*80)
    print(f"{'INICJALIZACJA WIELKIEGO FINAŁU AI VS AI (21 MODELI)':^80}")
    print("="*80)

    # 1. Pobranie i załadowanie modeli ze wszystkich folderów
    models = {}
    print("Skanowanie folderów i ładowanie modeli do pamięci...")
    
    for directory in MODEL_DIRS:
        if not os.path.exists(directory):
            print(f"OSTRZEŻENIE: Folder {directory} nie istnieje. Pomijam.")
            continue
            
        for f in os.listdir(directory):
            if f.endswith(".zip"):
                name = f.replace(".zip", "")
                file_path = os.path.join(directory, f)
                # Zabezpieczenie przed nadpisaniem modeli o tej samej nazwie (choć tutaj nie powinny)
                if name in models:
                    name = f"{name}_(duplicate)"
                models[name] = load_model(file_path, f)
                
    if len(models) < 2:
        print("Błąd: Znaleziono za mało modeli do rozegrania turnieju.")
        return

    print(f"\nPomyślnie załadowano {len(models)} potężnych gladiatorów.\n")
    
    # 2. Struktura na statystyki
    stats = {name: {
        "wins": 0, "losses": 0, "draws": 0,
        "wins_left": 0, "matches_left": 0,
        "wins_right": 0, "matches_right": 0,
        "matchups": {other: {"wins": 0, "losses": 0, "draws": 0} for other in models if other != name}
    } for name in models}

    # 3. Generowanie unikalnych par (każdy z każdym)
    matchups = list(itertools.combinations(models.keys(), 2))
    total_matches = len(matchups) * MATCHES_PER_SIDE * 2
    
    # ============================================================================
    # GŁÓWNA PĘTLA SYMULACJI
    # ============================================================================
    with tqdm(total=total_matches, desc="Wielki Finał", unit="walka") as pbar:
        for m1, m2 in matchups:
            
            # FAZA 1: m1 z lewej, m2 z prawej
            for _ in range(MATCHES_PER_SIDE):
                result = run_headless_match(models[m1], models[m2])
                stats[m1]["matches_left"] += 1
                stats[m2]["matches_right"] += 1
                
                if result == "LEFT":
                    stats[m1]["wins"] += 1
                    stats[m1]["wins_left"] += 1
                    stats[m1]["matchups"][m2]["wins"] += 1
                    stats[m2]["losses"] += 1
                    stats[m2]["matchups"][m1]["losses"] += 1
                elif result == "RIGHT":
                    stats[m2]["wins"] += 1
                    stats[m2]["wins_right"] += 1
                    stats[m2]["matchups"][m1]["wins"] += 1
                    stats[m1]["losses"] += 1
                    stats[m1]["matchups"][m2]["losses"] += 1
                else:
                    stats[m1]["draws"] += 1
                    stats[m2]["draws"] += 1
                    stats[m1]["matchups"][m2]["draws"] += 1
                    stats[m2]["matchups"][m1]["draws"] += 1
                    
                pbar.update(1)

            # FAZA 2: m2 z lewej, m1 z prawej
            for _ in range(MATCHES_PER_SIDE):
                result = run_headless_match(models[m2], models[m1])
                stats[m2]["matches_left"] += 1
                stats[m1]["matches_right"] += 1
                
                if result == "LEFT":
                    stats[m2]["wins"] += 1
                    stats[m2]["wins_left"] += 1
                    stats[m2]["matchups"][m1]["wins"] += 1
                    stats[m1]["losses"] += 1
                    stats[m1]["matchups"][m2]["losses"] += 1
                elif result == "RIGHT":
                    stats[m1]["wins"] += 1
                    stats[m1]["wins_right"] += 1
                    stats[m1]["matchups"][m2]["wins"] += 1
                    stats[m2]["losses"] += 1
                    stats[m2]["matchups"][m1]["losses"] += 1
                else:
                    stats[m1]["draws"] += 1
                    stats[m2]["draws"] += 1
                    stats[m1]["matchups"][m2]["draws"] += 1
                    stats[m2]["matchups"][m1]["draws"] += 1
                    
                pbar.update(1)

    # ============================================================================
    # RAPORT I ZAPIS DO PLIKU
    # ============================================================================
    print("\nTurniej zakończony! Trwa generowanie raportu...")
    
    ranking = []
    for name, data in stats.items():
        total = data["wins"] + data["losses"] + data["draws"]
        winrate = (data["wins"] / total * 100) if total > 0 else 0
        wr_left = (data["wins_left"] / data["matches_left"] * 100) if data["matches_left"] > 0 else 0
        wr_right = (data["wins_right"] / data["matches_right"] * 100) if data["matches_right"] > 0 else 0
        ranking.append((name, winrate, wr_left, wr_right, data["wins"], data["losses"], data["draws"]))
        
    ranking.sort(key=lambda x: x[1], reverse=True) 

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("="*90 + "\n")
        f.write(f"{'RANKING GŁÓWNY WIELKIEGO FINAŁU (Sortowanie po Winrate)':^90}\n")
        f.write("="*90 + "\n")
        f.write(f"{'POZYCJA':<8} | {'BOT NAME':<30} | {'WINRATE':<8} | {'WR (LEWA)':<10} | {'WR (PRAWA)':<10} | {'W-L-D'}\n")
        f.write("-" * 90 + "\n")
        for i, (name, wr, wr_l, wr_r, w, l, d) in enumerate(ranking):
            f.write(f"#{i+1:<6} | {name:<30} | {wr:>6.1f}% | {wr_l:>8.1f}% | {wr_r:>8.1f}% | {w}-{l}-{d}\n")

        f.write("\n\n" + "="*90 + "\n")
        f.write(f"{'SZCZEGÓŁOWE WYNIKI (MATCHUPS)':^90}\n")
        f.write("="*90 + "\n")
        for name in stats:
            f.write(f"\n[{name}] Winrate przeciwko:\n")
            # Sortujemy przeciwników alfabetycznie dla czytelności
            for opponent in sorted(stats[name]["matchups"].keys()):
                m_data = stats[name]["matchups"][opponent]
                total = m_data["wins"] + m_data["losses"] + m_data["draws"]
                if total > 0:
                    wr = m_data["wins"] / total * 100
                    f.write(f"  - vs {opponent:<30} : {wr:>5.1f}% (W: {m_data['wins']:<3} L: {m_data['losses']:<3} D: {m_data['draws']:<3})\n")

    print(f"Gotowe! Pełny raport został zapisany w pliku: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()