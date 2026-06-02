import os
import numpy as np
from tqdm import tqdm
from stable_baselines3 import PPO, DQN, A2C
from src.envs.boss_env import BossArenaEnv
from src.ai.rewards import RewardStyle, calculate_reward

# === SPECYFIKACJA PRZECIWNIKA ===
OPPONENT_NAME = "dqn_balanced"
OPPONENT_CLASS = DQN
# ================================

class VsModelEnv(BossArenaEnv):
    def __init__(self, opponent_model, reward_style=RewardStyle.BALANCED):
        super().__init__(reward_style=reward_style)
        self.opponent_model = opponent_model

    def step(self, action):
        self.current_step += 1
        
        dist_x = self.engine.boss_pos[0] - self.engine.player_pos[0] 
        dist_y = abs(self.engine.boss_pos[1] - self.engine.player_pos[1])
        
        obs_opponent = np.array([
            self.engine.player_pos[1], self.engine.player_hp, self.engine.player_cooldown, 
            self.engine.player_facing, dist_x, dist_y, self.engine.boss_hp
        ], dtype=np.float32)

        opponent_action, _ = self.opponent_model.predict(obs_opponent, deterministic=True)
        dummy_player_action = int(opponent_action)

        self.engine.update_physics(player_action=dummy_player_action, orc_action=action)

        boss_hp_delta = self.engine.boss_hp - self.prev_boss_hp
        player_hp_delta = self.engine.player_hp - self.prev_player_hp
        
        self.prev_boss_hp = self.engine.boss_hp
        self.prev_player_hp = self.engine.player_hp

        reward = calculate_reward(player_hp_delta, boss_hp_delta, self.reward_style)
        
        if self.engine.player_hp <= 0: reward += 100.0
        if self.engine.boss_hp <= 0: reward -= 100.0

        terminated = self.engine.boss_hp <= 0 or self.engine.player_hp <= 0
        truncated = self.current_step >= self.max_steps
        
        return self._get_obs(), reward, terminated, truncated, {}

def main():
    MODELS_DIR = f"src/ai/models_vs_{OPPONENT_NAME}"
    LOGS_DIR = f"src/ai/logs_vs_{OPPONENT_NAME}"
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    algorithms = {"PPO": PPO, "DQN": DQN}
    styles = [RewardStyle.AGGRESSIVE, RewardStyle.DEFENSIVE, RewardStyle.BALANCED]
    TIMESTEPS = 3000000 

    print("="*60)
    print(f" TRENING MATRYCY KONTRUJĄCEJ: {OPPONENT_NAME.upper()}")
    print("="*60)

    # Zaktualizowana ścieżka do folderu models_v2
    opponent_path = f"src/ai/models_v2/{OPPONENT_NAME}"
    if not os.path.exists(opponent_path + ".zip"):
        print(f"BŁĄD: Nie znaleziono modelu przeciwnika: {opponent_path}.zip")
        return
        
    print("Ładowanie mózgu mistrza...\n")
    opponent_model = OPPONENT_CLASS.load(opponent_path)

    total_models = len(algorithms) * len(styles)
    
    # Główny pasek postępu (1 do 9 modeli)
    with tqdm(total=total_models, desc="Ogólny postęp (Modele)", unit="model") as pbar:
        for algo_name, AlgoClass in algorithms.items():
            for style in styles:
                model_name = f"{algo_name.lower()}_{style.value}"
                model_path = os.path.join(MODELS_DIR, model_name)
                
                if os.path.exists(model_path + ".zip"):
                    pbar.write(f"[POMINIĘTO] Model {model_name} już istnieje.")
                    pbar.update(1)
                    continue

                pbar.write(f"\n---> Trenowanie kontry: {algo_name} | Styl: {style.name} <---")
                env = VsModelEnv(opponent_model=opponent_model, reward_style=style)
                model = AlgoClass("MlpPolicy", env, verbose=0, tensorboard_log=LOGS_DIR)
                
                # Pasek wewnętrzny (3 mln kroków) z biblioteki SB3
                model.learn(total_timesteps=TIMESTEPS, tb_log_name=model_name, progress_bar=True)
                model.save(model_path)
                
                pbar.write(f"[ZAPISANO] {model_name}.zip w folderze {MODELS_DIR}/")
                pbar.update(1)

if __name__ == "__main__":
    main()