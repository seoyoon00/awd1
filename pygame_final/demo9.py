import pygame
import sys
import random

pygame.init()

screen_width, screen_height = 800, 1000
screen = pygame.display.set_mode((screen_width, screen_height))

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.width = 150
        self.height = 150
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(red)
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
        elif keys[pygame.K_RIGHT] and self.rect.x - 25 < 500 and not self.is_moving_right:
            self.rect.x += 200
            self.is_moving_left = False
            self.is_moving_right = True

        if not keys[pygame.K_LEFT]:
            self.is_moving_left = False
        if not keys[pygame.K_RIGHT]:
            self.is_moving_right = False

        # Check if the player is on top of a platform
        on_platform = pygame.sprite.spritecollide(self, platforms, False)
        if not on_platform:
            # Player fell down, game over
            global playing
            playing = True

        # Shoot bullets when spacebar is pressed
        if keys[pygame.K_SPACE]:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets.add(bullet)
            all_sprites.add(bullet)

class Platform(pygame.sprite.Sprite):
    platform_count = 0
    vy = 2
    accelerate_when = 3
    accelerate_applied = False

    def __init__(self, x, y, height):
        super().__init__()
        self.width = 200
        self.height = height
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(white)
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
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(green)  # Fill with the desired color or image later
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
        self.rect.y += random.randrange(1,5)  # Adjust the falling speed

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
        self.font = pygame.font.Font(None, 36)
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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 10
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(blue)
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


# Group setup
all_sprites = pygame.sprite.LayeredUpdates()
list_of_platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
buttons = pygame.sprite.Group()

# Create buttons
play_button = Button("Play Game", (screen_width // 2 - 100, screen_height // 2), action="play")
how_to_play_button = Button("How to Play", (screen_width // 2 - 100, screen_height // 2 + 200))
buttons.add(play_button, how_to_play_button)

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

# Game loop
running = True
playing = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if playing:
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
        screen.fill(black)
        list_of_platforms.draw(screen)
        all_sprites.draw(screen)

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

        # Update display for specific rectangles
        pygame.display.update(player.rect)
        pygame.display.update(list_of_platforms.sprites())
        pygame.display.update(enemies.sprites())
        pygame.display.update(bullets.sprites())

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    else:
        # Draw title screen with buttons
        screen.fill(black)
        buttons.update()
        for button in buttons:
            screen.blit(button.image, button.rect.topleft)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

        # Check for button clicks on the title screen
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button.rect.collidepoint(event.pos):
                    if button.action == "play":
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

# Quit Pygame
pygame.quit()
sys.exit()
