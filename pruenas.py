import pygame, sys, random, math, os

pygame.init()

# ---------------- CONFIG ----------------
SCREEN_MAX_W, SCREEN_MAX_H = 1366, 768
# ventana inicial (se ajusta al seleccionar dificultad)
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Selva Mortal")

WHITE = (255,255,255)
GREEN = (34,139,34)
RED = (200,0,0)
BLACK = (0,0,0)
MODAL_BG = (30,30,30,230)

font = pygame.font.SysFont(None, 36)
bigfont = pygame.font.SysFont(None, 72)

# ---------------- ESPACIOS PARA IMÁGENES ----------------
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

# ---------------- ESPACIOS PARA SONIDOS ----------------
pygame.mixer.init()
try:
    pygame.mixer.music.load("assets/sounds/fondo.mp3")
    pygame.mixer.music.play(-1)
except:
    print("[Aviso] No se encontro musica de fondo.")

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        print(f"[Aviso] No se pudo cargar {path}")
        return None

machete_sound  = load_sound("assets/sounds/machete.mp3")
tigre_sound    = load_sound("assets/sounds/rugido_tigre.mp3")
click_sound    = load_sound("assets/sounds/click.mp3")
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

# 🔹 Slider para volumen
class Slider:
    def __init__(self, x, y, w, h, min_val=0.0, max_val=1.0, start_val=1.0):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                rel_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.w))
                pct = (rel_x - self.rect.x) / self.rect.w
                self.value = self.min_val + pct * (self.max_val - self.min_val)

    def draw(self, surf):
        pygame.draw.rect(surf, (100,100,100), self.rect)
        filled_w = int(self.rect.w * ((self.value - self.min_val)/(self.max_val-self.min_val)))
        pygame.draw.rect(surf, (0,200,0), (self.rect.x, self.rect.y, filled_w, self.rect.h))
        knob_x = self.rect.x + filled_w
        pygame.draw.circle(surf, (255,0,0), (knob_x, self.rect.centery), self.rect.h//2 + 2)

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
        self.flagged = False  # 🔹 nueva

    def draw(self, surf):
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        if not self.revealed:
            if arbusto_img:
                arb = pygame.transform.scale(arbusto_img, (self.size, self.size))
                surf.blit(arb, (self.x, self.y))
            else:
                pygame.draw.rect(surf, GREEN, rect)
            pygame.draw.rect(surf, BLACK, rect, 1)
            if self.flagged:
                pygame.draw.polygon(surf, RED, [
                    (self.x + self.size//4, self.y + self.size//4),
                    (self.x + self.size//4, self.y + self.size*3//4),
                    (self.x + self.size*3//4, self.y + self.size//2)
                ])
        else:
            if self.is_tigre:
                if tigre_img:
                    tig = pygame.transform.scale(tigre_img, (self.size, self.size))
                    surf.blit(tig, (self.x, self.y))
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

# ---------------- LÓGICA TABLERO ----------------
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

# ---------------- FUNCIONES ----------------
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
            if grid[i][j].is_tigre: continue
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
    if cell.revealed or cell.flagged:
        return
    cell.revealed = True
    if click_sound: click_sound.play()
    if cell.is_tigre:
        player.lives -= 1
        if player.lives <= 0:
            if gameover_sound: gameover_sound.play()
            open_modal("gameover")
        else:
            if tigre_sound: tigre_sound.play()
    else:
        if machete_sound: machete_sound.play()
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
        if victory_sound: victory_sound.play()
        open_modal("victory")

# ---------------- MODALES ----------------
def open_modal(kind):
    global modal_active, modal_type, modal_buttons
    modal_active = True
    modal_type = kind
    mw, mh = SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.45
    mx, my = (SCREEN_WIDTH - mw)//2, (SCREEN_HEIGHT - mh)//2
    btn_y = my + mh - 80  
    b1 = Button("Salir", (mx + mw/2 - 80, btn_y), size=(120,45))
    b2 = Button("Reintentar", (mx + mw/2 + 80, btn_y), size=(150,45))
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
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    surf.blit(overlay, (0,0))
    mw, mh = SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.45
    mx, my = (SCREEN_WIDTH - mw)//2, (SCREEN_HEIGHT - mh)//2
    pygame.draw.rect(surf, (40,40,40), (mx, my, mw, mh), border_radius=14)
    pygame.draw.rect(surf, WHITE, (mx, my, mw, mh), 2, border_radius=14)
    if modal_type == "gameover":
        title = bigfont.render("Perdiste", True, WHITE)
        surf.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, my + 30))
        sub = font.render("Has perdido todas tus vidas.", True, WHITE)
        surf.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, my + 120))
    elif modal_type == "victory":
        title = bigfont.render("¡Felicidades!", True, WHITE)
        surf.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, my + 30))
        sub = font.render("Has superado el tablero.", True, WHITE)
        surf.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, my + 120))
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
    if fondo_img: screen.blit(pygame.transform.scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
    else: screen.fill(GREEN)
    draw_title()
    play_btn = Button("Jugar", (SCREEN_WIDTH//2, 260))
    opt_btn  = Button("Opciones", (SCREEN_WIDTH//2, 360))
    exit_btn = Button("Salir", (SCREEN_WIDTH//2, 460))
    for b in [play_btn, opt_btn, exit_btn]: b.draw(screen)
    return play_btn, opt_btn, exit_btn

def options_menu():
    if fondo_img: screen.blit(pygame.transform.scale(fondo_img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
    else: screen.fill(GREEN)
    draw_title()
    txt = font.render("Opciones", True, WHITE)
    screen.blit(txt, (40, 200))
    toggle_text = "Música: ON" if music_on else "Música: OFF"
    toggle_btn = Button(toggle_text, (SCREEN_WIDTH//2, 320), size=(240,60))
    toggle_btn.draw(screen)
    volume_label = font.render("Volumen:", True, WHITE)
    screen.blit(volume_label, (150, 250))
    volume_slider.draw(screen)
    back_btn = Button("Volver", (SCREEN_WIDTH//2, 420))
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
    for b in [easy, med, hard, back]: b.draw(screen)
    return easy, med, hard, back

# ---------------- START GAME ----------------
def start_game_with(rows_in, cols_in, tigre_num):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, cell_size, player, rows, cols, tigre_count
    rows = rows_in; cols = cols_in; tigre_count = tigre_num
    new_w, new_h, csize = compute_layout_for(rows, cols)
    cell_size = csize
    SCREEN_WIDTH, SCREEN_HEIGHT = new_w, new_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    try:
        if os.path.exists("assets/images/fondo.jpg"):
            tmp = pygame.image.load("assets/images/fondo.jpg").convert()
            tmp = pygame.transform.scale(tmp, (SCREEN_WIDTH, SCREEN_HEIGHT))
            global fondo_img
            fondo_img = tmp
        elif os.path.exists("assets/images/fondo.png"):
            tmp = pygame.image.load("assets/images/fondo.png").convert()
            tmp = pygame.transform.scale(tmp, (SCREEN_WIDTH, SCREEN_HEIGHT))
            fondo_img = tmp
    except:
        pass

    create_grid(rows, cols, cell_size, tigre_count)
    player.x = SCREEN_WIDTH//2
    player.y = 80
    player.target = None
    player.lives = 3

# ---------------- GAME LOOP ----------------
clock = pygame.time.Clock()
volume_slider = Slider(320, 250, 300, 20, start_val=pygame.mixer.music.get_volume())

running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_btn.is_clicked(event.pos):
                    if click_sound: click_sound.play()
                    state = DIFFICULTY
                elif opt_btn.is_clicked(event.pos):
                    if click_sound: click_sound.play()
                    state = OPTIONS
                elif exit_btn.is_clicked(event.pos):
                    running = False

        elif state == OPTIONS:
            volume_slider.handle_event(event)
            pygame.mixer.music.set_volume(volume_slider.value)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if toggle_btn.is_clicked(event.pos):
                    if click_sound: click_sound.play()
                    music_on = not music_on
                    if music_on: pygame.mixer.music.unpause()
                    else: pygame.mixer.music.pause()
                elif back_btn.is_clicked(event.pos):
                    if click_sound: click_sound.play()
                    state = MENU

        elif state == DIFFICULTY:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if easy.is_clicked(event.pos):
                    start_game_with(8,8,10)
                    state = GAME
                elif med.is_clicked(event.pos):
                    start_game_with(12,12,20)
                    state = GAME
                elif hard.is_clicked(event.pos):
                    start_game_with(16,16,40)
                    state = GAME
                elif back.is_clicked(event.pos):
                    state = MENU

        elif state == GAME:
            if not modal_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Clic izquierdo → revelar
                    if event.button == 1:
                        mx, my = event.pos
                        for i,row in enumerate(grid):
                            for j,c in enumerate(row):
                                if c.x <= mx < c.x+c.size and c.y <= my < c.y+c.size:
                                    player.set_target(c.x + c.size//2, c.y + c.size//2)
                                    reveal_cell_by_index(i,j)
                                    break
                    # Clic derecho → bandera
                    elif event.button == 3:
                        mx, my = event.pos
                        for row in grid:
                            for c in row:
                                if c.x <= mx < c.x+c.size and c.y <= my < c.y+c.size:
                                    c.flagged = not c.flagged

            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if modal_buttons[0].is_clicked(event.pos): # salir
                        close_modal_to_menu()
                    elif modal_buttons[1].is_clicked(event.pos): # reintentar
                        close_modal_to_difficulty()

    # -------- DIBUJADO --------
    if state == MENU:
        play_btn,opt_btn,exit_btn = main_menu()
    elif state == OPTIONS:
        toggle_btn,back_btn = options_menu()
    elif state == DIFFICULTY:
        easy,med,hard,back = difficulty_menu()
    elif state == GAME:
        if fondo_img: screen.blit(fondo_img, (0,0))
        else: screen.fill((50,150,50))
        for row in grid:
            for c in row: c.draw(screen)
        player.update(dt)
        player.draw(screen)
        lives_text = font.render(f"Vidas: {player.lives}", True, WHITE)
        screen.blit(lives_text, (10,10))
        if modal_active: draw_modal(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

           
