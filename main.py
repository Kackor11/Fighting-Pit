# ============================================================================
# IMPORTY
# ============================================================================
import pygame
import sys
import os
import numpy as np
from stable_baselines3 import PPO, DQN

from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_Y, MAX_HP, MELEE_RANGE,
    CHAR_WIDTH, CHAR_HEIGHT, MOVE_SPEED
)
from src.core.engine import CombatEngine
from src.gui.animation import Animator
# DODANO run_eve_menu:
from src.gui.main_menu import run_main_menu, run_start_menu, run_pve_menu, run_eve_menu

# ============================================================================
# INICJALIZACJA PYGAME I KONFIGURACJA
# ============================================================================
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("IO Final Project - AI Arena")
clock = pygame.time.Clock()

# --- KOLORY ---
WHITE = (255, 255, 255)
BLACK = (15, 15, 20)      
RED = (220, 50, 50)        
GREEN = (50, 200, 50)      
YELLOW = (255, 200, 0)    
FLOOR_COLOR = (77, 64, 64)

font_path = "src/gui/assets/fonts/Vighty.otf"

TITLE_FONT = pygame.font.Font(font_path, 72)
INFO_FONT = pygame.font.Font(font_path, 16)
TIMER_FONT = pygame.font.Font(font_path, 48)

# ============================================================================
# ASSETY I GRAFIKI (TŁO)
# ============================================================================
BACKGROUND_LAYERS = []
bg_path = "src/gui/assets/forest/background/"

if os.path.exists(bg_path):
    files = sorted([f for f in os.listdir(bg_path) if f.endswith('.png')], reverse=True)
    for file_name in files:
        file_path = os.path.join(bg_path, file_name)
        img = pygame.image.load(file_path).convert_alpha()
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        BACKGROUND_LAYERS.append(img)

# ============================================================================
# KONFIGURACJA MODELI AI (RAM CACHE)
# ============================================================================
BOT_CONFIGS = {
    1: (PPO, "src/ai/final_models/ppo_aggressive_vs_dqn_d"),
    2: (PPO, "src/ai/final_models/ppo_aggressive"),
    3: (DQN, "src/ai/final_models/dqn_balanced"),
    4: (DQN, "src/ai/final_models/dqn_aggressive_vs_ppo_a"),
    5: (PPO, "src/ai/final_models/ppo_balanced_vs_dqn_b"),
    6: (DQN, "src/ai/final_models/dqn_aggressive_vs_dqn_d"),
    7: (PPO, "src/ai/final_models/ppo_aggressive_vs_dqn_b"),
    8: (PPO, "src/ai/final_models/ppo_defensive_vs_ppo_a")
}

LOADED_MODELS = {}

# ============================================================================
# EKRAN WALKI (Zunifikowana Logika)
# ============================================================================          
def get_actions(state_left, state_right, engine, model_left=None, model_right=None):
    """Uniwersalna funkcja pobierająca akcje niezależnie od tego, czy gra człowiek, czy AI."""
    soldier_action = 0
    orc_action = 0
    keys = pygame.key.get_pressed()

    # --- STRONA LEWA (ŻOŁNIERZ) ---
    if state_left == 0: 
        # Sterowanie gracza
        if engine.player_hp > 0:
            if keys[pygame.K_w]: soldier_action = 3
            elif keys[pygame.K_a]: soldier_action = 1
            elif keys[pygame.K_d]: soldier_action = 2
            if keys[pygame.K_LSHIFT]: soldier_action = 4
            elif keys[pygame.K_SPACE]: soldier_action = 5
    else:
        # Sterowanie AI (Wektor jak w tournament.py z lewej strony)
        if model_left is not None and engine.player_hp > 0:
            dist_x = engine.boss_pos[0] - engine.player_pos[0]
            dist_y = abs(engine.boss_pos[1] - engine.player_pos[1])
            obs_left = np.array([
                engine.player_pos[1], engine.player_hp, engine.player_cooldown, engine.player_facing,
                dist_x, dist_y, engine.boss_hp
            ], dtype=np.float32)
            action, _ = model_left.predict(obs_left, deterministic=True)
            soldier_action = int(action)

    # --- STRONA PRAWA (ORK) ---
    if state_right == 0: 
        # Sterowanie gracza (zawsze jako orc)
        if engine.boss_hp > 0:
            if keys[pygame.K_UP]: orc_action = 3
            elif keys[pygame.K_LEFT]: orc_action = 1
            elif keys[pygame.K_RIGHT]: orc_action = 2
            if keys[pygame.K_k]: orc_action = 4
            elif keys[pygame.K_l]: orc_action = 5
    else:
        # Sterowanie AI (Wektor z prawej strony)
        if model_right is not None and engine.boss_hp > 0:
            dist_x = engine.player_pos[0] - engine.boss_pos[0]
            dist_y = abs(engine.player_pos[1] - engine.boss_pos[1])
            obs_right = np.array([
                engine.boss_pos[1], engine.boss_hp, engine.boss_cooldown, engine.boss_facing,
                dist_x, dist_y, engine.player_hp
            ], dtype=np.float32)
            action, _ = model_right.predict(obs_right, deterministic=True)
            orc_action = int(action)
    
    return soldier_action, orc_action
    
def run_fight(state_left, state_right):
    """Zunifikowana funkcja walki dla PvP, PvE i EvE."""
    # --- ŁADOWANIE MODELI DO PAMIĘCI (Z cache) ---
    model_left = None
    model_right = None

    for state in (state_left, state_right):
        if state in BOT_CONFIGS and state not in LOADED_MODELS:
            AlgoClass, path = BOT_CONFIGS[state]
            print(f"[{path}] - Ładowanie modelu z dysku...")
            LOADED_MODELS[state] = AlgoClass.load(path)
            print("Model załadowany i zapisany w Cache!")

    if state_left in BOT_CONFIGS: model_left = LOADED_MODELS[state_left]
    if state_right in BOT_CONFIGS: model_right = LOADED_MODELS[state_right]

    engine = CombatEngine()
    
    SCALE = 4.0
    FRAME_SIZE = 100
    
    soldier_anims = {
        "idle": Animator("src/gui/assets/characters/soldier/Soldier-Idle.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=True),
        "walk": Animator("src/gui/assets/characters/soldier/Soldier-Walk.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=True),
        "attack": Animator("src/gui/assets/characters/soldier/Soldier-Attack01.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=False, animation_speed=4),
        "hurt": Animator("src/gui/assets/characters/soldier/Soldier-Hurt.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=False, animation_speed=6),
        "death": Animator("src/gui/assets/characters/soldier/Soldier-Death.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=False, animation_speed=8)
    }

    orc_anims = {
        "idle": Animator("src/gui/assets/characters/orc/Orc-Idle.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=True),
        "walk": Animator("src/gui/assets/characters/orc/Orc-Walk.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=True),
        "attack": Animator("src/gui/assets/characters/orc/Orc-Attack01.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=False, animation_speed=4),
        "hurt": Animator("src/gui/assets/characters/orc/Orc-Hurt.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=False, animation_speed=6),
        "death": Animator("src/gui/assets/characters/orc/Orc-Death.png", FRAME_SIZE, FRAME_SIZE, scale=SCALE, loop=False, animation_speed=8)
    }

    arrow_image_raw = pygame.image.load("src/gui/assets/characters/Arrow01(32x32).png").convert_alpha()
    arrow_image = pygame.transform.scale(arrow_image_raw, (int(32 * SCALE), int(32 * SCALE)))

    soldier_state = "idle"
    orc_state = "idle"

    prev_soldier_hp = engine.player_hp
    prev_orc_hp = engine.boss_hp
    prev_orc_x = engine.boss_pos[0]
    
    soldier_melee_timer = 0
    orc_melee_timer = 0

    start_ticks = pygame.time.get_ticks()
    TIME_LIMIT_SEC = 60
    time_left = TIME_LIMIT_SEC
    match_ended_by_time = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "EXIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Inteligentny powrót zależnie od trybu
                if state_left == 0 and state_right == 0:
                    return "MENU_START" # PvP
                elif state_left != 0 and state_right != 0:
                    return "MENU_EVE"   # AI vs AI
                else:
                    return "MENU_PVE"   # PvE

        if engine.player_hp > 0 and engine.boss_hp > 0:
            current_ticks = pygame.time.get_ticks()
            elapsed_sec = (current_ticks - start_ticks) // 1000
            time_left = max(0, TIME_LIMIT_SEC - elapsed_sec)

            if time_left == 0 and not match_ended_by_time:
                match_ended_by_time = True
                if engine.player_hp > engine.boss_hp: engine.boss_hp = 0
                elif engine.boss_hp > engine.player_hp: engine.player_hp = 0
                else:
                    engine.boss_hp = 0
                    engine.player_hp = 0

        # KLAWIATURA I FIZYKA
        soldier_action, orc_action = get_actions(state_left, state_right, engine, model_left, model_right)
        
        if engine.player_hp > 0 and engine.boss_hp > 0:
            engine.update_physics(soldier_action, orc_action)

        # ANIMACJE ŻOŁNIERZA
        if engine.player_hp <= 0:
            if soldier_state != "death":
                soldier_state = "death"
                soldier_anims["death"].reset()
        elif engine.player_hp < prev_soldier_hp:
            soldier_state = "hurt"
            soldier_anims["hurt"].reset()
        elif soldier_state == "hurt" and soldier_anims["hurt"].finished:
            soldier_state = "idle"
        elif soldier_action in [4, 5] and soldier_state not in ["hurt", "death"]:
            if soldier_state != "attack":
                soldier_state = "attack"
                soldier_anims["attack"].reset()
        elif soldier_state == "attack" and soldier_anims["attack"].finished:
            soldier_state = "idle"
        elif soldier_state not in ["hurt", "attack", "death"]:
            if soldier_action in [1, 2]: soldier_state = "walk"
            else: soldier_state = "idle"

        # ANIMACJE ORKA
        if engine.boss_hp <= 0:
            if orc_state != "death":
                orc_state = "death"
                orc_anims["death"].reset()
        elif engine.boss_hp < prev_orc_hp:
            orc_state = "hurt"
            orc_anims["hurt"].reset()
        elif orc_state == "hurt" and orc_anims["hurt"].finished:
            orc_state = "idle"
        elif orc_action in [4, 5] and orc_state not in ["hurt", "death"]:
            if orc_state != "attack":
                orc_state = "attack"
                orc_anims["attack"].reset()
        elif orc_state == "attack" and orc_anims["attack"].finished:
            orc_state = "idle"
        elif orc_state not in ["hurt", "death", "attack"]:
            if abs(engine.boss_pos[0] - prev_orc_x) > 0.5: orc_state = "walk"
            else: orc_state = "idle"

        prev_soldier_hp = engine.player_hp
        prev_orc_hp = engine.boss_hp
        prev_orc_x = engine.boss_pos[0]

        soldier_anims[soldier_state].update()
        orc_anims[orc_state].update()

        # RENDEROWANIE
        screen.fill(BLACK)
        if BACKGROUND_LAYERS:
            for layer in BACKGROUND_LAYERS: screen.blit(layer, (0, 0))
        
        pygame.draw.line(screen, FLOOR_COLOR, (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 5)
        
        soldier_rect = pygame.Rect(int(engine.player_pos[0] - CHAR_WIDTH/2), int(engine.player_pos[1] - CHAR_HEIGHT), int(CHAR_WIDTH), int(CHAR_HEIGHT))
        orc_rect = pygame.Rect(int(engine.boss_pos[0] - CHAR_WIDTH/2), int(engine.boss_pos[1] - CHAR_HEIGHT), int(CHAR_WIDTH), int(CHAR_HEIGHT))

        Y_OFFSET = 175

        sol_frame = soldier_anims[soldier_state].get_current_frame()
        if engine.player_facing == -1.0: sol_frame = pygame.transform.flip(sol_frame, True, False)
        sol_x = soldier_rect.centerx - sol_frame.get_width() // 2
        sol_y = soldier_rect.bottom - sol_frame.get_height() + Y_OFFSET
        screen.blit(sol_frame, (sol_x, sol_y))

        orc_frame = orc_anims[orc_state].get_current_frame()
        if engine.boss_facing == -1.0: orc_frame = pygame.transform.flip(orc_frame, True, False)
        orc_x = orc_rect.centerx - orc_frame.get_width() // 2
        orc_y = orc_rect.bottom - orc_frame.get_height() + Y_OFFSET
        screen.blit(orc_frame, (orc_x, orc_y))

        pygame.draw.rect(screen, WHITE, soldier_rect, 1)
        pygame.draw.rect(screen, WHITE, orc_rect, 1)

        if soldier_melee_timer > 0 and engine.player_hp > 0:
            hitbox_width = int(MELEE_RANGE - 10) 
            hitbox_rect = pygame.Rect(0, 0, hitbox_width, int(CHAR_HEIGHT))
            if engine.player_facing == 1.0: hitbox_rect.left = soldier_rect.right
            else: hitbox_rect.right = soldier_rect.left
            hitbox_rect.bottom = soldier_rect.bottom
            pygame.draw.rect(screen, WHITE, hitbox_rect, 1) 
            soldier_melee_timer -= 1
        
        if orc_melee_timer > 0 and engine.boss_hp > 0:
            hitbox_width = int(MELEE_RANGE - 10)
            hitbox_rect = pygame.Rect(0, 0, hitbox_width, int(CHAR_HEIGHT))
            if engine.boss_facing == 1.0: hitbox_rect.left = orc_rect.right
            else: hitbox_rect.right = orc_rect.left
            hitbox_rect.bottom = orc_rect.bottom
            pygame.draw.rect(screen, RED, hitbox_rect, 1)
            orc_melee_timer -= 1

        if engine.player_projectile_active:
            arrow = arrow_image
            if engine.player_projectile_facing == -1.0:
                arrow = pygame.transform.flip(arrow_image, True, False)
            arrow_x = int(engine.player_projectile_pos[0]) - arrow.get_width() // 2
            arrow_y = int(engine.player_projectile_pos[1] - 40) - arrow.get_height() // 2
            screen.blit(arrow, (arrow_x, arrow_y))

        if engine.boss_projectile_active:
            arrow = arrow_image
            if engine.boss_projectile_facing == -1.0:
                arrow = pygame.transform.flip(arrow_image, True, False)
            arrow_x = int(engine.boss_projectile_pos[0]) - arrow.get_width() // 2
            arrow_y = int(engine.boss_projectile_pos[1] - 40) - arrow.get_height() // 2
            screen.blit(arrow, (arrow_x, arrow_y))

        # UI
        pygame.draw.rect(screen, RED, (20, 80, MAX_HP * 2, 25))
        if engine.player_hp > 0: pygame.draw.rect(screen, GREEN, (20, 80, engine.player_hp * 2, 25))
        
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 220, 80, MAX_HP * 2, 25))
        if engine.boss_hp > 0:
            health_width = engine.boss_hp * 2
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 20 - health_width, 80, health_width, 25))

        if time_left > 10: timer_color = WHITE
        elif time_left > 0: timer_color = RED
        else: timer_color = BLACK
            
        if time_left > 0:
            timer_surface = TIMER_FONT.render(f"{time_left}", True, timer_color)
            screen.blit(timer_surface, timer_surface.get_rect(center=(SCREEN_WIDTH // 2, 92)))

        if engine.boss_hp <= 0 and engine.player_hp <= 0:
            textobj = TITLE_FONT.render("Draw!", True, YELLOW)
            screen.blit(textobj, textobj.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        elif engine.boss_hp <= 0:
            textobj = TITLE_FONT.render("Soldier won!", True, GREEN)
            screen.blit(textobj, textobj.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        elif engine.player_hp <= 0:
            textobj = TITLE_FONT.render("Orc won!", True, RED)
            screen.blit(textobj, textobj.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            
        if engine.boss_hp <= 0 or engine.player_hp <= 0:
            textobj = INFO_FONT.render("Nacisnij ESC aby wrocic", True, WHITE)
            screen.blit(textobj, textobj.get_rect(center=(SCREEN_WIDTH//2, 20)))

        pygame.display.flip()
        clock.tick(60)
        
# ============================================================================
# GŁÓWNA PĘTLA GRY (STATE MACHINE)
# ============================================================================
if __name__ == "__main__":
    current_state = "MENU_MAIN"
    while True:
        if current_state == "MENU_MAIN":
            current_state = run_main_menu(screen, clock)
        elif current_state == "MENU_START":
            current_state = run_start_menu(screen, clock)
        elif current_state == "MENU_PVE":
            current_state = run_pve_menu(screen, clock)
        elif current_state == "MENU_EVE":
            current_state = run_eve_menu(screen, clock)
        elif current_state == "FIGHT_START_0":
            current_state = run_fight(0, 0)
        elif isinstance(current_state, str) and current_state.startswith("FIGHT_START_"):
            bot_id = int(current_state.split("_")[2])
            current_state = run_fight(0, bot_id)
        # Odbieramy pakiet z trybu EvE: ("FIGHT_EVE", lewy_bot, prawy_bot)
        elif isinstance(current_state, tuple) and current_state[0] == "FIGHT_EVE":
            _, left_id, right_id = current_state
            current_state = run_fight(left_id, right_id)
        elif current_state == "EXIT":
            pygame.quit()
            sys.exit()