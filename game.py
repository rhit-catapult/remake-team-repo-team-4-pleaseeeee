import os
import sys
import pygame


def main():
    pygame.init()
    base_dir = os.path.join(os.path.dirname(__file__), 'images')
    bg1_path = os.path.join(base_dir, 'background 1.png')
    bg2_path = os.path.join(base_dir, 'background 2.png')
    start_btn_path = os.path.join(base_dir, 'start button.png')

    if not (os.path.exists(bg1_path) and os.path.exists(bg2_path) and os.path.exists(start_btn_path)):
        print('Required images not found in images/ folder:')
        print('Make sure background 1.png, background 2.png and start button.png exist.')
        sys.exit(1)

    bg1 = pygame.image.load(bg1_path)
    bg2 = pygame.image.load(bg2_path)
    start_btn = pygame.image.load(start_btn_path)

    screen = pygame.display.set_mode(bg1.get_size())
    bg1 = bg1.convert()
    bg2 = bg2.convert()
    start_btn = start_btn.convert_alpha()
    pygame.display.set_caption('Start Screen Example')
    clock = pygame.time.Clock()

    btn_rect = start_btn.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    started = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not started and btn_rect.collidepoint(event.pos):
                    started = True

        if started:
            if bg2.get_size() != screen.get_size():
                bg2_scaled = pygame.transform.smoothscale(bg2, screen.get_size())
            else:
                bg2_scaled = bg2
            screen.blit(bg2_scaled, (0, 0))
        else:
            screen.blit(bg1, (0, 0))
            screen.blit(start_btn, btn_rect)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
