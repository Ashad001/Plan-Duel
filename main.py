import pygame
import os
import time
import random
import sys
from random import choice, randint
from pygame.locals import *

WHITE = (255, 255, 255)

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self,fileName, pos, up_key, down_key, left_key, right_key, shoot_key, speed):
        super().__init__()
        self.image = pygame.image.load(os.path.join('Assets', fileName)).convert_alpha()
        self.rect = self.image.get_rect(midbottom = pos)
        self.up_key = up_key
        self.down_key = down_key
        self.left_key = left_key
        self.right_key = right_key
        self.shoot_key = shoot_key
        self.speed = speed
        self.max_x_constraint = SCREEN_WIDTH
        self.max_y_constraint = SCREEN_HEIGHT
        self.ready = True
        self.bullet_time = 0
        self.bullet_cooldown = 0.5
        self.bullets = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound('laser.wav')
        self.laser_sound.set_volume(0.3)
        
        
    def get_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[self.right_key]:
            self.rect.x += self.speed
        elif keys[self.left_key]:
            self.rect.x -= self.speed
        elif keys[self.up_key]:
            self.rect.y -= self.speed
        elif keys[self.down_key]:
            self.rect.y += self.speed
        
        if keys[self.shoot_key] and self.ready:
            self.shoot_bullet()
            self.laser_sound.play()
            self.ready = False
            self.bullet_time = pygame.time.get_ticks()

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.max_x_constraint:
            self.rect.right = self.max_x_constraint
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.max_y_constraint:
            self.rect.bottom = self.max_y_constraint

        
    def recharge(self):
        if not self.ready:
            curr_time = pygame.time.get_ticks()
            if curr_time - self.bullet_time > self.bullet_cooldown * 1000:
                self.ready = True
            
    def shoot_bullet(self):
        self.bullets.add(Bullet(self.rect.midtop, 8))

    def update(self):
        self.get_input()
        self.recharge()
        self.bullets.update()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, speed = 8):
        super().__init__()
        self.image = pygame.image.load(os.path.join('Assets', 'bullet.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom = pos)
        self.speed = speed
        self.speed = speed
        
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0 and self.rect.top > SCREEN_HEIGHT:
            self.kill()
   
class Blocker(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = (x,y))
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x,y, color):
        super().__init__()
        path = os.path.dirname(__file__)
        filePath = path + '\Assets\enemy' + color + '.png'
        self.image = pygame.image.load(filePath).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x,y))
        if color == 'Red':
            self.value = 3
            self.defence = 5
        elif color == 'Yellow':
            self.value = 2
            self.defence = 3
        else:
            self.value = 1
            self.defence = 1
        
    def update(self, direction):
        self.rect.x += direction




class Mystery(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.image = pygame.image.load(os.path.join('Assets', 'mystery.png')).convert_alpha()
        if side == 'right':
            x = SCREEN_WIDTH + 100
            self.speed = -3
        else:
            x = -50
            self.speed = 3
        self.rect = self.image.get_rect(center = (x, 30))


    def update(self):
        self.rect.x = self.rect.x + self.speed
        


class Game:
    def __init__(self): 
        # Players spread sheet and other things
        player_sprite_red = Player('plane.png', (SCREEN_WIDTH // 4,SCREEN_HEIGHT),  pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE, speed = 5)
        player_sprite_green = Player('plane2.png', (SCREEN_WIDTH // 2, SCREEN_HEIGHT), pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT, speed = 5)
        self.players = pygame.sprite.Group()
        self.players.add(player_sprite_green)
        self.players.add(player_sprite_red)
        self.start = 0
        
        # Making Blocks / Obstacles
        self.shape = BLOCK_SHAPE
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.blocks_amount = 4
        self.block_x_postition = [num for num in range(0, SCREEN_WIDTH, SCREEN_WIDTH // self.blocks_amount)]
        self.create_obstacles(SCREEN_WIDTH / 15, SCREEN_HEIGHT // 1.5, *self.block_x_postition)
        
        # Enemies Setup
        self.enemies = pygame.sprite.Group()
        self.enemy_setup(rows = 6, cols= 8, color = 'Yellow')
        self.enemy_direction = 1
        self.enemy_bullets = pygame.sprite.Group() 
        # Mystery Setup
        self.mystery = pygame.sprite.GroupSingle()
        self.mystery_spawn_time = randint(40,80)
        
        
        # Health powerup and score
        self.lives = 5
        self.lives_surf = pygame.image.load(os.path.join('Assets', 'plane.png')).convert_alpha()
        self.lives_surf = pygame.transform.scale(self.lives_surf, (self.lives_surf.get_size()[0] // 2, self.lives_surf.get_size()[1] // 2))
        self.lives_x_start_pos = SCREEN_WIDTH - (self.lives_surf.get_size()[0] * self.lives + 20)
        self.score = 0
        self.font = pygame.font.Font("space_invaders.ttf", 20)
        
        # Music and Audio
        self.music = pygame.mixer.Sound('music.wav')
        self.music.set_volume(0.2)
        self.music.play(loops=-1)
        self.bullet_sound = pygame.mixer.Sound('shoot.wav')
        self.bullet_sound.set_volume(0.2)
        self.explosion = pygame.mixer.Sound('audio_explosion.wav')
        self.explosion.set_volume(0.3)
        
        self.win = False
        
    def enemy_setup(self,color, rows, cols, x_dist = 80,  y_dist=40, offset_x=80, offset_y=80):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_dist + offset_x
                y = row_index * y_dist + offset_y
                if row_index == 0:
                    enemy_sprite = Enemy(x, y, 'Red')
                elif row_index >= 1 and row_index <= 2:
                    enemy_sprite = Enemy(x, y, 'Yellow')
                else:
                    enemy_sprite = Enemy(x, y, 'Green')
                self.enemies.add(enemy_sprite)

    def create_blocks(self, x_st, y_st, offset):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    self.blocks.add(Blocker(self.block_size, (240, 80, 80), x_st + (col_index * self.block_size) + offset, y_st + (row_index * self.block_size)))
    
    def create_obstacles(self, x_st, y_st, *offsets):
        for x in offsets:
            self.create_blocks(x_st, y_st, x)
    
    def enemy_position(self):
        all_enemies = self.enemies.sprites()
        for enemy in all_enemies:
            if enemy.rect.right >= SCREEN_WIDTH:
                self.enemy_direction = -1 
                self.enemy_movement(0.5)
            elif enemy.rect.left <= 0:
                self.enemy_direction = 1
                # self.enemy_movement(0.5)
            
    def enemy_movement(self, dist):
        if( self.enemies):
            for enemy in self.enemies.sprites():
                enemy.rect.y += dist
    
    def enemy_shoot(self):
        if self.enemies.sprites():
            random_enemy = random.choice(self.enemies.sprites())
            bullet_sprite = Bullet(random_enemy.rect.midbottom, -5)
            self.enemy_bullets.add(bullet_sprite)
            self.bullet_sound.play()
    
    def mystery_spawn(self):
        self.mystery_spawn_time -= 1
        if self.mystery_spawn_time <= 0:
            self.mystery.add(Mystery(choice(['left', 'right'])))
            self.mystery_spawn_time = randint(400,500)   
            
    
    def display_score(self):
        score_surf = self.font.render(f'Score: , {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft = (10,10))
        screen.blit(score_surf, score_rect)
    
    def collision_checks(self):
        # Player bullets
        if self.players:
            all_players = self.players.sprites()
            for player in all_players:
                for bullet in player.bullets.sprites():
                    if pygame.sprite.spritecollide(bullet, self.blocks, True):
                        bullet.kill()    
                    enemy_hit = pygame.sprite.spritecollide(bullet, self.enemies, False)
                    if enemy_hit:
                        for enemy in enemy_hit:
                            if enemy.defence < 1:
                                self.score += enemy.value   
                                self.explosion.play()
                                enemy.kill()
                            enemy.defence -= 1
                        bullet.kill()
                    if pygame.sprite.spritecollide(bullet, self.mystery, True):
                        self.score += 10 
                        self.explosion.play()
                        # self.mystery.kill()a
                        self.win = True
                        self.GAMEOVER()
                        bullet.kill()
        # alien bullets
        if self.enemy_bullets:
            for bullet in self.enemy_bullets:
                if pygame.sprite.spritecollide(bullet, self.blocks, True):
                    bullet.kill()
                if pygame.sprite.spritecollide(bullet, self.players, False):
                    bullet.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.GAMEOVER()
                        sys.exit()
        # aliens
        if self.enemies:
            for enemy in self.enemies:
                pygame.sprite.spritecollide(enemy, self.blocks, True);
                if pygame.sprite.spritecollide(enemy, self.players, False):
                    self.GAMEOVER()
                    sys.exit()
       
    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.lives_x_start_pos + (live * (self.lives_surf.get_size()[0] + 10))
            screen.blit(self.lives_surf, (x , 8))       
    
    def run(self):
        # update all sprite groups 
        if self.start == 1:
            self.enemies.update(self.enemy_direction)
            for player in self.players.sprites():
                player.bullets.draw(screen)
            self.enemy_bullets.update()
            
            
            self.players.update()
            self.enemy_position()
            self.mystery_spawn()
            self.mystery.update()
            
            self.collision_checks()
            
            self.players.draw(screen)
            self.blocks.draw(screen)
            self.enemies.draw(screen)
            self.enemy_bullets.draw(screen)
            self.mystery.draw(screen);
            self.display_score()
            self.display_lives()
        
    def GAMEOVER(self):
        self.bullet_sound.stop()
        self.explosion.stop()
        self.music.stop()

        if self.win == True:
                game_over_sound = pygame.mixer.Sound('game_over.wav')
                game_over_sound.set_volume(2)

                # Play the game over sound
                game_over_sound.play()

                # quit_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                game_over_font = pygame.font.Font("space_invaders.ttf", 64)
                game_over_text = game_over_font.render("You win", True, (255, 255, 255))
                game_over_text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                score_font = pygame.font.Font("space_invaders.ttf", 32)
                score_text = score_font.render("Score: " + str(self.score), True, (255, 255, 255))
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT/2 + 70))
                # Display the game over message and update the screen
                screen.blit(game_over_text, game_over_text_rect)
                screen.blit(score_text, score_rect)
                
                
                pygame.display.update()

                # Wait for 3 seconds before quitting the game
                pygame.time.wait(3000)

                # Quit the game
                pygame.quit()
                sys.exit()

    # Load the game over sound
        else:
                game_over_sound = pygame.mixer.Sound('game_over.wav')
                game_over_sound.set_volume(2)

                # Play the game over sound
                game_over_sound.play()

                # quit_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                game_over_font = pygame.font.Font("space_invaders.ttf", 64)
                game_over_text = game_over_font.render("Game Over", True, (255, 255, 255))
                game_over_text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                score_font = pygame.font.Font("space_invaders.ttf", 32)
                score_text = score_font.render("Score: " + str(self.score), True, (255, 255, 255))
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT/2 + 70))
                # Display the game over message and update the screen
                screen.blit(game_over_text, game_over_text_rect)
                screen.blit(score_text, score_rect)
                
                
                pygame.display.update()

                # Wait for 3 seconds before quitting the game
                pygame.time.wait(3000)

                # Quit the game
                pygame.quit()
                sys.exit()
                
    


if __name__ == '__main__':
    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    ENEMY_LASER_SPEED = pygame.USEREVENT + 1
    pygame.time.set_timer(ENEMY_LASER_SPEED, 1000)

    BLOCK_SHAPE = [
        '  xxxxxxx',
        ' xxxxxxxxx',
        'xxxxxxxxxxx',
        'xxxxxxxxxxx',
        'xxxx    xxx',
        'xx       xx',
        'x         x'
    ]

    # Set up the Pygame window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Space Invader")

    
    # Set up the font
    font = pygame.font.Font(None, 50)

    # Create a text object for the title
    title_text = font.render("Space Invader", True, (255, 255, 255))

    # Set up the font
    font = pygame.font.Font(None, 50)

    # Create a list of menu options
    menu_options = [
        "Play Game",
        "Quit"
    ]

    # Create a dict of text objects for the menu options
    menu_texts = {}
    for option in menu_options:
        text = font.render(option, True, (255, 255, 255))
        sprite = pygame.sprite.Sprite()
        sprite.image = text
        sprite.rect = text.get_rect(center=(400, 300 + len(menu_texts) * 100))
        sprite.normal_alpha = 255
        sprite.hover_alpha = 100
        menu_texts[sprite] = option

    # Create a sprite group for the menu options
    menu_sprites = pygame.sprite.Group(*menu_texts.keys())

    # Main loop
    # Define a variable to keep track of the current screen
    current_screen = "menu"

    # Main loop
    clock = pygame.time.Clock()
    running = True
    game = Game()
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == ENEMY_LASER_SPEED:
                game.enemy_shoot()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                for sprite in menu_sprites:
                    if sprite.rect.collidepoint(pygame.mouse.get_pos()):
                        option = menu_texts[sprite]
                        if option == "Play Game":
                            # Switch to the game screen
                            current_screen = "game"
                            pass
                        elif option == "Quit":
                            running = False

        # Check if the mouse is hovering over a menu option
        for sprite in menu_sprites:
            if sprite.rect.collidepoint(pygame.mouse.get_pos()):
                sprite.image.set_alpha(sprite.hover_alpha)
            else:
                sprite.image.set_alpha(sprite.normal_alpha)

        # Draw the current screen
        if current_screen == "menu":
            # Draw the menu
            screen.fill((0, 0, 0))
            screen.blit(title_text, title_text.get_rect(center=(400, 100)))
            for sprite in menu_sprites:
                screen.blit(sprite.image, sprite.rect)
        elif current_screen == "game":
            # Start the game
            game.start = 1
            screen.fill((0, 0, 0))
            game.run()

        # Update the display
        
        pygame.display.flip()
        clock.tick(60)
    
    # Clean up
    pygame.quit()
