"""
Main driver file for the pygame project.
This file handles the main game loop and coordinates all game components.
"""

import pygame
import sys
import random
from player import Player
from enemy import BasicEnemy, JumpingEnemy, AmbushEnemy
from level import Level

class Game:
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        
        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        
        # Create the display
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Echoes of Lyra")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Game state
        self.running = True
        self.game_over = False
        
        # Initialize game objects (load level from CSV)
        self.level = Level("levels/level1.csv", tile_size=64)
        # Start player near the left side on top of the first available ground
        start_x = 100
        start_y = self.level.height - 150
        self.player = Player(start_x, start_y)
        self.enemies = pygame.sprite.Group()

        # Camera system
        self.camera_x = 0
        self.camera_y = 0

        # Create enemies on platforms
        self.spawn_enemies()

        # Font for UI
        self.font = pygame.font.Font(None, 36)
    
    def spawn_enemies(self):
        """Spawn enemies based on CSV spawn markers."""
        spawn_positions = self.level.get_enemy_spawn_positions()
        
        # Get tile information for ambush enemies
        solid_tiles, one_way_tiles = self.level.get_platforms()
        
        for spawn in spawn_positions:
            enemy_type = spawn.get('type', 'basic')  # Default to basic if type missing
            
            if enemy_type == 'ambush':
                # AmbushEnemy needs tile information to find hanging position
                enemy = AmbushEnemy(spawn['x'], spawn['y'], solid_tiles, one_way_tiles)
            elif enemy_type == 'jumping':
                enemy = JumpingEnemy(spawn['x'], spawn['y'])
            else:  # basic or unknown types
                enemy = BasicEnemy(spawn['x'], spawn['y'])
            
            self.enemies.add(enemy)
    
    def handle_events(self):
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
    
    def update(self):
        """Update all game objects."""
        if self.game_over:
            return
        
        # Get pressed keys for continuous input
        keys = pygame.key.get_pressed()
        
        # Get platforms for collision detection (solid, one-way)
        solid_tiles, one_way_tiles = self.level.get_platforms()

        # Update player (pass level pixel bounds)
        self.player.update(keys, solid_tiles, one_way_tiles, self.level.width, self.level.height)

        # Update enemies
        player_pos = self.player.get_position()
        for enemy in self.enemies:
            if isinstance(enemy, AmbushEnemy):
                enemy.update(solid_tiles, one_way_tiles, self.level.height, self.level.width, player_pos)
            else:
                enemy.update(solid_tiles, one_way_tiles, self.level.height, self.level.width)
        
        # Update level
        self.level.update()
        
        # Check for player-enemy collisions
        player_rect = self.player.get_rect()
        for enemy in self.enemies:
            if enemy.active and player_rect.colliderect(enemy.get_rect()):
                self.player.take_damage(1)
                break  # Only take damage from one enemy per frame

        # Check collectible pickups
        for item in self.level.collectibles:
            if not item['collected'] and player_rect.colliderect(item['rect']):
                item['collected'] = True
                # You can add effects here (score/heal). For now, print and mark.
                print("Collected an item!")
        
        # Update camera to follow player
        self.update_camera()
        
        # Check if player is dead
        if not self.player.is_alive():
            self.game_over = True
    
    def update_camera(self):
        """Update camera position to follow player."""
        # Center camera on player
        target_x = self.player.rect.centerx - self.SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - self.SCREEN_HEIGHT // 2
        
        # Constrain camera to level bounds
        self.camera_x = max(0, min(target_x, self.level.width - self.SCREEN_WIDTH))
        self.camera_y = max(0, min(target_y, self.level.height - self.SCREEN_HEIGHT))

    def draw(self):
        """Draw all game objects to the screen."""
        # Clear screen
        self.screen.fill((135, 206, 250))  # Sky blue background
        
        # Draw level (background and platforms) with camera offset
        self.level.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw player with camera offset
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw enemies with camera offset
        for enemy in self.enemies:
            if enemy.active:
                enemy.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
        else:
            # Draw collectibles HUD
            total = len(self.level.collectibles)
            collected = sum(1 for it in self.level.collectibles if it['collected'])
            hud_text = self.font.render(f"Collected: {collected}/{total}", True, (255, 255, 255))
            self.screen.blit(hud_text, (10, 40))
        
        # Update display
        pygame.display.flip()
    
    def draw_game_over(self):
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Restart instruction
        restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        """Restart the game."""
        self.game_over = False
        self.player.reset_position(100, self.SCREEN_HEIGHT - 150)
        # Reload level to reset collectibles
        self.level.load_from_csv(self.level.csv_path)

        # Clear and respawn enemies
        self.enemies.empty()
        self.spawn_enemies()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point of the program."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()