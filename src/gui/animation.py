import pygame

class Animator:
    def __init__(self, sprite_sheet_path, frame_width, frame_height, scale=1.5, loop=True, animation_speed=6):
        self.sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale = scale
        self.loop = loop
        self.finished = False
        
        # Obliczamy ile jest klatek w pasku
        self.total_frames = self.sheet.get_width() // frame_width
        self.frames = []
        
        # Wycinamy i skalujemy klatki
        for i in range(self.total_frames):
            rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame = self.sheet.subsurface(rect)
            scaled_w = int(frame_width * scale)
            scaled_h = int(frame_height * scale)
            self.frames.append(pygame.transform.scale(frame, (scaled_w, scaled_h)))
            
        self.current_frame = 0
        self.timer = 0
        self.animation_speed = animation_speed

    def update(self):
        # Jeśli animacja się skończyła (np. śmierć), nie odtwarzaj jej dalej
        if self.finished:
            return
            
        self.timer += 1
        if self.timer >= self.animation_speed:
            self.timer = 0
            # Jeśli to ostatnia klatka
            if self.current_frame == self.total_frames - 1:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.finished = True
            else:
                self.current_frame += 1
                
    def get_current_frame(self):
        return self.frames[self.current_frame]
        
    def reset(self):
        """Resetuje animację od początku (przydatne przy atakach i otrzymywaniu obrażeń)."""
        self.current_frame = 0
        self.timer = 0
        self.finished = False