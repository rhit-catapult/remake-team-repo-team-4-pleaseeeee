import pygame
import sys


class Character:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y
        self.image = pygame.image.load("brownie.png")

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))


# This function is called when you run this file, and is used to test the Character class individually.
# When you create more files with different classes, copy the code below, then
# change it to properly test that class.
def test_character(): 
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    character = Character(screen, 400, 400) 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill("white")
        character.draw()
        pygame.display.update()


if __name__ == "__main__":
    test_character()
