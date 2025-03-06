import pygame
import random

# Settings (Constants for layout and game settings)
SCALE = 25
SCREEN_HEIGHT = 20 * SCALE  # format 20:9
SCREEN_WIDTH = 9 * SCALE
LANE_COUNT = 3
LANE_WIDTH = SCREEN_WIDTH // (LANE_COUNT + 1)
LEFT_MARGIN = (SCREEN_WIDTH - (LANE_COUNT * LANE_WIDTH)) // 2
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 80
PLAYER_SPEED = None
OBSTACLE_SPEED = 5
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Cyclist")
clock = pygame.time.Clock() #creates Clock object to help control the frame rate

# Load assets
pygame.mixer.init()
game_music = pygame.mixer.Sound('game_music.mp3')
game_over_music = pygame.mixer.Sound('game_over_music.mp3')
crash_sound = pygame.mixer.Sound('crash_sound.wav')
background_image = pygame.image.load('background.png').convert()

# Play background music
pygame.mixer.Sound.play(game_music, loops=-1)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load both animation frames
        self.frames = [
            pygame.image.load('player1.png'),
            pygame.image.load('player2.png')
        ]
        
        
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.animation_timer = 0
        self.animation_delay = 500  # 500 milliseconds = 0.5 seconds
        
        self.current_lane = 2  # Start in the middle lane
        self.rect = self.image.get_rect()
        self.rect.x = LEFT_MARGIN + self.current_lane * LANE_WIDTH - LANE_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 20

    def update(self):
        # Update animation frame
        current_time = pygame.time.get_ticks() #time in milliseconds
        if current_time - self.animation_timer > self.animation_delay: 
            self.animation_timer = current_time
            self.current_frame = (self.current_frame + 1) % len(self.frames) # modulo 2
            self.image = self.frames[self.current_frame]

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, lane): #constructor takes lane as an argument
        super().__init__()
        self.image = pygame.image.load('carRed.png')
        self.lane = lane
        self.rect = self.image.get_rect()
        self.rect.x = LEFT_MARGIN + lane * LANE_WIDTH - LANE_WIDTH // 2 - OBSTACLE_WIDTH // 2
        self.rect.y = -OBSTACLE_HEIGHT

    def update(self):
        self.rect.y += OBSTACLE_SPEED # Move the obstacle down
        if self.rect.top > SCREEN_HEIGHT: # Remove the obstacle when it goes off screen
            self.kill()

# Game class
class Game:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group() #later used for collision detection
        self.obstacles = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.difficulty = 1
        self.score = 0
        self.highscore = 0
        self.font = pygame.font.Font(None, 36)

        # Background scrolling
        self.bg_y1 = 0
        self.bg_y2 = -750
        self.bg_speed = 5  

    def run(self):
        running = True
        while running:
            clock.tick(FPS) # Limit the frame rate
            self.handle_events()
            self.update()
            self.draw()
            if pygame.sprite.spritecollideany(self.player, self.obstacles):
                pygame.mixer.Sound.play(crash_sound)
                running = False
        self.show_game_over()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.player.current_lane > 1:
                    self.player.current_lane -= 1
                elif event.key == pygame.K_RIGHT and self.player.current_lane < LANE_COUNT:
                    self.player.current_lane += 1
                self.player.rect.x = LEFT_MARGIN + self.player.current_lane * LANE_WIDTH - LANE_WIDTH // 2 - PLAYER_WIDTH // 2

    def update(self):
        self.all_sprites.update()
        self.obstacles.update()
        self.spawn_obstacles()
        self.score += 1 if pygame.time.get_ticks() % 10 == 0 else 0  # Slow down score increment
        self.difficulty = min(59, self.score // 10 + 1)

        # Update background position
        self.bg_y1 += self.bg_speed
        self.bg_y2 += self.bg_speed

        # Reset background positions to create a loop
        if self.bg_y1 >= 750:
            self.bg_y1 = -750
        if self.bg_y2 >= 750:
            self.bg_y2 = -750

    def draw(self):
        # Draw the scrolling background
        screen.blit(background_image, (0, self.bg_y1))
        screen.blit(background_image, (0, self.bg_y2))

        # Draw sprites
        self.all_sprites.draw(screen)
        self.obstacles.draw(screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))  # Blit is a method to draw text on the screen
        pygame.display.flip()  # Update the display

    def spawn_obstacles(self):
        if random.randint(1, 60 - self.difficulty) == 1:
            random_lane = random.randint(1, LANE_COUNT)
            '''
            # Rule 0: Bias lane selection to balance obstacle distribution
            lane_weights = [len([ob for ob in self.obstacles if ob.lane == i]) for i in range(1, LANE_COUNT + 1)]
            min_weight = min(lane_weights)
            balanced_lanes = [i + 1 for i, weight in enumerate(lane_weights) if weight == min_weight]
            random_lane = random.choice(balanced_lanes)'''

            # Rule 1: Check if any adjacent lane is not too crowded
            left_lane = random_lane - 1 if random_lane > 1 else None
            right_lane = random_lane + 1 if random_lane < LANE_COUNT else None
            
            def calculate_lane_length(obstacles):
                total_length = 0
                obstacles_sorted = sorted(obstacles, key=lambda ob: ob.rect.y)
                for i in range(len(obstacles_sorted) - 1):
                    gap = obstacles_sorted[i + 1].rect.y - (obstacles_sorted[i].rect.y + OBSTACLE_HEIGHT)
                    if gap < 160:
                        total_length += OBSTACLE_HEIGHT + gap
                    else:
                        total_length = 0
                return total_length

            left_length = calculate_lane_length([ob for ob in self.obstacles if ob.lane == left_lane]) if left_lane else 0
            right_length = calculate_lane_length([ob for ob in self.obstacles if ob.lane == right_lane]) if right_lane else 0

            # If both adjacent lanes have length equal to 250, do not place obstacle
            if left_length >= 250 and right_length >= 250:
                return
            
            # Rule 2: Check for obstacle alignment that would create a wall
            other_lanes = [lane for lane in range(1, LANE_COUNT + 1) if lane != random_lane]
            if all(any(ob.lane == lane and ob.rect.y < 3 * OBSTACLE_HEIGHT for ob in self.obstacles) for lane in other_lanes):
                return
            
            # Additional Rule: Ensure sufficient vertical gap between obstacles in the same lane 
            for ob in self.obstacles:
                if ob.lane == random_lane and ob.rect.y < 0:
                    return
                
            # Spawn obstacle if all conditions are met
            obstacle = Obstacle(random_lane)
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

    def show_game_over(self):
        pygame.mixer.Sound.stop(game_music)
        pygame.mixer.Sound.play(game_over_music, loops=-1)

        if self.score > self.highscore:
            self.highscore = self.score

        game_over = True
        while game_over:
            screen.fill(WHITE)
            game_over_text = self.font.render("Game Over", True, BLACK, WHITE)
            score_text = self.font.render(f"Score: {self.score}", True, BLACK, WHITE)
            highscore_text = self.font.render(f"Highscore: {self.highscore}", True, BLACK, WHITE)
            restart_text1 = self.font.render("Press SPACE", True, BLUE, WHITE)
            restart_text2 = self.font.render("to try again", True, BLUE, WHITE)

            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 4))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 4 + 50))
            screen.blit(highscore_text, (SCREEN_WIDTH // 2 - highscore_text.get_width() // 2, SCREEN_HEIGHT // 4 + 100))
            screen.blit(restart_text1, (SCREEN_WIDTH // 2 - restart_text1.get_width() // 2, SCREEN_HEIGHT // 4 + 150))
            screen.blit(restart_text2, (SCREEN_WIDTH // 2 - restart_text2.get_width() // 2, SCREEN_HEIGHT // 4 + 180))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pygame.mixer.Sound.stop(game_over_music)
                    pygame.mixer.Sound.play(game_music, loops=-1)
                    game_over = False
                    self.reset_game()
                    self.run()

    def reset_game(self):
        # Reset game state
        self.all_sprites.empty()
        self.obstacles.empty()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.difficulty = 1
        self.score = 0

# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()
