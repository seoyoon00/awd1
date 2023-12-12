import pygame
import sys
import random
from os import path

img = path.join(path.dirname(__file__), 'img')

pygame.init()

pygame.display.set_caption("20191162_final")

screen_width, screen_height = 800, 1000
screen = pygame.display.set_mode((screen_width, screen_height))

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

player_img = pygame.image.load(path.join(img, "player.png")).convert()
enemy_img =pygame.image.load(path.join(img, "enemy.png")).convert()
background_img=pygame.image.load(path.join(img, "background.png")).convert()

bgm_path = path.join(path.dirname(__file__), 'snd', 'bgm.mp3')
pygame.mixer.music.load(bgm_path)

def load_sound(filename):
    sound_path = path.join(path.dirname(__file__), 'snd', filename)
    return pygame.mixer.Sound(sound_path)

# Usage
shoot_sound = load_sound('shoot.mp3')
jump_sound = load_sound('jump.mp3')

font_path = path.join(path.dirname(__file__), 'Font.TTF')
font = pygame.font.Font(font_path, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.width = 150
        self.height = 150
        self.image = player_img
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.rect.x = x + 25
        self.rect.y = 700
        self.is_moving_left = False
        self.is_moving_right = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.rect.x - 25 > 100 and not self.is_moving_left:
            self.rect.x -= 200
            self.is_moving_left = True
            self.is_moving_right = False
            jump_sound.play()

        elif keys[pygame.K_RIGHT] and self.rect.x - 25 < 500 and not self.is_moving_right:
            self.rect.x += 200
            self.is_moving_left = False
            self.is_moving_right = True
            jump_sound.play()

        if not keys[pygame.K_LEFT]:
            self.is_moving_left = False
        if not keys[pygame.K_RIGHT]:
            self.is_moving_right = False

        # Check if the player is on top of a platform
        on_platform = pygame.sprite.spritecollide(self, platforms, False)
        if not on_platform:
            # Player fell down, game over
            global playing
            playing = False

        # Shoot bullets when spacebar is pressed
        if keys[pygame.K_SPACE]:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets.add(bullet)
            all_sprites.add(bullet)
            shoot_sound.play()

class Platform(pygame.sprite.Sprite):
    platform_count = 0
    vy = 2
    accelerate_when = 3
    accelerate_applied = False


    height_image_mapping = {
        300: 'platform_300.jpg',
        400: 'platform_400.jpg',
        500: 'platform_500.jpg',
        600: 'platform_600.jpg',
    }

    def __init__(self, x, y, height):
        super().__init__()
        self.width = 200
        self.height = height
        self.image =pygame.image.load(path.join(img, self.height_image_mapping.get(height, 'platform_300.jpg'))).convert()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.id = Platform.platform_count
        Platform.platform_count += 1

    def update(self):
        self.rect.y += Platform.vy

        if Platform.platform_count % Platform.accelerate_when == 0 and not Platform.accelerate_applied:
            Platform.vy += 0.5
            Platform.accelerate_applied = True

        elif Platform.platform_count % Platform.accelerate_when != 0:
            Platform.accelerate_applied = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, platforms, player_top):
        super().__init__()
        self.width = 100
        self.height = 100

        self.image = enemy_img
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()

        # Convert the platforms group to a list for random.choice
        platform_list = list(platforms)

        # Set the x-coordinate within the platform's boundaries
        platform = platform_list[-1]
        self.rect.x = platform.rect.x + 50

        # Set the y-coordinate within the platform's top and bottom
        self.rect.y = 0

        self.platforms = platforms

    def update(self):
        #Enmey is falling
        self.rect.y += random.randrange(2,8)

class Button(pygame.sprite.Sprite):
    def __init__(self, text, position, action=None):
        super().__init__()
        self.width = 200
        self.height = 50
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.text = text
        self.font = font
        self.render_text()
        self.action = action

    def render_text(self):
        text_surface = self.font.render(self.text, True, black)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.image.fill(white)
        self.image.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action == "play":
                    global playing
                    playing = True
                    list_of_platforms.empty()
                    enemies.empty()
                    bullets.empty()
                    all_sprites.empty()
                    bullet_count = 0
                    score = 0
                    start_time = pygame.time.get_ticks()

                    # Create initial platform
                    first_platform = Platform(300, 400, 500)
                    list_of_platforms.add(first_platform)
                    all_sprites.add(first_platform)

                    player = Player(300)  # Reset player's position to 300
                    all_sprites.add(player)

                    generate_platform = True

    def draw(self,screen):
        screen.blit(self.image, self.rect.topleft)
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 10
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.x = x - self.width // 2
        self.rect.y = y

    def update(self):
        self.rect.y -= 15  # Adjust the bullet's vertical speed
        if self.rect.bottom < 0:
            self.kill()  # Remove the bullet when it goes off-screen

def player_on_last_platform(player, platforms):
    return platforms and player.rect.colliderect(platforms.sprites()[-1].rect)

def generate_platform_at_player(player, platforms, generate_flag):
    if player_on_last_platform(player, platforms) and not generate_flag:
        return True
    return False

def reset_game():
    global bullet_count, score, start_time, prev_platform_x, playing, generate_platform, enemy_killed_count

    bullet_count = 0
    score = 0
    start_time = pygame.time.get_ticks()
    prev_platform_x = 300
    playing = False
    generate_platform = False
    enemy_killed_count = 0


# Group setup
all_sprites = pygame.sprite.LayeredUpdates()
list_of_platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
buttons = pygame.sprite.Group()
how_to_play = pygame.sprite.Group()

# Create buttons
play_button = Button("Play Game", (screen_width // 2 - 100, screen_height // 2+100), action="play")
quit_button = Button("Quit Game", (screen_width // 2 - 100, screen_height // 2+200), action="quit")

# Create player
player = Player(300)
all_sprites.add(player)


# Clock
clock = pygame.time.Clock()

# Game variables
bullet_count = 0
score = 0
start_time = pygame.time.get_ticks()
prev_platform_x = 300
playing = False
generate_platform = False
enemy_killed_count=0

pygame.mixer.music.play(-1)

# Game loop
running = True
playing = False

while running:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if playing:

        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

        score = elapsed_time+enemy_killed_count


        # Check if the player is on top of a platform
        on_top_platform = pygame.sprite.spritecollide(player, list_of_platforms, False)
        if on_top_platform and generate_platform and player.rect.top < list_of_platforms.sprites()[-1].rect.bottom:
            top_platforms = [platform for platform in list_of_platforms if platform.rect.y < player.rect.y]
            if not top_platforms or top_platforms[-1].rect.x != prev_platform_x:
                next_platform_x = 300
                if prev_platform_x == 100:
                    next_platform_x = 300
                elif prev_platform_x == 300:
                    next_platform_x = random.choice([100, 500])
                elif prev_platform_x == 500:
                    next_platform_x = 300


                # Calculate the y-coordinate for the new platform if top_platforms is not empty
                if top_platforms:
                    next_platform_height = random.choice([300, 400, 500, 600])
                    next_platform_y = top_platforms[-1].rect.y - next_platform_height + 100
                else:
                    next_platform_height = random.choice([300, 400, 500, 600])
                    next_platform_y = 700 - next_platform_height + 100

                # Create and add the new platform
                next_platform = Platform(next_platform_x, next_platform_y, next_platform_height)
                list_of_platforms.add(next_platform)
                prev_platform_x = next_platform_x  # Update prev_platform_x

                # Set the flag to False after generating the platform
                generate_platform = False

        # Check if the player is on the last generated platform
        if generate_platform_at_player(player, list_of_platforms, generate_platform):
            # Set the flag to True when the player moves onto the generated platform
            generate_platform = True

        # Update player and platforms
        player.update(list_of_platforms)
        list_of_platforms.update()

        # Draw
        screen.blit(background_img, (0,0))
        list_of_platforms.draw(screen)
        all_sprites.draw(screen)
        
        font_name= pygame.font.match_font('arial')
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text,(10,10))

        # Create enemies on platforms and above the player
        if generate_platform_at_player(player, list_of_platforms, generate_platform):
            platform = list_of_platforms.sprites()[-1]  
            
            if random.choice([True,False]):
                enemy = Enemy(list_of_platforms, player.rect.top)
                enemies.add(enemy)
                all_sprites.add(enemy)

        # Update enemies
        enemies.update()
        enemies.draw(screen)

        bullets.update()
        bullets.draw(screen)

        # Check for collisions between player and enemies
        enemy_collision = pygame.sprite.spritecollide(player, enemies, False)
        if enemy_collision:
            # Player collided with an enemy, end the game
            playing = False


        # Check for collisions between enemies and bullets
        bullet_collision = pygame.sprite.groupcollide(bullets, enemies, True, True)
        enemy_killed_count += len(bullet_collision)

        # Draw
        screen.blit(background_img, (0,0))
        list_of_platforms.draw(screen)
        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score}", True, white)
        text_rect = score_text.get_rect()
        text_rect.midtop=(screen_width/2, 30)
        screen.blit(score_text, text_rect)

        enemies.draw(screen)
        bullets.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    else:
        reset_game()


        # title screen
        screen.blit(background_img, (0,0))
        screen.blit(play_button.image, play_button.rect.topleft)
        screen.blit(quit_button.image, quit_button.rect.topleft)

        title_font = pygame.font.Font(font_path, 70)
        title = title_font.render("CODE RUNNER", True, white)
        text_rect = title.get_rect()
        text_rect.midtop=(screen_width/2, 300)
        screen.blit(title, text_rect)

        pygame.display.flip()
        clock.tick(60)

        # Check for button clicks on the title screen
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if play_button.rect.collidepoint(event.pos):
                play_button.handle_event(event)
                if play_button.action == "play":
                    playing = True
                    list_of_platforms.empty()
                    enemies.empty()
                    bullets.empty()
                    all_sprites.empty()
                    bullet_count = 0
                    score = 0
                    start_time = pygame.time.get_ticks()

                    # Create initial platform
                    first_platform = Platform(300, 400, 500)
                    list_of_platforms.add(first_platform)
                    all_sprites.add(first_platform)

                    player = Player(300)  # Reset player's position to 300
                    all_sprites.add(player)

                    generate_platform = True

            if quit_button.rect.collidepoint(event.pos):
                quit_button.handle_event(event)
                if quit_button.action == "quit":
                    running = False
                    


# Quit Pygame
pygame.quit()
sys.exit()
