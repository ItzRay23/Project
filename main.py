"""
Main driver file for the pygame project.
This file handles the main game loop and coordinates all game components.
"""

import pygame
import sys
import random
from player import Player
from enemy import BasicEnemy, JumpingEnemy, AmbushEnemy, BossEnemy
from level import Level
from menu import MainMenu, LevelSelect
from bullet import Bullet

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
        self.bullets = pygame.sprite.Group()

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
            elif enemy_type == 'boss':
                enemy = BossEnemy(spawn['x'], spawn['y'])
            else:  # basic or unknown types
                enemy = BasicEnemy(spawn['x'], spawn['y'])
            
            self.enemies.add(enemy)
    
    def load_level(self, level_file, level_index):
        """Load a specific level."""
        self.current_level_file = level_file
        self.current_level_index = level_index
        self.level = Level(level_file, tile_size=64)
        
        # Check if level has a custom player spawn point (X in CSV)
        player_spawn = self.level.get_player_spawn_position()
        if player_spawn:
            # Use custom spawn point from level
            start_x, start_y = player_spawn
        else:
            # Fall back to calculated spawn (near left side, above ground)
            start_x = 100
            highest_ground_y = self.level.get_highest_ground_y(start_x)
            start_y = highest_ground_y - 20  # Spawn 20 pixels above the ground
        
        self.player = Player(start_x, start_y)
        
        # Clear and spawn enemies
        self.enemies.empty()
        self.spawn_enemies()
        
        # Clear bullets
        self.bullets.empty()
        
        # Reset camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Reset game state
        self.game_over = False
        self.state = "playing"
    
    def check_level_complete(self):
        """Check if player has reached the exit door after collecting all items."""
        if self.level and self.level.exit_rect:
            # Check if all collectibles are collected
            total = len(self.level.collectibles)
            collected = sum(1 for it in self.level.collectibles if it['collected'])
            all_collected = (total == 0) or (collected == total)
            
            # Only complete if all items collected AND player touches exit
            if all_collected:
                player_rect = self.player.get_rect()
                return player_rect.colliderect(self.level.exit_rect)
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
                elif event.key == pygame.K_f and self.state == "playing" and not self.game_over:
                    # Shoot bullet
                    bullet_info = self.player.shoot()
                    if bullet_info:
                        bullet = Bullet(bullet_info['x'], bullet_info['y'], bullet_info['direction'])
                        self.bullets.add(bullet)
            
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
                if isinstance(enemy, AmbushEnemy) or isinstance(enemy, BossEnemy):
                    enemy.update(solid_tiles, one_way_tiles, self.level.height, self.level.width, player_pos)
                else:
                    enemy.update(solid_tiles, one_way_tiles, self.level.height, self.level.width)
            
            # Update bullets
            for bullet in self.bullets:
                bullet.update(self.level.width, self.level.height)
                # Remove inactive bullets
                if not bullet.active:
                    self.bullets.remove(bullet)
            
            # Check bullet-enemy collisions
            for bullet in self.bullets:
                if not bullet.active:
                    continue
                bullet_rect = bullet.get_rect()
                for enemy in self.enemies:
                    if enemy.active and bullet_rect.colliderect(enemy.get_rect()):
                        was_boss = isinstance(enemy, BossEnemy)
                        enemy.take_damage(bullet.damage)
                        bullet.hit()
                        
                        # If boss was defeated, remove boss tiles
                        if was_boss and not enemy.is_alive():
                            self.level.remove_boss_tiles()
                        break
            
            # Update level
            self.level.update()
            
            # Check for player-enemy collisions
            player_rect = self.player.get_rect()
            for enemy in self.enemies:
                if enemy.active and player_rect.colliderect(enemy.get_rect()):
                    self.player.take_damage(1)
                    break  # Only take damage from one enemy per frame
            
            # Check boss bullet collisions with player
            for enemy in self.enemies:
                if isinstance(enemy, BossEnemy) and enemy.active:
                    boss_bullets = enemy.get_bullets()
                    for boss_bullet in boss_bullets:
                        if boss_bullet.active and player_rect.colliderect(boss_bullet.get_rect()):
                            self.player.take_damage(boss_bullet.damage)
                            boss_bullet.hit()
                            break

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
            
            # Draw player with camera offset (pass collectibles for crystal UI)
            total_crystals = len(self.level.collectibles)
            collected_crystals = sum(1 for it in self.level.collectibles if it['collected'])
            self.player.draw(self.screen, self.camera_x, self.camera_y, total_crystals, collected_crystals)
            
            # Draw enemies with camera offset
            for enemy in self.enemies:
                if enemy.active:
                    enemy.draw(self.screen, self.camera_x, self.camera_y)
            
            # Draw bullets with camera offset
            for bullet in self.bullets:
                if bullet.active:
                    bullet.draw(self.screen, self.camera_x, self.camera_y)
            
            # Draw game over screen if needed
            if self.game_over:
                self.draw_game_over()
            else:
                # Draw level name (top left, below hearts)
                level_name = f"Level {self.current_level_index + 1}"
                level_text = self.font.render(level_name, True, (255, 255, 255))
                self.screen.blit(level_text, (10, 45))
                
                # Crystal UI is now drawn by player.draw() method
        
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