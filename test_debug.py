import pygame
import sys

pygame.init()

class Character:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y
        self.image = pygame.image.load("brownie.png")

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))

# Test
screen = pygame.display.set_mode((640, 480))
c = Character(screen, 400, 400)
print(f"Character object: {c}")
print(f"Has draw method: {hasattr(c, 'draw')}")
print(f"Methods: {[m for m in dir(c) if not m.startswith('_')]}")
