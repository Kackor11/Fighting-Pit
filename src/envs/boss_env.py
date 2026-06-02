# ============================================================================
# IMPORTY I ZALEŻNOŚCI
# ============================================================================
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random  

from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAX_HP, RANGED_COOLDOWN
from src.core.engine import CombatEngine
from src.ai.rewards import RewardStyle, calculate_reward

# ============================================================================
# GŁÓWNA KLASA ŚRODOWISKA GYMNASIUM
# ============================================================================
class BossArenaEnv(gym.Env):
    """
    Uniwersalne środowisko walki. Model uczy się być uniwersalnym wojownikiem,
    którego można podłączyć zarówno pod Orka (Prawa strona) jak i Żołnierza (Lewa strona).
    """
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, render_mode=None, reward_style=RewardStyle.BALANCED):
        super(BossArenaEnv, self).__init__()
        self.render_mode = render_mode
        self.reward_style = reward_style
        
        self.engine = CombatEngine()

        self.action_space = spaces.Discrete(6)

        # --- PRZESTRZEŃ OBSERWACJI ---
        # Wektor: [Moje_Y, Moje_HP, Mój_Cooldown, Mój_Zwrot, Dystans_X, Dystans_Y, Jego_HP]
        # Dystans_X = (Pozycja_Wroga_X - Moja_Pozycja_X) * Mój_Zwrot 
        
        low = np.array([0, 0, 0, -1, -SCREEN_WIDTH, 0, 0], dtype=np.float32)
        high = np.array([SCREEN_HEIGHT, MAX_HP, RANGED_COOLDOWN, 1, SCREEN_WIDTH, SCREEN_HEIGHT, MAX_HP], dtype=np.float32)
        
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.engine.reset()
        
        # DOMAIN RANDOMIZATION: Losujemy strony areny!
        if random.random() > 0.5:
            # Ork po lewej, Żołnierz po prawej
            self.engine.player_pos[0] = 600.0
            self.engine.player_facing = -1.0
            self.engine.boss_pos[0] = 200.0
            self.engine.boss_facing = 1.0
        else:
            # Klasycznie
            self.engine.player_pos[0] = 200.0
            self.engine.player_facing = 1.0
            self.engine.boss_pos[0] = 600.0
            self.engine.boss_facing = -1.0
        
        self.current_step = 0
        self.max_steps = 1000  
        
        self.prev_boss_hp = self.engine.boss_hp
        self.prev_player_hp = self.engine.player_hp
        
        return self._get_obs(), {}

    def step(self, action):
        self.current_step += 1
        
        # --- DYNAMICZNY MANEKIN (Zawsze steruje Żołnierzem, a AI Orkiem) ---
        dist_x = self.engine.boss_pos[0] - self.engine.player_pos[0]
        behavior_roll = random.random()
        
        if behavior_roll < 0.70: # Agresja
            if dist_x > 50: dummy_player_action = 2  
            elif dist_x < -50: dummy_player_action = 1  
            else: dummy_player_action = random.choice([4, 4, 5, 0]) 
        elif behavior_roll < 0.90: # Ucieczka/Czekanie
            if behavior_roll < 0.80: dummy_player_action = 0  
            else: dummy_player_action = 1 if dist_x > 0 else 2  
        else: # Chaos
            dummy_player_action = random.choice([0, 1, 2, 3, 5])

        self.engine.update_physics(player_action=dummy_player_action, orc_action=action)

        boss_hp_delta = self.engine.boss_hp - self.prev_boss_hp
        player_hp_delta = self.engine.player_hp - self.prev_player_hp
        
        self.prev_boss_hp = self.engine.boss_hp
        self.prev_player_hp = self.engine.player_hp

        # Obliczamy nagrodę Z PERSPEKTYWY ORKA
        reward = calculate_reward(player_hp_delta, boss_hp_delta, self.reward_style)
        
        if self.engine.player_hp <= 0:
            reward += 100.0 # Agent (Ork) wygrywa
        if self.engine.boss_hp <= 0:
            reward -= 100.0 # Agent (Ork) przegrywa

        terminated = self.engine.boss_hp <= 0 or self.engine.player_hp <= 0
        truncated = self.current_step >= self.max_steps
        
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        """Buduje uniwersalny, symetryczny wektor stanu niezależny od pozycji na mapie."""
        # Prosty wektor kierunkowy: Wrog_X - Moje_X
        # Dodatni wynik = wróg jest po prawej. Ujemny = po lewej.
        dist_x = self.engine.player_pos[0] - self.engine.boss_pos[0]
        dist_y = abs(self.engine.player_pos[1] - self.engine.boss_pos[1])

        return np.array([
            self.engine.boss_pos[1],           # Moje_Y
            self.engine.boss_hp,               # Moje_HP
            self.engine.boss_cooldown,         # Mój_Cooldown
            self.engine.boss_facing,           # Mój_Zwrot (czy muszę się obrócić do ataku)
            dist_x,                            # Dystans_X
            dist_y,                            # Dystans_Y
            self.engine.player_hp              # Jego_HP
        ], dtype=np.float32)

    def render(self):
        pass