import os
from stable_baselines3 import PPO, DQN, A2C
import warnings
warnings.filterwarnings("ignore")

models_to_test = {
    "ppo_aggressive": PPO, "ppo_defensive": PPO, "ppo_balanced": PPO,
    "dqn_aggressive": DQN, "dqn_defensive": DQN, "dqn_balanced": DQN,
    "a2c_aggressive": A2C, "a2c_defensive": A2C, "a2c_balanced": A2C
}

print("--- MASOWY TEST MODELI ---")
for name, model_class in models_to_test.items():
    bunker_path = f"C:\\temp_models\\{name}"
    project_path = f"src/ai/models/{name}"
    
    print(f"\nTestowanie {name}:")
    
    # Test Bunkra
    try:
        model = model_class.load(bunker_path, device="cpu")
        print(f"  ✅ BUNKIER (C:): Działa!")
    except Exception:
        print(f"  ❌ BUNKIER (C:): Uszkodzony.")
        
    # Test Projektu
    try:
        model = model_class.load(project_path, device="cpu")
        print(f"  ✅ PROJEKT: Działa!")
    except Exception:
        print(f"  ❌ PROJEKT: Uszkodzony.")