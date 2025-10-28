"""
Enemy class for the pygame project.
Handles enemy behavior, movement, and AI.
"""

import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_start_x, patrol_end_x, enemy_type="basic"):
        """Initialize the enemy."""
        super().__init__()
        
        # Enemy type
        self.enemy_type = enemy_type
        
        # Enemy dimensions
        self.width = 32
        self.height = 32
        
        # Create enemy surface and rectangle
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Set enemy properties based on type
        self.setup_enemy_type()
        
        # Patrol movement
        self.patrol_start_x = patrol_start_x
        self.patrol_end_x = patrol_end_x
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 1
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.8
        self.max_fall_speed = 10
        self.on_ground = False
        
        # State
        self.active = True
    
    def setup_enemy_type(self):
        """Set up enemy properties based on type."""
        if self.enemy_type == "basic":
            self.image.fill((255, 0, 0))  # Red color
            self.speed = 1
            self.health = 1
            self.max_health = 1
            self.damage = 1
        elif self.enemy_type == "fast":
            self.image.fill((255, 165, 0))  # Orange color
            self.speed = 2
            self.health = 1
            self.max_health = 1
            self.damage = 1
        elif self.enemy_type == "tank":
            self.image.fill((139, 0, 0))  # Dark red color
            self.width = 48
            self.height = 48
            self.speed = 0.5
            self.health = 3
            self.max_health = 3
            self.damage = 1
            # Recreate image with new size
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((139, 0, 0))
            self.rect = self.image.get_rect()
        else:
            # Default to basic
            self.enemy_type = "basic"
            self.setup_enemy_type()
    
    def update(self, platforms, screen_height):
        """Update enemy position and behavior."""
        if not self.active:
            return
        
        # Simple patrol movement
        self.velocity_x = self.direction * self.speed
        
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
        
        # Move horizontally
        self.rect.x += self.velocity_x
        
        # Check if reached patrol boundaries
        if self.rect.centerx <= self.patrol_start_x or self.rect.centerx >= self.patrol_end_x:
            self.direction *= -1  # Reverse direction
            # Keep within bounds
            if self.rect.centerx <= self.patrol_start_x:
                self.rect.centerx = self.patrol_start_x
            elif self.rect.centerx >= self.patrol_end_x:
                self.rect.centerx = self.patrol_end_x
        
        # Check horizontal platform collisions
        self.check_horizontal_collisions(platforms)
        
        # Move vertically
        self.rect.y += self.velocity_y
        
        # Check vertical collisions
        self.check_vertical_collisions(platforms, screen_height)
    
    def check_horizontal_collisions(self, platforms):
        """Check for horizontal collisions with platforms."""
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = platform.left
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = platform.right
                self.direction *= -1  # Reverse direction on collision
    
    def check_vertical_collisions(self, platforms, screen_height):
        """Check for vertical collisions with platforms."""
        self.on_ground = False
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Moving up (shouldn't happen for enemies)
                    self.rect.top = platform.bottom
                    self.velocity_y = 0
        
        # Check ground collision
        if self.rect.bottom >= screen_height - 50:  # Ground level
            self.rect.bottom = screen_height - 50
            self.velocity_y = 0
            self.on_ground = True
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the enemy to the screen with camera offset."""
        if not self.active:
            return
        
        # Draw enemy with camera offset
        screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)
        screen.blit(self.image, screen_pos)
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            self.draw_health_bar(screen, camera_x, camera_y)
    
    def draw_health_bar(self, screen, camera_x=0, camera_y=0):
        """Draw enemy's health bar with camera offset."""
        bar_width = self.width
        bar_height = 6
        bar_x = self.rect.x - camera_x
        bar_y = self.rect.y - camera_y - 10
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health (green)
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), 
                        (bar_x, bar_y, bar_width, bar_height), 1)
    
    def get_rect(self):
        """Return the enemy's rectangle for collision detection."""
        return self.rect
    
    def take_damage(self, damage):
        """Reduce enemy health by damage amount."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.active = False
    
    def is_alive(self):
        """Check if enemy is still alive."""
        return self.health > 0 and self.active
    
    def get_damage(self):
        """Return the damage this enemy deals."""
        return self.damage
    
    def get_position(self):
        """Return enemy's current position."""
        return (self.rect.x, self.rect.y)
    
    def set_position(self, x, y):
        """Set enemy's position."""
        self.rect.x = x
        self.rect.y = y