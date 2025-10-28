"""
Player class for the pygame project.
Handles player movement, rendering, and interactions.
"""

import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """Initialize the player."""
        super().__init__()
        
        # Player dimensions
        self.width = 32
        self.height = 48
        
        # Create player surface and rectangle
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 128, 255))  # Blue color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Player attributes - Heart-based health system
        self.hearts = 3
        self.max_hearts = 3
        
        # Physics attributes
        self.speed = 5
        self.jump_speed = -15
        self.gravity = 0.8
        self.max_fall_speed = 15
        
        # Movement state
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.can_jump = True
        
        # Damage immunity
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1000  # 1 second in milliseconds
    
    def update(self, keys, solid_tiles, one_way_tiles, level_width, level_height):
        """Update player position and state.

        solid_tiles: list of Rect that are full solid (ground)
        one_way_tiles: list of Rect that are one-way platforms (collide only when falling)
        level_width/level_height: pixel bounds of the level for camera/clamp
        """
        # Handle invulnerability timer
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_time > self.invulnerable_duration:
                self.invulnerable = False

        # Remember previous position for one-way checks
        prev_rect = self.rect.copy()

        # Reset horizontal velocity
        self.velocity_x = 0
        
        # Handle horizontal input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
        
        # Handle jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground and self.can_jump:
            self.velocity_y = self.jump_speed
            self.on_ground = False
            self.can_jump = False
        
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
        
        # Move horizontally and check collisions
        self.rect.x += self.velocity_x
        # horizontal collisions against both solid and one-way platforms
        self.check_horizontal_collisions(solid_tiles + one_way_tiles)

        # Move vertically and check collisions
        self.rect.y += self.velocity_y
        self.check_vertical_collisions(solid_tiles, one_way_tiles, prev_rect, level_height)

        # Keep player within level bounds horizontally and vertically
        self.rect.x = max(0, min(self.rect.x, level_width - self.width))
        self.rect.y = max(0, min(self.rect.y, level_height - self.height))
    
    def check_horizontal_collisions(self, tiles):
        """Check for horizontal collisions with tiles (solid or platforms)."""
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = tile.left
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = tile.right
    
    def check_vertical_collisions(self, solid_tiles, one_way_tiles, prev_rect, level_height):
        """Vertical collision resolving.

        - Solid tiles (ground) always block both up and down.
        - One-way tiles only block when falling (velocity_y > 0) and the player's previous bottom was <= tile.top
        """
        self.on_ground = False

        # First check collisions with solid tiles
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.velocity_y > 0:  # falling
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.can_jump = True
                elif self.velocity_y < 0:  # moving up
                    self.rect.top = tile.bottom
                    self.velocity_y = 0

        # Then check one-way platforms: only when falling and crossing from above
        for tile in one_way_tiles:
            if self.rect.colliderect(tile):
                # Only if moving downwards and previous bottom was above the platform top
                if self.velocity_y > 0 and prev_rect.bottom <= tile.top:
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.can_jump = True

        # Clamp to level bottom
        if self.rect.bottom >= level_height:
            self.rect.bottom = level_height
            self.velocity_y = 0
            self.on_ground = True
            self.can_jump = True
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the player to the screen with camera offset."""
        # Flash player when invulnerable
        if self.invulnerable:
            if (pygame.time.get_ticks() // 100) % 2:  # Flash every 100ms
                return
        
        # Draw player with camera offset
        screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)
        screen.blit(self.image, screen_pos)
        
        # Draw hearts (UI elements stay in fixed position)
        self.draw_hearts(screen)
    
    def draw_hearts(self, screen):
        """Draw player's hearts (health)."""
        heart_size = 20
        heart_spacing = 25
        start_x = 10
        start_y = 10
        
        for i in range(self.max_hearts):
            x = start_x + i * heart_spacing
            y = start_y
            
            if i < self.hearts:
                # Full heart (red)
                pygame.draw.polygon(screen, (255, 0, 0), [
                    (x + 8, y + 6), (x + 4, y + 2), (x, y + 6),
                    (x, y + 10), (x + 8, y + 18), (x + 16, y + 10),
                    (x + 16, y + 6), (x + 12, y + 2)
                ])
            else:
                # Empty heart (gray outline)
                pygame.draw.polygon(screen, (128, 128, 128), [
                    (x + 8, y + 6), (x + 4, y + 2), (x, y + 6),
                    (x, y + 10), (x + 8, y + 18), (x + 16, y + 10),
                    (x + 16, y + 6), (x + 12, y + 2)
                ], 2)
    
    def get_rect(self):
        """Return the player's rectangle for collision detection."""
        return self.rect
    
    def take_damage(self, damage=1):
        """Reduce player hearts by damage amount."""
        if not self.invulnerable and self.hearts > 0:
            self.hearts -= damage
            if self.hearts < 0:
                self.hearts = 0
            
            # Make player invulnerable for a short time
            self.invulnerable = True
            self.invulnerable_time = pygame.time.get_ticks()
    
    def heal(self, hearts=1):
        """Restore player hearts."""
        self.hearts += hearts
        if self.hearts > self.max_hearts:
            self.hearts = self.max_hearts
    
    def is_alive(self):
        """Check if player is still alive."""
        return self.hearts > 0
    
    def get_position(self):
        """Return player's current position."""
        return (self.rect.x, self.rect.y)
    
    def set_position(self, x, y):
        """Set player's position."""
        self.rect.x = x
        self.rect.y = y
    
    def reset_position(self, x, y):
        """Reset player to starting position with full health."""
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.hearts = self.max_hearts
        self.invulnerable = False