"""
Bullet class for the pygame project.
Handles player projectiles that damage enemies.
"""

import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        """Initialize a bullet.
        
        Args:
            x: Starting x position
            y: Starting y position
            direction: -1 for left, 1 for right
        """
        super().__init__()
        
        # Bullet dimensions
        self.width = 16
        self.height = 12
        
        # Create bullet surface (teardrop rotated 90 degrees counterclockwise)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_bullet()
        
        # Position and movement
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction  # -1 for left, 1 for right
        self.speed = 10
        
        # Bullet properties
        self.damage = 1
        self.active = True
    
    def draw_bullet(self):
        """Draw a teardrop shape rotated 90 degrees counterclockwise (pointing right)."""
        # Teardrop pointing right (for right-facing bullets)
        # Points form a teardrop: rounded back, pointed front
        points = [
            (2, self.height // 2),           # Back left
            (4, 2),                           # Top curve
            (self.width // 2, 1),             # Top mid
            (self.width - 2, self.height // 2), # Tip (point)
            (self.width // 2, self.height - 1), # Bottom mid
            (4, self.height - 2)              # Bottom curve
        ]
        
        # Draw filled bullet (bright yellow/orange)
        pygame.draw.polygon(self.image, (255, 200, 0), points)
        # Draw outline for definition
        pygame.draw.polygon(self.image, (200, 150, 0), points, 2)
    
    def update(self, level_width, level_height):
        """Update bullet position and check if it's out of bounds."""
        # Move bullet
        self.rect.x += self.speed * self.direction
        
        # Deactivate if out of bounds
        if self.rect.right < 0 or self.rect.left > level_width:
            self.active = False
        if self.rect.bottom < 0 or self.rect.top > level_height:
            self.active = False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the bullet to the screen with camera offset."""
        if not self.active:
            return
        
        # Flip image if shooting left
        if self.direction < 0:
            flipped_image = pygame.transform.flip(self.image, True, False)
            screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)
            screen.blit(flipped_image, screen_pos)
        else:
            screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)
            screen.blit(self.image, screen_pos)
    
    def get_rect(self):
        """Return the bullet's rectangle for collision detection."""
        return self.rect
    
    def hit(self):
        """Mark bullet as inactive after hitting something."""
        self.active = False
