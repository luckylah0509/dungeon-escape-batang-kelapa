import pygame
import math
class Monster:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.hp = 20
        self.ukuran = 32
        self.kecepatan = 1.5
        self.hitbox = pygame.Rect(x, y, self.ukuran, self.ukuran)

    def update(self):
            pemain = self.game.pemain.hitbox
            dx = pemain.centerx - self.hitbox.centerx
            dy = pemain.centery - self.hitbox.centery
    
            jarak = math.hypot(dx, dy)
    
            if jarak > 0:
                self.x += (dx/jarak) * self.kecepatan
                self.y += (dy/jarak) * self.kecepatan
    
            self.hitbox.topleft = (round(self.x), round(self.y))

    def draw(self, layar):
        pygame.draw.rect(layar, (200,50,50), self.hitbox)
