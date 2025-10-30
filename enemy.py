"""
Enemy classes for the pygame project.
Base Enemy class with inheritance for different enemy types.
"""

import pygame
import random
import math

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
        # Store current position before creating new rect
        old_x = self.rect.x if hasattr(self, 'rect') else 0
        old_y = self.rect.y if hasattr(self, 'rect') else 0
        
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        
        # Restore position after creating new rect
        self.rect.x = old_x
        self.rect.y = old_y
    
    def get_movement_behavior(self):
        """Get movement behavior for this enemy type. Override in subclasses."""
        return self.direction * self.speed
    
    def update(self, solid_tiles, one_way_tiles, level_height, level_width):
        """Update enemy position and behavior.

        Solid tiles block movement in all directions.
        One-way platforms only block vertical movement from above.
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

        # Check horizontal tile collisions (only solid tiles, not one-way platforms)
        # Direction changes will happen in check_horizontal_collisions
        self.check_horizontal_collisions(solid_tiles)

        # Move vertically
        self.rect.y += self.velocity_y

        # Check vertical collisions
        self.check_vertical_collisions(solid_tiles, one_way_tiles, level_height)
    
    def check_horizontal_collisions(self, tiles):
        """Check for horizontal collisions with solid tiles only (platforms ignore horizontal collision)."""
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = tile.left
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = tile.right
                self.direction *= -1  # Reverse direction on collision
    
    def check_vertical_collisions(self, solid_tiles, one_way_tiles, level_height):
        """Check vertical collisions. Solid tiles block all directions, platforms only block from above."""
        self.on_ground = False

        # Check solid tiles (full collision)
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Moving up
                    self.rect.top = tile.bottom
                    self.velocity_y = 0

        # Check one-way platforms (only block when falling onto them from above)
        for tile in one_way_tiles:
            if self.rect.colliderect(tile):
                if self.velocity_y > 0:  # Only when falling
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True

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
    """Enemy that hangs from platforms/blocks and ambushes players within an expanding 75-degree cone below itself."""
    
    def __init__(self, x, y, solid_tiles=None, one_way_tiles=None):
        super().__init__(x, y)
        self.detection_range = 500  # How far the enemy can detect the player
        self.attack_range = 500   # How far the enemy will dash to attack
        self.is_attacking = False
        self.attack_cooldown = 0
        self.max_attack_cooldown = 180  # 3 seconds at 60fps
        self.dash_speed = 5  # Speed when dashing towards player
        self.return_speed = 2  # Speed when returning to original position
        self.is_returning = False
        self.has_gravity = False  # This enemy ignores gravity
        self.hanging_position = None  # Position where enemy hangs from platform
        
        # Find platform/block to hang from during initialization
        if solid_tiles is not None or one_way_tiles is not None:
            self.find_hanging_position(x, y, solid_tiles or [], one_way_tiles or [])
        else:
            # Fallback to original position if no tiles provided
            self.hanging_position = (x, y)
        
        self.original_position = self.hanging_position  # Remember hanging position
        
    def find_hanging_position(self, spawn_x, spawn_y, solid_tiles, one_way_tiles):
        """Find the nearest platform or block above the spawn point to hang from."""
        all_tiles = solid_tiles + one_way_tiles
        search_radius = 200  # How far to search for platforms/blocks
        closest_tile = None
        closest_distance = float('inf')
        
        # Search for tiles within range and above the spawn point
        for tile in all_tiles:
            # Check if tile is within horizontal search range
            if abs(tile.centerx - spawn_x) <= search_radius:
                # Check if tile is above the spawn point
                if tile.bottom <= spawn_y:
                    # Calculate distance to this tile
                    distance = ((tile.centerx - spawn_x) ** 2 + (tile.bottom - spawn_y) ** 2) ** 0.5
                    
                    # Keep track of closest tile
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_tile = tile
        
        if closest_tile:
            # Position enemy to hang from the bottom of the closest tile
            hang_x = closest_tile.centerx - self.width // 2
            hang_y = closest_tile.bottom  # Top of enemy touches bottom of tile
            self.hanging_position = (hang_x, hang_y)
            
            # Update enemy position immediately
            self.rect.x = hang_x
            self.rect.y = hang_y
        else:
            # No suitable platform found, use original spawn position
            self.hanging_position = (spawn_x, spawn_y)
            self.rect.x = spawn_x
            self.rect.y = spawn_y

    def is_within_attack_cone(self, distance_x, distance_y):
        """Check if the player is within the 75-degree expanding cone below the enemy."""
        # Only check if player is below the enemy (distance_y must be positive)
        if distance_y <= 0:
            return False
        
        # Calculate the cone boundaries at the player's distance
        # The cone expands as it gets further from the enemy
        player_distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
        
        # 75-degree cone means 37.5 degrees on each side of straight down
        half_cone_angle_radians = math.radians(37.5)
        
        # Calculate the maximum horizontal distance allowed at this vertical distance
        # Using trigonometry: tan(angle) = opposite/adjacent = horizontal_distance/vertical_distance
        max_horizontal_distance = distance_y * math.tan(half_cone_angle_radians)
        
        # Check if the player is within the cone boundaries
        return abs(distance_x) <= max_horizontal_distance
    
    def has_clear_path_to_player(self, player_x, player_y, solid_tiles):
        """Check if there's a clear path to the player through solid blocks (platforms are ignored)."""
        # Calculate the path from enemy to player
        start_x, start_y = self.rect.centerx, self.rect.centery
        end_x, end_y = player_x, player_y
        
        # Use line-of-sight checking with multiple sample points along the path
        num_checks = 10  # Number of points to check along the path
        
        for i in range(1, num_checks + 1):
            # Calculate intermediate point along the line from enemy to player
            t = i / num_checks  # Parameter from 0 to 1
            check_x = start_x + t * (end_x - start_x)
            check_y = start_y + t * (end_y - start_y)
            
            # Create a small rect for this check point
            check_rect = pygame.Rect(check_x - 5, check_y - 5, 10, 10)
            
            # Check if this point intersects with any solid tiles (not platforms)
            for tile in solid_tiles:
                if check_rect.colliderect(tile):
                    return False  # Path is blocked by solid tile
        
        return True  # Clear path found
    
    def setup_properties(self):
        """Set up ambush enemy properties."""
        self.speed = 0  # No normal movement speed
        self.health = 2
        self.max_health = 2
        self.damage = 2  # Higher damage since it's an ambush attack
        self.color = (139, 0, 139)  # Dark magenta
    
    def get_movement_behavior(self):
        """Ambush movement behavior - no normal movement, only dashing."""
        # Reduce attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # No normal movement - this enemy stays in place when not attacking
        return 0
    
    def update(self, solid_tiles, one_way_tiles, level_height, level_width, player_pos=None):
        """Update with player detection for ambush dash attacks from below only."""
        if not self.active:
            return
        
        # Reduce attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Check if player is in range and we can attack
        if (player_pos and self.attack_cooldown == 0 and 
            not self.is_attacking and not self.is_returning):
            
            player_x, player_y = player_pos
            distance_x = player_x - self.rect.centerx
            distance_y = player_y - self.rect.centery
            total_distance = (distance_x ** 2 + distance_y ** 2) ** 0.5
            
            # Only attack if player is within range, within expanding attack cone, and has clear path
            if (total_distance <= self.detection_range and 
                self.is_within_attack_cone(distance_x, distance_y) and
                self.has_clear_path_to_player(player_x, player_y, solid_tiles)):
                
                self.is_attacking = True
                
                # Calculate dash direction towards player
                if total_distance > 0:  # Avoid division by zero
                    direction_x = distance_x / total_distance
                    direction_y = distance_y / total_distance
                    
                    self.velocity_x = direction_x * self.dash_speed
                    self.velocity_y = direction_y * self.dash_speed
                
                self.attack_cooldown = self.max_attack_cooldown
        
        # If attacking, continue dash movement (no gravity applied)
        if self.is_attacking:
            # Move with current velocity
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y
            
            # Check if we've moved far enough or hit something, then start returning
            original_x, original_y = self.original_position
            distance_from_start = ((self.rect.centerx - original_x) ** 2 + 
                                 (self.rect.centery - original_y) ** 2) ** 0.5
            
            if distance_from_start > self.attack_range:
                self.is_attacking = False
                self.is_returning = True
        
        # If returning to original hanging position
        elif self.is_returning:
            hang_x, hang_y = self.hanging_position
            
            # Calculate direction back to hanging position
            distance_x = hang_x - self.rect.x
            distance_y = hang_y - self.rect.y
            total_distance = (distance_x ** 2 + distance_y ** 2) ** 0.5
            
            if total_distance > 5:  # If not close enough to hanging position
                direction_x = distance_x / total_distance
                direction_y = distance_y / total_distance
                
                self.velocity_x = direction_x * self.return_speed
                self.velocity_y = direction_y * self.return_speed
                
                self.rect.x += self.velocity_x
                self.rect.y += self.velocity_y
            else:
                # Close enough to hanging position, snap back and stop
                self.rect.x = hang_x
                self.rect.y = hang_y
                self.velocity_x = 0
                self.velocity_y = 0
                self.is_returning = False
        
        # When idle, stay at hanging position (no gravity)
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            # Ensure enemy stays at hanging position when idle
            if self.hanging_position:
                hang_x, hang_y = self.hanging_position
                self.rect.x = hang_x
                self.rect.y = hang_y
        
        # Check collisions with tiles only when not in attack/return mode
        if not self.is_attacking and not self.is_returning:
            # Check level boundaries
            if self.rect.left <= 0:
                self.rect.left = 0
            elif self.rect.right >= level_width:
                self.rect.right = level_width
            
            if self.rect.top <= 0:
                self.rect.top = 0
            elif self.rect.bottom >= level_height:
                self.rect.bottom = level_height


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