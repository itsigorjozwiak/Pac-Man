import pygame
import sys
import math
import random
import os
import json
from collections import deque

SCREEN_WIDTH = 570
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE_WALL = (25, 25, 166)
PINK_DOOR = (255, 184, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

LAYOUT = [
    "0000000000000000000",
    "0111111110111111110",
    "0200100010100010020",
    "0111111111111111110",
    "0100100100010010010",
    "0111100100010011110",
    "0000103333333010000",
    "0000103009003010000",
    "0000103044403010000",
    "3333333044403333333",
    "0000103000003010000",
    "0000103333333010000",
    "0111100100010011110",
    "0100100100010010010",
    "021111111P111111120",
    "0001000000000001000",
    "0111111100011111110",
    "0100000010100000010",
    "0111111111111111110",
    "0000000000000000000",
]

class AssetManager:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
    def load_image(self, filename, optional=False):
        path = os.path.join(self.base_path, 'assets', 'images', filename)
        if not os.path.exists(path):
            if optional: return None
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((255, 0, 255))
            return s
        return pygame.image.load(path).convert_alpha()

    def get_sound_path(self, filename):
        return os.path.join(self.base_path, 'assets', 'sounds', filename)

    def get_sprite_exact(self, sheet, x, y, w, h):
        w, h = int(w), int(h)
        img = pygame.Surface((w, h), pygame.SRCALPHA)
        img.blit(sheet, (0, 0), (x, y, w, h))
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except:
            self.sound_enabled = False

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.Font(None, 24)
        self.mid_font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 60)
        
        self.assets = AssetManager()
        self.load_all_assets()
        self.load_high_scores()
        
        if self.sound_enabled:
            self.channel_bg = pygame.mixer.Channel(0)
            self.channel_eat = pygame.mixer.Channel(1)
            self.channel_fruit = pygame.mixer.Channel(2)
            self.channel_fail = pygame.mixer.Channel(3)

        self.state = "NICK_INPUT"
        self.nick = ""
        self.score = 0
        self.lives = 3
        self.level = 1
        
        self.reset_game()

    def load_all_assets(self):
        self.logo = self.assets.load_image('logo.png', optional=True)
        if self.logo and self.logo.get_width() > 400:
            scale = 400 / self.logo.get_width()
            self.logo = pygame.transform.scale(self.logo, (400, int(self.logo.get_height() * scale)))

        sheet = self.assets.load_image('pac-man.png')
        self.pacman_frames = []
        frame_h = sheet.get_height() // 12
        w = sheet.get_width()
        for i in range(12):
            self.pacman_frames.append(self.assets.get_sprite_exact(sheet, 0, i * frame_h, w, frame_h))

        self.ghost_sprites = {}
        ghost_files = {
            'red': 'red_spirit.png',
            'pink': 'pink_spirit.png',
            'cyan': 'turquoise_spirit.png',
            'orange': 'orange_spirit.png'
        }
        
        for color, filename in ghost_files.items():
            sheet = self.assets.load_image(filename)
            self.ghost_sprites[color] = {}
            gw = sheet.get_width() // 2
            gh = sheet.get_height() // 4
            
            self.ghost_sprites[color]['down'] = [
                self.assets.get_sprite_exact(sheet, 0, 0, gw, gh),
                self.assets.get_sprite_exact(sheet, 0, gh, gw, gh)
            ]
            self.ghost_sprites[color]['up'] = [
                self.assets.get_sprite_exact(sheet, gw, 0, gw, gh),
                self.assets.get_sprite_exact(sheet, gw, gh, gw, gh)
            ]
            self.ghost_sprites[color]['left'] = [
                self.assets.get_sprite_exact(sheet, 0, 2 * gh, gw, gh),
                self.assets.get_sprite_exact(sheet, 0, 3 * gh, gw, gh)
            ]
            self.ghost_sprites[color]['right'] = [
                self.assets.get_sprite_exact(sheet, gw, 2 * gh, gw, gh),
                self.assets.get_sprite_exact(sheet, gw, 3 * gh, gw, gh)
            ]

        sheet = self.assets.load_image('blue_ghost.png')
        bw = sheet.get_width() // 2
        bh = sheet.get_height() // 2
        self.frightened_sprites = [
            self.assets.get_sprite_exact(sheet, 0, 0, bw, bh),
            self.assets.get_sprite_exact(sheet, 0, bh, bw, bh),
            self.assets.get_sprite_exact(sheet, bw, 0, bw, bh),
            self.assets.get_sprite_exact(sheet, bw, bh, bw, bh)
        ]

        sheet = self.assets.load_image('ghost_eyes.png')
        ew = sheet.get_width() // 2
        eh = sheet.get_height()
        self.eyes_left = self.assets.get_sprite_exact(sheet, 0, 0, ew, eh)
        self.eyes_right = self.assets.get_sprite_exact(sheet, ew, 0, ew, eh)

        sheet = self.assets.load_image('fruits.png')
        fw = sheet.get_width() // 2
        fh = sheet.get_height() // 2
        
        self.fruit_sprites = [
            self.assets.get_sprite_exact(sheet, fw, fh, fw, fh),
            self.assets.get_sprite_exact(sheet, 0, fh, fw, fh), 
            self.assets.get_sprite_exact(sheet, 0, 0, fw, fh),   
            self.assets.get_sprite_exact(sheet, fw, 0, fw, fh)   
        ]

        sheet = self.assets.load_image('death.png')
        self.death_frames = []
        dh = sheet.get_height() // 11
        dw = sheet.get_width()
        for i in range(11):
            self.death_frames.append(self.assets.get_sprite_exact(sheet, 0, i * dh, dw, dh))

        self.sounds = {}
        if self.sound_enabled:
            sound_files = {
                'start': 'start_music.mp3',
                'move_normal': 'normal_ghost_movement.mp3',
                'move_blue': 'blue_ghost_movement.mp3',
                'return_ghost': 'return_the_eaten_ghost_to_the_ghost_house.mp3',
                'eat_fruit': 'eating_the_fruit.mp3',
                'eat_ghost': 'eating_the_ghost.mp3',
                'eat_dot': 'eating_the_pac-dots.mp3',
                'fail': 'fail.mp3'
            }
            for name, file in sound_files.items():
                path = self.assets.get_sound_path(file)
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                    if name == 'eat_dot': self.sounds[name].set_volume(0.2)
                    elif name == 'fail': self.sounds[name].set_volume(0.5)
                    else: self.sounds[name].set_volume(0.3)

    def load_high_scores(self):
        self.high_scores = []
        path = os.path.join(self.assets.base_path, 'scores.txt')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    self.high_scores = json.load(f)
            except: pass

    def save_high_scores(self):
        self.high_scores.append({'nick': self.nick, 'score': self.score})
        self.high_scores = sorted(self.high_scores, key=lambda x: x['score'], reverse=True)[:3]
        path = os.path.join(self.assets.base_path, 'scores.txt')
        with open(path, 'w') as f:
            json.dump(self.high_scores, f)

    def reset_game(self):
        self.create_map()
        self.ghosts = [
            Ghost(self, 'red', 9, 6),
            Ghost(self, 'pink', 9, 8),
            Ghost(self, 'cyan', 8, 8),
            Ghost(self, 'orange', 10, 8)
        ]
        self.fruit = None
        self.fruit_timer = 0
        self.fruit_spawned_at_70 = False
        self.fruit_spawned_at_170 = False
        self.scatter_mode = True
        self.mode_timer = pygame.time.get_ticks()
        self.frightened_mode = False
        self.frightened_end_time = 0
        self.start_music_played = False
        self.start_timer = pygame.time.get_ticks()
        self.flashing_walls = False
        self.flash_timer = 0
        self.flash_color = BLUE_WALL
        self.dots_eaten = 0
        if self.sound_enabled:
            self.channel_bg.stop()
            self.channel_eat.stop()
            self.channel_fruit.stop()

    def create_map(self):
        self.walls = []
        self.ghost_barriers = [] 
        self.dots = []
        self.door_rect = None
        self.house_tiles = []
        
        self.player = Pacman(self, 1, 1)

        for row_idx, row in enumerate(LAYOUT):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                
                if char == '0':
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == '1':
                    self.dots.append({'rect': pygame.Rect(x + TILE_SIZE//2 - 2, y + TILE_SIZE//2 - 2, 4, 4), 'type': 'small'})
                elif char == '2':
                    self.dots.append({'rect': pygame.Rect(x + TILE_SIZE//2 - 6, y + TILE_SIZE//2 - 6, 12, 12), 'type': 'big'})
                elif char == '4':
                    self.house_tiles.append((col_idx, row_idx))
                    self.ghost_barriers.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == '9':
                    self.door_rect = pygame.Rect(x, y + TILE_SIZE//2 - 2, TILE_SIZE, 4)
                    self.house_tiles.append((col_idx, row_idx))
                    self.ghost_barriers.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == 'P':
                    self.player = Pacman(self, col_idx, row_idx)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if self.state == "NICK_INPUT":
                mx, my = pygame.mouse.get_pos()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(self.nick) > 0:
                        self.state = "PLAYING"
                        self.start_timer = pygame.time.get_ticks()
                        if self.sound_enabled:
                            self.channel_bg.play(self.sounds['start'])
                    elif event.key == pygame.K_BACKSPACE:
                        self.nick = self.nick[:-1]
                    else:
                        if len(self.nick) < 8:
                            self.nick += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if len(self.nick) > 0:
                        if SCREEN_WIDTH//2 - 100 < mx < SCREEN_WIDTH//2 + 100:
                            if 350 < my < 390:
                                self.state = "PLAYING"
                                self.start_timer = pygame.time.get_ticks()
                                if self.sound_enabled:
                                    self.channel_bg.play(self.sounds['start'])
            
            elif self.state == "GAME_OVER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if SCREEN_WIDTH//2 - 100 < mx < SCREEN_WIDTH//2 + 100:
                        if 550 < my < 600:
                            self.score = 0
                            self.lives = 3
                            self.level = 1
                            self.reset_game()
                            self.state = "PLAYING"
                            self.start_timer = pygame.time.get_ticks()
                            if self.sound_enabled:
                                self.channel_bg.play(self.sounds['start'])
                        elif 610 < my < 660:
                            sys.exit()

    def update(self):
        if self.state == "PLAYING":
            current_time = pygame.time.get_ticks()
            if not self.start_music_played:
                 if current_time - self.start_timer < 4200: return
                 else: self.start_music_played = True

            self.player.update(self.walls + self.ghost_barriers)
            
            if not self.frightened_mode:
                if current_time - self.mode_timer > 20000:
                    self.scatter_mode = not self.scatter_mode
                    self.mode_timer = current_time
                    for ghost in self.ghosts: ghost.reverse_direction()
            else:
                time_left = self.frightened_end_time - current_time
                if time_left <= 0:
                    self.frightened_mode = False
                    for ghost in self.ghosts:
                        if ghost.mode == 'frightened':
                            ghost.mode = 'normal'
                            ghost.pixel_pos = [ghost.grid_pos[0]*TILE_SIZE, ghost.grid_pos[1]*TILE_SIZE]

            for ghost in self.ghosts:
                if not self.start_music_played:
                    ghost.direction = (0, -1)
                else:
                    ghost.update(self.player, self.walls)
                
                if self.player.grid_pos == ghost.grid_pos:
                    if ghost.mode == 'frightened':
                        ghost.mode = 'dead'
                        self.score += 200
                        if self.sound_enabled:
                            self.channel_fruit.play(self.sounds['eat_ghost'])
                        ghost.pixel_pos = [ghost.grid_pos[0]*TILE_SIZE, ghost.grid_pos[1]*TILE_SIZE]
                    elif ghost.mode == 'dead':
                        pass
                    else:
                        self.player_die()

            player_rect = pygame.Rect(self.player.pixel_pos[0] + 10, self.player.pixel_pos[1] + 10, 10, 10)
            
            ate_something = False
            for dot in self.dots[:]:
                if player_rect.colliderect(dot['rect']):
                    self.dots.remove(dot)
                    ate_something = True
                    self.dots_eaten += 1
                    if dot['type'] == 'small':
                        self.score += 10
                    else:
                        self.score += 50
                        self.frightened_mode = True
                        self.frightened_end_time = pygame.time.get_ticks() + 5000
                        for ghost in self.ghosts:
                            if ghost.mode != 'dead':
                                ghost.mode = 'frightened'
                                ghost.reverse_direction()
            
            if ate_something and self.sound_enabled:
                if not self.channel_eat.get_busy():
                    self.channel_eat.play(self.sounds['eat_dot'], loops=0)

            should_spawn = False
            if self.dots_eaten >= 70 and not self.fruit_spawned_at_70:
                should_spawn = True
                self.fruit_spawned_at_70 = True
            elif self.dots_eaten >= 170 and not self.fruit_spawned_at_170:
                should_spawn = True
                self.fruit_spawned_at_170 = True

            if should_spawn and not self.fruit:
                attempts = 0
                while attempts < 100:
                    rx = random.randint(1, len(LAYOUT[0])-2)
                    ry = random.randint(1, len(LAYOUT)-2)
                    tile = LAYOUT[ry][rx]
                    if tile != '0' and tile != '4' and tile != '9':
                        pool = [0]
                        if self.level == 2: pool = [0, 1] 
                        elif self.level == 3: pool = [0, 1, 2]
                        elif self.level >= 4: pool = [0, 1, 2, 3]
                        
                        f_type = random.choice(pool)
                        self.fruit = {'rect': pygame.Rect(rx * TILE_SIZE, ry * TILE_SIZE, TILE_SIZE, TILE_SIZE), 
                                      'type': f_type}
                        self.fruit_timer = pygame.time.get_ticks()
                        break
                    attempts += 1
            
            if self.fruit:
                if player_rect.colliderect(self.fruit['rect']):
                    self.score += 100 * self.level
                    if self.sound_enabled:
                        self.channel_fruit.play(self.sounds['eat_fruit'])
                    self.fruit = None
                elif pygame.time.get_ticks() - self.fruit_timer > 9000:
                    self.fruit = None

            if not self.dots:
                self.state = "LEVEL_TRANSITION"
                self.flash_timer = pygame.time.get_ticks()
                if self.sound_enabled:
                    self.channel_bg.stop()
                    self.channel_eat.stop()

            self.update_audio()

        elif self.state == "LEVEL_TRANSITION":
            now = pygame.time.get_ticks()
            if (now // 200) % 2 == 0: self.flash_color = WHITE
            else: self.flash_color = BLUE_WALL
            if now - self.flash_timer > 3000:
                self.level += 1
                self.reset_game()
                self.start_music_played = True
                self.state = "PLAYING"
                self.flash_color = BLUE_WALL

    def player_die(self):
        if self.sound_enabled:
            self.channel_bg.stop()
            self.channel_eat.stop()
            self.channel_fail.play(self.sounds['fail'])
        
        total_duration = 2500
        frame_duration = total_duration // 11
        
        for i in range(11):
            now = pygame.time.get_ticks()
            while pygame.time.get_ticks() - now < frame_duration:
                self.screen.fill(BLACK) 
                self.draw_game_elements(draw_player=False)
                self.screen.blit(self.death_frames[i], self.player.pixel_pos)
                pygame.display.flip()
                self.clock.tick(60)
        
        self.lives -= 1
        if self.lives <= 0:
            self.save_high_scores()
            self.state = "GAME_OVER"
        else:
            self.player.reset_position()
            self.ghosts = [
                Ghost(self, 'red', 9, 6),
                Ghost(self, 'pink', 9, 8),
                Ghost(self, 'cyan', 8, 8),
                Ghost(self, 'orange', 10, 8)
            ]
            self.start_timer = pygame.time.get_ticks()
            self.start_music_played = False

    def update_audio(self):
        if not self.sound_enabled: return
        if not self.start_music_played: return

        target_sound = self.sounds['move_normal']
        if any(g.mode == 'dead' for g in self.ghosts):
            target_sound = self.sounds['return_ghost']
        elif self.frightened_mode:
            target_sound = self.sounds['move_blue']
        
        if not self.channel_bg.get_busy() or self.channel_bg.get_sound() != target_sound:
            self.channel_bg.play(target_sound, loops=-1)

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == "NICK_INPUT":
            if self.logo:
                self.screen.blit(self.logo, (SCREEN_WIDTH//2 - self.logo.get_width()//2, 50))
            else:
                title = self.big_font.render("Pac-Man", True, YELLOW)
                self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            
            lbl = self.mid_font.render("Podaj swoj Nick:", True, WHITE)
            self.screen.blit(lbl, (SCREEN_WIDTH//2 - lbl.get_width()//2, 250))
            input_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 40)
            pygame.draw.rect(self.screen, BLUE_WALL, input_rect, 2)
            nick_txt = self.mid_font.render(self.nick, True, (0, 255, 255))
            self.screen.blit(nick_txt, (input_rect.centerx - nick_txt.get_width()//2, input_rect.centery - nick_txt.get_height()//2))
            
            pygame.draw.rect(self.screen, (0, 0, 150), (SCREEN_WIDTH//2 - 100, 350, 200, 40))
            btn_txt = self.mid_font.render("ZATWIERDZ", True, WHITE)
            self.screen.blit(btn_txt, (SCREEN_WIDTH//2 - btn_txt.get_width()//2, 355))
            
        elif self.state == "PLAYING" or self.state == "LEVEL_TRANSITION":
            self.draw_game_elements()

        elif self.state == "GAME_OVER":
            title = self.big_font.render("GAME OVER", True, RED)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
            header = self.mid_font.render("TOP 3 SCORES", True, YELLOW)
            self.screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, 160))
            y = 220
            for idx, entry in enumerate(self.high_scores):
                txt = self.font.render(f"{idx+1}. {entry['nick']} - {entry['score']}", True, WHITE)
                self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, y))
                y += 40
            
            pygame.draw.rect(self.screen, (0, 0, 150), (SCREEN_WIDTH//2 - 100, 550, 200, 50))
            btn1 = self.mid_font.render("ZAGRAJ ZNOWU", True, WHITE)
            self.screen.blit(btn1, (SCREEN_WIDTH//2 - btn1.get_width()//2, 560))
            
            pygame.draw.rect(self.screen, (0, 0, 150), (SCREEN_WIDTH//2 - 100, 610, 200, 50))
            btn2 = self.mid_font.render("WYJSCIE", True, WHITE)
            self.screen.blit(btn2, (SCREEN_WIDTH//2 - btn2.get_width()//2, 620))

        pygame.display.flip()

    def draw_game_elements(self, draw_player=True):
        for wall in self.walls:
            pygame.draw.rect(self.screen, self.flash_color if self.state == "LEVEL_TRANSITION" else BLUE_WALL, wall, 1)
        
        if self.door_rect:
            pygame.draw.rect(self.screen, PINK_DOOR, self.door_rect)

        for dot in self.dots:
            if dot['type'] == 'small':
                pygame.draw.rect(self.screen, (255, 183, 174), dot['rect'])
            else:
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    pygame.draw.circle(self.screen, (255, 183, 174), dot['rect'].center, 8)

        if self.fruit:
            idx = self.fruit['type']
            if idx < len(self.fruit_sprites):
                self.screen.blit(self.fruit_sprites[idx], self.fruit['rect'])

        if draw_player:
            self.player.draw(self.screen)
            
        for ghost in self.ghosts: ghost.draw(self.screen)
        
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(score_text, (10, 5))
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, 5))
        
        if self.pacman_frames:
            life_icon = self.pacman_frames[1] 
            for i in range(self.lives):
                self.screen.blit(life_icon, (10 + i * 35, SCREEN_HEIGHT - 35))

class Pacman:
    def __init__(self, game, col, row):
        self.game = game
        self.start_pos = [col * TILE_SIZE, row * TILE_SIZE]
        self.reset_position()
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.speed = 3
        self.frame_index = 0
        self.anim_timer = 0

    def reset_position(self):
        self.pixel_pos = self.start_pos[:]
        self.grid_pos = (self.start_pos[0]//TILE_SIZE, self.start_pos[1]//TILE_SIZE)
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def update(self, walls):
        if self.can_move(self.next_direction, walls):
            if (self.pixel_pos[0] % TILE_SIZE == 0) and (self.pixel_pos[1] % TILE_SIZE == 0):
                self.direction = self.next_direction

        if self.can_move(self.direction, walls):
            self.pixel_pos[0] += self.direction[0] * self.speed
            self.pixel_pos[1] += self.direction[1] * self.speed
        
        if self.pixel_pos[0] < -TILE_SIZE: 
            self.pixel_pos[0] = SCREEN_WIDTH
        elif self.pixel_pos[0] > SCREEN_WIDTH: 
            self.pixel_pos[0] = -TILE_SIZE
        
        self.grid_pos = (int((self.pixel_pos[0] + TILE_SIZE//2) // TILE_SIZE),
                         int((self.pixel_pos[1] + TILE_SIZE//2) // TILE_SIZE))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.next_direction = (-1, 0)
        if keys[pygame.K_RIGHT]: self.next_direction = (1, 0)
        if keys[pygame.K_UP]: self.next_direction = (0, -1)
        if keys[pygame.K_DOWN]: self.next_direction = (0, 1)

    def can_move(self, vec, walls):
        future_rect = pygame.Rect(self.pixel_pos[0] + vec[0]*self.speed, 
                                  self.pixel_pos[1] + vec[1]*self.speed, TILE_SIZE, TILE_SIZE)
        
        for wall in walls:
            if future_rect.colliderect(wall): return False
        
        return True

    def draw(self, screen):
        if not self.game.start_music_played:
            screen.blit(self.game.pacman_frames[0], self.pixel_pos)
            return

        if self.direction != (0, 0):
            if pygame.time.get_ticks() - self.anim_timer > 80:
                self.frame_index = (self.frame_index + 1) % 2
                self.anim_timer = pygame.time.get_ticks()
        else:
            self.frame_index = 0
            
        base_idx = 0
        if self.direction == (1, 0): base_idx = 1
        elif self.direction == (-1, 0): base_idx = 7
        elif self.direction == (0, -1): base_idx = 10
        elif self.direction == (0, 1): base_idx = 4
        else: base_idx = 1

        final_idx = base_idx + self.frame_index
        screen.blit(self.game.pacman_frames[final_idx], self.pixel_pos)

class Ghost:
    def __init__(self, game, color, col, row):
        self.game = game
        self.color = color
        self.start_pos = [col * TILE_SIZE, row * TILE_SIZE]
        self.pixel_pos = self.start_pos[:]
        self.grid_pos = (col, row)
        self.direction = (0, -1)
        self.speed = 3
        self.mode = "normal"
        self.last_eye_frame = None
        self.visual_direction = (0, -1)

    def reset_pos(self):
        self.pixel_pos = self.start_pos[:]
        self.grid_pos = (self.start_pos[0]//TILE_SIZE, self.start_pos[1]//TILE_SIZE)
        self.mode = "normal"
        self.last_eye_frame = self.game.eyes_right
        self.direction = (0, -1)
        self.visual_direction = (0, -1)

    def reverse_direction(self):
        self.direction = (-self.direction[0], -self.direction[1])

    def update(self, player, walls):
        target_speed = self.speed
        if self.mode == 'frightened': target_speed = 2
        if self.mode == 'dead': target_speed = 5

        move_amount = target_speed
        
        rem_x = self.pixel_pos[0] % TILE_SIZE
        rem_y = self.pixel_pos[1] % TILE_SIZE
        
        dist_to_center = 0
        if self.direction == (1, 0): dist_to_center = (TILE_SIZE - rem_x) if rem_x != 0 else 0
        elif self.direction == (-1, 0): dist_to_center = rem_x if rem_x != 0 else 0
        elif self.direction == (0, 1): dist_to_center = (TILE_SIZE - rem_y) if rem_y != 0 else 0
        elif self.direction == (0, -1): dist_to_center = rem_y if rem_y != 0 else 0
        
        if dist_to_center > 0 and move_amount >= dist_to_center:
            self.pixel_pos[0] += self.direction[0] * dist_to_center
            self.pixel_pos[1] += self.direction[1] * dist_to_center
            move_amount -= dist_to_center
            
            self.grid_pos = (int(self.pixel_pos[0] // TILE_SIZE), int(self.pixel_pos[1] // TILE_SIZE))
            
            if self.mode == 'dead':
                self.calculate_dead_move()
            else:
                self.choose_direction(player)
                
        self.pixel_pos[0] += self.direction[0] * move_amount
        self.pixel_pos[1] += self.direction[1] * move_amount
        
        if self.pixel_pos[0] < -TILE_SIZE: self.pixel_pos[0] = SCREEN_WIDTH
        elif self.pixel_pos[0] > SCREEN_WIDTH: self.pixel_pos[0] = -TILE_SIZE
        
        self.grid_pos = (int((self.pixel_pos[0] + TILE_SIZE//2) // TILE_SIZE),
                         int((self.pixel_pos[1] + TILE_SIZE//2) // TILE_SIZE))

    def calculate_dead_move(self):
        target = (9, 7)
        if self.grid_pos == target:
            self.direction = (0, 1)
        elif self.grid_pos == (9, 8):
            self.mode = 'normal'
            self.direction = (0, -1)
            self.pixel_pos = [self.grid_pos[0]*TILE_SIZE, self.grid_pos[1]*TILE_SIZE]
            return
        else:
            next_step = self.bfs_next_step(self.grid_pos, target)
            if next_step:
                self.direction = (next_step[0] - self.grid_pos[0], next_step[1] - self.grid_pos[1])

    def bfs_next_step(self, start, target):
        queue = deque([(start, [])])
        visited = set([start])
        while queue:
            current, path = queue.popleft()
            if current == target:
                return path[0] if path else None
            x, y = current
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            for nx, ny in neighbors:
                if 0 <= ny < len(LAYOUT) and 0 <= nx < len(LAYOUT[0]):
                    tile = LAYOUT[ny][nx]
                    if tile != '0' and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        new_path = list(path)
                        new_path.append((nx, ny))
                        queue.append(((nx, ny), new_path))
        return None

    def choose_direction(self, player):
        options = []
        possible = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        if (self.grid_pos in self.game.house_tiles) and self.mode == 'normal':
             self.direction = (0, -1)
             return

        for d in possible:
            if d[0] == -self.direction[0] and d[1] == -self.direction[1]: continue
            
            nx, ny = self.grid_pos[0] + d[0], self.grid_pos[1] + d[1]
            if 0 <= ny < len(LAYOUT) and 0 <= nx < len(LAYOUT[0]):
                tile = LAYOUT[ny][nx]
                if tile == '0': continue
                if tile == '9': 
                    if not (self.grid_pos in self.game.house_tiles): continue 
                options.append(d)

        if not options: 
            self.direction = (-self.direction[0], -self.direction[1])
            return

        if self.mode == 'frightened':
            self.direction = random.choice(options)
            return

        target = player.grid_pos
        if self.game.scatter_mode:
            if self.color == 'red': target = (len(LAYOUT[0])-2, 1)
            elif self.color == 'pink': target = (1, 1)
            elif self.color == 'cyan': target = (len(LAYOUT[0])-2, len(LAYOUT)-2)
            else: target = (1, len(LAYOUT)-2)
        
        best_dir = options[0]
        min_dist = float('inf')
        for opt in options:
            nx, ny = self.grid_pos[0] + opt[0], self.grid_pos[1] + opt[1]
            dist = math.hypot(nx - target[0], ny - target[1])
            if dist < min_dist:
                min_dist = dist
                best_dir = opt
        self.direction = best_dir

    def draw(self, screen):
        if not hasattr(self, "visual_direction"):
            self.visual_direction = self.direction

        if self.pixel_pos[0] % TILE_SIZE == 0 and self.pixel_pos[1] % TILE_SIZE == 0:
            self.visual_direction = self.direction

        if self.mode == 'dead':
            dx, dy = self.visual_direction
            if dx > 0:
                self.last_eye_frame = self.game.eyes_right
            elif dx < 0:
                self.last_eye_frame = self.game.eyes_left
            
            if self.last_eye_frame is None:
                self.last_eye_frame = self.game.eyes_right
                
            screen.blit(self.last_eye_frame, self.pixel_pos)
            return

        if self.mode == 'frightened':
            idx = 0
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                idx = 1
            if self.game.frightened_end_time - pygame.time.get_ticks() < 2000:
                if (pygame.time.get_ticks() // 150) % 2 == 0:
                    idx += 2
            screen.blit(self.game.frightened_sprites[idx], self.pixel_pos)
            return

        anim_offset = 1 if (pygame.time.get_ticks() // 150) % 2 == 0 else 0

        dx, dy = self.visual_direction

        if dx > 0:
            dir_key = 'right'
        elif dx < 0:
            dir_key = 'left'
        elif dy < 0:
            dir_key = 'up'
        else:
            dir_key = 'down'

        frame = self.game.ghost_sprites[self.color][dir_key][anim_offset]
        screen.blit(frame, self.pixel_pos)

if __name__ == '__main__':
    game = Game()
    game.run()