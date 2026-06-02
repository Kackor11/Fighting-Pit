import gymnasium as gym
from stable_baselines3 import PPO
import os

print("--- TEST CZYSTEJ BIBLIOTEKI ---")
try:
    env = gym.make("CartPole-v1")
    model = PPO("MlpPolicy", env, verbose=0)
    
    print("1. Trenowanie (100 kroków)...")
    model.learn(total_timesteps=100)
    
    print("2. Zapisywanie pliku test_cartpole.zip...")
    model.save("test_cartpole")
    
    print("3. Próba załadowania z dysku...")
    loaded = PPO.load("test_cartpole")
    print("✅ SUKCES! Biblioteka PyTorch działa perfekcyjnie. Winny jest Enum w Twoim kodzie.")
    
    # Sprzątanie
    if os.path.exists("test_cartpole.zip"):
        os.remove("test_cartpole.zip")

except Exception as e:
    print(f"❌ KRYTYCZNY BŁĄD BIBLIOTEKI (Python 3.12 / PyTorch): {e}")