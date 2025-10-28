"""
Enemy classes for the pygame project.
Base Enemy class with inheritance for different enemy types.
"""

import pygame
import random

class Enemy(pygame.sprite.Sprite):
    """Base enemy class with common functionality."""
    
    def __init__(self, x, y):
        """Initialize the base enemy."""
        super().__init__()
        
        # Default dimensions (can be overridden by subclasses)
        self.width = 32
        self.height = 32
        
        # Create enemy surface and rectangle
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Default properties (should be overridden by subclasses)
        self.speed = 1
        self.health = 1
        self.max_health = 1
        self.damage = 1
        self.color = (255, 0, 0)  # Default red
        
        # Movement - enemies will change direction on collision
        self.direction = 1  # 1 for right, -1 for left
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.8
        self.max_fall_speed = 10
        self.on_ground = False
        
        # State
        self.active = True
        
        # Setup this specific enemy type
        self.setup_properties()
        self.create_visual()
    
    def setup_properties(self):
        """Set up enemy-specific properties. Override in subclasses."""
        pass
    
    def create_visual(self):
        """Create the visual representation. Override in subclasses."""
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.x  # Preserve position
        self.rect.y = self.rect.y
    
    def get_movement_behavior(self):
        """Get movement behavior for this enemy type. Override in subclasses."""
        return self.direction * self.speed
    
    def update(self, solid_tiles, one_way_tiles, level_height, level_width):
        """Update enemy position and behavior.

        Enemies treat platforms as solid.
        """
        if not self.active:
            return

        # Get movement behavior (can be overridden by subclasses)
        self.velocity_x = self.get_movement_behavior()

        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed

        # Move horizontally
        self.rect.x += self.velocity_x

        # Check level boundaries and reverse direction if at edge
        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction *= -1
        elif self.rect.right >= level_width:
            self.rect.right = level_width
            self.direction *= -1

        # Check horizontal tile collisions (solid + one-way treated as solid)
        # Direction changes will happen in check_horizontal_collisions
        self.check_horizontal_collisions(solid_tiles + one_way_tiles)

        # Move vertically
        self.rect.y += self.velocity_y

        # Check vertical collisions
        self.check_vertical_collisions(solid_tiles + one_way_tiles, level_height)
    
    def check_horizontal_collisions(self, tiles):
        """Check for horizontal collisions with tiles (treat platforms as solid)."""
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = tile.left
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = tile.right
                self.direction *= -1  # Reverse direction on collision
    
    def check_vertical_collisions(self, tiles, level_height):
        """Check vertical collisions with tiles (treat platforms as solid)."""
        self.on_ground = False

        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = tile.bottom
                    self.velocity_y = 0

        # Clamp to level bottom
        if self.rect.bottom >= level_height:
            self.rect.bottom = level_height
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


class BasicEnemy(Enemy):
    """Basic enemy with simple left-right movement."""
    
    def setup_properties(self):
        """Set up basic enemy properties."""
        self.speed = 1
        self.health = 1
        self.max_health = 1
        self.damage = 1
        self.color = (255, 0, 0)  # Red


class AmbushEnemy(Enemy):
    """Enemy that sticks to platforms and jumps down to attack the player."""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.detection_range = 80  # How far the enemy can detect the player
        self.attack_range = 100    # How far the enemy will jump to attack
        self.is_attacking = False
        self.attack_cooldown = 0
        self.max_attack_cooldown = 120  # 2 seconds at 60fps
        self.original_platform_y = y  # Remember original platform position
        self.patrol_distance = 32  # Small patrol distance on platform
        self.patrol_center_x = x   # Center of patrol area
        
    def setup_properties(self):
        """Set up ambush enemy properties."""
        self.speed = 0.5  # Slow patrol speed
        self.health = 2
        self.max_health = 2
        self.damage = 1
        self.color = (139, 0, 139)  # Dark magenta
    
    def get_movement_behavior(self):
        """Ambush movement behavior - patrol platform and attack when player is near."""
        # Reduce attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # If currently attacking, don't change horizontal movement
        if self.is_attacking:
            return 0
        
        # Normal patrol behavior on platform
        # Check if we've moved too far from patrol center
        if abs(self.rect.centerx - self.patrol_center_x) > self.patrol_distance:
            self.direction *= -1  # Reverse direction
            
        return self.direction * self.speed
    
    def update(self, solid_tiles, one_way_tiles, level_height, level_width, player_pos=None):
        """Update with player detection for ambush attacks."""
        if not self.active:
            return
        
        # Check if player is in range and we can attack
        if (player_pos and self.attack_cooldown == 0 and 
            not self.is_attacking and self.on_ground):
            
            player_x, player_y = player_pos
            distance_x = abs(player_x - self.rect.centerx)
            distance_y = abs(player_y - self.rect.centery)
            
            # If player is below and within range, jump down to attack
            if (distance_x <= self.detection_range and 
                player_y > self.rect.centery and 
                distance_y <= self.attack_range):
                
                self.is_attacking = True
                self.velocity_y = -8  # Jump down with some initial upward velocity
                # Jump towards player
                if player_x > self.rect.centerx:
                    self.velocity_x = 3
                else:
                    self.velocity_x = -3
                
                self.attack_cooldown = self.max_attack_cooldown
        
        # Call parent update
        super().update(solid_tiles, one_way_tiles, level_height, level_width)
        
        # Reset attacking state when landing
        if self.is_attacking and self.on_ground and self.velocity_y == 0:
            self.is_attacking = False


class JumpingEnemy(Enemy):
    """Enemy that occasionally jumps while moving back and forth."""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_timer = 0
        self.jump_interval = random.randint(90, 150)  # 1.5-2.5 seconds at 60fps
        self.jump_force = -10  # Moderate jump height
    
    def setup_properties(self):
        """Set up jumping enemy properties."""
        self.speed = 1.2  # Moderate speed
        self.health = 1
        self.max_health = 1
        self.damage = 1
        self.color = (0, 255, 255)  # Cyan
    
    def get_movement_behavior(self):
        """Movement with occasional jumping."""
        self.jump_timer += 1
        
        # Jump occasionally if on ground
        if self.on_ground and self.jump_timer >= self.jump_interval:
            self.velocity_y = self.jump_force
            self.jump_timer = 0
            # Randomize next jump interval
            self.jump_interval = random.randint(90, 150)
        
        return self.direction * self.speed