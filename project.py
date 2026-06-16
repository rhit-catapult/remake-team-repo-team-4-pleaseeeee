import os
import sys
import pygame
import my_character
import upgrade_module


END_SCORE = 1_000_000

CLICK_UPGRADES = (
    "Click Power",
    "Lucky Charm",
    "Chef Boost",
    "Town Buzz",
    "Mega Oven",
)
AUTO_UPGRADES = (
    "Sweet Spark",
    "Auto Clicker",
    "Kitchen Crew",
    "City Expansion",
    "Double Chocolate",
    "Factory Line",
)


def should_trigger_end_screen(score):
    return score >= END_SCORE


def build_upgrade_state():
    manager = upgrade_module.UpgradeManager()
    manager.add_upgrade(upgrade_module.Upgrade("Click Power", 10, "Adds 1 point per click", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Sweet Spark", 40, "Adds 1 point per second", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Auto Clicker", 50, "Adds 1 point per second", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Lucky Charm", 80, "Adds 2 points per click", effect=2))
    manager.add_upgrade(upgrade_module.Upgrade("Chef Boost", 100, "Adds 10 points per click", effect=10))
    manager.add_upgrade(upgrade_module.Upgrade("Kitchen Crew", 120, "Adds 10 points per second", effect=10))
    manager.add_upgrade(upgrade_module.Upgrade("Double Chocolate", 2500, "Adds 20 points per second", effect=20))
    manager.add_upgrade(upgrade_module.Upgrade("Town Buzz", 1200, "Adds 100 points per click", effect=100))
    manager.add_upgrade(upgrade_module.Upgrade("City Expansion", 1000, "Adds 100 points per second", effect=100))
    manager.add_upgrade(upgrade_module.Upgrade("Factory Line", 10000, "Adds 1000 points per second", effect=1000))
    manager.add_upgrade(upgrade_module.Upgrade("Mega Oven", 15000, "Adds 1000 points per click", effect=1000))

    upgrade_names = [
        "Click Power",
        "Sweet Spark",
        "Auto Clicker",
        "Lucky Charm",
        "Chef Boost",
        "Kitchen Crew",
        "Double Chocolate",
        "Town Buzz",
        "City Expansion",
        "Factory Line",
        "Mega Oven",
    ]
    upgrade_button_positions = [
        pygame.Rect(35, 125, 260, 80),
        pygame.Rect(345, 125, 260, 80),
        pygame.Rect(35, 215, 260, 80),
        pygame.Rect(345, 215, 260, 80),
    ]
    upgrade_colors = [
        (255, 214, 102),
        (255, 170, 110),
        (120, 180, 255),
        (120, 220, 140),
        (255, 140, 120),
        (176, 224, 230),
        (255, 215, 0),
        (255, 192, 203),
    ]
    upgrade_pages = upgrade_module.split_upgrades_into_pages([manager.upgrades[name] for name in upgrade_names], page_size=4)
    return manager, upgrade_names, upgrade_button_positions, upgrade_colors, upgrade_pages


def draw_text_with_shadow(screen, font, text, pos, color, shadow_color=(0, 0, 0), offset=(1, 1)):
    shadow_surface = font.render(text, True, shadow_color)
    screen.blit(shadow_surface, (pos[0] + offset[0], pos[1] + offset[1]))
    main_surface = font.render(text, True, color)
    screen.blit(main_surface, pos)


def draw_button(screen, rect, color, text, font, text_color, shadow_color=(0, 0, 0), radius=16):
    shadow_rect = rect.move(3, 3)
    pygame.draw.rect(screen, (70, 70, 70), shadow_rect, border_radius=radius)
    pygame.draw.rect(screen, color, rect, border_radius=radius)

    text_surface = font.render(text, True, text_color)
    text_x = rect.x + (rect.width - text_surface.get_width()) // 2
    text_y = rect.y + (rect.height - text_surface.get_height()) // 2
    draw_text_with_shadow(screen, font, text, (text_x, text_y), text_color, shadow_color=shadow_color)


def draw_wrapped_text(screen, font, text, pos, color, max_width, line_height=18, center=False):
    words = text.split()
    if not words:
        return

    lines = []
    current_line = words[0]
    for word in words[1:]:
        candidate = f"{current_line} {word}"
        if font.size(candidate)[0] <= max_width:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    for index, line in enumerate(lines):
        line_surface = font.render(line, True, color)
        x = pos[0] + (max_width - line_surface.get_width()) // 2 if center else pos[0]
        y = pos[1] + index * line_height
        screen.blit(line_surface, (x, y))


def draw_upgrade_button(screen, rect, color, title, cost, description, title_font, desc_font, text_color, affordable=True):
    shadow_rect = rect.move(3, 3)
    pygame.draw.rect(screen, (70, 70, 70), shadow_rect, border_radius=16)

    button_color = color if affordable else tuple(max(0, c - 80) for c in color)
    pygame.draw.rect(screen, button_color, rect, border_radius=16)

    title_y = rect.y + 8
    cost_y = rect.y + 32
    desc_y = rect.y + 54

    draw_wrapped_text(screen, title_font, title, (rect.x + 8, title_y), text_color, rect.width - 16, line_height=18, center=True)
    cost_color = "#8fbc8f" if affordable else "#e07b7b"
    draw_wrapped_text(screen, desc_font, f"Cost: {cost}", (rect.x + 8, cost_y), cost_color, rect.width - 16, line_height=16, center=True)
    draw_wrapped_text(screen, desc_font, description, (rect.x + 8, desc_y), text_color, rect.width - 16, line_height=14, center=True)


def draw_end_screen(screen, end_title):
    if end_title is not None:
        scaled_end_title = pygame.transform.smoothscale(end_title, (420, 220))
        title_rect = scaled_end_title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        screen.blit(scaled_end_title, title_rect)

    message_font = pygame.font.SysFont("comicsansms", 24)
    message = message_font.render("Click to play again", True, "white")
    message_rect = message.get_rect(center=(screen.get_width() // 2, screen.get_height() - 60))
    screen.blit(message, message_rect)


def draw_goal_banner(screen, font):
    goal_text = "Your goal is to reach a score of one million."
    text_surface = font.render(goal_text, True, "#fff8e1")
    panel = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 12), pygame.SRCALPHA)
    panel.fill((40, 40, 40, 180))
    screen.blit(panel, (16, 72))
    screen.blit(text_surface, (28, 78))


def get_upgrade_effect(manager, name):
    try:
        return manager.get_total_effect(name)
    except KeyError:
        return 0


def get_click_bonus(manager):
    return sum(get_upgrade_effect(manager, name) for name in CLICK_UPGRADES)


def get_auto_bonus(manager):
    return sum(get_upgrade_effect(manager, name) for name in AUTO_UPGRADES)


def show_start_screen(screen):
    pygame.display.set_caption("Brownie Clicker")

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

    font = pygame.font.SysFont("comicsansms", 56)
    button_font = pygame.font.SysFont("comicsansms", 28)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                button_rect = pygame.Rect(screen.get_width() // 2 - 115, screen.get_height() // 2 + 60, 230, 60)
                if button_rect.collidepoint(event.pos):
                    return

        if bg1 is not None and bg2 is not None:
            bg_scaled = pygame.transform.smoothscale(bg1, screen.get_size())
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((20, 30, 60))

        title_text = font.render("Brownie Clicker", True, "black")
        title_x = (screen.get_width() - title_text.get_width()) // 2
        title_y = (screen.get_height() - title_text.get_height()) // 2 - 40
        screen.blit(title_text, (title_x, title_y))

        button_rect = pygame.Rect(screen.get_width() // 2 - 115, screen.get_height() // 2 + 60, 230, 60)
        draw_button(screen, button_rect, (220, 70, 70), "Play Brownies", button_font, "white")

        pygame.display.update()
        clock.tick(60)


def run_game(screen):
    pygame.display.set_caption("Brownie Clicker")

    base_dir = os.path.join(os.path.dirname(__file__), "images")
    bg2_path = os.path.join(base_dir, "background 2.png")
    background = None
    if os.path.exists(bg2_path):
        background = pygame.image.load(bg2_path).convert()

    end_title_path = os.path.join(os.path.dirname(__file__), "end title.png")
    end_title = None
    if os.path.exists(end_title_path):
        end_title = pygame.image.load(end_title_path).convert_alpha()

    environment_images = {}
    for name in ["chef", "city", "factory"]:
        image_path = os.path.join(os.path.dirname(__file__), f"{name}.png")
        if os.path.exists(image_path):
            environment_images[name] = pygame.image.load(image_path).convert_alpha()

    character = my_character.Character(screen, 220, 140)

    # Load brownie click sound (if available)
    brownie_sound = None
    sound_path = os.path.join(os.path.dirname(__file__), "brownie.mp3")
    if os.path.exists(sound_path):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            brownie_sound = pygame.mixer.Sound(sound_path)
        except Exception:
            brownie_sound = None

    manager, upgrade_names, upgrade_button_positions, upgrade_colors, upgrade_pages = build_upgrade_state()
    current_page = 0
    purchase_message = ""

    score = 0
    frame_count = 0
    font = pygame.font.SysFont("comicsansms", 28)
    button_font = pygame.font.SysFont("comicsansms", 24)
    clock = pygame.time.Clock()
    screen_mode = "play"
    # Scrolling setup: upgrades live below the main play area
    upgrades_offset = screen.get_height()
    total_height = screen.get_height() + screen.get_height()
    max_scroll = max(0, total_height - screen.get_height())
    scroll_y = 0

    while True:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse wheel support (pygame.MOUSEWHEEL)
            if event.type == pygame.MOUSEWHEEL:
                scroll_y = min(max(scroll_y - event.y * 40, 0), max_scroll)

            # Older mouse wheel via button 4/5
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_y = min(max(scroll_y - 40, 0), max_scroll)
                    continue
                if event.button == 5:
                    scroll_y = min(max(scroll_y + 40, 0), max_scroll)
                    continue

                mouse_pos = pygame.mouse.get_pos()
                # translate to canvas/world coordinates
                world_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)

                if screen_mode == "play":
                    character_rect = character.get_rect()
                    upgrades_button = pygame.Rect(470, 20, 140, 40)

                    if character_rect.collidepoint(world_pos):
                        click_bonus = 1 + get_click_bonus(manager)
                        score += click_bonus
                        if brownie_sound:
                            try:
                                brownie_sound.play()
                            except Exception:
                                pass

                    if upgrades_button.collidepoint(world_pos):
                        # toggle scroll to upgrades section
                        if scroll_y < upgrades_offset // 2:
                            scroll_y = upgrades_offset
                        else:
                            scroll_y = 0

                elif screen_mode == "end":
                    manager, upgrade_names, upgrade_button_positions, upgrade_colors, upgrade_pages = build_upgrade_state()
                    current_page = 0
                    score = 0
                    frame_count = 0
                    screen_mode = "play"

                # Handle clicks in the upgrades area (below the play area)
                # world_pos is defined above when processing MOUSEBUTTONDOWN
                try:
                    if world_pos[1] >= upgrades_offset:
                        # Back button scrolls to top
                        back_button = pygame.Rect(20, 16 + upgrades_offset, 110, 40)
                        prev_page_button = pygame.Rect(150, 420 + upgrades_offset, 100, 34)
                        next_page_button = pygame.Rect(390, 420 + upgrades_offset, 100, 34)

                        if back_button.collidepoint(world_pos):
                            scroll_y = 0
                            purchase_message = ""

                        if prev_page_button.collidepoint(world_pos) and current_page > 0:
                            current_page -= 1
                            purchase_message = ""

                        if next_page_button.collidepoint(world_pos) and current_page < len(upgrade_pages) - 1:
                            current_page += 1
                            purchase_message = ""

                        for index, upgrade in enumerate(upgrade_pages[current_page]):
                            if index >= len(upgrade_button_positions):
                                continue

                            rect = upgrade_button_positions[index].move(0, upgrades_offset)
                            if rect.collidepoint(world_pos):
                                bought, cost, _, status = manager.buy(upgrade.name, score)
                                if bought:
                                    score -= cost
                                    purchase_message = f"Bought {status['name']}!"
                                else:
                                    purchase_message = f"Need {cost} points for {status['name']}"
                except NameError:
                    # world_pos may not be defined for non-MOUSEBUTTONDOWN events
                    pass

        if screen_mode == "play" and frame_count % 60 == 0:
            auto_bonus = get_auto_bonus(manager)
            score += auto_bonus

        if screen_mode == "play" and should_trigger_end_screen(score):
            screen_mode = "end"

        # Draw everything to a taller canvas, then blit the visible portion
        canvas = pygame.Surface((screen.get_width(), total_height))

        if background is not None:
            bg_scaled = pygame.transform.smoothscale(background, (canvas.get_width(), canvas.get_height()))
            canvas.blit(bg_scaled, (0, 0))
        else:
            canvas.fill((255, 255, 255))

        # Play area (top of canvas)
        # ensure character draws onto the canvas surface
        character.screen = canvas
        character.draw()

        score_text = font.render(f"Score: {score}", True, "#fff8e1")
        score_panel = pygame.Surface((score_text.get_width() + 24, score_text.get_height() + 12), pygame.SRCALPHA)
        score_panel.fill((40, 40, 40, 160))
        score_x = 20
        score_y = 16
        canvas.blit(score_panel, (score_x, score_y))
        draw_text_with_shadow(canvas, font, f"Score: {score}", (score_x + 12, score_y + 6), "#fff8e1")
        draw_goal_banner(canvas, button_font)

        upgrades_button = pygame.Rect(450, 16, 170, 46)
        draw_button(canvas, upgrades_button, (92, 184, 92), "Upgrades", button_font, "white")

        # Upgrades area (below play area)
        base_y = upgrades_offset

        header_text = font.render("Upgrades", True, "#3a220c")
        header_width = header_text.get_width() + 32
        header_height = header_text.get_height() + 14
        header_panel = pygame.Surface((header_width, header_height), pygame.SRCALPHA)
        header_panel.fill((255, 247, 224, 170))
        header_x = (canvas.get_width() - header_width) // 2
        header_y = base_y + 2
        canvas.blit(header_panel, (header_x, header_y))
        draw_text_with_shadow(
            canvas,
            font,
            "Upgrades",
            (header_x + 16, header_y + 4),
            "#3a220c",
        )

        back_button = pygame.Rect(20, 16 + base_y, 110, 40)
        draw_button(canvas, back_button, (225, 225, 225), "Back", button_font, "#3a220c")

        click_income = 1 + get_click_bonus(manager)
        auto_income = get_auto_bonus(manager)

        image_x = canvas.get_width() - 128
        image_y = base_y + canvas.get_height() - 130

        if current_page == 0 and "chef" in environment_images:
            chef_image = pygame.transform.smoothscale(environment_images["chef"], (92, 92))
            canvas.blit(chef_image, (image_x, image_y))
        elif current_page == 1 and "factory" in environment_images:
            factory_image = pygame.transform.smoothscale(environment_images["factory"], (124, 100))
            canvas.blit(factory_image, (image_x, image_y))
        elif current_page == 2 and "city" in environment_images:
            city_image = pygame.transform.smoothscale(environment_images["city"], (120, 92))
            canvas.blit(city_image, (image_x, image_y))

        # level panel
        level_text = button_font.render(
            f"Click Income: {click_income}   Auto Income: {auto_income}",
            True,
            "#3a220c",
        )
        level_width = level_text.get_width() + 28
        level_height = level_text.get_height() + 12
        level_panel = pygame.Surface((level_width, level_height), pygame.SRCALPHA)
        level_panel.fill((255, 247, 224, 170))
        level_x = (canvas.get_width() - level_width) // 2
        level_y = base_y + 56
        canvas.blit(level_panel, (level_x, level_y))
        draw_text_with_shadow(
            canvas,
            button_font,
            f"Click Income: {click_income}   Auto Income: {auto_income}",
            (level_x + 14, level_y + 4),
            "#3a220c",
        )

        for index, upgrade in enumerate(upgrade_pages[current_page]):
            status = manager.get_status(upgrade.name)
            rect = upgrade_button_positions[index].move(0, base_y)
            button_color = upgrade_colors[index] if index < len(upgrade_colors) else (200, 200, 200)
            can_afford = score >= status['cost']
            draw_upgrade_button(
                canvas,
                rect,
                button_color,
                status['name'],
                status['cost'],
                status['description'],
                pygame.font.SysFont("comicsansms", 16),
                pygame.font.SysFont("comicsansms", 12),
                "#3a220c",
                affordable=can_afford,
            )

        draw_button(canvas, pygame.Rect(150, 420 + base_y, 100, 32), (220, 220, 220), "Prev", button_font, "#3a220c")
        draw_button(canvas, pygame.Rect(390, 420 + base_y, 100, 32), (220, 220, 220), "Next", button_font, "#3a220c")

        page_text = button_font.render(f"Page {current_page + 1}/{len(upgrade_pages)}", True, "#3a220c")
        canvas.blit(page_text, (270, 426 + base_y))

        if purchase_message:
            draw_text_with_shadow(canvas, button_font, purchase_message, (20, 370 + base_y), "#3a220c")

        # End screen overlay if triggered
        if screen_mode != "end":
            # blit visible portion of canvas
            screen.blit(canvas, (0, -scroll_y))
        else:
            # show end overlay on top of visible canvas
            screen.blit(canvas, (0, -scroll_y))
            draw_end_screen(screen, end_title)

        pygame.display.update()


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    show_start_screen(screen)
    run_game(screen)


if __name__ == "__main__":
    main()