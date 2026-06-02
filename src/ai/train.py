import os
from stable_baselines3 import PPO, DQN, A2C
from src.envs.boss_env import BossArenaEnv
from src.ai.rewards import RewardStyle

def main():
    MODELS_DIR = "src/ai/models"
    LOGS_DIR = "src/ai/logs"
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Definiujemy pełną matrycę modeli 3x3
    algorithms = {
        "PPO": PPO,
        "DQN": DQN,
        "A2C": A2C
    }
    
    styles = [RewardStyle.AGGRESSIVE, RewardStyle.DEFENSIVE, RewardStyle.BALANCED]

    # Docelowa liczba kroków (3 MILIONY)
    TIMESTEPS = 3000000 

    print("="*50)
    print(" ROZPOCZĘCIE TRENOWANIA MATRYCY MODELI (3x3)")
    print("="*50)

    for algo_name, AlgoClass in algorithms.items():
        for style in styles:
            model_name = f"{algo_name.lower()}_{style.value}" # np. ppo_aggressive
            model_path = os.path.join(MODELS_DIR, model_name)
            
            # Bezpiecznik: pomija poprawnie wytrenowane modele przy restarcie
            if os.path.exists(model_path + ".zip"):
                print(f"[POMINIĘTO] Model {model_name} już istnieje.")
                continue

            print(f"\n---> Trenowanie: {algo_name} | Styl: {style.name} <---")
            
            # Inicjalizacja środowiska i modelu
            env = BossArenaEnv(reward_style=style)
            model = AlgoClass("MlpPolicy", env, verbose=0, tensorboard_log=LOGS_DIR)
            
            # --- DODANY PASEK POSTĘPU (progress_bar=True) ---
            model.learn(total_timesteps=TIMESTEPS, tb_log_name=model_name, progress_bar=True)
            model.save(model_path)
            
            print(f"[ZAPISANO] {model_name}.zip w folderze models/")

    print("\n" + "="*50)
    print(" WSZYSTKIE 9 MODELI WYTRENOWANE I ZAPISANE!")
    print("="*50)

if __name__ == "__main__":
    main()