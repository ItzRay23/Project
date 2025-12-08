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
        
        # Draw eye on the enemy
        self.draw_eye_on_sprite()
    
    def draw_eye_on_sprite(self):
        """Draw a simple white square eye on the enemy sprite"""
        # Position eye near the head area
        eye_size = 6  # Small square
        eye_x = self.width // 2 - eye_size // 2  # Center horizontally
        eye_y = 8  # Near the top (head area)
        
        # Offset eye based on movement direction
        offset = 6  # Pixels to offset
        
        # Horizontal offset based on direction
        if self.direction > 0:  # Moving right
            eye_x += offset
        else:  # Moving left
            eye_x -= offset
        
        # Vertical offset based on velocity
        if self.velocity_y < 0:  # Moving up (jumping)
            eye_y -= offset
        elif self.velocity_y > 0:  # Moving down (falling)
            eye_y += offset
        
        # Draw white square eye directly on the sprite
        pygame.draw.rect(self.image, (0, 0, 0), (eye_x, eye_y, eye_size, eye_size))
    
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
        
        # Recreate visual (including eye) each frame to reflect current state
        self.image.fill(self.color)
        self.draw_eye_on_sprite()
        
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
    """Enemy that hangs from platforms/blocks, dashes to detected player positions, stays there briefly, then returns to hanging position."""
    
    def __init__(self, x, y, solid_tiles=None, one_way_tiles=None):
        super().__init__(x, y)
        self.detection_range = 500  # How far the enemy can detect the player
        self.max_dash_distance = 500  # Maximum distance the enemy can dash
        self.is_attacking = False
        self.attack_cooldown = 0
        self.max_attack_cooldown = 180  # 3 seconds at 60fps
        self.dash_speed = 5  # Speed when dashing towards player
        self.return_speed = 2  # Speed when returning to original position
        self.is_returning = False
        self.has_gravity = False  # This enemy ignores gravity
        self.hanging_position = None  # Position where enemy hangs from platform
        self.attack_start_position = None  # Position where dash attack started
        self.target_position = None  # Where the player was detected (dash target)
        self.is_staying = False  # Whether enemy is staying at target position
        self.stay_timer = 0  # Timer for staying at target position
        self.stay_duration = 120  # How long to stay at target (2 seconds at 60fps)
        
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
        
        # Only reduce attack cooldown when enemy is back at original position (idle state)
        if (self.attack_cooldown > 0 and 
            not self.is_attacking and not self.is_staying and not self.is_returning):
            self.attack_cooldown -= 1
        
        # Check if player is in range and we can attack
        if (player_pos and self.attack_cooldown == 0 and 
            not self.is_attacking and not self.is_staying and not self.is_returning):
            
            player_x, player_y = player_pos
            distance_x = player_x - self.rect.centerx
            distance_y = player_y - self.rect.centery
            total_distance = (distance_x ** 2 + distance_y ** 2) ** 0.5
            
            # Only attack if player is within range, within expanding attack cone, and has clear path
            if (total_distance <= self.detection_range and 
                self.is_within_attack_cone(distance_x, distance_y) and
                self.has_clear_path_to_player(player_x, player_y, solid_tiles)):
                
                self.is_attacking = True
                
                # Store starting position for distance limiting
                self.attack_start_position = (self.rect.centerx, self.rect.centery)
                
                # Store the center position of the player (assuming player is 32x48)
                # This makes the ambush target the player's center instead of top-left corner
                player_width = 32
                player_height = 48
                player_center_x = player_x + player_width // 2
                player_center_y = player_y + player_height // 2
                
                # Limit target position to max_dash_distance from starting position
                target_distance_x = player_center_x - self.rect.centerx
                target_distance_y = player_center_y - self.rect.centery
                target_total_distance = math.sqrt(target_distance_x ** 2 + target_distance_y ** 2)
                
                # If target is beyond max dash distance, clamp it
                if target_total_distance > self.max_dash_distance:
                    # Scale down to max_dash_distance
                    scale = self.max_dash_distance / target_total_distance
                    player_center_x = self.rect.centerx + target_distance_x * scale
                    player_center_y = self.rect.centery + target_distance_y * scale
                
                self.target_position = (player_center_x, player_center_y)
                
                # Calculate dash direction towards the player's CENTER position
                distance_to_center_x = player_center_x - self.rect.centerx
                distance_to_center_y = player_center_y - self.rect.centery
                distance_to_center = math.sqrt(distance_to_center_x ** 2 + distance_to_center_y ** 2)
                
                if distance_to_center > 0:  # Avoid division by zero
                    direction_x = distance_to_center_x / distance_to_center
                    direction_y = distance_to_center_y / distance_to_center
                    
                    self.velocity_x = direction_x * self.dash_speed
                    self.velocity_y = direction_y * self.dash_speed
                
                self.attack_cooldown = self.max_attack_cooldown
        
        # If attacking, dash towards the target position
        if self.is_attacking and self.target_position and self.attack_start_position:
            target_x, target_y = self.target_position
            start_x, start_y = self.attack_start_position
            
            # Calculate distance from starting position (for range limit)
            distance_from_start_x = self.rect.centerx - start_x
            distance_from_start_y = self.rect.centery - start_y
            distance_from_start = math.sqrt(distance_from_start_x ** 2 + distance_from_start_y ** 2)
            
            # Calculate distance to target
            distance_to_target_x = target_x - self.rect.centerx
            distance_to_target_y = target_y - self.rect.centery
            distance_to_target = math.sqrt(distance_to_target_x ** 2 + distance_to_target_y ** 2)
            
            # Stop if we've reached the target OR exceeded max dash distance
            if distance_to_target <= 20 or distance_from_start >= self.max_dash_distance:
                self.is_attacking = False
                self.is_staying = True
                self.stay_timer = self.stay_duration
                self.velocity_x = 0
                self.velocity_y = 0
                self.attack_start_position = None
            else:
                # Check if next movement would overshoot the target
                next_x = self.rect.x + self.velocity_x
                next_y = self.rect.y + self.velocity_y
                next_center_x = next_x + self.width // 2
                next_center_y = next_y + self.height // 2
                
                next_distance_to_target_x = target_x - next_center_x
                next_distance_to_target_y = target_y - next_center_y
                next_distance_to_target = math.sqrt(next_distance_to_target_x ** 2 + next_distance_to_target_y ** 2)
                
                # If we would overshoot, just snap to target
                if next_distance_to_target > distance_to_target:
                    # We're about to overshoot, snap to target instead
                    self.rect.centerx = target_x
                    self.rect.centery = target_y
                    self.is_attacking = False
                    self.is_staying = True
                    self.stay_timer = self.stay_duration
                    self.velocity_x = 0
                    self.velocity_y = 0
                    self.attack_start_position = None
                else:
                    # Continue moving towards target
                    self.rect.x += self.velocity_x
                    self.rect.y += self.velocity_y
        
        # If staying at target position for a few seconds
        elif self.is_staying:
            # Count down the stay timer
            self.stay_timer -= 1
            
            # Stay motionless at current position
            self.velocity_x = 0
            self.velocity_y = 0
            
            # When timer expires, start returning
            if self.stay_timer <= 0:
                self.is_staying = False
                self.is_returning = True
                self.target_position = None  # Clear target
        
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


class BossBullet(pygame.sprite.Sprite):
    """Boss bullet projectile."""
    
    def __init__(self, x, y, velocity_x, velocity_y):
        """Initialize a boss bullet with specific velocity."""
        super().__init__()
        
        # Bullet dimensions
        self.width = 12
        self.height = 12
        
        # Create circular bullet
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 50, 50), (self.width // 2, self.height // 2), self.width // 2)
        pygame.draw.circle(self.image, (200, 0, 0), (self.width // 2, self.height // 2), self.width // 2, 2)
        
        # Position and movement
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        
        # Bullet properties
        self.damage = 1
        self.active = True
    
    def update(self, level_width, level_height):
        """Update bullet position."""
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Deactivate if out of bounds
        if (self.rect.right < -100 or self.rect.left > level_width + 100 or
            self.rect.bottom < -100 or self.rect.top > level_height + 100):
            self.active = False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the bullet to the screen with camera offset."""
        if not self.active:
            return
        
        screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)
        screen.blit(self.image, screen_pos)
    
    def get_rect(self):
        """Return the bullet's rectangle for collision detection."""
        return self.rect
    
    def hit(self):
        """Mark bullet as inactive after hitting something."""
        self.active = False


class BossEnemy(Enemy):
    """Boss enemy with three special attacks: jump-shoot, jump-slam, and ultimate circular barrage."""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # Boss is larger
        self.width = 64
        self.height = 64
        
        # Attack state
        self.current_attack = None
        self.attack_cooldown = 0
        self.min_attack_cooldown = 120  # 2 seconds between attacks
        self.attack_counter = 0  # Track number of attacks for ultimate timing
        
        # Jump-shoot attack
        self.jump_shoot_state = None  # 'jumping', 'shooting', 'landing'
        self.jump_shoot_bullets_fired = 0
        self.jump_shoot_fire_timer = 0
        
        # Jump-slam attack
        self.jump_slam_state = None  # 'jumping', 'slamming', 'recovering'
        self.slam_bullets_created = False
        self.slam_recovery_timer = 0
        
        # Ultimate attack
        self.ultimate_state = None  # 'rising', 'shooting', 'descending'
        self.ultimate_timer = 0
        self.ultimate_shoot_timer = 0
        self.ultimate_angle = 0
        self.ultimate_position = None  # Where boss rises to
        
        # Boss bullets sprite group
        self.bullets = pygame.sprite.Group()
        
    def setup_properties(self):
        """Set up boss properties."""
        self.speed = 0.8  # Slower movement
        self.health = 30  # Much more health
        self.max_health = 30
        self.damage = 2
        self.color = (150, 0, 150)  # Purple
        self.jump_force = -15  # Higher jumps
    
    def choose_attack(self):
        """Choose which attack to perform."""
        self.attack_counter += 1
        
        # Every 4th attack is ultimate
        if self.attack_counter % 4 == 0:
            return 'ultimate'
        else:
            # Randomly choose between jump-shoot and jump-slam
            return random.choice(['jump_shoot', 'jump_slam'])
    
    def update(self, solid_tiles, one_way_tiles, level_height, level_width, player_pos=None):
        """Update boss with attack patterns."""
        if not self.active:
            return
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update bullets
        for bullet in self.bullets:
            bullet.update(level_width, level_height)
            if not bullet.active:
                self.bullets.remove(bullet)
        
        # If no current attack and cooldown is done, choose new attack
        if self.current_attack is None and self.attack_cooldown == 0:
            self.current_attack = self.choose_attack()
            
            if self.current_attack == 'jump_shoot':
                self.jump_shoot_state = 'rising'
                self.jump_shoot_bullets_fired = 0
                self.jump_shoot_fire_timer = 0
                # Store target position (above player)
                if player_pos:
                    target_x = player_pos[0] - self.width // 2  # Center above player
                    target_y = player_pos[1] - 150  # 150 pixels above player
                else:
                    target_x = self.rect.x
                    target_y = self.rect.y - 150
                self.jump_shoot_target = (target_x, target_y)
                
            elif self.current_attack == 'jump_slam':
                self.jump_slam_state = 'jumping'
                self.velocity_y = self.jump_force * 0.8  # Slightly lower jump
                self.slam_bullets_created = False
                self.slam_recovery_timer = 0
                
            elif self.current_attack == 'ultimate':
                self.ultimate_state = 'rising'
                self.ultimate_timer = 0
                self.ultimate_shoot_timer = 0
                self.ultimate_angle = 0
                # Store target position (high in the air)
                self.ultimate_position = (self.rect.x, self.rect.y - 200)
        
        # Execute current attack
        if self.current_attack == 'jump_shoot':
            self.execute_jump_shoot(solid_tiles, one_way_tiles, level_height, level_width, player_pos)
        elif self.current_attack == 'jump_slam':
            self.execute_jump_slam(solid_tiles, one_way_tiles, level_height, level_width)
        elif self.current_attack == 'ultimate':
            self.execute_ultimate(solid_tiles, one_way_tiles, level_height, level_width)
        else:
            # Normal movement when not attacking
            self.normal_movement(solid_tiles, one_way_tiles, level_height, level_width)
    
    def normal_movement(self, solid_tiles, one_way_tiles, level_height, level_width):
        """Normal back-and-forth movement."""
        self.velocity_x = self.direction * self.speed
        
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
        
        # Move horizontally
        self.rect.x += self.velocity_x
        
        # Check boundaries and reverse
        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction *= -1
        elif self.rect.right >= level_width:
            self.rect.right = level_width
            self.direction *= -1
        
        self.check_horizontal_collisions(solid_tiles)
        
        # Move vertically
        self.rect.y += self.velocity_y
        self.check_vertical_collisions(solid_tiles, one_way_tiles, level_height)
    
    def execute_jump_shoot(self, solid_tiles, one_way_tiles, level_height, level_width, player_pos=None):
        """Execute jump and shoot attack: rise above player, hover and shoot, then fall."""
        # Stop velocities during controlled movement
        self.velocity_x = 0
        self.velocity_y = 0
        
        if self.jump_shoot_state == 'rising':
            # Continuously update target X position to follow player
            if player_pos:
                target_x = player_pos[0] - self.width // 2  # Center above player
                target_y = player_pos[1] - 150  # 150 pixels above player
                self.jump_shoot_target = (target_x, target_y)
            
            target_x, target_y = self.jump_shoot_target
            
            # Move horizontally toward player's current X position
            if abs(self.rect.x - target_x) > 5:
                if self.rect.x < target_x:
                    self.rect.x += 5
                else:
                    self.rect.x -= 5
            
            # Move vertically toward target
            if self.rect.y > target_y:
                self.rect.y -= 5
            else:
                # Reached hover position, start shooting
                self.jump_shoot_state = 'hovering'
        
        elif self.jump_shoot_state == 'hovering':
            # Continuously follow player's X position while hovering
            if player_pos:
                target_x = player_pos[0] - self.width // 2  # Center above player
                # Smoothly move toward player's X position
                if abs(self.rect.x - target_x) > 3:
                    if self.rect.x < target_x:
                        self.rect.x += 3
                    else:
                        self.rect.x -= 3
                else:
                    self.rect.x = target_x
            
            # Maintain hover height
            _, target_y = self.jump_shoot_target
            self.rect.y = target_y
            
            # Fire bullets
            self.jump_shoot_fire_timer += 1
            if self.jump_shoot_fire_timer >= 15 and self.jump_shoot_bullets_fired < 3:  # Fire every 0.25 seconds
                self.fire_bullet_spread()
                self.jump_shoot_bullets_fired += 1
                self.jump_shoot_fire_timer = 0
            
            # After firing all bullets, start falling
            if self.jump_shoot_bullets_fired >= 3:
                self.jump_shoot_state = 'falling'
        
        elif self.jump_shoot_state == 'falling':
            # Apply gravity and fall back down
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
            
            self.rect.y += self.velocity_y
            self.check_vertical_collisions(solid_tiles, one_way_tiles, level_height)
            
            # When landing, end attack
            if self.on_ground:
                self.current_attack = None
                self.jump_shoot_state = None
                self.attack_cooldown = self.min_attack_cooldown
                self.velocity_x = 0
                self.velocity_y = 0
    
    def fire_bullet_spread(self):
        """Fire 3 bullets in a spread pattern."""
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        # Three directions: down-left, down, down-right
        angles = [-45, 0, 45]  # Degrees from straight down
        bullet_speed = 6
        
        for angle_deg in angles:
            angle_rad = math.radians(angle_deg + 90)  # +90 because 0 degrees is right, we want down
            vel_x = bullet_speed * math.cos(angle_rad)
            vel_y = bullet_speed * math.sin(angle_rad)
            
            bullet = BossBullet(center_x, center_y, vel_x, vel_y)
            self.bullets.add(bullet)
    
    def execute_jump_slam(self, solid_tiles, one_way_tiles, level_height, level_width):
        """Execute jump and slam with horizontal projectiles shot while in air."""
        # Stop horizontal movement during attack
        self.velocity_x = 0
        
        if self.jump_slam_state == 'jumping':
            # Apply gravity
            self.velocity_y += self.gravity * 1.5  # Fall faster for slam
            if self.velocity_y > self.max_fall_speed * 1.5:
                self.velocity_y = self.max_fall_speed * 1.5
            
            self.rect.y += self.velocity_y
            self.check_vertical_collisions(solid_tiles, one_way_tiles, level_height)
            
            # Shoot bullets while falling (in the air)
            if self.velocity_y > 0 and not self.slam_bullets_created:  # Falling downward
                self.create_slam_projectiles()
                self.slam_bullets_created = True
            
            # When landing, go to recovery state
            if self.on_ground:
                self.jump_slam_state = 'slamming'
        
        elif self.jump_slam_state == 'slamming':
            # Stay on ground during recovery
            self.velocity_x = 0
            self.velocity_y = 0
            
            # Initialize recovery timer when entering this state
            if self.slam_recovery_timer == 0:
                self.slam_recovery_timer = 30  # 0.5 second recovery
            
            # Count down recovery
            self.slam_recovery_timer -= 1
            
            # End attack when recovery is complete
            if self.slam_recovery_timer <= 0:
                self.current_attack = None
                self.jump_slam_state = None
                self.slam_recovery_timer = 0  # Reset for next attack
                self.attack_cooldown = self.min_attack_cooldown
                self.velocity_x = 0
                self.velocity_y = 0
    
    def create_slam_projectiles(self):
        """Create horizontal projectiles on both sides after slam."""
        center_y = self.rect.centery
        
        # Create 3 bullets going left
        for i in range(3):
            bullet = BossBullet(self.rect.left, center_y + i * 8 - 8, -8, 0)
            self.bullets.add(bullet)
        
        # Create 3 bullets going right
        for i in range(3):
            bullet = BossBullet(self.rect.right, center_y + i * 8 - 8, 8, 0)
            self.bullets.add(bullet)
    
    def execute_ultimate(self, solid_tiles, one_way_tiles, level_height, level_width):
        """Execute ultimate attack: rise up and shoot bullets in circular pattern rapidly."""
        if self.ultimate_state == 'rising':
            # Stop all movement
            self.velocity_x = 0
            self.velocity_y = 0
            
            # Move upward to ultimate position
            target_x, target_y = self.ultimate_position
            
            # Move toward target
            if self.rect.y > target_y:
                self.rect.y -= 5
            else:
                self.ultimate_state = 'shooting'
                self.ultimate_timer = 180  # Shoot for 3 seconds
        
        elif self.ultimate_state == 'shooting':
            # Stay in place and shoot bullets in circle
            self.velocity_x = 0
            self.velocity_y = 0
            
            self.ultimate_shoot_timer += 1
            if self.ultimate_shoot_timer >= 5:  # Fire very rapidly
                self.fire_circular_bullet()
                self.ultimate_shoot_timer = 0
                self.ultimate_angle += 30  # Rotate pattern
            
            self.ultimate_timer -= 1
            if self.ultimate_timer <= 0:
                self.ultimate_state = 'descending'
        
        elif self.ultimate_state == 'descending':
            # Stop horizontal movement
            self.velocity_x = 0
            
            # Fall back down
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
            
            self.rect.y += self.velocity_y
            
            # Check collisions to detect landing
            self.check_vertical_collisions(solid_tiles, one_way_tiles, level_height)
            
            # When landed on ground, end attack
            if self.on_ground:
                self.velocity_y = 0
                self.velocity_x = 0
                self.current_attack = None
                self.ultimate_state = None
                self.attack_cooldown = self.min_attack_cooldown * 2  # Longer cooldown after ultimate
    
    def fire_circular_bullet(self):
        """Fire a bullet in the current angle direction."""
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        bullet_speed = 5
        angle_rad = math.radians(self.ultimate_angle)
        
        vel_x = bullet_speed * math.cos(angle_rad)
        vel_y = bullet_speed * math.sin(angle_rad)
        
        bullet = BossBullet(center_x, center_y, vel_x, vel_y)
        self.bullets.add(bullet)
    
    def get_bullets(self):
        """Return the bullets sprite group for collision detection."""
        return self.bullets
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the boss and its bullets."""
        # Draw bullets first (behind boss)
        for bullet in self.bullets:
            bullet.draw(screen, camera_x, camera_y)
        
        # Draw boss (calls parent draw which includes eye)
        super().draw(screen, camera_x, camera_y)