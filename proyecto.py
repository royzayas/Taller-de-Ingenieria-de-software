import pygame, sys, random, math, os

def resource_path(rel):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(".")
    return os.path.join(base, rel)

pygame.init()

MENU_SCREEN = (900, 700)

SCREEN_MAX_W, SCREEN_MAX_H = 1366, 768
SCREEN_WIDTH, SCREEN_HEIGHT = MENU_SCREEN 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Selva Mortal")

WHITE = (255,255,255)
GREEN = (34,139,34)
RED = (200,0,0)
BLACK = (0,0,0)

font = pygame.font.SysFont(None, 36)
bigfont = pygame.font.SysFont(None, 72)

def try_load_image(path, alpha=True):
    try:
        full = resource_path(path)
        img = pygame.image.load(full)
        return img.convert_alpha() if alpha else img.convert()
    except Exception as e:
        print(f"[Aviso imagen] {path} no encontrado ({e})")
        return None

def try_scale(img, size):
    try:
        return pygame.transform.smoothscale(img, size)
    except Exception:
        try:
            return pygame.transform.scale(img, size)
        except Exception:
            return None

fondo_img = try_load_image("assets/images/fondo.jpg", alpha=False)
titulo_img = try_load_image("assets/images/titulo.png", alpha=True)
boton_img = try_load_image("assets/images/boton.png", alpha=True)

personaje_frames = []
for i in range(1, 3):
    img = try_load_image(f"assets/images/personaje{i}.png", alpha=True)
    if img:
        personaje_frames.append(img)
    else:
        personaje_frames.append(None)
personaje_frames_valid = [f for f in personaje_frames if f is not None]

tigre_img = try_load_image("assets/images/tigre.png", alpha=True)
arbusto_img = try_load_image("assets/images/arbusto.jpg", alpha=True)
bandera_img = try_load_image("assets/images/bandera.png", alpha=True)

def load_sound(path):
    try:
        full = resource_path(path)
        return pygame.mixer.Sound(full)
    except Exception as e:
        print(f"[Aviso sonido] {path} no encontrado ({e})")
        return None

try:
    pygame.mixer.init()
except Exception:
    pass

try:
    pygame.mixer.music.load(resource_path("assets/sounds/fondo.mp3"))
    pygame.mixer.music.play(-1)
except Exception:
    print("[Aviso] No se encontró música de fondo.")

machete_sound  = load_sound("assets/sounds/machete.mp3")
tigre_sound    = load_sound("assets/sounds/rugido_tigre.mp3")
gameover_sound = load_sound("assets/sounds/gameover.mp3")
victory_sound  = load_sound("assets/sounds/victory.mp3")

scores = []
max_saved_scores = 200
difficulty_points_map = {8: 100, 12: 250, 16: 500}
max_lives = 3

name_input_active = False
name_input_str = ""
pending_score = 0
pending_result = None
pending_difficulty_label = ""
pending_difficulty_rows = 8

MENU, OPTIONS, DIFFICULTY, GAME, SCORES = 0,1,2,3,4
state = MENU

game_resized = False

class Button:
    def __init__(self, text, center, size=(200,70)):
        self.text = text
        self.size = size
        self.rect = pygame.Rect(0,0,*size)
        self.rect.center = center
        self.color = (70,140,70)
        self.radius = 18

    def draw(self, surf):
        if boton_img:
            img = try_scale(boton_img, self.size)
            if img:
                surf.blit(img, self.rect)
            else:
                pygame.draw.rect(surf, self.color, self.rect, border_radius=self.radius)
        else:
            pygame.draw.rect(surf, self.color, self.rect, border_radius=self.radius)
        txt = font.render(self.text, True, BLACK)
        surf.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Cell:
    def __init__(self, col, row, x, y, size):
        self.col = col
        self.row = row
        self.x = x
        self.y = y
        self.size = size
        self.is_tigre = False
        self.revealed = False
        self.neighbors = 0
        self.flagged = False

    def draw(self, surf):
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        if not self.revealed:
            if self.flagged:
                if arbusto_img:
                    arb = try_scale(arbusto_img, (self.size, self.size))
                    if arb:
                        surf.blit(arb, (self.x, self.y))
                    else:
                        pygame.draw.rect(surf, GREEN, rect)
                else:
                    pygame.draw.rect(surf, GREEN, rect)
                if bandera_img:
                    flag_img = try_scale(bandera_img, (int(self.size*0.6), int(self.size*0.6)))
                    if flag_img:
                        fx = self.x + (self.size - flag_img.get_width())//2
                        fy = self.y + (self.size - flag_img.get_height())//2
                        surf.blit(flag_img, (fx, fy))
                    else:
                        p1 = (self.x + int(self.size * 0.2), self.y + int(self.size * 0.8))
                        p2 = (self.x + int(self.size * 0.2), self.y + int(self.size * 0.2))
                        p3 = (self.x + int(self.size * 0.7), self.y + int(self.size * 0.5))
                        pygame.draw.polygon(surf, (220,20,60), [p1, p2, p3])
                else:
                    p1 = (self.x + int(self.size * 0.2), self.y + int(self.size * 0.8))
                    p2 = (self.x + int(self.size * 0.2), self.y + int(self.size * 0.2))
                    p3 = (self.x + int(self.size * 0.7), self.y + int(self.size * 0.5))
                    pygame.draw.polygon(surf, (220,20,60), [p1, p2, p3])
            else:
                if arbusto_img:
                    arb = try_scale(arbusto_img, (self.size, self.size))
                    if arb:
                        surf.blit(arb, (self.x, self.y))
                    else:
                        pygame.draw.rect(surf, GREEN, rect)
                else:
                    pygame.draw.rect(surf, GREEN, rect)
            pygame.draw.rect(surf, BLACK, rect, 1)
        else:
            if self.is_tigre:
                if tigre_img:
                    tig = try_scale(tigre_img, (self.size, self.size))
                    if tig:
                        surf.blit(tig, (self.x, self.y))
                    else:
                        pygame.draw.rect(surf, RED, rect)
                else:
                    pygame.draw.rect(surf, RED, rect)
            else:
                pygame.draw.rect(surf, WHITE, rect)
                if self.neighbors > 0:
                    txt = font.render(str(self.neighbors), True, BLACK)
                    surf.blit(txt, (self.x + self.size//3, self.y + self.size//4))
            pygame.draw.rect(surf, BLACK, rect, 1)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target = None
        self.speed = 220.0
        self.frame_idx = 0
        self.anim_timer = 0.0
        self.anim_interval = 0.28
        self.lives = 3
        self.min_movement_to_animate = 2.0

    def update(self, dt):
        moving = False
        if self.target:
            tx, ty = self.target
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist < 1.0:
                self.x, self.y = tx, ty
                self.target = None
            else:
                if dist > self.min_movement_to_animate:
                    moving = True
                step = self.speed * dt
                if step >= dist:
                    self.x, self.y = tx, ty
                    self.target = None
                else:
                    self.x += (dx/dist)*step
                    self.y += (dy/dist)*step

        if moving and personaje_frames_valid:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_interval:
                self.anim_timer -= self.anim_interval
                self.frame_idx = (self.frame_idx + 1) % len(personaje_frames_valid)
        else:
            self.anim_timer = 0.0
            self.frame_idx = 0

    def draw(self, surf):
        global cell_size
        frame = None
        if personaje_frames_valid:
            idx = self.frame_idx % len(personaje_frames_valid)
            frame = personaje_frames_valid[idx]
        if frame:
            size = max(8, int(cell_size * 0.8))
            img = try_scale(frame, (size, size))
            if img:
                rect = img.get_rect(center=(int(self.x), int(self.y)))
                surf.blit(img, rect)
            else:
                pygame.draw.circle(surf, (255,200,0), (int(self.x), int(self.y)), max(8, int(cell_size*0.3)))
        else:
            pygame.draw.circle(surf, (255,200,0), (int(self.x), int(self.y)), max(8, int(cell_size*0.3)))

    def set_target(self, cx, cy):
        self.target = (cx, cy)

class Slider:
    def __init__(self, x, y, w=200, h=20, value=1.0):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = value
        self.dragging = False

    def draw(self, surf):
        pygame.draw.rect(surf, (180,180,180), self.rect)
        fill_w = int(self.rect.w * self.value)
        pygame.draw.rect(surf, (70,200,70), (self.rect.x, self.rect.y, fill_w, self.rect.h))
        pygame.draw.rect(surf, BLACK, self.rect, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
            rel_x = event.pos[0] - self.rect.x
            self.value = max(0.0, min(1.0, rel_x / self.rect.w))
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            self.value = max(0.0, min(1.0, rel_x / self.rect.w))

grid = []
cell_size = 50
rows = cols = 8
tigre_count = 10

modal_active = False
modal_type = None
modal_buttons = []

player = Player(SCREEN_WIDTH//2, 100)
music_on = True

current_rows = 8

def compute_layout_for(rows_in, cols_in):
    title_height = 180
    max_w = min(1200, SCREEN_MAX_W - 100)
    max_h = min(700, SCREEN_MAX_H - 50)
    avail_w = max_w - 40
    avail_h = max_h - title_height - 40
    cell_w = avail_w // cols_in
    cell_h = avail_h // rows_in
    csize = max(16, min(cell_w, cell_h))
    window_w = cols_in * csize + 40
    window_h = rows_in * csize + title_height + 40
    window_w = min(window_w, SCREEN_MAX_W - 20)
    window_h = min(window_h, SCREEN_MAX_H - 20)
    return int(window_w), int(window_h), int(csize)

def create_grid(rows_in, cols_in, csize, tigres):
    global grid
    grid = []
    start_x = 20
    start_y = 140
    for r in range(rows_in):
        row = []
        for c in range(cols_in):
            x = start_x + c * csize
            y = start_y + r * csize
            row.append(Cell(c, r, x, y, csize))
        grid.append(row)
    placed = 0
    while placed < tigres:
        i = random.randrange(rows_in)
        j = random.randrange(cols_in)
        if not grid[i][j].is_tigre:
            grid[i][j].is_tigre = True
            placed += 1
    for i in range(rows_in):
        for j in range(cols_in):
            if grid[i][j].is_tigre:
                continue
            cnt = 0
            for di in (-1,0,1):
                for dj in (-1,0,1):
                    ni, nj = i+di, j+dj
                    if 0 <= ni < rows_in and 0 <= nj < cols_in:
                        if grid[ni][nj].is_tigre:
                            cnt += 1
            grid[i][j].neighbors = cnt

def save_score_and_prepare_name(result, pts, difficulty_label, difficulty_rows):
    global name_input_active, name_input_str, pending_score, pending_result, pending_difficulty_label, pending_difficulty_rows
    pending_score = pts
    pending_result = result
    pending_difficulty_label = difficulty_label
    pending_difficulty_rows = difficulty_rows
    name_input_str = ""
    name_input_active = True

def award_score_entry(name, pts, result, difficulty_label, difficulty_rows):
    global scores
    entry = {
        'name': name,
        'score': int(pts),
        'result': result,
        'difficulty': difficulty_label,
        'difficulty_rows': difficulty_rows
    }
    scores.insert(0, entry)
    if len(scores) > max_saved_scores:
        scores = scores[:max_saved_scores]

def reveal_cell_by_index(i, j):
    global player, modal_active, modal_type, current_rows
    cell = grid[i][j]
    if hasattr(cell, "flagged") and cell.flagged:
        return
    if cell.revealed:
        return

    base_points = difficulty_points_map.get(current_rows, 100)

    if cell.is_tigre:
        prev_lives = player.lives
        player.lives -= 1
        cell.revealed = True
        if player.lives <= 0:
            partial = int(base_points * (prev_lives / max_lives)) if prev_lives > 0 else 0
            if gameover_sound:
                gameover_sound.play()
            open_modal("gameover")
            save_score_and_prepare_name("gameover", partial, f"{current_rows}x{current_rows}", current_rows)
        else:
            if tigre_sound:
                tigre_sound.play()
    else:
        cell.revealed = True
        if machete_sound:
            machete_sound.play()
        if cell.neighbors == 0:
            for di in (-1,0,1):
                for dj in (-1,0,1):
                    ni, nj = i+di, j+dj
                    if 0 <= ni < len(grid) and 0 <= nj < len(grid[0]):
                        if not grid[ni][nj].revealed:
                            reveal_cell_by_index(ni, nj)

    won = True
    for row in grid:
        for c in row:
            if not c.is_tigre and not c.revealed:
                won = False
                break
        if not won:
            break
    if won:
        pts = difficulty_points_map.get(current_rows, 100)
        if victory_sound:
            victory_sound.play()
        open_modal("victory")
        save_score_and_prepare_name("victory", pts, f"{current_rows}x{current_rows}", current_rows)

def open_modal(kind):
    global modal_active, modal_type, modal_buttons
    modal_active = True
    modal_type = kind
    modal_buttons = []

def close_modal_to_menu():
    global modal_active, modal_type, state
    modal_active = False
    modal_type = None
    state = MENU
    restore_menu_size()

def close_modal_to_difficulty():
    global modal_active, modal_type, state
    modal_active = False
    modal_type = None
    state = DIFFICULTY
    restore_menu_size()

def draw_modal(surf):
    global name_input_active, name_input_str, pending_score, pending_result, pending_difficulty_label, modal_buttons
    if name_input_active:
        mw, mh = SCREEN_WIDTH * 0.82, SCREEN_HEIGHT * 0.62
    else:
        mw, mh = SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.45
    mx, my = (SCREEN_WIDTH - mw)//2, (SCREEN_HEIGHT - mh)//2
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,180))
    surf.blit(overlay, (0,0))
    pygame.draw.rect(surf, (40,40,40), (mx, my, mw, mh), border_radius=14)
    pygame.draw.rect(surf, WHITE, (mx, my, mw, mh), 2, border_radius=14)

    title_y = my + 28
    if modal_type == "gameover":
        title = bigfont.render("Perdiste", True, WHITE)
        surf.blit(title, (mx + mw/2 - title.get_width()//2, title_y))
        sub = font.render("Has perdido todas tus vidas.", True, WHITE)
        surf.blit(sub, (mx + mw/2 - sub.get_width()//2, title_y + 68))
    elif modal_type == "victory":
        title = bigfont.render("¡Felicidades!", True, WHITE)
        surf.blit(title, (mx + mw/2 - title.get_width()//2, title_y))
        sub = font.render("Has superado el tablero.", True, WHITE)
        surf.blit(sub, (mx + mw/2 - sub.get_width()//2, title_y + 68))

    content_top = title_y + 120
    if modal_type in ("gameover", "victory") and name_input_active:
        prompt = font.render("Ingresa tu nombre y dale Enter:", True, WHITE)
        surf.blit(prompt, (mx + 30, content_top))
        ibox = pygame.Rect(mx + 30, content_top + 48, int(mw - 60), 56)
        pygame.draw.rect(surf, WHITE, ibox, border_radius=8)
        txt = font.render(name_input_str or "_", True, BLACK)
        surf.blit(txt, (ibox.x + 12, ibox.y + 12))
        score_txt = font.render(f"Puntos obtenidos: {pending_score} ({pending_difficulty_label})", True, WHITE)
        surf.blit(score_txt, (mx + 30, content_top + 130))

    btn_y = int(my + mh - 64)
    left_center = (mx + int(mw*0.28), btn_y)
    right_center = (mx + int(mw*0.72), btn_y)
    b1 = Button("Salir", left_center, size=(120,40))
    b2 = Button("Reintentar", right_center, size=(140,50))
    modal_buttons = [b1, b2]

    for b in modal_buttons:
        b.draw(surf)

def restore_menu_size():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, fondo_img, titulo_img, game_resized
    try:
        SCREEN_WIDTH, SCREEN_HEIGHT = MENU_SCREEN
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        fpath = resource_path("assets/images/fondo.jpg")
        if os.path.exists(fpath):
            tmp = pygame.image.load(fpath).convert()
            tmp = pygame.transform.scale(tmp, (SCREEN_WIDTH, SCREEN_HEIGHT))
            fondo_img = tmp
        tpath = resource_path("assets/images/titulo.png")
        if os.path.exists(tpath):
            tmp = pygame.image.load(tpath).convert_alpha()
            tmp = pygame.transform.scale(tmp, (400,150))
            titulo_img = tmp
    except Exception:
        pass
    game_resized = False

def draw_title():
    if titulo_img:
        max_w = min(500, SCREEN_WIDTH - 40)
        max_h = 150
        ow, oh = titulo_img.get_width(), titulo_img.get_height()
        if ow == 0 or oh == 0:
            t = bigfont.render("Selva Mortal", True, WHITE)
            screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 10))
            return
        scale = min(max_w / ow, max_h / oh, 1.0)
        nw, nh = int(ow * scale), int(oh * scale)
        img = try_scale(titulo_img, (nw, nh))
        if img:
            screen.blit(img, (SCREEN_WIDTH//2 - img.get_width()//2, 10))
            return
    t = bigfont.render("Selva Mortal", True, WHITE)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 10))

def main_menu():
    if fondo_img:
        scaled_bg = try_scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        if scaled_bg:
            screen.blit(scaled_bg, (0,0))
        else:
            screen.fill(GREEN)
    else:
        screen.fill(GREEN)
    draw_title()
    play_btn = Button("Jugar", (SCREEN_WIDTH//2, 240))
    scores_btn = Button("Puntuaciones", (SCREEN_WIDTH//2, 320))
    opt_btn  = Button("Opciones", (SCREEN_WIDTH//2, 400))
    exit_btn = Button("Salir", (SCREEN_WIDTH//2, 480))
    for b in [play_btn, scores_btn, opt_btn, exit_btn]:
        b.draw(screen)
    return play_btn, scores_btn, opt_btn, exit_btn

def scores_menu(selected_filter_rows=None):
    if fondo_img:
        scaled_bg = try_scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        if scaled_bg:
            screen.blit(scaled_bg, (0,0))
        else:
            screen.fill((30,60,30))
    else:
        screen.fill((30,60,30))
    title = bigfont.render("Puntuaciones", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))

    easy = Button("Fácil (8x8)", (SCREEN_WIDTH//2 - 220, 120), size=(180,50))
    med  = Button("Normal (12x12)", (SCREEN_WIDTH//2, 120), size=(180,50))
    hard = Button("Difícil (16x16)", (SCREEN_WIDTH//2 + 220, 120), size=(180,50))
    back = Button("Volver", (100, SCREEN_HEIGHT - 60), size=(160,50))

    for b in [easy, med, hard, back]:
        b.draw(screen)

    sx = 80
    sy = 200
    if selected_filter_rows is None:
        info = font.render("Selecciona una dificultad para ver su tabla.", True, WHITE)
        screen.blit(info, (sx, sy))
        sy += 36
        filt = scores
    else:
        info = font.render(f"Tabla - {selected_filter_rows}x{selected_filter_rows}", True, WHITE)
        screen.blit(info, (sx, sy))
        sy += 36
        filt = [s for s in scores if s.get('difficulty_rows') == selected_filter_rows]

    filt_sorted = sorted(filt, key=lambda e: e['score'], reverse=True)
    max_show = 12
    for i, e in enumerate(filt_sorted[:max_show]):
        txt = font.render(f"{i+1}. {e['name'][:18]:18s} {e['score']:5d} pts  {e['result']:8s}", True, WHITE)
        screen.blit(txt, (sx, sy))
        sy += 30

    return easy, med, hard, back

def options_menu():
    if fondo_img:
        scaled_bg = try_scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        if scaled_bg:
            screen.blit(scaled_bg, (0,0))
        else:
            screen.fill(GREEN)
    else:
        screen.fill(GREEN)
    draw_title()
    txt = font.render("Opciones", True, WHITE)
    screen.blit(txt, (40, 150))

    labels = [
        ("Volumen Música", 250, music_slider),
        ("Volumen Machete", 300, machete_slider),
        ("Volumen Tigre", 350, tigre_slider),
        ("Volumen Game Over", 400, gameover_slider),
        ("Volumen Victoria", 450, victory_slider)
    ]

    for text, y, slider in labels:
        txt = font.render(text, True, WHITE)
        screen.blit(txt, (50, y))
        slider.draw(screen)

    toggle_text = "Música: ON" if music_on else "Música: OFF"
    toggle_btn = Button(toggle_text, (SCREEN_WIDTH//2 - 120, 560), size=(180,50))
    toggle_btn.draw(screen)
    back_btn = Button("Volver", (SCREEN_WIDTH//2 + 120, 560), size=(160,50))
    back_btn.draw(screen)
    return toggle_btn, back_btn

def difficulty_menu():
    if fondo_img:
        scaled_bg = try_scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        if scaled_bg:
            screen.blit(scaled_bg, (0,0))
        else:
            screen.fill(GREEN)
    else:
        screen.fill(GREEN)
    draw_title()
    easy = Button("Fácil (8x8)", (SCREEN_WIDTH//2, 260))
    med  = Button("Normal (12x12)", (SCREEN_WIDTH//2, 360))
    hard = Button("Difícil (16x16)", (SCREEN_WIDTH//2, 460))
    back = Button("Volver", (100, SCREEN_HEIGHT - 60), size=(160,50))

    for b in [easy, med, hard, back]:
        b.draw(screen)
    return easy, med, hard, back

def start_game_with(rows_in, cols_in, tigre_num):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, cell_size, player, rows, cols, tigre_count, fondo_img, titulo_img, current_rows, game_resized
    rows = rows_in; cols = cols_in; tigre_count = tigre_num
    current_rows = rows_in
    new_w, new_h, csize = compute_layout_for(rows, cols)
    cell_size = csize
    SCREEN_WIDTH, SCREEN_HEIGHT = new_w, new_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_resized = True
    
    fpath_jpg = resource_path("assets/images/fondo.jpg")
    fpath_png = resource_path("assets/images/fondo.png")
    try:
        if os.path.exists(fpath_jpg):
            tmp = pygame.image.load(fpath_jpg).convert()
            tmp = pygame.transform.scale(tmp, (SCREEN_WIDTH, SCREEN_HEIGHT))
            fondo_img = tmp
        elif os.path.exists(fpath_png):
            tmp = pygame.image.load(fpath_png).convert()
            tmp = pygame.transform.scale(tmp, (SCREEN_WIDTH, SCREEN_HEIGHT))
            fondo_img = tmp
    except:
        fondo_img = None

    tpath = resource_path("assets/images/titulo.png")
    try:
        if os.path.exists(tpath):
            tmp = pygame.image.load(tpath).convert_alpha()
            titulo_img = tmp
    except:
        titulo_img = None

    create_grid(rows, cols, cell_size, tigre_count)
    player.x = SCREEN_WIDTH//2
    player.y = 100
    player.target = None
    player.lives = 3

cell_size = 50
create_grid(8, 8, cell_size, 10)
player = Player(SCREEN_WIDTH//2, 100)

clock = pygame.time.Clock()
running = True

play_btn = scores_btn = opt_btn = exit_btn = None
toggle_btn = back_btn = None
easy_btn = med_btn = hard_btn = None

music_slider    = Slider(300, 250, value=1.0)
machete_slider  = Slider(300, 300, value=1.0)
tigre_slider    = Slider(300, 350, value=1.0)
gameover_slider = Slider(300, 400, value=1.0)
victory_slider  = Slider(300, 450, value=1.0)

scores_selected_filter = None
prev_state = state

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            scores = []
            running = False

        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                if play_btn and play_btn.is_clicked((mx,my)):
                    state = DIFFICULTY
                elif scores_btn and scores_btn.is_clicked((mx,my)):
                    state = SCORES
                    scores_selected_filter = None
                elif opt_btn and opt_btn.is_clicked((mx,my)):
                    state = OPTIONS
                elif exit_btn and exit_btn.is_clicked((mx,my)):
                    scores = []
                    running = False

        elif state == SCORES:
            easy_b, med_b, hard_b, back_b = scores_menu(scores_selected_filter)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                if easy_b.is_clicked((mx,my)):
                    scores_selected_filter = 8
                elif med_b.is_clicked((mx,my)):
                    scores_selected_filter = 12
                elif hard_b.is_clicked((mx,my)):
                    scores_selected_filter = 16
                elif back_b.is_clicked((mx,my)):
                    state = MENU
                    scores_selected_filter = None

        elif state == OPTIONS:
            music_slider.handle_event(event)
            machete_slider.handle_event(event)
            tigre_slider.handle_event(event)
            gameover_slider.handle_event(event)
            victory_slider.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                if 'toggle_btn' in globals() and toggle_btn and toggle_btn.is_clicked((mx,my)):
                    music_on = not music_on
                    try:
                        if music_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                    except:
                        pass
                if back_btn and back_btn.is_clicked((mx,my)):
                    state = MENU

        elif state == DIFFICULTY:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                if easy_btn and easy_btn.is_clicked((mx,my)):
                    start_game_with(8,8,10); state = GAME
                elif med_btn and med_btn.is_clicked((mx,my)):
                    start_game_with(12,12,20); state = GAME
                elif hard_btn and hard_btn.is_clicked((mx,my)):
                    start_game_with(16,16,40); state = GAME
                elif back_btn and back_btn.is_clicked((mx,my)):
                    state = MENU

        elif state == GAME:
            if modal_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = event.pos
                    if modal_buttons and modal_buttons[0].is_clicked((mx,my)):
                        close_modal_to_menu()
                    elif modal_buttons and modal_buttons[1].is_clicked((mx,my)):
                        close_modal_to_difficulty()
                if name_input_active and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        name_input_str = name_input_str[:-1]
                    elif event.key == pygame.K_RETURN:
                        name = name_input_str.strip() or "Anónimo"
                        award_score_entry(name, pending_score, pending_result, pending_difficulty_label, pending_difficulty_rows)
                        name_input_active = False
                    else:
                        ch = event.unicode
                        if ch.isprintable() and len(name_input_str) < 20:
                            name_input_str += ch
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = event.pos
                    if my > 120:
                        col = (mx - 20) // cell_size
                        row = (my - 140) // cell_size
                        if 0 <= row < rows and 0 <= col < cols:
                            cell = grid[row][col]
                            if event.button == 1:
                                cx = cell.x + cell.size//2
                                cy = cell.y + cell.size//2
                                player.set_target(cx, cy)
                                reveal_cell_by_index(row, col)
                            elif event.button == 3:
                                if not cell.revealed:
                                    cell.flagged = not cell.flagged
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        state = MENU
    if game_resized and state in (MENU, DIFFICULTY, SCORES, OPTIONS) and prev_state == GAME:
        restore_menu_size()

    prev_state = state

    if state == GAME and not modal_active:
        player.update(dt)

    try:
        pygame.mixer.music.set_volume(music_slider.value)
    except:
        pass
    if machete_sound: machete_sound.set_volume(machete_slider.value)
    if tigre_sound: tigre_sound.set_volume(tigre_slider.value)
    if gameover_sound: gameover_sound.set_volume(gameover_slider.value)
    if victory_sound: victory_sound.set_volume(victory_slider.value)

    if state == MENU:
        play_btn, scores_btn, opt_btn, exit_btn = main_menu()

    elif state == SCORES:
        easy_btn, med_btn, hard_btn, back_btn = scores_menu(scores_selected_filter)

    elif state == OPTIONS:
        toggle_btn, back_btn = options_menu()

    elif state == DIFFICULTY:
        easy_btn, med_btn, hard_btn, back_btn = difficulty_menu()

    elif state == GAME:
        if fondo_img:
            scaled_bg = try_scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            if scaled_bg:
                screen.blit(scaled_bg, (0,0))
            else:
                screen.fill(GREEN)
        else:
            screen.fill(GREEN)
        draw_title()
        lives_txt = font.render(f"Vidas: {player.lives}", True, WHITE)
        screen.blit(lives_txt, (20, 60))
        for row in grid:
            for c in row:
                c.draw(screen)
        player.draw(screen)
        if modal_active:
            draw_modal(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()