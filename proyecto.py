import pygame, sys, random, math, os

pygame.init()

# ---------------- CONFIG ----------------
SCREEN_MAX_W, SCREEN_MAX_H = 1366, 768
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Selva Mortal")

WHITE = (255,255,255)
GREEN = (34,139,34)
RED = (200,0,0)
BLACK = (0,0,0)

font = pygame.font.SysFont(None, 36)
bigfont = pygame.font.SysFont(None, 72)

# ---------------- ESPACIOS PARA IMÁGENES (TRY/EXCEPT) ----------------
try:
    fondo_img = pygame.image.load("assets/images/fondo.jpg").convert()
    fondo_img = pygame.transform.scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    fondo_img = None

try:
    titulo_img = pygame.image.load("assets/images/titulo.png").convert_alpha()
    titulo_img = pygame.transform.scale(titulo_img, (500, 150))
except:
    titulo_img = None

try:
    boton_img = pygame.image.load("assets/images/boton.png").convert_alpha()
except:
    boton_img = None

# Personaje (2 frames)
personaje_frames = []
for i in range(1, 3):
    try:
        img = pygame.image.load(f"assets/images/personaje{i}.png").convert_alpha()
        personaje_frames.append(pygame.transform.scale(img, (60, 60)))
    except:
        personaje_frames.append(None)

try:
    tigre_img = pygame.image.load("assets/images/tigre.png").convert_alpha()
    tigre_img = pygame.transform.scale(tigre_img, (60, 60))
except:
    tigre_img = None

try:
    arbusto_img = pygame.image.load("assets/images/arbusto.jpg").convert_alpha()
    arbusto_img = pygame.transform.scale(arbusto_img, (60, 60))
except:
    arbusto_img = None

# Bandera (opcional)
try:
    bandera_img = pygame.image.load("assets/images/bandera.png").convert_alpha()
    # no la escalamos permanentemente; se escalará al dibujar según la casilla
except:
    bandera_img = None

# ---------------- ESPACIOS PARA SONIDOS (TRY/EXCEPT) ----------------
try:
    pygame.mixer.init()
except:
    pass

try:
    pygame.mixer.music.load("assets/sounds/fondo.mp3")
    pygame.mixer.music.play(-1)
except:
    print("[Aviso] No se encontró música de fondo.")

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        print(f"[Aviso] No se pudo cargar {path}")
        return None

machete_sound  = load_sound("assets/sounds/machete.mp3")
tigre_sound    = load_sound("assets/sounds/rugido_tigre.mp3")
# click_sound removed
gameover_sound = load_sound("assets/sounds/gameover.mp3")
victory_sound  = load_sound("assets/sounds/victory.mp3")

# ---------------- CLASES ----------------
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
            img = pygame.transform.scale(boton_img, self.size)
            surf.blit(img, self.rect)
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
        self.flagged = False   # <-- agregado para banderas

    def draw(self, surf):
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        if not self.revealed:
            # Si está marcada con bandera, mostrar bandera encima del arbusto/verde
            if self.flagged:
                # dibuja arbusto o verde como fondo
                if arbusto_img:
                    try:
                        arb = pygame.transform.scale(arbusto_img, (self.size, self.size))
                        surf.blit(arb, (self.x, self.y))
                    except:
                        pygame.draw.rect(surf, GREEN, rect)
                else:
                    pygame.draw.rect(surf, GREEN, rect)
                # si existe imagen de bandera, usarla; si no, triángulo rojo
                if bandera_img:
                    try:
                        flag_img = pygame.transform.scale(bandera_img, (int(self.size*0.6), int(self.size*0.6)))
                        # centrar la bandera en la casilla
                        fx = self.x + (self.size - flag_img.get_width())//2
                        fy = self.y + (self.size - flag_img.get_height())//2
                        surf.blit(flag_img, (fx, fy))
                    except:
                        # fallback triángulo
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
                # casilla sin revelar y sin bandera: dibujar arbusto o verde
                if arbusto_img:
                    try:
                        arb = pygame.transform.scale(arbusto_img, (self.size, self.size))
                        surf.blit(arb, (self.x, self.y))
                    except:
                        pygame.draw.rect(surf, GREEN, rect)
                else:
                    pygame.draw.rect(surf, GREEN, rect)
            pygame.draw.rect(surf, BLACK, rect, 1)
        else:
            # casilla revelada
            if self.is_tigre:
                if tigre_img:
                    try:
                        tig = pygame.transform.scale(tigre_img, (self.size, self.size))
                        surf.blit(tig, (self.x, self.y))
                    except:
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
        self.speed = 500.0
        self.frame_idx = 0
        self.lives = 3

    def update(self, dt):
        if self.target:
            tx, ty = self.target
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist < 1.0:
                self.x, self.y = tx, ty
                self.target = None
            else:
                step = self.speed * dt
                if step >= dist:
                    self.x, self.y = tx, ty
                    self.target = None
                else:
                    self.x += (dx/dist)*step
                    self.y += (dy/dist)*step

    def draw(self, surf):
        global cell_size
        frame = None
        if personaje_frames and personaje_frames[0]:
            frame = personaje_frames[self.frame_idx % len(personaje_frames)]
            if frame:
                size = max(8, int(cell_size * 0.8))
                img = pygame.transform.scale(frame, (size, size))
                rect = img.get_rect(center=(int(self.x), int(self.y)))
                surf.blit(img, rect)
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
            # update immediately to click pos
            rel_x = event.pos[0] - self.rect.x
            self.value = max(0.0, min(1.0, rel_x / self.rect.w))
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            self.value = max(0.0, min(1.0, rel_x / self.rect.w))

# ---------------- LÓGICA TABLERO / LAYOUT ----------------
grid = []
cell_size = 50
rows = cols = 8
tigre_count = 10

modal_active = False
modal_type = None
modal_buttons = []

MENU, OPTIONS, DIFFICULTY, GAME = 0,1,2,3
state = MENU

player = Player(SCREEN_WIDTH//2, 100)
music_on = True

# ---------------- FUNCIONES DE LAYOUT Y GRID ----------------
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

def reveal_cell_by_index(i, j):
    global player, modal_active, modal_type
    cell = grid[i][j]
    # NO revelar si hay bandera
    if hasattr(cell, "flagged") and cell.flagged:
        return
    if cell.revealed:
        return
    cell.revealed = True
    # click sound removed: no playback here

    if cell.is_tigre:
        player.lives -= 1
        if player.lives <= 0:
            # última vida -> solo gameover
            if gameover_sound:
                gameover_sound.play()
            open_modal("gameover")
        else:
            if tigre_sound:
                tigre_sound.play()
    else:
        if machete_sound:
            machete_sound.play()
        if cell.neighbors == 0:
            for di in (-1,0,1):
                for dj in (-1,0,1):
                    ni, nj = i+di, j+dj
                    if 0 <= ni < len(grid) and 0 <= nj < len(grid[0]):
                        if not grid[ni][nj].revealed:
                            reveal_cell_by_index(ni, nj)
    # check win
    won = True
    for row in grid:
        for c in row:
            if not c.is_tigre and not c.revealed:
                won = False
                break
        if not won:
            break
    if won:
        if victory_sound:
            victory_sound.play()
        open_modal("victory")

# ---------------- MODALES ----------------
def open_modal(kind):
    global modal_active, modal_type, modal_buttons
    modal_active = True
    modal_type = kind

    mw, mh = SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.45
    mx, my = (SCREEN_WIDTH - mw)//2, (SCREEN_HEIGHT - mh)//2

    # colocamos botones relativos al modal, más juntos y más estrechos
    btn_y = int(my + mh - 70)
    b1 = Button("Salir", (int(mx + mw/2 - 80), btn_y), size=(120,45))
    b2 = Button("Reintentar", (int(mx + mw/2 + 80), btn_y), size=(150,45))
    modal_buttons = [b1, b2]

def close_modal_to_menu():
    global modal_active, modal_type, state
    modal_active = False
    modal_type = None
    state = MENU

def close_modal_to_difficulty():
    global modal_active, modal_type, state
    modal_active = False
    modal_type = None
    state = DIFFICULTY

def draw_modal(surf):
    mw, mh = SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.45
    mx, my = (SCREEN_WIDTH - mw)//2, (SCREEN_HEIGHT - mh)//2
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    surf.blit(overlay, (0,0))
    pygame.draw.rect(surf, (40,40,40), (mx, my, mw, mh), border_radius=14)
    pygame.draw.rect(surf, WHITE, (mx, my, mw, mh), 2, border_radius=14)

    # texto dentro del modal (centrado en la caja)
    title_y = my + 30
    sub_y = my + 110
    if modal_type == "gameover":
        title = bigfont.render("Perdiste", True, WHITE)
        surf.blit(title, (mx + mw/2 - title.get_width()//2, title_y))
        sub = font.render("Has perdido todas tus vidas.", True, WHITE)
        surf.blit(sub, (mx + mw/2 - sub.get_width()//2, sub_y))
    elif modal_type == "victory":
        title = bigfont.render("¡Felicidades!", True, WHITE)
        surf.blit(title, (mx + mw/2 - title.get_width()//2, title_y))
        sub = font.render("Has superado el tablero.", True, WHITE)
        surf.blit(sub, (mx + mw/2 - sub.get_width()//2, sub_y))

    # dibujar botones (ya calculados en open_modal)
    for b in modal_buttons:
        b.draw(surf)

# ---------------- MENUS ----------------
def draw_title():
    if titulo_img:
        w = min(titulo_img.get_width(), SCREEN_WIDTH - 40)
        img = pygame.transform.scale(titulo_img, (w, int(w * titulo_img.get_height()/titulo_img.get_width())))
        screen.blit(img, (SCREEN_WIDTH//2 - img.get_width()//2, 10))
    else:
        t = bigfont.render("Selva Mortal", True, WHITE)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 10))

def main_menu():
    if fondo_img:
        screen.blit(pygame.transform.scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
    else:
        screen.fill(GREEN)
    draw_title()
    play_btn = Button("Jugar", (SCREEN_WIDTH//2, 260))
    opt_btn  = Button("Opciones", (SCREEN_WIDTH//2, 360))
    exit_btn = Button("Salir", (SCREEN_WIDTH//2, 460))
    for b in [play_btn, opt_btn, exit_btn]:
        b.draw(screen)
    return play_btn, opt_btn, exit_btn

def options_menu():
    if fondo_img:
        screen.blit(pygame.transform.scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
    else:
        screen.fill(GREEN)

    draw_title()
    txt = font.render("Opciones", True, WHITE)
    screen.blit(txt, (40, 150))

    labels = [
        ("Volumen Música", 250, music_slider),
        ("Volumen Machete", 300, machete_slider),
        ("Volumen Tigre", 350, tigre_slider),
        # click volume removed
        ("Volumen Game Over", 400, gameover_slider),
        ("Volumen Victoria", 450, victory_slider)
    ]

    for text, y, slider in labels:
        txt = font.render(text, True, WHITE)
        screen.blit(txt, (50, y))
        slider.draw(screen)

    # toggle música (pequeño botón)
    toggle_text = "Música: ON" if music_on else "Música: OFF"
    toggle_btn = Button(toggle_text, (SCREEN_WIDTH//2 - 120, 560), size=(180,50))
    toggle_btn.draw(screen)
    back_btn = Button("Volver", (SCREEN_WIDTH//2 + 120, 560), size=(160,50))
    back_btn.draw(screen)
    return toggle_btn, back_btn

def difficulty_menu():
    if fondo_img:
        screen.blit(pygame.transform.scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
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

# ---------------- START GAME ----------------
def start_game_with(rows_in, cols_in, tigre_num):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, cell_size, player, rows, cols, tigre_count, fondo_img, titulo_img
    rows = rows_in; cols = cols_in; tigre_count = tigre_num
    new_w, new_h, csize = compute_layout_for(rows, cols)
    cell_size = csize
    SCREEN_WIDTH, SCREEN_HEIGHT = new_w, new_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # reload scaled background and title if exist
    try:
        if os.path.exists("assets/images/fondo.jpg"):
            tmp = pygame.image.load("assets/images/fondo.jpg").convert()
            tmp = pygame.transform.scale(tmp, (SCREEN_WIDTH, SCREEN_HEIGHT))
            fondo_img = tmp
        elif os.path.exists("assets/images/fondo.png"):
            tmp = pygame.image.load("assets/images/fondo.png").convert()
            tmp = pygame.transform.scale(tmp, (SCREEN_WIDTH, SCREEN_HEIGHT))
            fondo_img = tmp
    except:
        fondo_img = None

    try:
        if os.path.exists("assets/images/titulo.png"):
            tmp = pygame.image.load("assets/images/titulo.png").convert_alpha()
            tmp = pygame.transform.scale(tmp, (500,150))
            titulo_img = tmp
    except:
        titulo_img = None

    create_grid(rows, cols, cell_size, tigre_count)
    player.x = SCREEN_WIDTH//2
    player.y = 100
    player.target = None
    player.lives = 3

# ---------------- INICIALIZACIÓN ----------------
cell_size = 50
create_grid(8, 8, cell_size, 10)
player = Player(SCREEN_WIDTH//2, 100)

clock = pygame.time.Clock()
running = True

play_btn = opt_btn = exit_btn = None
toggle_btn = back_btn = None
easy_btn = med_btn = hard_btn = None

# Sliders de volumen (globales)
music_slider    = Slider(300, 250, value=1.0)
machete_slider  = Slider(300, 300, value=1.0)
tigre_slider    = Slider(300, 350, value=1.0)
# click_slider removed
gameover_slider = Slider(300, 400, value=1.0)
victory_slider  = Slider(300, 450, value=1.0)

# ---------------- BUCLE PRINCIPAL ----------------
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---------- ESTADO: MENU ----------
        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                if play_btn and play_btn.is_clicked((mx,my)):
                    state = DIFFICULTY
                elif opt_btn and opt_btn.is_clicked((mx,my)):
                    state = OPTIONS
                elif exit_btn and exit_btn.is_clicked((mx,my)):
                    running = False

        # ---------- ESTADO: OPTIONS ----------
        elif state == OPTIONS:
            # sliders siempre manejan el evento (drag/click)
            music_slider.handle_event(event)
            machete_slider.handle_event(event)
            tigre_slider.handle_event(event)
            # click_slider removed
            gameover_slider.handle_event(event)
            victory_slider.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                # toggle_btn y back_btn vienen del draw al final del frame (asegúrate de reasignarlos)
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

        # ---------- ESTADO: DIFFICULTY ----------
        elif state == DIFFICULTY:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                if easy_btn and easy_btn.is_clicked((mx,my)):
                    start_game_with(8,8,1); state = GAME
                elif med_btn and med_btn.is_clicked((mx,my)):
                    start_game_with(12,12,20); state = GAME
                elif hard_btn and hard_btn.is_clicked((mx,my)):
                    start_game_with(16,16,40); state = GAME
                elif back_btn and back_btn.is_clicked((mx,my)):
                    state = MENU

        # ---------- ESTADO: GAME ----------
        elif state == GAME:
            if modal_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = event.pos
                    if modal_buttons[0].is_clicked((mx,my)):  # Salir -> menú
                        close_modal_to_menu()
                    elif modal_buttons[1].is_clicked((mx,my)):  # Reintentar -> dificultad
                        close_modal_to_difficulty()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = event.pos
                    if my > 120:
                        col = (mx - 20) // cell_size
                        row = (my - 140) // cell_size
                        if 0 <= row < rows and 0 <= col < cols:
                            cell = grid[row][col]
                            # click izquierdo: mover+revelar
                            if event.button == 1:
                                cx = cell.x + cell.size//2
                                cy = cell.y + cell.size//2
                                player.set_target(cx, cy)
                                reveal_cell_by_index(row, col)
                            # click derecho: bandera (si no está revelada)
                            elif event.button == 3:
                                if not cell.revealed:
                                    cell.flagged = not cell.flagged
                                    # click sound removed
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        state = MENU

    # ---------- UPDATES ----------
    if state == GAME and not modal_active:
        player.update(dt)

    # Aplicar volúmenes antes de dibujar
    try:
        pygame.mixer.music.set_volume(music_slider.value)
    except:
        pass
    if machete_sound: machete_sound.set_volume(machete_slider.value)
    if tigre_sound: tigre_sound.set_volume(tigre_slider.value)
    # click_sound volume removed
    if gameover_sound: gameover_sound.set_volume(gameover_slider.value)
    if victory_sound: victory_sound.set_volume(victory_slider.value)

    # ---------- DIBUJADO por Estado ----------
    if state == MENU:
        play_btn, opt_btn, exit_btn = main_menu()

    elif state == OPTIONS:
        toggle_btn, back_btn = options_menu()

    elif state == DIFFICULTY:
        easy_btn, med_btn, hard_btn, back_btn = difficulty_menu()

    elif state == GAME:
        if fondo_img:
            screen.blit(pygame.transform.scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
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