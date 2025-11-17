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
from menu import MainMenu, LevelSelect

class Game:
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        
        # Screen dimensions
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 800
        
        # Create the display
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Echoes of Lyra")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Game state management
        self.running = True
        self.state = "main_menu"  # States: main_menu, level_select, playing, level_complete
        self.game_over = False
        
        # Current level info
        self.current_level_index = 0
        self.current_level_file = None
        
        # Menu systems
        self.main_menu = MainMenu(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.level_select = LevelSelect(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Game objects (initialized when level starts)
        self.level = None
        self.player = None
        self.enemies = pygame.sprite.Group()

        # Camera system
        self.camera_x = 0
        self.camera_y = 0

        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 64)
    
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
    
    def load_level(self, level_file, level_index):
        """Load a specific level."""
        self.current_level_file = level_file
        self.current_level_index = level_index
        self.level = Level(level_file, tile_size=64)
        
        # Start player near the left side on top of the first available ground
        start_x = 100
        start_y = self.level.height - 150
        self.player = Player(start_x, start_y)
        
        # Clear and spawn enemies
        self.enemies.empty()
        self.spawn_enemies()
        
        # Reset camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Reset game state
        self.game_over = False
        self.state = "playing"
    
    def check_level_complete(self):
        """Check if all collectibles are collected."""
        if self.level:
            total = len(self.level.collectibles)
            collected = sum(1 for it in self.level.collectibles if it['collected'])
            return collected == total
        return False
    
    def complete_level(self):
        """Handle level completion."""
        # Save progress
        self.level_select.save_progress(self.current_level_index)
        self.state = "level_complete"
    
    def handle_events(self):
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        # Return to level select
                        self.state = "level_select"
                    elif self.state == "level_select":
                        # Return to main menu
                        self.state = "main_menu"
                    elif self.state == "level_complete":
                        # Return to level select
                        self.state = "level_select"
                    else:
                        # Quit from main menu
                        self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
                elif event.key == pygame.K_RETURN and self.state == "level_complete":
                    # Continue to level select after completing level
                    self.state = "level_select"
            
            # Handle menu events
            if self.state == "main_menu":
                action = self.main_menu.handle_events(event)
                if action == "level_select":
                    self.state = "level_select"
                elif action == "quit":
                    self.running = False
            
            elif self.state == "level_select":
                result = self.level_select.handle_events(event)
                if result == "main_menu":
                    self.state = "main_menu"
                elif result and result[0] == "play":
                    _, level_index, level_file = result
                    self.load_level(level_file, level_index)
    
    def update(self):
        """Update all game objects."""
        if self.state == "main_menu":
            self.main_menu.update()
        
        elif self.state == "level_select":
            self.level_select.update()
        
        elif self.state == "playing":
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
            
            # Check if level is complete
            if self.check_level_complete() and not self.game_over:
                self.complete_level()
            
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
        if self.state == "main_menu":
            self.main_menu.draw(self.screen)
        
        elif self.state == "level_select":
            self.level_select.draw(self.screen)
        
        elif self.state == "playing":
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
                
                # Draw level name
                level_name = f"Level {self.current_level_index + 1}"
                level_text = self.font.render(level_name, True, (255, 255, 255))
                self.screen.blit(level_text, (10, 10))
        
        elif self.state == "level_complete":
            self.draw_level_complete()
        
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
        game_over_text = self.large_font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Restart instruction
        restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        # Back to menu instruction
        menu_text = self.font.render("Press ESC for Level Select", True, (200, 200, 200))
        menu_rect = menu_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 + 100))
        self.screen.blit(menu_text, menu_rect)
    
    def draw_level_complete(self):
        """Draw level complete screen."""
        # Background with gradient effect
        self.screen.fill((20, 40, 60))
        
        # Congratulations text
        congrats_text = self.large_font.render("LEVEL COMPLETE!", True, (100, 255, 100))
        congrats_rect = congrats_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 - 100))
        self.screen.blit(congrats_text, congrats_rect)
        
        # Level info
        level_text = self.font.render(f"You completed Level {self.current_level_index + 1}!", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2))
        self.screen.blit(level_text, level_rect)
        
        # Next level unlocked message
        if self.current_level_index < 2:  # Not the last level
            unlock_text = self.font.render(f"Level {self.current_level_index + 2} Unlocked!", True, (255, 255, 100))
            unlock_rect = unlock_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 + 50))
            self.screen.blit(unlock_text, unlock_rect)
        else:
            # Last level completed
            final_text = self.font.render("You completed all levels!", True, (255, 255, 100))
            final_rect = final_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 + 50))
            self.screen.blit(final_text, final_rect)
        
        # Continue instruction
        continue_text = self.font.render("Press ENTER to Continue", True, (200, 200, 200))
        continue_rect = continue_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 + 150))
        self.screen.blit(continue_text, continue_rect)
    
    def restart_game(self):
        """Restart the current level."""
        if self.current_level_file:
            self.load_level(self.current_level_file, self.current_level_index)
    
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