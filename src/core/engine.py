# ============================================================================
# IMPORTY I ZALEŻNOŚCI
# ============================================================================
import numpy as np
from src.core.constants import (
    SCREEN_WIDTH, FLOOR_Y, MOVE_SPEED, JUMP_FORCE, GRAVITY, MAX_HP, 
    RANGED_COOLDOWN, MELEE_COOLDOWN, MELEE_RANGE, 
    MELEE_DAMAGE, RANGED_DAMAGE, PROJECTILE_SPEED, PROJECTILE_RANGE,
    CHAR_WIDTH, CHAR_HEIGHT
)
import random

# ============================================================================
# GŁÓWNA KLASA SILNIKA FIZYCZNEGO (SYMETRYCZNA)
# ============================================================================
class CombatEngine:
    """Silnik matematyczny obsługujący pozycje, fizykę, kolizje i walkę obu postaci."""
    
    def __init__(self):
        self.reset()

    def reset(self):
        # --- ŻOŁNIERZ (PLAYER) ---
        self.player_pos = np.array([200.0, FLOOR_Y], dtype=np.float32)   
        self.player_facing = 1.0  
        self.player_vel_y = 0.0
        self.player_hp = MAX_HP
        self.player_cooldown = 0.0
        
        self.player_projectile_active = False
        self.player_projectile_pos = np.array([0.0, 0.0], dtype=np.float32)
        self.player_projectile_facing = 1.0

        # --- ORK (BOSS) ---
        self.boss_pos = np.array([600.0, FLOOR_Y], dtype=np.float32)   
        self.boss_facing = -1.0  
        self.boss_vel_y = 0.0
        self.boss_hp = MAX_HP
        self.boss_cooldown = 0.0
        
        self.boss_projectile_active = False
        self.boss_projectile_pos = np.array([0.0, 0.0], dtype=np.float32)
        self.boss_projectile_facing = -1.0

    def update_physics(self, player_action, orc_action):
        # ========================================================================
        # 1. AKCJE ŻOŁNIERZA (PLAYER - STEROWANY KLAWIATURĄ W SANDBOXIE)
        # ========================================================================
        if self.player_hp > 0:
            if player_action == 1:
                self.player_pos[0] -= MOVE_SPEED
                self.player_facing = -1.0
            elif player_action == 2:
                self.player_pos[0] += MOVE_SPEED
                self.player_facing = 1.0
            elif player_action == 3 and self.player_pos[1] >= FLOOR_Y:
                self.player_vel_y = JUMP_FORCE
                
            # Atak wręcz Żołnierza
            elif player_action == 4 and self.player_cooldown <= 0:
                dist_x = self.boss_pos[0] - self.player_pos[0]
                dist_y = abs(self.boss_pos[1] - self.player_pos[1])
                self.player_cooldown = MELEE_COOLDOWN
                
                # Atak trafia, jeśli postacie nakładają się na siebie LUB dystans od krawędzi mieści się w MELEE_RANGE
                if 0 <= (dist_x * self.player_facing) <= (MELEE_RANGE + CHAR_WIDTH) and dist_y <= CHAR_HEIGHT:
                    self.boss_hp -= MELEE_DAMAGE
                    
            # Atak zasięgowy Żołnierza
            elif player_action == 5 and self.player_cooldown <= 0 and not self.player_projectile_active:
                self.player_projectile_active = True
                self.player_projectile_pos = np.copy(self.player_pos)
                self.player_projectile_facing = self.player_facing
                self.player_cooldown = RANGED_COOLDOWN

        # ========================================================================
        # 2. AKCJE ORKA
        # ========================================================================
        if self.boss_hp > 0:
            # --- ZAMIANA MANEKINA NA WERSJĘ TRENINGOWĄ ---
            if orc_action == -1:
                dist_x = self.player_pos[0] - self.boss_pos[0] # Wektor od Orka do Żołnierza
                behavior_roll = random.random()
                
                if behavior_roll < 0.70:
                    # AGRESJA
                    if dist_x > 50:
                        orc_action = 2  # Idź w prawo (do Żołnierza)
                    elif dist_x < -50:
                        orc_action = 1  # Idź w lewo (do Żołnierza)
                    else:
                        orc_action = random.choice([4, 4, 5, 0]) 
                        
                elif behavior_roll < 0.90:
                    # PASYWNOŚĆ/UCIECZKA
                    if behavior_roll < 0.80:
                        orc_action = 0  # Stój w miejscu
                    else:
                        orc_action = 1 if dist_x > 0 else 2  # Uciekaj od Żołnierza
                        
                else:
                    # CHAOS
                    orc_action = random.choice([0, 1, 2, 3, 5])

            # --- WYKONANIE AKCJI ---
            # Powyższy blok zamienił '-1' na prawdziwą akcję (0-5). 
            # Jeśli gra prawdziwe AI, orc_action po prostu omija blok wyżej i trafia od razu tutaj.
            if orc_action == 1:
                self.boss_pos[0] -= MOVE_SPEED
                self.boss_facing = -1.0
                
            elif orc_action == 2:
                self.boss_pos[0] += MOVE_SPEED
                self.boss_facing = 1.0
                
            elif orc_action == 3 and self.boss_pos[1] >= FLOOR_Y:
                self.boss_vel_y = JUMP_FORCE
                
            elif orc_action == 4 and self.boss_cooldown <= 0:
                dist_x = self.player_pos[0] - self.boss_pos[0]
                dist_y = abs(self.player_pos[1] - self.boss_pos[1])
                self.boss_cooldown = MELEE_COOLDOWN
                
                if 0 <= (dist_x * self.boss_facing) <= (MELEE_RANGE + CHAR_WIDTH) and dist_y <= CHAR_HEIGHT:
                    self.player_hp -= MELEE_DAMAGE
                    
            elif orc_action == 5 and self.boss_cooldown <= 0 and not self.boss_projectile_active:
                self.boss_projectile_active = True
                self.boss_projectile_pos = np.copy(self.boss_pos)
                self.boss_projectile_facing = self.boss_facing
                self.boss_cooldown = RANGED_COOLDOWN

        # ========================================================================
        # 3. GRAWITACJA I GRANICE ŚWIATA
        # ========================================================================
        self.player_vel_y += GRAVITY
        self.player_pos[1] += self.player_vel_y
        if self.player_pos[1] >= FLOOR_Y:
            self.player_pos[1] = FLOOR_Y
            self.player_vel_y = 0.0
        self.player_pos[0] = np.clip(self.player_pos[0], 0.0, float(SCREEN_WIDTH))

        self.boss_vel_y += GRAVITY
        self.boss_pos[1] += self.boss_vel_y
        if self.boss_pos[1] >= FLOOR_Y:
            self.boss_pos[1] = FLOOR_Y
            self.boss_vel_y = 0.0
        self.boss_pos[0] = np.clip(self.boss_pos[0], 0.0, float(SCREEN_WIDTH))

        # ========================================================================
        # 4. LOGIKA POCISKÓW
        # ========================================================================
        if self.player_projectile_active:
            self.player_projectile_pos[0] += PROJECTILE_SPEED * self.player_projectile_facing
            p_dist_x = abs(self.player_projectile_pos[0] - self.boss_pos[0])
            p_dist_y = abs(self.player_projectile_pos[1] - self.boss_pos[1])
            if p_dist_x <= PROJECTILE_RANGE and p_dist_y <= 40.0:
                self.boss_hp -= RANGED_DAMAGE
                self.player_projectile_active = False
            elif self.player_projectile_pos[0] < 0 or self.player_projectile_pos[0] > SCREEN_WIDTH:
                self.player_projectile_active = False

        if self.boss_projectile_active:
            self.boss_projectile_pos[0] += PROJECTILE_SPEED * self.boss_projectile_facing
            p_dist_x = abs(self.boss_projectile_pos[0] - self.player_pos[0])
            p_dist_y = abs(self.boss_projectile_pos[1] - self.player_pos[1])
            if p_dist_x <= PROJECTILE_RANGE and p_dist_y <= 40.0:
                self.player_hp -= RANGED_DAMAGE
                self.boss_projectile_active = False
            elif self.boss_projectile_pos[0] < 0 or self.boss_projectile_pos[0] > SCREEN_WIDTH:
                self.boss_projectile_active = False

        # ========================================================================
        # 5. ODŚWIEŻANIE COOLDOWNÓW
        # ========================================================================
        if self.player_cooldown > 0: self.player_cooldown -= 1
        if self.boss_cooldown > 0: self.boss_cooldown -= 1