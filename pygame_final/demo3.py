import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width, screen_height = 800, 1000
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.width = 150
        self.height = 150
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 700

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 100:
            self.rect.x -= 200
        elif keys[pygame.K_RIGHT] and self.rect.x < 500:
            self.rect.x += 200

        # Check if the player is on top of a platform
        on_platform = pygame.sprite.spritecollide(self, platforms, False)
        if not on_platform:
            # Player fell below the platform, game over
            global playing
            playing = False

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 200
        self.height = 500
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(white)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.y += 1
        if self.rect.top > screen_height:
            self.rect.y = 0
            self.rect.x = random.choice([100, 300, 500])

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.height = 100
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(green)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.width)
        self.rect.y = random.randint(0, screen_height - self.height)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.width = 50
        self.height = 50
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(blue)
        self.rect = self.image.get_rect()
        self.rect.center = player_rect.center

    def update(self):
        self.rect.y -= 5

# Button class
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

# Group setup
all_sprites = pygame.sprite.LayeredUpdates()
list_of_platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
buttons = pygame.sprite.Group()

# Create initial platform
first_platform = Platform(300, 400)
list_of_platforms.add(first_platform)
all_sprites.add(first_platform)

# Create player
player = Player(300)  # Initial horizontal position at 300
all_sprites.add(player)

# Spawn platforms
if random.randint(0, 100) < 1:
            platform = Platform(random.choice([100, 300, 500]), 0)
            list_of_platforms.add(platform)
            all_sprites.add(platform)

# Create buttons
play_button = Button("Play Game", (screen_width // 2 - 100, screen_height // 2), action="play")
how_to_play_button = Button("How to Play", (screen_width // 2 - 100, screen_height // 2 + 200))
buttons.add(play_button, how_to_play_button)

# Clock
clock = pygame.time.Clock()

# Game variables
bullet_count = 0
score = 0
start_time = pygame.time.get_ticks()

# Game loop
running = True
playing = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        keys = pygame.key.get_pressed()

        if not playing:
            if keys[pygame.K_SPACE]:
                playing = True
                list_of_platforms.empty()
                enemies.empty()
                bullets.empty()
                all_sprites.empty()
                bullet_count = 0
                score = 0
                start_time = pygame.time.get_ticks()
                # Create initial platform
                first_platform = Platform(300, 400)
                list_of_platforms.add(first_platform)
                all_sprites.add(first_platform)
                player = Player(300)  # Reset player's position to 300
                all_sprites.add(player)

    if playing:

        # Spawn enemies
        if random.randint(0, 500) == 0:
            enemy = Enemy()
            enemies.add(enemy)
            all_sprites.add(enemy)

        # Check for collisions
        enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
        for hit in enemy_hits:
            playing = False

        # Check for bullet-enemy collisions
        bullet_hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in bullet_hits:
            score += 2

        # Update player and platforms
        player.update(list_of_platforms)
        list_of_platforms.update()

        # Draw everything
        screen.fill(black)
        all_sprites.draw(screen)

        # Display bullet count and score
        font = pygame.font.Font(None, 36)
        text = font.render(f"Bullets: {bullet_count} Score: {score}", True, white)
        screen.blit(text, (10, 10))

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
                        first_platform = Platform(300, 400)
                        list_of_platforms.add(first_platform)
                        all_sprites.add(first_platform)
                        player = Player(300)  # Reset player's position to 300
                        all_sprites.add(player)

# Quit Pygame
pygame.quit()
sys.exit()
