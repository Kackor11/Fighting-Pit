import os
import itertools
import numpy as np
from tqdm import tqdm  # <-- Nasz nowy pasek postępu!
from stable_baselines3 import PPO, DQN, A2C
from src.core.engine import CombatEngine

# ============================================================================
# KONFIGURACJA TURNIEJU
# ============================================================================
MODELS_DIR = "src/ai/models"
MATCHES_PER_SIDE = 50  # 50 po lewej, 50 po prawej (razem 100 na parę)
MAX_TICKS = 60 * 60    # 60 sekund * 60 klatek = 3600 kroków na walkę

def load_model(file_path, file_name):
    """Dynamicznie ładuje model na podstawie jego nazwy."""
    if "ppo" in file_name.lower(): return PPO.load(file_path)
    if "dqn" in file_name.lower(): return DQN.load(file_path)
    if "a2c" in file_name.lower(): return A2C.load(file_path)
    raise ValueError(f"Nieznany algorytm w nazwie pliku: {file_name}")

def get_observation(engine, is_left_side):
    """Buduje symetryczny wektor 7-elementowy w zależności od strony areny."""
    if is_left_side:
        # Perspektywa Żołnierza (Lewa strona)
        dist_x = engine.boss_pos[0] - engine.player_pos[0]
        dist_y = abs(engine.boss_pos[1] - engine.player_pos[1])
        return np.array([
            engine.player_pos[1], engine.player_hp, engine.player_cooldown, engine.player_facing,
            dist_x, dist_y, engine.boss_hp
        ], dtype=np.float32)
    else:
        # Perspektywa Orka (Prawa strona)
        dist_x = engine.player_pos[0] - engine.boss_pos[0]
        dist_y = abs(engine.player_pos[1] - engine.boss_pos[1])
        return np.array([
            engine.boss_pos[1], engine.boss_hp, engine.boss_cooldown, engine.boss_facing,
            dist_x, dist_y, engine.player_hp
        ], dtype=np.float32)

def run_headless_match(model_left, model_right):
    """Symuluje jedną walkę bez GUI i zwraca zwycięzcę: 'LEFT', 'RIGHT' lub 'DRAW'."""
    engine = CombatEngine()
    
    for _ in range(MAX_TICKS):
        if engine.player_hp <= 0 or engine.boss_hp <= 0:
            break
            
        obs_left = get_observation(engine, is_left_side=True)
        action_left, _ = model_left.predict(obs_left, deterministic=True)
        
        obs_right = get_observation(engine, is_left_side=False)
        action_right, _ = model_right.predict(obs_right, deterministic=True)
        
        engine.update_physics(int(action_left), int(action_right))

    if engine.player_hp <= 0 and engine.boss_hp <= 0:
        return "DRAW"
    elif engine.boss_hp <= 0:
        return "LEFT"
    elif engine.player_hp <= 0:
        return "RIGHT"
    else:
        if engine.player_hp > engine.boss_hp: return "LEFT"
        elif engine.boss_hp > engine.player_hp: return "RIGHT"
        else: return "DRAW"

def main():
    print("="*80)
    print(f"{'INICJALIZACJA TURNIEJU AI VS AI (HEADLESS)':^80}")
    print("="*80)

    # 1. Pobranie i załadowanie modeli
    model_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".zip")]
    if len(model_files) < 2:
        print("Błąd: Potrzebujesz przynajmniej 2 modeli w folderze.")
        return

    print(f"Znaleziono {len(model_files)} modeli. Ładowanie do pamięci...\n")
    models = {}
    for f in model_files:
        name = f.replace(".zip", "")
        models[name] = load_model(os.path.join(MODELS_DIR, f), f)
    
    # 2. Struktura na statystyki
    stats = {name: {
        "wins": 0, "losses": 0, "draws": 0,
        "wins_left": 0, "matches_left": 0,
        "wins_right": 0, "matches_right": 0,
        "matchups": {other: {"wins": 0, "losses": 0, "draws": 0} for other in models if other != name}
    } for name in models}

    # 3. Generowanie unikalnych par (każdy z każdym bez dubli)
    matchups = list(itertools.combinations(models.keys(), 2))
    total_matches = len(matchups) * MATCHES_PER_SIDE * 2
    
    # ============================================================================
    # GŁÓWNA PĘTLA SYMULACJI Z PASKIEM POSTĘPU
    # ============================================================================
    with tqdm(total=total_matches, desc="Rozgrywanie pojedynków", unit="walka") as pbar:
        for m1, m2 in matchups:
            
            # --- FAZA 1: m1 z lewej, m2 z prawej ---
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
                    
                pbar.update(1) # Aktualizacja paska postępu o 1 walkę

            # --- FAZA 2: m2 z lewej, m1 z prawej ---
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
                    
                pbar.update(1) # Aktualizacja paska postępu o 1 walkę

    # ============================================================================
    # RAPORT I RANKING KOŃCOWY
    # ============================================================================
    print("\n\n" + "="*80)
    print(f"{'RANKING GŁÓWNY (Sortowanie po Winrate)':^80}")
    print("="*80)
    
    ranking = []
    for name, data in stats.items():
        total = data["wins"] + data["losses"] + data["draws"]
        winrate = (data["wins"] / total * 100) if total > 0 else 0
        wr_left = (data["wins_left"] / data["matches_left"] * 100) if data["matches_left"] > 0 else 0
        wr_right = (data["wins_right"] / data["matches_right"] * 100) if data["matches_right"] > 0 else 0
        ranking.append((name, winrate, wr_left, wr_right, data["wins"], data["losses"], data["draws"]))
        
    ranking.sort(key=lambda x: x[1], reverse=True) 

    print(f"{'POZYCJA':<8} | {'BOT NAME':<18} | {'WINRATE':<8} | {'WR (LEWA)':<10} | {'WR (PRAWA)':<10} | {'W-L-D'}")
    print("-" * 80)
    for i, (name, wr, wr_l, wr_r, w, l, d) in enumerate(ranking):
        print(f"#{i+1:<6} | {name:<18} | {wr:>6.1f}% | {wr_l:>8.1f}% | {wr_r:>8.1f}% | {w}-{l}-{d}")

    print("\n" + "="*80)
    print(f"{'SZCZEGÓŁOWE WYNIKI (MATCHUPS)':^80}")
    print("="*80)
    for name in stats:
        print(f"\n[{name}] Winrate przeciwko:")
        for opponent, m_data in stats[name]["matchups"].items():
            total = m_data["wins"] + m_data["losses"] + m_data["draws"]
            if total > 0:
                wr = m_data["wins"] / total * 100
                print(f"  - vs {opponent:<18} : {wr:>5.1f}% (W: {m_data['wins']} L: {m_data['losses']} D: {m_data['draws']})")

if __name__ == "__main__":
    main()