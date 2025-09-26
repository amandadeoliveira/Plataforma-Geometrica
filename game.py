import pgzrun
import random
import math
from pygame import Rect  # permitido por exceção

# --- Configurações do Jogo ---
WIDTH = 800
HEIGHT = 600
TITLE = "Plataforma Geométrica II"

# --- Estado do Jogo ---
game_state = "menu"  # "menu", "playing", "level_complete", "game_over", "game_won"
music_on = True
current_level = 0

# --- Constantes ---
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5
PLAYER_ATTACK_COOLDOWN = 20  # Frames entre tiros
PROJECTILE_SPEED = 8

# Portal: 2x maior do que antes
PORTAL_RADIUS = 40

# --- Definição dos Níveis ---
# Observe: índices humanos Nível 1..5 correspondem a índices 0..4
LEVELS = [
    # Nível 1
    {
        "player_start": (50, 500),
        "platforms": [
            Rect((0, 560), (WIDTH, 40)),
            Rect((200, 450), (150, 20)),
            Rect((450, 350), (150, 20))
        ],
        "enemies": [
            {'type': 'weak', 'pos': (250, 420), 'patrol': 50},
            {'type': 'strong', 'pos': (500, 320), 'patrol': 50},
        ],
        "portal_pos": None
    },
    # Nível 2
    {
        "player_start": (50, 500),
        "platforms": [
            Rect((0, 560), (WIDTH, 40)),
            Rect((100, 440), (100, 20)),
            Rect((300, 320), (100, 20)),
            Rect((500, 200), (100, 20)),
            Rect((300, 80), (100, 20))
        ],
        "enemies": [
            {'type': 'weak', 'pos': (150, 410), 'patrol': 40},
            {'type': 'strong', 'pos': (350, 290), 'patrol': 40},
            {'type': 'weak', 'pos': (550, 170), 'patrol': 40},
        ],
        "portal_pos": None
    },
    # Nível 3 (novo)
    {
        "player_start": (750, 500),
        "platforms": [
            Rect((0, 560), (WIDTH, 40)),
            Rect((600, 450), (150, 20)),
            Rect((350, 400), (150, 20)),
            Rect((100, 350), (150, 20)),
            Rect((250, 250), (120, 20))
        ],
        "enemies": [
            {'type': 'strong', 'pos': (650, 420), 'patrol': 60},
            {'type': 'weak',  'pos': (375, 370), 'patrol': 40},
            {'type': 'weak',  'pos': (130, 320), 'patrol': 30},
        ],
        "portal_pos": None
    },
    # Nível 4 (novo)
    {
        "player_start": (50, 100),
        "platforms": [
            Rect((0, 560), (WIDTH, 40)),
            Rect((0, 150), (150, 20)),
            Rect((200, 250), (150, 20)),
            Rect((400, 350), (150, 20)),
            Rect((600, 450), (150, 20)),
            Rect((420, 140), (120, 20))
        ],
        "enemies": [
            {'type': 'weak',  'pos': (250, 220), 'patrol': 50},
            {'type': 'strong','pos': (450, 320), 'patrol': 50},
            {'type': 'strong','pos': (650, 420), 'patrol': 50},
        ],
        "portal_pos": None
    },
    # Nível 5 (chefe final) - sem portal
    {
        "player_start": (100, 500),
        "platforms": [
            Rect((0, 560), (WIDTH, 40)),
            Rect((150, 480), (120, 20)),
            Rect((530, 480), (120, 20))
        ],
        "enemies": [
            {'type': 'boss', 'pos': (WIDTH / 2, 420), 'patrol': 200},
        ],
        "portal_pos": None
    },
]

# --- Classes do Jogo ---

class Player:
    def __init__(self, pos, size):
        self.rect = Rect((0, 0), size)
        self.rect.center = pos
        self.velocity_y = 0
        self.on_ground = False
        self.attack_cooldown = 0
        self.facing_right = True

    def update_movement(self, platforms):
        dx = 0
        if keyboard.left:
            dx = -PLAYER_SPEED
            self.facing_right = False
        elif keyboard.right:
            dx = PLAYER_SPEED
            self.facing_right = True

        self.velocity_y += GRAVITY
        if self.velocity_y > 10: self.velocity_y = 10

        self.rect.x += dx
        self.rect.y += self.velocity_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity_y >= 0:
                # checar se caiu em cima do platô
                if self.rect.bottom - self.velocity_y <= platform.top + 1:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True
                    break
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH

    def attack(self, projectiles):
        if self.attack_cooldown == 0:
            self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
            direction = 1 if self.facing_right else -1
            # centralizar projétil no jogador
            proj_center = (self.rect.centerx, self.rect.centery)
            projectiles.append(Projectile(proj_center, direction))

    def draw(self):
        screen.draw.filled_rect(self.rect, "cyan")

class Enemy:
    def __init__(self, type, pos, size, patrol_range):
        self.rect = Rect((0, 0), size)
        self.rect.center = (int(pos[0]), int(pos[1]))
        self.type = type
        self.start_x = int(pos[0])
        self.patrol_range = patrol_range
        self.speed = random.uniform(1.0, 2.5) if type != 'boss' else random.uniform(2.0, 4.0)

        # HP por tipo
        if self.type == 'weak':
            self.hp = 1
            self.color = "red"
        elif self.type == 'strong':
            self.hp = 3   # cinza morre com 3 hits
            self.color = "gray"
        elif self.type == 'boss':
            self.hp = 5   # boss morre com 5 hits
            self.color = "purple"
        else:
            self.hp = 1
            self.color = "red"

    def update_movement(self):
        self.rect.x += self.speed
        if abs(self.rect.centerx - self.start_x) >= self.patrol_range:
            self.speed *= -1

    def take_damage(self, amount=1):
        self.hp -= amount

    def draw(self):
        # desenha também uma barra de vida pequena acima do inimigo
        screen.draw.filled_rect(self.rect, self.color)
        # barra de vida simples
        bar_w = self.rect.width
        bar_h = 6
        bar_x = self.rect.left
        bar_y = self.rect.top - bar_h - 4
        # fundo
        screen.draw.filled_rect(Rect((bar_x, bar_y), (bar_w, bar_h)), "black")
        # vida atual (proporcional)
        if self.hp > 0:
            hp_ratio = max(0.0, min(1.0, self.hp / (5 if self.type == 'boss' else (3 if self.type == 'strong' else 1))))
            screen.draw.filled_rect(Rect((bar_x, bar_y), (int(bar_w * hp_ratio), bar_h)), "green")

class Projectile:
    def __init__(self, center_pos, direction):
        # cria retângulo de 10x10 centrado em center_pos
        self.rect = Rect((int(center_pos[0] - 5), int(center_pos[1] - 5)), (10, 10))
        self.speed = PROJECTILE_SPEED * direction

    def update(self):
        self.rect.x += int(self.speed)

    def draw(self):
        screen.draw.filled_circle(self.rect.center, 5, "orange")

class Portal:
    def __init__(self, pos):
        # pos é o centro do portal
        self.pos = (int(pos[0]), int(pos[1]))
        self.radius = PORTAL_RADIUS

    def draw(self):
        screen.draw.filled_circle(self.pos, self.radius, "yellow")
        screen.draw.circle(self.pos, self.radius, "orange")

    def collides_with(self, player_rect):
        dist_x = abs(self.pos[0] - player_rect.centerx)
        dist_y = abs(self.pos[1] - player_rect.centery)
        if dist_x > (player_rect.width / 2 + self.radius): return False
        if dist_y > (player_rect.height / 2 + self.radius): return False
        if dist_x <= (player_rect.width / 2): return True 
        if dist_y <= (player_rect.height / 2): return True
        corner_distance_sq = (dist_x - player_rect.width / 2)**2 + (dist_y - player_rect.height / 2)**2
        return corner_distance_sq <= (self.radius**2)

# --- Variáveis Globais ---
player = Player(pos=(0,0), size=(30, 40))
platforms = []
enemies = []
projectiles = []
portal = None

# --- Funções ---
def setup_level(level_index):
    global platforms, enemies, projectiles, portal, player, game_state
    
    if level_index >= len(LEVELS):
        game_state = "game_won"
        return

    level_data = LEVELS[level_index]
    
    player.rect.center = (int(level_data["player_start"][0]), int(level_data["player_start"][1]))
    player.velocity_y = 0
    
    # Reconstruir plataformas (novas instâncias de Rect)
    platforms = [Rect(p.topleft, p.size) for p in level_data["platforms"]]
    
    # Criar inimigos
    enemies.clear()
    for e_data in level_data["enemies"]:
        size = (80, 80) if e_data['type'] == 'boss' else (35, 30)
        enemies.append(Enemy(e_data['type'], e_data['pos'], size, e_data['patrol']))
        
    projectiles.clear()
    
    # Portal só aparece se NÃO for o último nível
    if level_index < len(LEVELS) - 1:
        if level_data["portal_pos"]:
            # se o designer definiu portal_pos, respeitamos (mas garantimos int)
            portal = Portal((int(level_data["portal_pos"][0]), int(level_data["portal_pos"][1])))
        else:
            if platforms:
                # escolhe a plataforma mais "alta" (menor top)
                highest = min(platforms, key=lambda p: p.top)
                portal_x = highest.centerx
                # coloca o centro do portal exatamente sobre a plataforma (top - radius)
                portal_y = highest.top - PORTAL_RADIUS
                portal = Portal((portal_x, portal_y))
            else:
                portal = None
    else:
        portal = None

def reset_game():
    global current_level, game_state
    current_level = 0
    setup_level(current_level)
    game_state = "playing"
    if music_on: start_music()

def start_music():
    try:
        music.play("background_music")
        music.set_volume(0.3)
    except Exception as e:
        print(f"Aviso: Música não encontrada. Erro: {e}")

# --- Funções do Pygame Zero ---
def draw():
    screen.fill((20, 20, 80))

    if game_state == "menu":
        screen.draw.text("Plataforma Geométrica II", center=(WIDTH / 2, 150), fontsize=60, color="white")
        start_button = Rect((WIDTH / 2 - 100, 250), (200, 50))
        music_button = Rect((WIDTH / 2 - 100, 320), (200, 50))
        exit_button = Rect((WIDTH / 2 - 100, 390), (200, 50))
        screen.draw.filled_rect(start_button, "darkgreen"); screen.draw.text("Começar Jogo", center=start_button.center, fontsize=30, color="white")
        screen.draw.filled_rect(music_button, "darkblue"); screen.draw.text(f"Música: {'LIGADA' if music_on else 'DESLIGADA'}", center=music_button.center, fontsize=30, color="white")
        screen.draw.filled_rect(exit_button, "darkred"); screen.draw.text("Sair", center=exit_button.center, fontsize=30, color="white")

    elif game_state == "playing":
        for p in platforms: screen.draw.filled_rect(p, "saddlebrown")
        if portal: portal.draw()
        player.draw()
        for e in enemies: e.draw()
        for p in projectiles: p.draw()
        screen.draw.text(f"Nível: {current_level + 1}", (10, 10), color="white", fontsize=30)

        # dica para o jogador no último nível
        if current_level == len(LEVELS) - 1:
            screen.draw.text("Derrote o chefe final!", center=(WIDTH/2, 40), fontsize=28, color="white")

    elif game_state == "level_complete":
        screen.draw.text(f"Nível {current_level + 1} Concluído!", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="green")
        screen.draw.text("Pressione ENTER para continuar", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color="white")

    elif game_state == "game_over":
        screen.draw.text("FIM DE JOGO", center=(WIDTH / 2, HEIGHT/2), fontsize=80, color="orange")
        screen.draw.text("Pressione ENTER para voltar ao menu", center=(WIDTH / 2, HEIGHT/2 + 60), fontsize=30, color="white")

    elif game_state == "game_won":
        screen.draw.text("VOCÊ VENCEU!", center=(WIDTH / 2, HEIGHT/2), fontsize=80, color="gold")
        screen.draw.text("Pressione ENTER para voltar ao menu", center=(WIDTH / 2, HEIGHT/2 + 60), fontsize=30, color="white")

def update(dt):
    global game_state, current_level
    if game_state != "playing": return

    player.update_movement(platforms)
    for e in enemies: e.update_movement()
    for p in projectiles: p.update()

    enemies_to_remove = []
    projectiles_to_remove = []

    # colisões jogador <-> inimigo e projéteis <-> inimigo
    for enemy in list(enemies):
        # colisão jogador x inimigo
        if player.rect.colliderect(enemy.rect):
            is_stomp = player.velocity_y > 0 and player.rect.bottom - player.velocity_y < enemy.rect.top + 5
            if enemy.type == 'weak' and is_stomp:
                # stomp derrota inimigos fracos
                enemies_to_remove.append(enemy)
                player.velocity_y = JUMP_STRENGTH * 0.6
            else:
                # qualquer outro contato lateral com inimigo causa game over
                game_state = "game_over"
                try:
                    music.stop()
                except:
                    pass

        # colisões projétil x inimigo
        for proj in list(projectiles):
            if proj.rect.colliderect(enemy.rect):
                # projétil causa 1 de dano
                enemy.take_damage(1)
                # remover projétil
                if proj not in projectiles_to_remove:
                    projectiles_to_remove.append(proj)
                # se inimigo morreu, marca para remoção
                if enemy.hp <= 0 and enemy not in enemies_to_remove:
                    enemies_to_remove.append(enemy)

    # aplicar remoções
    enemies[:] = [e for e in enemies if e not in enemies_to_remove]
    projectiles[:] = [p for p in projectiles if p not in projectiles_to_remove and 0 < p.rect.x < WIDTH]

    # portal (quando existir)
    if portal and portal.collides_with(player.rect):
        game_state = "level_complete"
        try:
            music.fadeout(1.0)
        except:
            pass

    # último nível: verifica se não há inimigos -> vitória
    if current_level == len(LEVELS) - 1 and not enemies:
        game_state = "game_won"
        try:
            music.fadeout(1.0)
        except:
            pass

    # queda abaixo da tela -> game over
    if player.rect.top > HEIGHT:
        game_state = "game_over"
        try:
            music.stop()
        except:
            pass

def on_key_down(key):
    global game_state, current_level
    if game_state == "playing":
        if key in [keys.SPACE, keys.UP]: player.jump()
        if key == keys.X: player.attack(projectiles)
    
    elif game_state in ["game_over", "game_won"]:
        if key == keys.RETURN: game_state = "menu"
    
    elif game_state == "level_complete":
        if key == keys.RETURN:
            current_level += 1
            setup_level(current_level)
            game_state = "playing"
            if music_on: start_music()

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == "menu":
        start_button = Rect((WIDTH / 2 - 100, 250), (200, 50))
        music_button = Rect((WIDTH / 2 - 100, 320), (200, 50))
        exit_button = Rect((WIDTH / 2 - 100, 390), (200, 50))
        if start_button.collidepoint(pos): reset_game()
        elif music_button.collidepoint(pos):
            music_on = not music_on
            if music_on: start_music()
            else:
                try:
                    music.stop()
                except:
                    pass
        elif exit_button.collidepoint(pos): exit()

# inicializa música e primeira tela/menu
if music_on: start_music()
pgzrun.go()
