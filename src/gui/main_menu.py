# ============================================================================
# IMPORTY
# ============================================================================
import pygame
import os
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# ============================================================================
# KOLORY I KONFIGURACJA WIZUALNA MENU
# ============================================================================
WHITE = (255, 255, 255)
BLACK = (15, 15, 20)      
YELLOW = (255, 200, 0)    
GRAY = (150, 150, 150)    
DARK_GRAY = (40, 40, 50)  
HOVER_COLOR = (80, 80, 100) 
GREEN = (50, 200, 50)

# ============================================================================
# TŁO MENU I GRAFIKI UI
# ============================================================================
MENU_BG_PATH = "src/gui/assets/background/forest_01.png"
MENU_BG_IMAGE = None

BUTTON_IMAGE_PATH = "src/gui/assets/buttons/button.png"
BUTTON_IMAGE_RAW = None
SCALED_BUTTONS = {} # Cache dla przeskalowanych przycisków

def draw_menu_bg(screen):
    """Ładuje i rysuje tło menu głównego."""
    global MENU_BG_IMAGE
    
    if MENU_BG_IMAGE is None:
        if os.path.exists(MENU_BG_PATH):
            img = pygame.image.load(MENU_BG_PATH).convert_alpha()
            MENU_BG_IMAGE = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Przyciemnienie tła dla lepszej czytelności tekstu
            darken = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            darken.set_alpha(120)
            darken.fill((0, 0, 0))
            MENU_BG_IMAGE.blit(darken, (0, 0))
        else:
            MENU_BG_IMAGE = False

    if MENU_BG_IMAGE:
        screen.blit(MENU_BG_IMAGE, (0, 0))
    else:
        screen.fill(BLACK)

def draw_button(screen, rect, is_hover, tint=None):
    """Uniwersalna funkcja rysująca graficzny przycisk z obsługą cache'owania i podświetlenia."""
    global BUTTON_IMAGE_RAW
    
    # 1. Ładowanie bazowej grafiki (Tylko raz)
    if BUTTON_IMAGE_RAW is None:
        if os.path.exists(BUTTON_IMAGE_PATH):
            BUTTON_IMAGE_RAW = pygame.image.load(BUTTON_IMAGE_PATH).convert_alpha()
        else:
            BUTTON_IMAGE_RAW = False

    if BUTTON_IMAGE_RAW:
        size = (rect.width, rect.height)
        
        # 2. Skalowanie i Cache'owanie (Dla wydajności)
        if size not in SCALED_BUTTONS:
            SCALED_BUTTONS[size] = pygame.transform.scale(BUTTON_IMAGE_RAW, size)
            
        screen.blit(SCALED_BUTTONS[size], rect.topleft)
        
        # 3. Nakładki graficzne (Hover i Tint)
        if tint:
            # Nakłada konkretny kolor (np. zielony dla RUN) z przezroczystością
            tint_surf = pygame.Surface(size, pygame.SRCALPHA)
            tint_surf.fill((*tint, 100)) # 100 to wartość alpha
            if is_hover: 
                tint_surf.fill((*tint, 140)) # Mocniejszy kolor przy najechaniu
            screen.blit(tint_surf, rect.topleft)
        elif is_hover:
            # Standardowe jasne podświetlenie grafiki
            hover_surf = pygame.Surface(size, pygame.SRCALPHA)
            hover_surf.fill((255, 255, 255, 30))
            screen.blit(hover_surf, rect.topleft)
    else:
        # Fallback do zwykłych klocków, jeśli brakuje pliku grafiki
        base_color = tint if tint else DARK_GRAY
        final_color = HOVER_COLOR if is_hover else base_color
        pygame.draw.rect(screen, final_color, rect, border_radius=10)

# ============================================================================
# FUNKCJE POMOCNICZE
# ============================================================================
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def get_fonts():
    """Zwraca słownik z zainicjalizowanymi czcionkami dla menu."""
    font_path = "src/gui/assets/fonts/Vighty.otf"
    
    return {
        "title": pygame.font.Font(font_path, 100),
        "menu": pygame.font.Font(font_path, 32),
        "info": pygame.font.Font(font_path, 24)
    }

# ============================================================================
# EKRAN 1.0: MENU GŁÓWNE
# ============================================================================
def run_main_menu(screen, clock):
    fonts = get_fonts()
    
    while True:
        draw_menu_bg(screen)
        draw_text("Ai Boss Arena", fonts["title"], WHITE, screen, SCREEN_WIDTH//2, 150)
        draw_text("Reinforcement Learning Project", fonts["info"], GRAY, screen, SCREEN_WIDTH//2, 240)

        mx, my = pygame.mouse.get_pos()
        button_start = pygame.Rect(SCREEN_WIDTH//2 - 125, 300, 250, 60)
        button_exit = pygame.Rect(SCREEN_WIDTH//2 - 125, 400, 250, 60)

        draw_button(screen, button_start, button_start.collidepoint((mx, my)))
        draw_button(screen, button_exit, button_exit.collidepoint((mx, my)))

        draw_text("Start", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2, 330)
        draw_text("Exit", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2, 430)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_start.collidepoint((mx, my)): return "MENU_START"
                if button_exit.collidepoint((mx, my)): return "EXIT"

        pygame.display.flip()
        clock.tick(60)

# ============================================================================
# EKRAN 1.1: WYBÓR TRYBU GRY
# ============================================================================
def run_start_menu(screen, clock):
    fonts = get_fonts()
    
    while True:
        draw_menu_bg(screen)
        draw_text("Wybierz tryb", fonts["title"], WHITE, screen, SCREEN_WIDTH//2, 120)
        draw_text("Nacisnij ESC aby wrocic", fonts["info"], GRAY, screen, SCREEN_WIDTH//2, 190)

        mx, my = pygame.mouse.get_pos()
        
        btn_pvp = pygame.Rect(SCREEN_WIDTH//2 - 150, 250, 300, 60)
        btn_pve = pygame.Rect(SCREEN_WIDTH//2 - 150, 350, 300, 60)
        btn_eve = pygame.Rect(SCREEN_WIDTH//2 - 150, 450, 300, 60)

        draw_button(screen, btn_pvp, btn_pvp.collidepoint((mx, my)))
        draw_button(screen, btn_pve, btn_pve.collidepoint((mx, my)))
        draw_button(screen, btn_eve, btn_eve.collidepoint((mx, my)))

        draw_text("PvP", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2, 280)
        draw_text("Player vs Ai", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2, 380)
        draw_text("Ai vs Ai", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2, 480)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "EXIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "MENU_MAIN"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_pvp.collidepoint((mx, my)): return "FIGHT_START_0"  
                if btn_pve.collidepoint((mx, my)): return "MENU_PVE"
                if btn_eve.collidepoint((mx, my)): return "MENU_EVE"

        pygame.display.flip()
        clock.tick(60)

# ============================================================================
# EKRAN 1.2: MENU PLAYER VS AI (WYBÓR PRZECIWNIKA)
# ============================================================================
def run_pve_menu(screen, clock):
    fonts = get_fonts()
    
    while True:
        draw_menu_bg(screen)
        draw_text("Player vs Ai", fonts["title"], WHITE, screen, SCREEN_WIDTH//2, 100)
        draw_text("Wybierz przeciwnika (nacisnij ESC aby wrocic)", fonts["info"], GRAY, screen, SCREEN_WIDTH//2, 170)

        mx, my = pygame.mouse.get_pos()
        btn_fight_1 = pygame.Rect(SCREEN_WIDTH//2 - 375, 220, 350, 60)
        btn_fight_2 = pygame.Rect(SCREEN_WIDTH//2 - 375, 300, 350, 60)
        btn_fight_3 = pygame.Rect(SCREEN_WIDTH//2 - 375, 380, 350, 60)
        btn_fight_4 = pygame.Rect(SCREEN_WIDTH//2 - 375, 460, 350, 60)
        btn_fight_5 = pygame.Rect(SCREEN_WIDTH//2 + 25, 220, 350, 60)
        btn_fight_6 = pygame.Rect(SCREEN_WIDTH//2 + 25, 300, 350, 60)
        btn_fight_7 = pygame.Rect(SCREEN_WIDTH//2 + 25, 380, 350, 60)
        btn_fight_8 = pygame.Rect(SCREEN_WIDTH//2 + 25, 460, 350, 60)

        btns = [btn_fight_1, btn_fight_2, btn_fight_3, btn_fight_4, btn_fight_5, btn_fight_6, btn_fight_7, btn_fight_8]
        for btn in btns:
            draw_button(screen, btn, btn.collidepoint((mx, my)))

        draw_text("Ppo_A_on_Dqn_D", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 - 200, 250)
        draw_text("Ppo_Agg", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 - 200, 330)
        draw_text("Dqn_Bal", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 - 200, 410)
        draw_text("Dqn_A_vs_Ppo_A", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 - 200, 490)
        draw_text("Ppo_B_on_Dqn_B", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 + 200, 250)
        draw_text("Dqn_A_on_Dqn_D", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 + 200, 330)
        draw_text("Ppo_A_on_Dqn_B", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 + 200, 410)
        draw_text("Ppo_D_on_Ppo_A", fonts["menu"], WHITE, screen, SCREEN_WIDTH//2 + 200, 490)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "EXIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "MENU_START"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, btn in enumerate(btns):
                    if btn.collidepoint((mx, my)):
                        return f"FIGHT_START_{i+1}"

        pygame.display.flip()
        clock.tick(60)

# ============================================================================
# EKRAN 1.3: MENU AI VS AI (DROPDOWNS)
# ============================================================================
def run_eve_menu(screen, clock):
    fonts = get_fonts()
    
    BOT_NAMES = {
        1: "Ppo_A_on_Dqn_D", 2: "Ppo_Agg", 3: "Dqn_Bal", 4: "Dqn_A_vs_Ppo_A",
        5: "Ppo_B_on_Dqn_B", 6: "Dqn_A_on_Dqn_D", 7: "Ppo_A_on_Dqn_B", 8: "Ppo_D_on_Ppo_A"
    }
    
    left_bot_id = 1
    right_bot_id = 3
    
    dd_left_open = False
    dd_right_open = False

    while True:
        draw_menu_bg(screen)
        draw_text("Ai vs Ai", fonts["title"], WHITE, screen, SCREEN_WIDTH//2, 70)
        draw_text("Wybierz algorytmy do walki (nacisnij ESC aby wrocic)", fonts["info"], GRAY, screen, SCREEN_WIDTH//2, 130)

        mx, my = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "EXIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "MENU_START"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: click = True

        box_left = pygame.Rect(SCREEN_WIDTH//2 - 350, 190, 300, 50)
        box_right = pygame.Rect(SCREEN_WIDTH//2 + 50, 190, 300, 50)
        btn_run = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 60)

        dd_left_rects = [pygame.Rect(box_left.x, box_left.bottom + i*40, box_left.width, 40) for i in range(8)]
        dd_right_rects = [pygame.Rect(box_right.x, box_right.bottom + i*40, box_right.width, 40) for i in range(8)]

        if click:
            if dd_left_open:
                clicked_item = False
                for i, rect in enumerate(dd_left_rects):
                    if rect.collidepoint((mx, my)):
                        left_bot_id = i + 1
                        clicked_item = True
                        break
                dd_left_open = False
                if clicked_item: continue

            elif dd_right_open:
                clicked_item = False
                for i, rect in enumerate(dd_right_rects):
                    if rect.collidepoint((mx, my)):
                        right_bot_id = i + 1
                        clicked_item = True
                        break
                dd_right_open = False
                if clicked_item: continue
                
            else:
                if box_left.collidepoint((mx, my)): dd_left_open = True
                elif box_right.collidepoint((mx, my)): dd_right_open = True
                elif btn_run.collidepoint((mx, my)): 
                    return ("FIGHT_EVE", left_bot_id, right_bot_id)

        draw_text("Strona lewa (Zolnierz)", fonts["info"], WHITE, screen, box_left.centerx, 160)
        draw_text("Strona prawa (Ork)", fonts["info"], WHITE, screen, box_right.centerx, 160)

        draw_button(screen, box_left, box_left.collidepoint((mx, my)))
        draw_text(BOT_NAMES[left_bot_id], fonts["info"], WHITE, screen, box_left.centerx, box_left.centery)

        draw_button(screen, box_right, box_right.collidepoint((mx, my)))
        draw_text(BOT_NAMES[right_bot_id], fonts["info"], WHITE, screen, box_right.centerx, box_right.centery)

        # Przycisk RUN z zielonym tintem, aby go wyróżnić
        draw_button(screen, btn_run, btn_run.collidepoint((mx, my)), tint=GREEN)
        draw_text("Run", fonts["menu"], WHITE, screen, btn_run.centerx, btn_run.centery)

        if dd_left_open:
            for i, rect in enumerate(dd_left_rects):
                draw_button(screen, rect, rect.collidepoint((mx, my)))
                draw_text(BOT_NAMES[i+1], fonts["info"], WHITE, screen, rect.centerx, rect.centery)

        if dd_right_open:
            for i, rect in enumerate(dd_right_rects):
                draw_button(screen, rect, rect.collidepoint((mx, my)))
                draw_text(BOT_NAMES[i+1], fonts["info"], WHITE, screen, rect.centerx, rect.centery)

        pygame.display.flip()
        clock.tick(60)