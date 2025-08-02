import pgzrun
import math
from pygame import Rect

WIDTH = 1200 
HEIGHT = 800 
TITLE = "SetorZero: The Game"
SUBTITLE = "Desenvolvedor: Vinícius Lima"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GOLD = (255, 215, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)

GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_LEVEL_COMPLETE = 2
GAME_STATE_GAME_OVER = 3

ANIMATION_SPEED = 0.1 

class AnimatedSprite:
    def __init__(self, x_position, y_position, sprite_prefix, num_idle_right_frames, num_idle_left_frames, 
                 num_run_right_frames, num_run_left_frames, num_jump_right_frames=0, num_jump_left_frames=0):
        self.x_position = x_position
        self.y_position = y_position
        self.sprite_prefix = sprite_prefix
        
        self.idle_frames_right = [f"sprites/idle/{sprite_prefix}_idle_right_{i}" for i in range(1, num_idle_right_frames + 1)]
        self.idle_frames_left = [f"sprites/idle/{sprite_prefix}_idle_left_{i}" for i in range(1, num_idle_left_frames + 1)]
        
        if not self.idle_frames_left:
            self.idle_frames_left = [f"sprites/idle/{sprite_prefix}_idle_right_{i}" for i in range(1, num_idle_right_frames + 1)]
            self.use_flip_for_idle_left = True
        else:
            self.use_flip_for_idle_left = False

        self.run_frames_right = [f"sprites/run/{sprite_prefix}_run_right_{i}" for i in range(1, num_run_right_frames + 1)]
        self.run_frames_left = [f"sprites/run/{sprite_prefix}_run_left_{i}" for i in range(1, num_run_left_frames + 1)]
        
        if not self.run_frames_left:
            self.run_frames_left = [f"sprites/run/{sprite_prefix}_run_right_{i}" for i in range(1, num_run_right_frames + 1)]
            self.use_flip_for_run_left = True
        else:
            self.use_flip_for_run_left = False

        self.jump_frames_right = [f"sprites/jump/{sprite_prefix}_jump_right_{i}" for i in range(1, num_jump_right_frames + 1)]
        self.jump_frames_left = [f"sprites/jump/{sprite_prefix}_jump_left_{i}" for i in range(1, num_jump_left_frames + 1)]

        if not self.jump_frames_left:
            self.jump_frames_left = [f"sprites/jump/{sprite_prefix}_jump_right_{i}" for i in range(1, num_jump_right_frames + 1)]
            self.use_flip_for_jump_left = True
        else:
            self.use_flip_for_jump_left = False

        self.is_jumping = False 

        self.current_frame = 0
        self.animation_timer = 0
        self.is_moving = False
        self.facing_right = True

        self.image = self.idle_frames_right[0]
        self.actor = Actor(self.image, (self.x_position, self.y_position))

    def update_animation(self, frame_time):
        self.animation_timer += frame_time
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_timer = 0
        
            if self.is_jumping: 
                if self.facing_right:
                    if self.jump_frames_right:
                        self.current_frame = (self.current_frame + 1) % len(self.jump_frames_right)
                        self.image = self.jump_frames_right[self.current_frame]
                    else:
                        self.image = self.idle_frames_right[0] 
                else: 
                    if self.jump_frames_left:
                        self.current_frame = (self.current_frame + 1) % len(self.jump_frames_left)
                        self.image = self.jump_frames_left[self.current_frame]
                    else: 
                        self.image = self.idle_frames_left[0]
            elif self.is_moving:
                if self.facing_right:
                    self.current_frame = (self.current_frame + 1) % len(self.run_frames_right)
                    self.image = self.run_frames_right[self.current_frame]
                else: 
                    self.current_frame = (self.current_frame + 1) % len(self.run_frames_left)
                    self.image = self.run_frames_left[self.current_frame]
            else: 
                if self.facing_right:
                    self.current_frame = (self.current_frame + 1) % len(self.idle_frames_right)
                    self.image = self.idle_frames_right[self.current_frame]
                else:
                    self.current_frame = (self.current_frame + 1) % len(self.idle_frames_left)
                    self.image = self.idle_frames_left[self.current_frame]
            self.actor.image = self.image

    def draw(self):
        flip_needed = False
        if not self.facing_right:
            if self.is_jumping and self.use_flip_for_jump_left:
                flip_needed = True
            elif self.is_moving and self.use_flip_for_run_left:
                flip_needed = True
            elif not self.is_moving and self.use_flip_for_idle_left:
                flip_needed = True
        
        self.actor.flip_x = flip_needed
        self.actor.draw()

class Player(AnimatedSprite):
    def __init__(self, x_position, y_position):
        super().__init__(x_position, y_position, "player", 
                         num_idle_right_frames=2, num_idle_left_frames=2, 
                         num_run_right_frames=4, num_run_left_frames=4, 
                         num_jump_right_frames=1, num_jump_left_frames=1)
        self.speed = 200
        self.jump_strength = -450
        self.gravity = 800
        self.velocity_y = 0
        self.on_ground = False
        self.actor.pos = (self.x_position, self.y_position)
        self.have_key = False
        self.score = 0 
        
        self.invulnerable = False
        self.invulnerability_duration = 5.0
        self.actor.image_alpha = 255

    def update(self, frame_time, platforms):
        self.is_moving = False
        self.is_jumping = not self.on_ground 
                
        if keyboard.left or keyboard.a:
            self.x_position -= self.speed * frame_time
            self.is_moving = True
            self.facing_right = False
        if keyboard.right or keyboard.d:
            self.x_position += self.speed * frame_time
            self.is_moving = True
            self.facing_right = True

        self.velocity_y += self.gravity * frame_time
        self.y_position += self.velocity_y * frame_time

        self.on_ground = False
        for platform in platforms:
            if self.actor.colliderect(platform.actor):
                if self.velocity_y > 0 and self.actor.bottom <= platform.actor.bottom:
                    self.y_position = platform.actor.top - self.actor.height / 2
                    self.velocity_y = 0
                    self.on_ground = True
                    self.is_jumping = False

        if (keyboard.space or keyboard.w) and self.on_ground:
            self.velocity_y = self.jump_strength
            self.is_jumping = True 

        if self.x_position < self.actor.width / 2:
            self.x_position = self.actor.width / 2
        if self.x_position > WIDTH - self.actor.width / 2:
            self.x_position = WIDTH - self.actor.width / 2
        
        self.actor.pos = (self.x_position, self.y_position)
        self.update_animation(frame_time)

class Enemy(AnimatedSprite):
    def __init__(self, x, y, patrol_range_x_min, patrol_range_x_max):
        super().__init__(x, y, "enemy", 
                         num_idle_right_frames=2, num_idle_left_frames=2, 
                         num_run_right_frames=2, num_run_left_frames=2, 
                         num_jump_right_frames=0, num_jump_left_frames=0)
        self.speed = 80
        self.chase_speed = 100 
        self.patrol_range_x_min = patrol_range_x_min
        self.patrol_range_x_max = patrol_range_x_max
        self.moving_to_max = True
        self.actor.pos = (self.x_position, self.y_position)
        self.is_moving = True 
        self.detection_range = 150
        self.gravity = 800 
        self.velocity_y = 0
        self.on_ground = False

    def update(self, frame_time, player, platforms):
        self.is_jumping = not self.on_ground

        self.velocity_y += self.gravity * frame_time
        self.y_position += self.velocity_y * frame_time

        self.on_ground = False
        for platform in platforms:
            if self.actor.colliderect(platform.actor):
                if self.velocity_y > 0 and self.actor.bottom <= platform.actor.bottom:
                    self.y_position = platform.actor.top - self.actor.height / 2
                    self.velocity_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.velocity_y < 0 and self.actor.top >= platform.actor.top:
                    self.y_position = platform.actor.bottom + self.actor.height / 2
                    self.velocity_y = 0
                    self.is_jumping = False

        dx = player.x_position - self.x_position
        distance = math.sqrt(dx*dx + (player.y_position - self.y_position)*(player.y_position - self.y_position))

        if distance < self.detection_range:
            self.is_moving = True
            if dx > 0:
                self.x_position += self.chase_speed * frame_time
                self.facing_right = True
            elif dx < 0:
                self.x_position -= self.chase_speed * frame_time
                self.facing_right = False
        else:
            self.is_moving = True
            if self.moving_to_max:
                self.x_position += self.speed * frame_time
                self.facing_right = True
                if self.x_position >= self.patrol_range_x_max:
                    self.x_position = self.patrol_range_x_max
                    self.moving_to_max = False
            else:
                self.x_position -= self.speed * frame_time
                self.facing_right = False
                if self.x_position <= self.patrol_range_x_min:
                    self.x_position = self.patrol_range_x_min
                    self.moving_to_max = True

        self.actor.pos = (self.x_position, self.y_position)
        self.update_animation(frame_time)

class Platform:
    def __init__(self, x_position, y_position, image_name="platform"):
        self.x_position = x_position
        self.y_position = y_position
        self.actor = Actor(image_name, (self.x_position, self.y_position)) 

    def draw(self):
        self.actor.draw()

class Coin:
    def __init__(self, x_position, y_position):
        self.x_position = x_position
        self.y_position = y_position
        self.actor = Actor("coin", (self.x_position, self.y_position))

    def draw(self):
        self.actor.draw()

class Key:
    def __init__(self, x_position, y_position):
        self.x_position = x_position
        self.y_position = y_position
        self.actor = Actor("key", (self.x_position, self.y_position))
        self.collected = False

    def draw(self):
        if not self.collected:
            self.actor.draw()

class Door:
    def __init__(self, x_position, y_position):
        self.x_position = x_position
        self.y_position = y_position
        self.actor = Actor("door_closed", (self.x_position, self.y_position))
        self.is_open = False

    def open_door(self):
        self.is_open = True
        self.actor.image = "door_open"
        sounds.door_open_sound.play()

    def draw(self):
        self.actor.draw()

class Button:
    def __init__(self, x, y, image_name, callback):
        self.actor = Actor(image_name, (x, y))
        self.callback = callback

    def draw(self):
        self.actor.draw()

    def on_mouse_down(self, pos):
        if self.actor.collidepoint(pos):
            self.callback()
            return True
        return False

class Game:
    def __init__(self):
        self.game_state = GAME_STATE_MENU
        self.player = None
        self.enemies = []
        self.platforms = []
        self.coins = []
        self.key = None
        self.door = None
        self.music_on = True
        self.menu_buttons = []
        self.total_lives = 3
        
        self._setup_menu()
        self._load_music_and_sounds()
        music.unpause()

    def _setup_menu(self):
        self.menu_buttons.append(Button(WIDTH / 2, HEIGHT / 2 - 30, "menu/button_start", self.start_game))
        self.music_button = Button(WIDTH / 2, HEIGHT / 2 + 30, "menu/button_music_on", self.toggle_music)
        self.menu_buttons.append(self.music_button)
        self.menu_buttons.append(Button(WIDTH / 2, HEIGHT / 2 + 90, "menu/button_exit", self.exit_game))

    def _load_music_and_sounds(self):
        music.play("background_music")
        music.set_volume(0.5)

    def start_game(self):
        self.total_lives = 3 
        self._load_level(1)
        self.game_state = GAME_STATE_PLAYING
        if self.music_on:
            music.unpause()

    def _load_level(self, level_number):
        if self.player: 
            self.player.x_position, self.player.y_position = 100, HEIGHT - 100
            self.player.velocity_y = 0
            self.player.have_key = False 
            self.player.on_ground = False 
            self.player.is_jumping = False
            self.player.invulnerable = False 
        else: 
            self.player = Player(100, HEIGHT - 100)
            
        self.enemies = []
        self.platforms = []
        self.coins = []
        self.key = None
        self.door = None
        self.show_door_message = False 

        PLATFORM_ONE_BLOCK_WIDTH = 192
        PLATFORM_ONE_BLOCK_HEIGHT = 64

        ENEMY_SPRITE_HEIGHT = 54 

        PLATFORM_TWO_BLOCK_WIDTH = 192 
        PLATFORM_TWO_BLOCK_HEIGHT = 37 

        if level_number == 1:
            ground_y = HEIGHT - (PLATFORM_ONE_BLOCK_HEIGHT / 2) 
            second_floor_y = HEIGHT - 150 - (PLATFORM_TWO_BLOCK_HEIGHT / 2)
            third_floor_y = HEIGHT - 280 - (PLATFORM_TWO_BLOCK_HEIGHT / 2) 
            fourth_floor_y = HEIGHT - 400 - (PLATFORM_TWO_BLOCK_HEIGHT / 2)
            fifth_floor_y = HEIGHT - 520 - (PLATFORM_TWO_BLOCK_HEIGHT / 2)    
            sixth_floor_y = HEIGHT - 640 - (PLATFORM_TWO_BLOCK_HEIGHT / 2) 
            
            current_x_pos = PLATFORM_ONE_BLOCK_WIDTH / 2 
            self.platforms.append(Platform(current_x_pos, ground_y, "tilesets/platform"))
            current_x_pos += PLATFORM_ONE_BLOCK_WIDTH 
            self.platforms.append(Platform(current_x_pos, ground_y, "tilesets/platform"))
            current_x_pos += (PLATFORM_ONE_BLOCK_WIDTH * 2) 
            self.platforms.append(Platform(current_x_pos, ground_y, "tilesets/platform"))
            current_x_pos += PLATFORM_ONE_BLOCK_WIDTH 
            self.platforms.append(Platform(current_x_pos, ground_y, "tilesets/platform"))
            current_x_pos += PLATFORM_ONE_BLOCK_WIDTH 
            self.platforms.append(Platform(current_x_pos, ground_y, "tilesets/platform"))

            while current_x_pos + (PLATFORM_ONE_BLOCK_WIDTH / 2) < WIDTH:
                 current_x_pos += PLATFORM_ONE_BLOCK_WIDTH
                 if current_x_pos - (PLATFORM_ONE_BLOCK_WIDTH / 2) < WIDTH:
                     self.platforms.append(Platform(current_x_pos, ground_y, "tilesets/platform"))
                 else:
                     self.platforms.append(Platform(WIDTH - (PLATFORM_ONE_BLOCK_WIDTH / 2), ground_y, "tilesets/platform"))
                     break

            second_floor_current_x = PLATFORM_TWO_BLOCK_WIDTH / 2 + 50 
            self.platforms.append(Platform(second_floor_current_x, second_floor_y, "tilesets/platform_two"))
            second_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(second_floor_current_x, second_floor_y, "tilesets/platform_two"))
            second_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH 
            self.platforms.append(Platform(second_floor_current_x, second_floor_y, "tilesets/platform_two"))
            second_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(second_floor_current_x, second_floor_y, "tilesets/platform_two"))
            second_floor_current_x += (PLATFORM_TWO_BLOCK_WIDTH * 2) 
            self.platforms.append(Platform(second_floor_current_x, second_floor_y, "tilesets/platform_two"))
            second_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(second_floor_current_x, second_floor_y, "tilesets/platform_two"))

            third_floor_current_x = WIDTH / 2 - PLATFORM_TWO_BLOCK_WIDTH - (PLATFORM_TWO_BLOCK_WIDTH / 2) 
            self.platforms.append(Platform(third_floor_current_x, third_floor_y, "tilesets/platform_two"))
            third_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(third_floor_current_x, third_floor_y, "tilesets/platform_two"))
            third_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH 
            self.platforms.append(Platform(third_floor_current_x, third_floor_y, "tilesets/platform_two"))
            third_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(third_floor_current_x, third_floor_y, "tilesets/platform_two"))
            third_floor_current_x += (PLATFORM_TWO_BLOCK_WIDTH * 2) 
            self.platforms.append(Platform(third_floor_current_x, third_floor_y, "tilesets/platform_two"))
            third_floor_current_x = WIDTH - (PLATFORM_TWO_BLOCK_WIDTH / 2) - 50 
            self.platforms.append(Platform(third_floor_current_x, third_floor_y, "tilesets/platform_two"))

            fourth_floor_current_x = PLATFORM_TWO_BLOCK_WIDTH / 2 + 150 
            self.platforms.append(Platform(fourth_floor_current_x, fourth_floor_y, "tilesets/platform_two"))
            fourth_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(fourth_floor_current_x, fourth_floor_y, "tilesets/platform_two"))
            fourth_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH 
            self.platforms.append(Platform(fourth_floor_current_x, fourth_floor_y, "tilesets/platform_two"))
            fourth_floor_current_x = WIDTH - (PLATFORM_TWO_BLOCK_WIDTH / 2) - 150
            self.platforms.append(Platform(fourth_floor_current_x, fourth_floor_y, "tilesets/platform_two"))
                                 
            fifth_floor_current_x = PLATFORM_TWO_BLOCK_WIDTH / 2 + 200 
            self.platforms.append(Platform(fifth_floor_current_x, fifth_floor_y, "tilesets/platform_two"))
            fifth_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(fifth_floor_current_x, fifth_floor_y, "tilesets/platform_two"))
            fifth_floor_current_x = WIDTH / 1.77
            self.platforms.append(Platform(fifth_floor_current_x, fifth_floor_y, "tilesets/platform_two"))
            fifth_floor_current_x = WIDTH - (PLATFORM_TWO_BLOCK_WIDTH / 2) - 50 
            self.platforms.append(Platform(fifth_floor_current_x, fifth_floor_y, "tilesets/platform_two"))
 
            sixth_floor_current_x = WIDTH / 2 - (PLATFORM_TWO_BLOCK_WIDTH / 2) - 100 
            self.platforms.append(Platform(sixth_floor_current_x, sixth_floor_y, "tilesets/platform_two"))
            sixth_floor_current_x += PLATFORM_TWO_BLOCK_WIDTH
            self.platforms.append(Platform(sixth_floor_current_x, sixth_floor_y, "tilesets/platform_two"))
            sixth_floor_current_x += (PLATFORM_TWO_BLOCK_WIDTH * 2) 
            self.platforms.append(Platform(sixth_floor_current_x, sixth_floor_y, "tilesets/platform_two"))
            sixth_floor_current_x = 15
            self.platforms.append(Platform(sixth_floor_current_x, sixth_floor_y, "tilesets/platform_two"))

            self.coins.append(Coin(35, 90))
            self.coins.append(Coin(560, 90))
            self.coins.append(Coin(400, 210))
            self.coins.append(Coin(1000, 330))
            self.coins.append(Coin(340, 450))
            self.coins.append(Coin(500, 580))
            self.coins.append(Coin(1100, 700))

            enemy2_x = 800
            enemy2_min_x = enemy2_x - PLATFORM_ONE_BLOCK_WIDTH / 2
            enemy2_max_x = enemy2_x + PLATFORM_ONE_BLOCK_WIDTH / 2
            self.enemies.append(Enemy(enemy2_x, ground_y + PLATFORM_ONE_BLOCK_HEIGHT / 3 - ENEMY_SPRITE_HEIGHT / 2, enemy2_min_x, enemy2_max_x))

            enemy3_x = 300 
            enemy3_min_x = enemy3_x - PLATFORM_TWO_BLOCK_WIDTH / 2
            enemy3_max_x = enemy3_x + PLATFORM_TWO_BLOCK_WIDTH / 2
            self.enemies.append(Enemy(enemy3_x, second_floor_y + PLATFORM_TWO_BLOCK_HEIGHT / 3 - ENEMY_SPRITE_HEIGHT / 2, enemy3_min_x, enemy3_max_x))

            enemy4_x = 700
            enemy4_min_x = enemy4_x - PLATFORM_TWO_BLOCK_WIDTH / 2
            enemy4_max_x = enemy4_x + PLATFORM_TWO_BLOCK_WIDTH / 2
            self.enemies.append(Enemy(enemy4_x, third_floor_y + PLATFORM_TWO_BLOCK_HEIGHT / 3 - ENEMY_SPRITE_HEIGHT / 2, enemy4_min_x, enemy4_max_x))

            enemy5_x = 450
            enemy5_min_x = enemy5_x - PLATFORM_TWO_BLOCK_WIDTH / 2
            enemy5_max_x = enemy5_x + PLATFORM_TWO_BLOCK_WIDTH / 2
            self.enemies.append(Enemy(enemy5_x, fourth_floor_y + PLATFORM_TWO_BLOCK_HEIGHT / 3 - ENEMY_SPRITE_HEIGHT / 2, enemy5_min_x, enemy5_max_x))
            
            enemy6_x = 500
            enemy6_min_x = enemy6_x - PLATFORM_TWO_BLOCK_WIDTH / 2
            enemy6_max_x = enemy6_x + PLATFORM_TWO_BLOCK_WIDTH / 2
            self.enemies.append(Enemy(enemy6_x, sixth_floor_y + PLATFORM_TWO_BLOCK_HEIGHT / 3 - ENEMY_SPRITE_HEIGHT / 2, enemy6_min_x, enemy6_max_x))

            self.key = Key(WIDTH - 220, HEIGHT - 710) 
            self.door = Door(WIDTH - 280, HEIGHT - 120) 

            self.level_complete()

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            music.unpause()
            self.music_button.actor.image = "menu/button_music_on"
        else:
            music.pause()
            self.music_button.actor.image = "menu/button_music_off"

    def exit_game(self):
        exit()

    def lose_life(self):
        if not self.player.invulnerable: 
            self.total_lives -= 1 
            sounds.hit_sound.play() 
            self.player.invulnerable = True
            clock.schedule_unique(self._reset_invulnerability, self.player.invulnerability_duration)

            if self.total_lives <= 0:
                self.game_over()

    def _reset_invulnerability(self):
        if self.player:
            self.player.invulnerable = False
            self.player.actor.image_alpha = 255

    def level_complete(self):
        self.game_state = GAME_STATE_LEVEL_COMPLETE
        sounds.level_up_sound.play()
        music.pause() 

    def game_over(self):
        self.game_state = GAME_STATE_GAME_OVER
        sounds.game_over_sound.play()
        music.pause()

    def update(self, frame_time):
        if self.game_state == GAME_STATE_PLAYING:

            self.player.update(frame_time, self.platforms)
            
            for enemy in self.enemies:
                enemy.update(frame_time, self.player, self.platforms)
                if self.player.actor.colliderect(enemy.actor) and not self.player.invulnerable:
                    self.lose_life()

            if self.player.y_position > HEIGHT + 100 and not self.player.invulnerable:
                self.lose_life()
                if self.game_state == GAME_STATE_PLAYING: 
                    self.player.x_position, self.player.y_position = 100, HEIGHT - 100
                    self.player.velocity_y = 0
                    self.player.is_jumping = False
                    self.player.on_ground = False
                    self.player.have_key = False

            coins_to_remove = []
            for coin in self.coins:
                if self.player.actor.colliderect(coin.actor):
                    sounds.coin_sound.play()
                    self.player.score += 10
                    coins_to_remove.append(coin)
            for coin in coins_to_remove:
                self.coins.remove(coin)

            if not self.key.collected and self.player.actor.colliderect(self.key.actor):
                self.key.collected = True
                self.player.have_key = True
                sounds.key_sound.play()

            self.show_door_message = False 
            if self.player.actor.colliderect(self.door.actor):
                self.show_door_message = True 
                
                if keyboard.f:
                    if not self.door.is_open:
                        if self.player.have_key: 
                            self.door.open_door()
                            self.level_complete()
                            
    def draw(self):
        screen.clear()
        screen.fill(BLACK) 

        if self.game_state == GAME_STATE_MENU:
            screen.draw.text(TITLE, center=(WIDTH / 2, HEIGHT / 2 - 160), color=BLUE, fontsize=60)
            screen.draw.text(SUBTITLE, center=(WIDTH / 2, HEIGHT / 2 - 120), color=WHITE, fontsize=30)
            for button in self.menu_buttons:
                button.draw()
        elif self.game_state == GAME_STATE_PLAYING:
            for platform in self.platforms:
                platform.draw()
            for coin in self.coins:
                coin.draw()
            self.key.draw()
            self.door.draw()
            for enemy in self.enemies:
                enemy.draw()

            self.player.draw()
            screen.draw.text(f"Moedas: {self.player.score}", topleft=(10, 10), color=GOLD, fontsize=30)
            screen.draw.text(f"Chave: {'SIM' if self.player.have_key else 'NÃO'}", topleft=(10, 40), color=BLUE, fontsize=30)
            screen.draw.text(f"Vidas: {self.total_lives}", topleft=(10, 70), color=RED, fontsize=30)

            if self.show_door_message:
                message = "Pressione F para abrir a porta!"
                screen.draw.text(message, center=(WIDTH - 280, HEIGHT - 120), color=YELLOW, fontsize=40)

        elif self.game_state == GAME_STATE_LEVEL_COMPLETE:
            screen.draw.text("VOCÊ VENCEU O JOGO!", center=(WIDTH / 2, HEIGHT / 2 - 100), color=GREEN, fontsize=80)
            screen.draw.text(f"Pontuação Final: {self.player.score}", center=(WIDTH / 2, HEIGHT / 2), color=GOLD, fontsize=50)
            screen.draw.text(f"Vidas Restantes: {self.total_lives}", center=(WIDTH / 2, HEIGHT / 2 + 60), color=RED, fontsize=40)
            
            screen.draw.text("Pressione ESPAÇO para continuar", center=(WIDTH / 2, HEIGHT - 100), color=GRAY, fontsize=30)
        
        elif self.game_state == GAME_STATE_GAME_OVER:
            screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2 - 50), color=RED, fontsize=70)
            screen.draw.text(f"Sua Pontuação: {self.player.score}", center=(WIDTH / 2, HEIGHT / 2 + 10), color=GOLD, fontsize=40)
            screen.draw.text("Pressione ESPAÇO para tentar novamente", center=(WIDTH / 2, HEIGHT / 2 + 80), color=GRAY, fontsize=30)

    def on_mouse_down(self, pos):
        if self.game_state == GAME_STATE_MENU:
            for button in self.menu_buttons:
                if button.on_mouse_down(pos):
                    break

    def on_key_down(self, key):
        if self.game_state == GAME_STATE_LEVEL_COMPLETE or self.game_state == GAME_STATE_GAME_OVER:
            if key == keys.SPACE:
                self.game_state = GAME_STATE_MENU
                music.unpause() 

                self.player = None
                self._setup_menu() 
                

game = Game()

def update(frame_time):
    game.update(frame_time)

def draw():
    game.draw()

def on_mouse_down(pos):
    game.on_mouse_down(pos)

def on_key_down(key):
    game.on_key_down(key)

pgzrun.go()