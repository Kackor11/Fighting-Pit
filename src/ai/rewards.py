# Różne wersje funkcji nagrody (Reward Shaping)

from enum import Enum

class RewardStyle(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"

def calculate_reward(player_hp_delta, boss_hp_delta, style: RewardStyle):
    """
    Oblicza nagrodę dla Bossa na podstawie wybranego charakteru (stylu walki).
    player_hp_delta: ujemna wartość oznacza, że gracz (żołnierz) dostał obrażenia.
    boss_hp_delta: ujemna wartość oznacza, że boss (ork) dostał obrażenia.
    """
    reward = 0.0
    
    # Zamieniamy delty na wartości absolutne dla ułatwienia (zadane obrażenia i otrzymane obrażenia)
    dmg_dealt = abs(player_hp_delta) if player_hp_delta < 0 else 0.0
    dmg_taken = abs(boss_hp_delta) if boss_hp_delta < 0 else 0.0

    if style == RewardStyle.AGGRESSIVE:
        # Berserker: Potężna nagroda za atak, mała kara za obrywanie, duża kara za uciekanie
        reward += dmg_dealt * 3.0
        reward -= dmg_taken * 0.5
        reward -= 0.2 # Presja czasu (atakuj natychmiast)

    elif style == RewardStyle.DEFENSIVE:
        # Tchórz/Snajper: Ogromna kara za otrzymanie obrażeń, mała nagroda za zadawanie
        reward += dmg_dealt * 1.0
        reward -= dmg_taken * 4.0
        reward += 0.01 # Nagroda za przetrwanie każdej kolejnej klatki (zachęca do ucieczki)

    elif style == RewardStyle.BALANCED:
        # Taktyk: Zrównoważone nagrody
        reward += dmg_dealt * 2.0
        reward -= dmg_taken * 2.0
        reward -= 0.2 # Umiarkowana presja czasu

    return reward