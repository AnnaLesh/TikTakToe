from typing import Literal
import pygame
import math
import random
pygame.init()

screen_width = 700
screen_height = 700
screen = pygame.display.set_mode(size=(screen_width, screen_height), flags=pygame.SRCALPHA)

clock = pygame.time.Clock()
running = True

target_fps = 60

cell_size_px = 90
img_size_px = 75
origin = (0, 0)

grid_color = (100, 100, 100)
drag_prev = None
f1 = pygame.font.Font('./fonts/mr_countryhouseg_0.ttf', 50)
text1 = f1.render("New Year's Tic Tac Toe", True,
                  (180, 0, 0))
text_rect = text1.get_rect(center=(screen_width/2, screen_height/2))
ghost_alpha = round(255 * 0.35)

snowflake_image = pygame.image.load("./img/snowflake.jpg")
snowflake_scale_x = snowflake_image.get_width() / snowflake_image.get_height()
snowflake_scale_y = 1
snowflake_image = pygame.transform.smoothscale(
    snowflake_image,
    (round(img_size_px * snowflake_scale_x), round(img_size_px * snowflake_scale_y)),
)

snowflake_image_transparent = pygame.Surface(
    (snowflake_image.get_width(), snowflake_image.get_height()),
)
snowflake_image_transparent.blit(snowflake_image, (0, 0))
snowflake_image_transparent.set_alpha(ghost_alpha)

ball_image = pygame.image.load("./img/ball.jpg")
ball_scale_x = ball_image.get_width() / ball_image.get_height()
ball_scale_y = 1
ball_image = pygame.transform.smoothscale(
    ball_image, (round(img_size_px * ball_scale_x), round(img_size_px * ball_scale_y))
)

ball_image_transparent = pygame.Surface(
    (ball_image.get_width(), ball_image.get_height())
)
ball_image_transparent.blit(ball_image, (0, 0))
ball_image_transparent.set_alpha(127)

# Starting animation
santa_sprite_4x4_image = pygame.image.load("./img/santa_sprite_4x4.jpg")


def get_santa_image(i: int):
    image = pygame.Surface((256, 256))
    x = (i % 4) * 256
    y = (i // 4) * 256
    image.blit(santa_sprite_4x4_image, (0, 0), (x, y, 256, 256))
    return image


images = [i for i in range(16)]
for i in images:
    images[i] = get_santa_image(i)


animation_time_current = 0
animation_time_total = 1.75

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
            break
    screen.fill((255, 255, 255))
    screen.blit(text1, (120, 110))
    pygame.display.update()

    sprite_index = math.floor((animation_time_current % 1) * 16)
    x = screen.get_width() / 2 - 128
    y = screen.get_height() / 2 - 128
    image = images[sprite_index]
    screen.blit(image, (x, y))
    pygame.display.flip()
    animation_time_current += clock.tick(target_fps) / 1000
    if animation_time_current >= animation_time_total:
        break

# Game

SNOWFLAKE = 0
BALL = 1

next_cell_type: Literal[0, 1] = SNOWFLAKE
winner: None | Literal[0, 1] = None

cells: dict[tuple[int, int], Literal[0, 1]] = {}


def screen_vec_to_game_vec(vec2: tuple[float, float]):
    return (vec2[0] / cell_size_px, vec2[1] / cell_size_px)


def screen_to_game_coords_no_origin(coords: tuple[float, float]):
    return (
        (coords[0] - screen.get_width() / 2) / cell_size_px,
        (coords[1] - screen.get_height() / 2) / cell_size_px,
    )


def screen_to_game_coords(coords: tuple[float, float]):
    coords = screen_to_game_coords_no_origin(coords)
    return (
        coords[0] - origin[0],
        coords[1] - origin[1],
    )


def game_to_screen_coords(coords: tuple[float, float]):
    return (
        (coords[0] + origin[0]) * cell_size_px + screen.get_width() / 2,
        (coords[1] + origin[1]) * cell_size_px + screen.get_height() / 2,
    )


def handle_events():
    global drag_prev
    for event in pygame.event.get():
        handle_event(event)


def handle_event(event: pygame.event.Event):
    global running
    match event.type:
        case pygame.QUIT:
            pygame.quit()
            running = False
        case pygame.MOUSEBUTTONDOWN:
            handle_mouse_button_down()
        case pygame.MOUSEBUTTONUP:
            handle_mouse_button_up()
        case pygame.MOUSEMOTION:
            handle_mouse_motion()


def handle_mouse_button_down():
    global drag_prev
    pressed = pygame.mouse.get_pressed()
    if pressed[0]:
        handle_left_mouse_button_down()
    if pressed[1]:
        handle_middle_mouse_button_down()


def handle_left_mouse_button_down():
    global cells, next_cell_type, winner
    cursor_pos = screen_to_game_coords(pygame.mouse.get_pos())
    cursor_pos = (round(cursor_pos[0]), round(cursor_pos[1]))
    if cursor_pos in cells:
        return

    cells[cursor_pos] = next_cell_type
    if (
        check_line(cursor_pos, (1, 0), next_cell_type)
        or check_line(cursor_pos, (0, 1), next_cell_type)
        or check_line(cursor_pos, (1, 1), next_cell_type)
        or check_line(cursor_pos, (1, -1), next_cell_type)
    ):
        winner = next_cell_type
        next_cell_type = SNOWFLAKE
        return

    next_cell_type = (next_cell_type + 1) % 2


def check_line(
    pos: tuple[int, int],
    direction: tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]],
    cell_type: Literal[0, 1],
):
    direction2 = (direction[0] * -1, direction[1] * -1)

    return (
        count_cells_in_direction(pos, direction, cell_type)
        + count_cells_in_direction(pos, direction2, cell_type)
        >= 4
    )


def count_cells_in_direction(
    prev_cell_pos: tuple[int, int],
    direction: tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]],
    cell_type: Literal[0, 1],
):
    cell_pos = (prev_cell_pos[0] + direction[0], prev_cell_pos[1] + direction[1])
    if cell_pos not in cells or cells[cell_pos] != cell_type:
        return 0

    return 1 + count_cells_in_direction(cell_pos, direction, cell_type)


def handle_middle_mouse_button_down():
    global drag_prev
    if drag_prev is not None:
        return
    drag_prev = pygame.mouse.get_pos()


def handle_mouse_button_up():
    pressed = pygame.mouse.get_pressed()
    if not pressed[1]:
        handle_middle_mouse_button_up()


def handle_middle_mouse_button_up():
    global drag_prev
    drag_prev = None


def handle_mouse_motion():
    global drag_prev, origin
    if drag_prev is None:
        return
    pos = pygame.mouse.get_pos()
    offset = screen_vec_to_game_vec((pos[0] - drag_prev[0], pos[1] - drag_prev[1]))
    origin = (origin[0] + offset[0], origin[1] + offset[1])
    drag_prev = pos


def get_mouse_position():
    if not pygame.mouse.get_focused():
        return None
    return pygame.mouse.get_pos()


def render_grid():
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    p0 = screen_to_game_coords((0, 0))
    p0 = (round(p0[0] - 0.5), round(p0[1] - 0.5))
    p1 = screen_to_game_coords((screen_width, screen_height))
    p1 = (round(p1[0] + 0.5), round(p1[1] + 0.5))

    for x in range(p0[0], p1[0] + 1):
        l0 = game_to_screen_coords((x - 0.5, p0[1] - 0.5))
        l1 = game_to_screen_coords((x - 0.5, p1[1] + 0.5))
        pygame.draw.line(screen, grid_color, l0, l1, 2)

    for y in range(p0[1], p1[1] + 1):
        l0 = game_to_screen_coords((p0[0] - 0.5, y - 0.5))
        l1 = game_to_screen_coords((p1[0] + 0.5, y - 0.5))
        pygame.draw.line(screen, grid_color, l0, l1, 2)


def game_loop():
    while running and winner is None:
        handle_events()
        if not running:
            break

        mouse_pos = get_mouse_position()
        cursor_pos = None

        if mouse_pos is not None:
            # origin = screen_to_game_coords_no_origin(mousePos)
            cursor_pos = screen_to_game_coords(mouse_pos)
            cursor_pos = (round(cursor_pos[0]), round(cursor_pos[1]))

        screen.fill((255, 255, 255))

        for cell_pos in cells:
            cell_type = cells[cell_pos]
            img = snowflake_image
            if cell_type == BALL:
                img = ball_image

            p0 = game_to_screen_coords((cell_pos[0], cell_pos[1]))

            screen.blit(
                img,
                (p0[0] - img.get_width() / 2, p0[1] - img.get_height() / 2),
            )

        if (cursor_pos is not None) and (cursor_pos not in cells):
            img = snowflake_image_transparent
            if next_cell_type == BALL:
                img = ball_image_transparent

            p0 = game_to_screen_coords((cursor_pos[0], cursor_pos[1]))
            screen.blit(
                img,
                (p0[0] - img.get_width() / 2, p0[1] - img.get_height() / 2),
            )

        render_grid()
        pygame.display.flip()
        clock.tick(target_fps)


font0 = pygame.font.Font("./fonts/Roboto-Regular.ttf", 56)
font1 = pygame.font.Font("./fonts/Roboto-Regular.ttf", 24)

snowflakes_won_text = font0.render("Снежинки победили", True, (0, 63, 189))
balls_won_text = font0.render("Шары победили", True, (0, 63, 189))
click_to_restart_text = font1.render(
    "Кликните, чтобы начать заново", True, (0, 63, 189)
)
text_gap = 16
all_text_height = (
    snowflakes_won_text.get_height() + text_gap + click_to_restart_text.get_height()
)


def win_screen():
    global running, winner, origin
    while running and winner is not None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                winner = None
                origin = (0, 0)
                cells.clear()
                return


        screen.fill((255, 255, 255))

        win_text = snowflakes_won_text
        if winner == BALL:
            win_text = balls_won_text

        text_x = (screen.get_width() - win_text.get_width()) / 2
        text_y = (screen.get_height() - all_text_height) / 2
        screen.blit(
            win_text,
            (text_x, text_y),
        )

        text_y += win_text.get_height() + text_gap
        text_x = (screen.get_width() - click_to_restart_text.get_width()) / 2
        screen.blit(
            click_to_restart_text,
            (text_x, text_y),
        )

        pygame.display.flip()
        clock.tick(target_fps)


while running:

    game_loop()
    win_screen()

