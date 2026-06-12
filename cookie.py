import pygame
import sys
import my_character

def main():
    BLACK = pygame.Color("Black")
    IMAGE_SIZE = 470
    TEXT_HEIGHT = 30

    pygame.init()

    screen = pygame.display.set_mode((IMAGE_SIZE, IMAGE_SIZE + TEXT_HEIGHT))
    pygame.display.set_caption("Text, Sound, and an Image")
    brownie_image = pygame.image.load("brownie.png")
    
    pygame.display.set_caption("Cool Project")
    screen = pygame.display.set_mode((640, 480))

    # let's set the framerate
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)  # this sets the framerate of your game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # TODO: Fill the screen with whatever background color you like!
        screen.fill((255, 255, 255))
        # TODO: Add your project code

        # don't forget the update, otherwise nothing will show up!
        pygame.display.update()


main()