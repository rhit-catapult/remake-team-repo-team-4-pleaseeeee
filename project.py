import pygame
import sys
import my_character
import upgrade_module


def main():
    # turn on pygame
    pygame.init()

    # create a screen
    pygame.display.set_caption("Cool Project")
    screen = pygame.display.set_mode((640, 480))

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
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                character_rect = pygame.Rect(character.x, character.y, 20, 20)
                click_button = pygame.Rect(40, 360, 220, 40)
                auto_button = pygame.Rect(280, 360, 220, 40)

                if character_rect.collidepoint(mouse_pos):
                    score += 1 + manager.get_total_effect("Click Power")

                if click_button.collidepoint(mouse_pos):
                    bought, cost, level, status = manager.buy("Click Power", score)
                    if bought:
                        score -= cost

                if auto_button.collidepoint(mouse_pos):
                    bought, cost, level, status = manager.buy("Auto Clicker", score)
                    if bought:
                        score -= cost

        # Passive income from Auto Clicker upgrades
        if frame_count % 60 == 0:
            score += manager.get_total_effect("Auto Clicker")

        # Fill the screen with background color
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


main()