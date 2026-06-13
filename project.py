import os
import sys
import pygame
import my_character
import upgrade_module


def show_start_screen(screen):
    pygame.display.set_caption("Start Screen")

    base_dir = os.path.join(os.path.dirname(__file__), "images")
    bg1_path = os.path.join(base_dir, "background 1.png")
    bg2_path = os.path.join(base_dir, "background 2.png")
    start_btn_path = os.path.join(base_dir, "start button.png")

    bg1 = None
    bg2 = None
    start_btn = None

    if os.path.exists(bg1_path) and os.path.exists(bg2_path) and os.path.exists(start_btn_path):
        bg1 = pygame.image.load(bg1_path).convert()
        bg2 = pygame.image.load(bg2_path).convert()
        start_btn = pygame.image.load(start_btn_path).convert_alpha()

    font = pygame.font.SysFont(None, 48)
    button_font = pygame.font.SysFont(None, 32)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn is not None:
                    btn_rect = start_btn.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                    if btn_rect.collidepoint(event.pos):
                        return
                else:
                    button_rect = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 40, 200, 50)
                    if button_rect.collidepoint(event.pos):
                        return

        if bg1 is not None and bg2 is not None and start_btn is not None:
            bg_scaled = pygame.transform.smoothscale(bg1, screen.get_size())
            screen.blit(bg_scaled, (0, 0))
            btn_rect = start_btn.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(start_btn, btn_rect)
        else:
            screen.fill((20, 30, 60))
            title_text = font.render("My Clicker Game", True, "white")
            screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 80))

            button_rect = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 40, 200, 50)
            pygame.draw.rect(screen, (70, 180, 90), button_rect)
            button_text = button_font.render("Start Game", True, "white")
            screen.blit(button_text, (button_rect.x + 35, button_rect.y + 10))

        pygame.display.update()
        clock.tick(60)


def run_game(screen):
    pygame.display.set_caption("Cool Project")

    base_dir = os.path.join(os.path.dirname(__file__), "images")
    bg2_path = os.path.join(base_dir, "background 2.png")
    background = None
    if os.path.exists(bg2_path):
        background = pygame.image.load(bg2_path).convert()

    # creates a Character from the my_character.py file
    character = my_character.Character(screen, 100, 100)

    # set up the upgrade system
    manager = upgrade_module.UpgradeManager()
    manager.add_upgrade(upgrade_module.Upgrade("Click Power", 10, "Adds 1 point per click", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Auto Clicker", 50, "Adds 1 point per second", effect=1))

    score = 0
    frame_count = 0
    font = pygame.font.SysFont(None, 28)
    button_font = pygame.font.SysFont(None, 24)

    # let's set the framerate
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)  # this sets the framerate of your game
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                character_rect = pygame.Rect(character.x, character.y, 20, 20)
                click_button = pygame.Rect(40, 360, 220, 40)
                auto_button = pygame.Rect(280, 360, 220, 40)

                if character_rect.collidepoint(mouse_pos):
                    score += 1 + manager.get_total_effect("Click Power")

                if click_button.collidepoint(mouse_pos):
                    bought, cost, _, _ = manager.buy("Click Power", score)
                    if bought:
                        score -= cost

                if auto_button.collidepoint(mouse_pos):
                    bought, cost, _, _ = manager.buy("Auto Clicker", score)
                    if bought:
                        score -= cost

        # Passive income from Auto Clicker upgrades
        if frame_count % 60 == 0:
            score += manager.get_total_effect("Auto Clicker")

        # Fill the screen with background color
        if background is not None:
            bg_scaled = pygame.transform.smoothscale(background, screen.get_size())
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((255, 255, 255))

        # draws the character every frame
        character.draw()

        # draw score
        score_text = font.render(f"Score: {score}", True, "black")
        screen.blit(score_text, (20, 20))

        # draw upgrade buttons
        click_status = manager.get_status("Click Power")
        auto_status = manager.get_status("Auto Clicker")

        pygame.draw.rect(screen, (220, 220, 220), (40, 360, 220, 40))
        pygame.draw.rect(screen, (220, 220, 220), (280, 360, 220, 40))

        click_button_text = button_font.render(
            f"{click_status['name']} ({click_status['cost']})",
            True,
            "black",
        )
        auto_button_text = button_font.render(
            f"{auto_status['name']} ({auto_status['cost']})",
            True,
            "black",
        )
        screen.blit(click_button_text, (50, 370))
        screen.blit(auto_button_text, (290, 370))

        level_text = button_font.render(
            f"Click Lv: {click_status['level']}   Auto Lv: {auto_status['level']}",
            True,
            "black",
        )
        screen.blit(level_text, (20, 320))

        # don't forget the update, otherwise nothing will show up!
        pygame.display.update()


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    show_start_screen(screen)
    run_game(screen)


main()