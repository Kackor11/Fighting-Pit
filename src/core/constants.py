# Stałe globalne, parametry fizyczne i konfiguracja środowiska gry

# ============================================================================
# WYMIARY ŚWIATA GRY (WIRTUALNA ARENA)
# ============================================================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FLOOR_Y = 530

# ============================================================================
# FIZYKA POSTACI (DOPASOWANA DO SYMULACJI 60 FPS)
# ============================================================================
MOVE_SPEED = 8.0
JUMP_FORCE = -16.0
GRAVITY = 0.8

# ============================================================================
# STATYSTYKI I BALANS WALKI
# ============================================================================
MAX_HP = 100.0
RANGED_COOLDOWN = 45
MELEE_COOLDOWN = 30

# ============================================================================
# PARAMETRY ATAKÓW I OBRAŻEŃ
# ============================================================================
MELEE_RANGE = 60.0
MELEE_DAMAGE = 15.0
RANGED_DAMAGE = 5.0
PROJECTILE_SPEED = 12.0
PROJECTILE_RANGE = 25.0

# ============================================================================
# WYMIARY HITBOXÓW (KOLIZJE FIZYCZNE)
# ============================================================================
# Rozmiar białej ramki wokół postaci. Zmieniając to, zmieniasz fizyczny rozmiar postaci 1:1.
CHAR_WIDTH = 40.0
CHAR_HEIGHT = 60.0