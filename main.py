"""
Main driver file for the pygame project.
This file handles the main game loop and coordinates all game components.
"""

import pygame
import sys
from player import Player
from enemy import Enemy
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
        pygame.display.set_caption("2D Platformer Game")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Game state
        self.running = True
        self.game_over = False
        
        # Initialize game objects
        self.level = Level(1)
        self.player = Player(100, self.SCREEN_HEIGHT - 150)  # Start on ground
        self.enemies = pygame.sprite.Group()
        
        # Camera system
        self.camera_x = 0
        self.camera_y = 0
        
        # Create enemies on platforms
        self.spawn_enemies()
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
    
    def spawn_enemies(self):
        """Spawn enemies on platforms."""
        spawn_positions = self.level.get_enemy_spawn_positions()
        
        for pos in spawn_positions[:3]:  # Limit to 3 enemies
            enemy = Enemy(pos['x'], pos['y'], pos['patrol_start'], pos['patrol_end'])
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
        
        # Get platforms for collision detection
        platforms = self.level.get_platforms()
        
        # Update player
        self.player.update(keys, platforms, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(platforms, self.SCREEN_HEIGHT)
        
        # Update level
        self.level.update()
        
        # Check for player-enemy collisions
        player_rect = self.player.get_rect()
        for enemy in self.enemies:
            if enemy.active and player_rect.colliderect(enemy.get_rect()):
                self.player.take_damage(1)
                break  # Only take damage from one enemy per frame
        
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