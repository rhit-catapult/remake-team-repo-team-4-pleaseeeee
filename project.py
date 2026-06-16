import os
import sys
import json
import random
import pygame
import my_character
import upgrade_module


END_SCORE = 1_000_000
LEADERBOARD_FILE = "leaderboard.json"

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


def load_leaderboard():
    """Load leaderboard from JSON file."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_leaderboard(leaderboard):
    """Save leaderboard to JSON file."""
    try:
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(leaderboard, f, indent=2)
    except Exception:
        pass


def add_to_leaderboard(name, time_seconds):
    """Add a new entry to the leaderboard and keep top 10."""
    leaderboard = load_leaderboard()
    leaderboard.append({"name": name, "time": time_seconds})
    leaderboard.sort(key=lambda x: x["time"])
    leaderboard = leaderboard[:10]
    save_leaderboard(leaderboard)
    return leaderboard


def reset_leaderboard():
    """Clear the leaderboard."""
    save_leaderboard([])


def should_trigger_end_screen(score):
    return score >= END_SCORE


def build_upgrade_state():
    manager = upgrade_module.UpgradeManager()
    manager.add_upgrade(upgrade_module.Upgrade("Click Power", 10, "Adds 1 brownie per click", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Sweet Spark", 40, "Adds 1 brownie per second", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Auto Clicker", 50, "Adds 1 brownie per second", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Lucky Charm", 80, "Adds 2 brownies per click", effect=2))
    manager.add_upgrade(upgrade_module.Upgrade("Chef Boost", 100, "Adds 10 brownies per click", effect=10))
    manager.add_upgrade(upgrade_module.Upgrade("Kitchen Crew", 120, "Adds 10 brownies per second", effect=10))
    manager.add_upgrade(upgrade_module.Upgrade("Double Chocolate", 2500, "Adds 20 brownies per second", effect=20))
    manager.add_upgrade(upgrade_module.Upgrade("Town Buzz", 1200, "Adds 100 brownies per click", effect=100))
    manager.add_upgrade(upgrade_module.Upgrade("City Expansion", 1000, "Adds 100 brownies per second", effect=100))
    manager.add_upgrade(upgrade_module.Upgrade("Factory Line", 10000, "Adds 1000 brownies per second", effect=1000))
    manager.add_upgrade(upgrade_module.Upgrade("Mega Oven", 15000, "Adds 1000 brownies per click", effect=1000))

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
        pygame.Rect(35, 125, 320, 110),
        pygame.Rect(375, 125, 320, 110),
        pygame.Rect(35, 255, 320, 110),
        pygame.Rect(375, 255, 320, 110),
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


def draw_upgrade_button(screen, rect, color, title, cost, description, title_font, desc_font, text_color, affordable=True, icon_image=None):
    shadow_rect = rect.move(3, 3)
    pygame.draw.rect(screen, (70, 70, 70), shadow_rect, border_radius=16)

    button_color = color if affordable else tuple(max(0, c - 80) for c in color)
    pygame.draw.rect(screen, button_color, rect, border_radius=16)

    title_y = rect.y + 8
    cost_y = rect.y + 32
    desc_y = rect.y + 54
    content_x = rect.x + 8
    content_width = rect.width - 16

    if icon_image is not None:
        icon_size = 40
        icon = pygame.transform.smoothscale(icon_image, (icon_size, icon_size))
        icon_y = rect.y + (rect.height - icon_size) // 2
        screen.blit(icon, (rect.x + 8, icon_y))
        content_x += icon_size + 8
        content_width -= icon_size + 8

    draw_wrapped_text(screen, title_font, title, (content_x, title_y), text_color, content_width, line_height=18, center=True)
    cost_color = "#8fbc8f" if affordable else "#e07b7b"
    draw_wrapped_text(screen, desc_font, f"Cost: {cost} brownies", (content_x, cost_y), cost_color, content_width, line_height=16, center=True)
    draw_wrapped_text(screen, desc_font, description, (content_x, desc_y), text_color, content_width, line_height=14, center=True)


def draw_end_screen(screen, end_title, time_seconds=0):
    if end_title is not None:
        scaled_end_title = pygame.transform.smoothscale(end_title, (420, 220))
        title_rect = scaled_end_title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        screen.blit(scaled_end_title, title_rect)

    message_font = pygame.font.SysFont("comicsansms", 24)
    
    
    minutes = time_seconds // 60
    seconds = time_seconds % 60
    time_text = message_font.render(f"Time: {minutes}m {seconds}s", True, "white")
    time_rect = time_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 100))
    screen.blit(time_text, time_rect)
    
    message = message_font.render("Click to play again", True, "white")
    message_rect = message.get_rect(center=(screen.get_width() // 2, screen.get_height() - 60))
    screen.blit(message, message_rect)


def draw_goal_banner(screen, font):
    goal_text = "Your goal is to reach one million brownies."
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
    leaderboard_font = pygame.font.SysFont("comicsansms", 18)
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
                
                
                reset_button_rect = pygame.Rect(screen.get_width() - 150, 10, 140, 40)
                if reset_button_rect.collidepoint(event.pos):
                    reset_leaderboard()

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

        
        leaderboard = load_leaderboard()
        if leaderboard:
            leaderboard_title = leaderboard_font.render("Top Times:", True, "white")
            screen.blit(leaderboard_title, (20, 20))
            
            for idx, entry in enumerate(leaderboard[:5]):
                minutes = entry["time"] // 60
                seconds = entry["time"] % 60
                time_text = f"{idx + 1}. {entry['name']}: {minutes}m {seconds}s"
                leaderboard_text = leaderboard_font.render(time_text, True, "white")
                screen.blit(leaderboard_text, (20, 50 + idx * 25))
        
        
        reset_button_rect = pygame.Rect(screen.get_width() - 150, 10, 140, 40)
        draw_button(screen, reset_button_rect, (200, 100, 100), "Reset Times", button_font, "white")

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

    upgrade_icon_images = {}
    upgrade_icon_files = {
        "Click Power": "clicker.png",
        "Auto Clicker": "auto click.png",
        "Sweet Spark": "sparkle.png",
        "Lucky Charm": "lucky.png",
        "Chef Boost": "double chef.png",
        "Double Chocolate": "double cake.png",
        "Kitchen Crew": "kitchen crew.png",
        "Town Buzz": "town.png",
        "City Expansion": "city expansion.png",
        "Factory Line": "factory line.png",
        "Mega Oven": "mega oven.png",
    }
    for upgrade_name, file_name in upgrade_icon_files.items():
        image_path = os.path.join(os.path.dirname(__file__), file_name)
        if os.path.exists(image_path):
            upgrade_icon_images[upgrade_name] = pygame.image.load(image_path).convert_alpha()

    character = my_character.Character(screen, 220, 140)

    
    brownie_sound = None
    sound_path = os.path.join(os.path.dirname(__file__), "brownie.mp3")
    if os.path.exists(sound_path):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            brownie_sound = pygame.mixer.Sound(sound_path)
        except Exception:
            brownie_sound = None

    jj_path = os.path.join(os.path.dirname(__file__), "jj.png")
    jj_image = None
    if os.path.exists(jj_path):
        jj_image = pygame.image.load(jj_path).convert_alpha()
        jj_image = pygame.transform.smoothscale(jj_image, (80, 80))
    jj_active = False
    jj_rect = pygame.Rect(0, 0, 80, 80)
    jj_dx = 4
    jj_dy = 3
    auto_boost_active = False
    auto_boost_end_time = 0

    manager, upgrade_names, upgrade_button_positions, upgrade_colors, upgrade_pages = build_upgrade_state()
    current_page = 0
    purchase_message = ""

    score = 0
    frame_count = 0
    font = pygame.font.SysFont("comicsansms", 28)
    button_font = pygame.font.SysFont("comicsansms", 24)
    clock = pygame.time.Clock()
    screen_mode = "play"
    game_start_time = pygame.time.get_ticks() / 1000
    game_end_time = 0
    player_name = ""
    
    upgrades_offset = screen.get_height()
    total_height = screen.get_height() + screen.get_height()
    max_scroll = max(0, total_height - screen.get_height())
    scroll_y = 0
    
    upgrade_counts = {"chef": 0, "factory": 0, "city": 0}
    
    upgrade_category_map = {
        "Chef Boost": "chef",
        "Kitchen Crew": "chef",
        "Factory Line": "factory",
        "Town Buzz": "city",
        "City Expansion": "city",
    }
    
    mute_sound = False
    
    is_fullscreen = True

    while True:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            
            if event.type == pygame.MOUSEWHEEL:
                scroll_y = min(max(scroll_y - event.y * 40, 0), max_scroll)

            
            if event.type == pygame.KEYDOWN and screen_mode == "name_input":
                if event.key == pygame.K_RETURN and len(player_name) > 0:
                    add_to_leaderboard(player_name, int(game_end_time))
                    manager, upgrade_names, upgrade_button_positions, upgrade_colors, upgrade_pages = build_upgrade_state()
                    current_page = 0
                    score = 0
                    frame_count = 0
                    game_start_time = pygame.time.get_ticks() / 1000
                    screen_mode = "play"
                    upgrade_counts = {"chef": 0, "factory": 0, "city": 0}
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 20 and event.unicode.isalnum() or event.unicode == " ":
                    player_name += event.unicode

            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_y = min(max(scroll_y - 40, 0), max_scroll)
                    continue
                if event.button == 5:
                    scroll_y = min(max(scroll_y + 40, 0), max_scroll)
                    continue

                mouse_pos = pygame.mouse.get_pos()
                
                world_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)

                if screen_mode == "play":
                    character_rect = character.get_rect()
                    upgrades_button = pygame.Rect(470, 20, 140, 40)

                    if character_rect.collidepoint(world_pos):
                        click_bonus = 1 + get_click_bonus(manager)
                        if auto_boost_active:
                            click_bonus *= 2
                        score += click_bonus
                        if random.random() < 0.01 and not jj_active and jj_image is not None:
                            jj_active = True
                            jj_rect.x = random.randint(0, max(0, screen.get_width()-80))
                            jj_rect.y = random.randint(80, max(80, screen.get_height()-80))
                        if brownie_sound and not mute_sound:
                            try:
                                brownie_sound.play()
                            except Exception:
                                pass

                    if jj_active and jj_rect.collidepoint(world_pos):
                        jj_active = False
                        auto_boost_active = True
                        auto_boost_end_time = pygame.time.get_ticks() + 10000

                    mute_button_rect = pygame.Rect(650, 20, 100, 38)
                    if mute_button_rect.collidepoint(world_pos):
                        mute_sound = not mute_sound

                    fullscreen_button_rect = pygame.Rect(770, 20, 130, 38)
                    if fullscreen_button_rect.collidepoint(world_pos):
                        is_fullscreen = not is_fullscreen
                        if is_fullscreen:
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((1200, 700))
                        
                        upgrades_offset = screen.get_height()
                        total_height = screen.get_height() + screen.get_height()
                        max_scroll = max(0, total_height - screen.get_height())
                        scroll_y = 0

                    if upgrades_button.collidepoint(world_pos):
                       
                        if scroll_y < upgrades_offset // 2:
                            scroll_y = upgrades_offset
                        else:
                            scroll_y = 0

                elif screen_mode == "end":
                    player_name = ""
                    screen_mode = "name_input"

                
                try:
                    if world_pos[1] >= upgrades_offset:
                        
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
                                    
                                    if upgrade.name in upgrade_category_map:
                                        category = upgrade_category_map[upgrade.name]
                                        upgrade_counts[category] += 1
                                else:
                                    purchase_message = f"Need {cost} brownies for {status['name']}"
                except NameError:
                    
                    pass

        if screen_mode == "play" and frame_count % 60 == 0:
            auto_bonus = get_auto_bonus(manager)
            if auto_boost_active:
                auto_bonus *= 2
            score += auto_bonus

        if screen_mode == "play" and should_trigger_end_screen(score):
            game_end_time = pygame.time.get_ticks() / 1000 - game_start_time
            screen_mode = "end"

        if auto_boost_active and pygame.time.get_ticks() > auto_boost_end_time:
            auto_boost_active = False

        
        canvas = pygame.Surface((screen.get_width(), total_height))

        if background is not None:
            bg_scaled = pygame.transform.smoothscale(background, (canvas.get_width(), canvas.get_height()))
            canvas.blit(bg_scaled, (0, 0))
        else:
            canvas.fill((255, 255, 255))

        
        character.screen = canvas
        character.draw()

        score_text = font.render(f"Brownies: {score}", True, "#fff8e1")
        score_panel = pygame.Surface((score_text.get_width() + 24, score_text.get_height() + 12), pygame.SRCALPHA)
        score_panel.fill((40, 40, 40, 160))
        score_x = 20
        score_y = 16
        canvas.blit(score_panel, (score_x, score_y))
        draw_text_with_shadow(canvas, font, f"Brownies: {score}", (score_x + 12, score_y + 6), "#fff8e1")
        draw_goal_banner(canvas, button_font)

        upgrades_button = pygame.Rect(450, 16, 170, 46)
        draw_button(canvas, upgrades_button, (92, 184, 92), "Upgrades", button_font, "white")

        
        mute_button = pygame.Rect(650, 20, 100, 38)
        mute_text = "Unmute" if mute_sound else "Mute"
        mute_color = (150, 150, 150) if mute_sound else (200, 200, 200)
        draw_button(canvas, mute_button, mute_color, mute_text, button_font, "#3a220c")

        
        fullscreen_button = pygame.Rect(770, 20, 130, 38)
        fullscreen_text = "Windowed" if is_fullscreen else "Fullscreen"
        fullscreen_color = (100, 180, 220)
        draw_button(canvas, fullscreen_button, fullscreen_color, fullscreen_text, button_font, "white")

        
        icon_column_x = canvas.get_width() - 80
        icon_positions = [(icon_column_x, 110), (icon_column_x, 170), (icon_column_x, 230)]
        icon_names = ["chef", "factory", "city"]
        for idx, (icon_name, pos) in enumerate(zip(icon_names, icon_positions)):
            if icon_name in environment_images:
                icon_img = pygame.transform.smoothscale(environment_images[icon_name], (50, 50))
                canvas.blit(icon_img, pos)

        if jj_active and jj_image is not None:
            jj_rect.x += jj_dx
            jj_rect.y += jj_dy
            if jj_rect.left <= 0 or jj_rect.right >= screen.get_width():
                jj_dx *= -1
            if jj_rect.top <= 0 or jj_rect.bottom >= screen.get_height():
                jj_dy *= -1
            canvas.blit(jj_image, jj_rect)

        
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

        
        image_x = canvas.get_width() - 150
        image_y = base_y + 320
        if current_page == 0 and "chef" in environment_images:
            chef_image = pygame.transform.smoothscale(environment_images["chef"], (120, 120))
            canvas.blit(chef_image, (image_x, image_y))
        elif current_page == 1 and "factory" in environment_images:
            factory_image = pygame.transform.smoothscale(environment_images["factory"], (140, 130))
            canvas.blit(factory_image, (image_x, image_y))
        elif current_page == 2 and "city" in environment_images:
            city_image = pygame.transform.smoothscale(environment_images["city"], (140, 120))
            canvas.blit(city_image, (image_x, image_y))

        
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
            icon_image = upgrade_icon_images.get(upgrade.name)
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
                icon_image=icon_image,
            )

        draw_button(canvas, pygame.Rect(150, 420 + base_y, 100, 32), (220, 220, 220), "Prev", button_font, "#3a220c")
        draw_button(canvas, pygame.Rect(390, 420 + base_y, 100, 32), (220, 220, 220), "Next", button_font, "#3a220c")

        page_text = button_font.render(f"Page {current_page + 1}/{len(upgrade_pages)}", True, "#3a220c")
        canvas.blit(page_text, (270, 426 + base_y))

        if purchase_message:
            draw_text_with_shadow(canvas, button_font, purchase_message, (20, 370 + base_y), "#3a220c")

        
        if screen_mode == "name_input":
            # Draw name input screen
            screen.blit(canvas, (0, -scroll_y))
            name_input_surf = pygame.Surface((400, 200), pygame.SRCALPHA)
            name_input_surf.fill((0, 0, 0, 180))
            screen.blit(name_input_surf, (screen.get_width() // 2 - 200, screen.get_height() // 2 - 100))
            
            prompt_font = pygame.font.SysFont("comicsansms", 32)
            input_font = pygame.font.SysFont("comicsansms", 28)
            
            prompt_text = prompt_font.render("Enter your name:", True, "white")
            screen.blit(prompt_text, (screen.get_width() // 2 - prompt_text.get_width() // 2, screen.get_height() // 2 - 80))
            
            name_display = input_font.render(player_name + "|", True, "white")
            screen.blit(name_display, (screen.get_width() // 2 - name_display.get_width() // 2, screen.get_height() // 2 - 20))
            
            instruction_font = pygame.font.SysFont("comicsansms", 20)
            instruction_text = instruction_font.render("Press ENTER to continue", True, "yellow")
            screen.blit(instruction_text, (screen.get_width() // 2 - instruction_text.get_width() // 2, screen.get_height() // 2 + 40))
        elif screen_mode == "end":
            
            screen.blit(canvas, (0, -scroll_y))
            draw_end_screen(screen, end_title, int(game_end_time))
        else:
            
            screen.blit(canvas, (0, -scroll_y))

        pygame.display.update()


def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 700))
    show_start_screen(screen)
    run_game(screen)


if __name__ == "__main__":
    main()

