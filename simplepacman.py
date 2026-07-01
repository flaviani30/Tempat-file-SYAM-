import pygame
import sys
import random
from pathlib import Path

# 1. INISIALISASI & KONFIGURASI DASAR
pygame.init()
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# Desain Labirin Utuh (1=Dinding, 0=Makanan, 2=Kosong/Penjara, 3=Pintu Penjara)
MAP = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
       [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
       [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1],
       [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
       [1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1],
       [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
       [1,1,1,0,1,0,1,1,1,1,3,1,1,1,1,0,1,0,1,1,1],
       [1,0,0,0,0,0,1,2,2,2,2,2,2,2,1,0,0,0,0,0,1],
       [1,0,1,1,1,0,1,2,1,1,2,1,1,2,1,0,1,1,1,0,1],
       [1,0,0,0,1,0,1,2,1,2,2,2,1,2,1,0,1,0,0,0,1],
       [1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1],
       [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
       [1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
       [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
       [1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1],
       [1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1],
       [1,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1],
       [1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
       [1,0,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
       [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
       [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 680
HUD_HEIGHT = 40
GRID_SIZE = min(28, max(20, (SCREEN_WIDTH - 20) // len(MAP[0])), max(20, (SCREEN_HEIGHT - HUD_HEIGHT - 20) // len(MAP)))

# Ukuran layar disesuaikan agar seluruh maze tampil penuh
WIDTH = len(MAP[0]) * GRID_SIZE
HEIGHT = (len(MAP) * GRID_SIZE) + HUD_HEIGHT
MAZE_OFFSET_X = max(0, (SCREEN_WIDTH - WIDTH) // 2)
MAZE_OFFSET_Y = max(0, (SCREEN_HEIGHT - HEIGHT) // 2)

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pacman Python - Dual Ghosts Jail Edition")
CLOCK = pygame.time.Clock()
FPS = 60

# Warna (RGB)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)

# 💾 MEKANISME MEMBACA HIGH SCORE DARI FILE
HS_FILE = BASE_DIR / "highscore.txt"
if HS_FILE.exists():
    with open(HS_FILE, "r") as f:
        try:
            high_score = int(f.read())
        except ValueError:
            high_score = 0
else:
    high_score = 0

# 2. VARIABLE STATS PACMAN
pacman_x, pacman_y = GRID_SIZE + 8, GRID_SIZE + 8  
pacman_speed = 2
pacman_radius = 12
score = 0
direction = (0, 0)  
requested_direction = (0, 0)
angle = 0           
font = pygame.font.SysFont("Arial", 22)
game_state = "PLAYING" 

# DATA STRUKTUR UNTUK 2 HANTU (Daftar Dictionary)
def load_image(relative_path, size=None):
    full_path = ASSETS_DIR / relative_path
    try:
        image = pygame.image.load(str(full_path))
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        return None

ghosts = [
    {"x": 10 * GRID_SIZE + 8, "y": 7 * GRID_SIZE + 8, "color": RED, "dir": (0, 0), "speed": 3, "radius": 12, "name": "Blinky", "style": "straight", "base_speed": 3, "frightened": False, "home_x": 10 * GRID_SIZE + 8, "home_y": 7 * GRID_SIZE + 8, "img": load_image("ghost/ghost_blinky.png", (24, 24))},
    {"x": 11 * GRID_SIZE + 8, "y": 7 * GRID_SIZE + 8, "color": ORANGE, "dir": (0, 0), "speed": 2, "radius": 12, "name": "Clyde", "style": "random", "base_speed": 2, "frightened": False, "home_x": 11 * GRID_SIZE + 8, "home_y": 7 * GRID_SIZE + 8, "img": load_image("ghost/ghost_clyde.png", (24, 24))},
    {"x": 9 * GRID_SIZE + 8, "y": 7 * GRID_SIZE + 8, "color": PINK, "dir": (0, 0), "speed": 2, "radius": 12, "name": "Pinky", "style": "ambush", "base_speed": 2, "frightened": False, "home_x": 9 * GRID_SIZE + 8, "home_y": 7 * GRID_SIZE + 8, "img": load_image("ghost/ghost_clyde.png", (24, 24))}
]
ghost_directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

POWER_MODE_DURATION = 6000
power_mode = False
power_mode_timer = 0
lives = 3
power_pellet_positions = [(1, 1), (19, 1), (1, 18), (19, 18)]
power_pellet_rects = []
dots = []

# TIMING UNTUK PINTU PENJARA
jail_timer = 5000  
door_open = False
start_ticks = pygame.time.get_ticks() 

# 3. MEMUAT GAMBAR PACMAN
pacman_frames = []
for frame_num in range(1, 6):
    frame = load_image(f"player/pacman_{frame_num}.png", (pacman_radius * 2, pacman_radius * 2))
    if frame:
        pacman_frames.append(frame)
pacman_img = pacman_frames[0] if pacman_frames else None
pacman_frame_index = 0
animation_timer = 0

# 4. MEMUAT ASSET VISUAL UNTUK LABIRIN DAN ITEM
wall_tile_img = load_image("tile/wall.png", (GRID_SIZE, GRID_SIZE))
wall_corner_img = load_image("tile/wall_corner.png", (GRID_SIZE, GRID_SIZE))
wall_horizontal_img = load_image("tile/wall_horizontal.png", (GRID_SIZE, GRID_SIZE))
wall_vertikal_img = load_image("tile/wall_vertikal.png", (GRID_SIZE, GRID_SIZE))
wall_fill_img = load_image("tile/wall_fill.png", (GRID_SIZE, GRID_SIZE))
door_img = load_image("tile/door.png", (GRID_SIZE, GRID_SIZE))
dot_img = load_image("item/dot.png", (8, 8))

def get_cell_value(x, y):
    col = max(0, min(len(MAP[0]) - 1, int(x // GRID_SIZE)))
    row = max(0, min(len(MAP) - 1, int(y // GRID_SIZE)))
    return MAP[row][col]

def check_collision(x, y, radius, ignore_jail_door=False):
    sample_points = [
        (x, y),
        (x - radius // 2, y),
        (x + radius // 2, y),
        (x, y - radius // 2),
        (x, y + radius // 2),
    ]
    for px, py in sample_points:
        val = get_cell_value(px, py)
        if val == 1:
            return True
        if val == 3 and not ignore_jail_door:
            return True
    return False

def save_high_score(new_high):
    with open(HS_FILE, "w") as f: 
        f.write(str(new_high))

def can_move_towards(x, y, dx, dy, radius, ignore_jail=False):
    return not check_collision(x + dx, y + dy, radius, ignore_jail_door=ignore_jail)


def choose_ghost_direction(ghost, target_x, target_y, ignore_jail=False, flee=False):
    valid_dirs = [d for d in ghost_directions if can_move_towards(ghost["x"], ghost["y"], d[0], d[1], ghost["radius"], ignore_jail=ignore_jail)]
    if not valid_dirs:
        return (0, 0)

    reverse_dir = (-ghost["dir"][0], -ghost["dir"][1])
    def direction_cost(d):
        nx, ny = ghost["x"] + d[0], ghost["y"] + d[1]
        distance = abs(nx - target_x) + abs(ny - target_y)
        if flee:
            return (d == reverse_dir, -distance)
        return (d == reverse_dir, distance)

    return min(valid_dirs, key=direction_cost)


def get_ghost_target(ghost, pacman_x, pacman_y, direction):
    if ghost["style"] == "ambush":
        return pacman_x + direction[0] * GRID_SIZE * 2, pacman_y + direction[1] * GRID_SIZE * 2
    return pacman_x, pacman_y


def draw_wall_tile(surface, x, y, r_idx, c_idx):
    x += MAZE_OFFSET_X
    y += MAZE_OFFSET_Y
    has_up = r_idx > 0 and MAP[r_idx - 1][c_idx] == 1
    has_down = r_idx < len(MAP) - 1 and MAP[r_idx + 1][c_idx] == 1
    has_left = c_idx > 0 and MAP[r_idx][c_idx - 1] == 1
    has_right = c_idx < len(MAP[0]) - 1 and MAP[r_idx][c_idx + 1] == 1

    if wall_tile_img:
        tile_img = wall_tile_img
        if has_left and has_right and not has_up and not has_down: 
            tile_img = wall_horizontal_img or wall_tile_img
        elif has_up and has_down and not has_left and not has_right: 
            tile_img = wall_vertikal_img or wall_tile_img
        surface.blit(tile_img, (x, y))
    else:
        pygame.draw.rect(surface, BLUE, (x, y, GRID_SIZE, GRID_SIZE), 2)

def reset_game():
    """Mengatur ulang semua posisi objek dan makanan ke kondisi awal"""
    global pacman_x, pacman_y, direction, requested_direction, angle, score, game_state, ghosts, dots, door_open, start_ticks, power_mode, power_mode_timer, lives
    pacman_x, pacman_y = GRID_SIZE + 8, GRID_SIZE + 8
    direction = (0, 0)
    requested_direction = (0, 0)
    angle = 0
    score = 0
    lives = 3
    game_state = "PLAYING"
    door_open = False
    start_ticks = pygame.time.get_ticks() 
    
    ghosts[0]["x"], ghosts[0]["y"], ghosts[0]["dir"], ghosts[0]["frightened"], ghosts[0]["speed"] = 10 * GRID_SIZE + 8, 7 * GRID_SIZE + 8, (0, 0), False, ghosts[0]["base_speed"]
    ghosts[1]["x"], ghosts[1]["y"], ghosts[1]["dir"], ghosts[1]["frightened"], ghosts[1]["speed"] = 11 * GRID_SIZE + 8, 7 * GRID_SIZE + 8, (0, 0), False, ghosts[1]["base_speed"]
    ghosts[2]["x"], ghosts[2]["y"], ghosts[2]["dir"], ghosts[2]["frightened"], ghosts[2]["speed"] = 9 * GRID_SIZE + 8, 7 * GRID_SIZE + 8, (0, 0), False, ghosts[2]["base_speed"]

    power_mode = False
    power_mode_timer = 0

    dots = []
    power_pellet_rects.clear()
    for r_idx, row in enumerate(MAP):
        for c_idx, val in enumerate(row):
            if val == 0:
                dots.append(pygame.Rect(c_idx * GRID_SIZE + 12, r_idx * GRID_SIZE + 12, 8, 8))

    for px, py in power_pellet_positions:
        power_pellet_rects.append(pygame.Rect(px * GRID_SIZE + 8, py * GRID_SIZE + 8, 12, 12))

reset_game()

if __name__ == "__main__":
    # 5. GAME LOOP UTAMA
    while True:
        CLOCK.tick(FPS)
        seconds_passed = pygame.time.get_ticks() - start_ticks
        time_left = max(0, (jail_timer - seconds_passed) // 1000)

        if seconds_passed >= jail_timer and not door_open:
            door_open = True
            ghosts[0]["dir"] = (0, -ghosts[0]["speed"])
            ghosts[1]["dir"] = (0, -ghosts[1]["speed"])

        # --- HANDLING INPUT ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and game_state in ["GAME_OVER", "VICTORY"]:
                if event.key == pygame.K_SPACE:
                    reset_game()

        # --- UPDATE LOGIKA GAME ---
        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                requested_direction = (0, -pacman_speed)
                angle = 90
            elif keys[pygame.K_DOWN]:
                requested_direction = (0, pacman_speed)
                angle = 270
            elif keys[pygame.K_LEFT]:
                requested_direction = (-pacman_speed, 0)
                angle = 180
            elif keys[pygame.K_RIGHT]:
                requested_direction = (pacman_speed, 0)
                angle = 0

            if requested_direction != (0, 0) and can_move_towards(pacman_x, pacman_y, requested_direction[0], requested_direction[1], pacman_radius):
                direction = requested_direction

            if can_move_towards(pacman_x, pacman_y, direction[0], direction[1], pacman_radius):
                pacman_x += direction[0]
                pacman_y += direction[1]
                
                if pacman_frames:
                    animation_timer += 1
                    if animation_timer % 8 == 0:
                        pacman_frame_index = (pacman_frame_index + 1) % len(pacman_frames)
                        pacman_img = pygame.transform.rotate(pacman_frames[pacman_frame_index], angle)
            else:
                if pacman_frames:
                    pacman_img = pygame.transform.rotate(pacman_frames[pacman_frame_index], angle)

            pacman_rect = pygame.Rect(pacman_x - pacman_radius, pacman_y - pacman_radius, pacman_radius * 2, pacman_radius * 2)
            for dot in dots[:]:
                if pacman_rect.colliderect(dot):
                    dots.remove(dot)
                    score += 10
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

            for pellet in power_pellet_rects[:]:
                if pacman_rect.colliderect(pellet):
                    power_pellet_rects.remove(pellet)
                    power_mode = True
                    power_mode_timer = pygame.time.get_ticks()
                    score += 50
                    for ghost in ghosts:
                        ghost["frightened"] = True
                        ghost["speed"] = max(1, ghost["base_speed"] - 1)

            if power_mode and pygame.time.get_ticks() - power_mode_timer >= POWER_MODE_DURATION:
                power_mode = False
                for ghost in ghosts:
                    ghost["frightened"] = False
                    ghost["speed"] = ghost["base_speed"]

            if not dots and not power_pellet_rects:
                game_state = "VICTORY"

            for ghost in ghosts:
                cell_val = get_cell_value(ghost["x"], ghost["y"])
                ignore_door = not door_open or (cell_val == 2)
                ghost_target_x, ghost_target_y = get_ghost_target(ghost, pacman_x, pacman_y, direction)

                if ghost["frightened"]:
                    ghost["dir"] = choose_ghost_direction(ghost, pacman_x, pacman_y, ignore_jail=ignore_door, flee=True)
                elif ghost["style"] == "random":
                    valid_dirs = [d for d in ghost_directions if can_move_towards(ghost["x"], ghost["y"], d[0], d[1], ghost["radius"], ignore_jail=ignore_door)]
                    if valid_dirs:
                        ghost["dir"] = random.choice(valid_dirs)
                else:
                    if not door_open and cell_val == 2:
                        if ghost["dir"] == (0, 0):
                            ghost["dir"] = random.choice(ghost_directions)
                    elif cell_val == 2:
                        ghost["dir"] = choose_ghost_direction(ghost, 10 * GRID_SIZE + 8, 6 * GRID_SIZE + 8, ignore_jail=True)
                    else:
                        ghost["dir"] = choose_ghost_direction(ghost, ghost_target_x, ghost_target_y, ignore_jail=ignore_door)

                if can_move_towards(ghost["x"], ghost["y"], ghost["dir"][0], ghost["dir"][1], ghost["radius"], ignore_jail=ignore_door):
                    ghost["x"] += ghost["dir"][0]
                    ghost["y"] += ghost["dir"][1]
                else:
                    if ghost["frightened"]:
                        ghost["dir"] = choose_ghost_direction(ghost, pacman_x, pacman_y, ignore_jail=ignore_door, flee=True)
                    else:
                        ghost["dir"] = choose_ghost_direction(ghost, ghost_target_x, ghost_target_y, ignore_jail=ignore_door)
                    if can_move_towards(ghost["x"], ghost["y"], ghost["dir"][0], ghost["dir"][1], ghost["radius"], ignore_jail=ignore_door):
                        ghost["x"] += ghost["dir"][0]
                        ghost["y"] += ghost["dir"][1]
                    else:
                        ghost["dir"] = (0, 0)

            for ghost in ghosts:
                ghost_rect = pygame.Rect(ghost["x"] - ghost["radius"], ghost["y"] - ghost["radius"], ghost["radius"] * 2, ghost["radius"] * 2)
                if pacman_rect.colliderect(ghost_rect):
                    if ghost["frightened"]:
                        ghost["x"], ghost["y"] = ghost["home_x"], ghost["home_y"]
                        ghost["dir"] = (0, 0)
                        ghost["frightened"] = False
                        ghost["speed"] = ghost["base_speed"]
                        score += 100
                    else:
                        lives -= 1
                        pacman_x, pacman_y = GRID_SIZE + 8, GRID_SIZE + 8
                        direction = (0, 0)
                        requested_direction = (0, 0)
                        angle = 0
                        if lives <= 0:
                            game_state = "GAME_OVER"

        # --- RENDERING ---
        SCREEN.fill((12, 16, 24))

        for r_idx, row in enumerate(MAP):
            for c_idx, val in enumerate(row):
                x = c_idx * GRID_SIZE + MAZE_OFFSET_X
                y = r_idx * GRID_SIZE + MAZE_OFFSET_Y
                if val == 1:
                    draw_wall_tile(SCREEN, c_idx * GRID_SIZE, r_idx * GRID_SIZE, r_idx, c_idx)
                elif val in (0, 2, 3):
                    pygame.draw.rect(SCREEN, (20, 28, 40), (x, y, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(SCREEN, (34, 46, 64), (x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2), 1)
                if val == 3 and not door_open:
                    if door_img:
                        SCREEN.blit(door_img, (x, y))
                    else:
                        pygame.draw.rect(SCREEN, RED, (x, y + 15, GRID_SIZE, 10))

        for pellet in power_pellet_rects:
            pygame.draw.circle(SCREEN, WHITE if not power_mode else (0, 255, 255), pellet.center, pellet.width // 2)

        for dot in dots:
            if dot_img:
                dot_rect = dot_img.get_rect(center=(dot.centerx + MAZE_OFFSET_X, dot.centery + MAZE_OFFSET_Y))
                SCREEN.blit(dot_img, dot_rect)
            else:
                pygame.draw.ellipse(SCREEN, WHITE, dot.move(MAZE_OFFSET_X, MAZE_OFFSET_Y))

        for g in ghosts:
            if g.get("img"):
                ghost_img = pygame.transform.scale(g["img"], (g["radius"] * 2, g["radius"] * 2))
                rect = ghost_img.get_rect(center=(int(g["x"]) + MAZE_OFFSET_X + 2, int(g["y"]) + MAZE_OFFSET_Y + 2))
                SCREEN.blit(ghost_img, rect.topleft)
            else:
                pygame.draw.circle(SCREEN, g["color"], (int(g["x"]) + MAZE_OFFSET_X, int(g["y"]) + MAZE_OFFSET_Y), g["radius"])
                pygame.draw.circle(SCREEN, WHITE, (int(g["x"]) + MAZE_OFFSET_X - 5, int(g["y"]) + MAZE_OFFSET_Y - 4), 4)
                pygame.draw.circle(SCREEN, WHITE, (int(g["x"]) + MAZE_OFFSET_X + 5, int(g["y"]) + MAZE_OFFSET_Y - 4), 4)

        if pacman_img:
            rect = pacman_img.get_rect(center=(int(pacman_x) + MAZE_OFFSET_X + 2, int(pacman_y) + MAZE_OFFSET_Y + 2))
            SCREEN.blit(pacman_img, rect.topleft)
        else:
            pygame.draw.circle(SCREEN, YELLOW, (int(pacman_x) + MAZE_OFFSET_X, int(pacman_y) + MAZE_OFFSET_Y), pacman_radius)

        score_text = font.render(f"SCORE: {score}", True, WHITE)
        hs_text = font.render(f"HIGH SCORE: {high_score}", True, YELLOW)
        lives_text = font.render(f"LIVES: {lives}", True, WHITE)
        SCREEN.blit(score_text, (15, SCREEN_HEIGHT - 35))
        SCREEN.blit(hs_text, (SCREEN_WIDTH - 260, SCREEN_HEIGHT - 35))
        SCREEN.blit(lives_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 35))

        if power_mode:
            power_text = font.render("POWER MODE", True, (0, 255, 255))
            SCREEN.blit(power_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT - 35))

        if game_state == "VICTORY":
            end_text = font.render("YOU WIN! Press SPACE to Restart", True, YELLOW)
            SCREEN.blit(end_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 35))
        elif game_state == "GAME_OVER":
            end_text = font.render("GAME OVER! Press SPACE to Restart", True, RED)
            SCREEN.blit(end_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 35))

        pygame.display.flip()
