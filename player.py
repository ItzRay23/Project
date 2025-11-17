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
        self.was_on_ground = False  # Track previous ground state
        self.can_jump = True
        
        # Double jump mechanic
        self.has_double_jump = False  # Can use double jump (starts false, enabled after landing)
        self.jump_key_was_pressed = False  # Track jump key state for edge detection
        self.double_jump_grace_period = 500  # Time window after jumping when double jump is allowed (milliseconds)
        self.jump_start_time = 0  # When the player last jumped
        self.has_landed_since_jump = True  # Track if player has landed since last jump
        
        # Shooting mechanic
        self.shoot_key_was_pressed = False  # Track shoot key for edge detection
        self.shoot_cooldown = 300  # Milliseconds between shots
        self.last_shot_time = 0
        self.facing_direction = 1  # 1 for right, -1 for left (track which way player is facing)
        
        # Damage immunity
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1000  # 1 second in milliseconds
        
        # Dash mechanic
        self.dash_speed = 15  # Speed during dash
        self.dash_duration = 200  # Duration of dash in milliseconds
        self.dash_cooldown = 500  # Cooldown between dashes in milliseconds
        self.dash_grace_period = 100  # Time after leaving ground when dash is still allowed (milliseconds)
        self.is_dashing = False
        self.dash_start_time = 0
        self.last_dash_time = 0
        self.dash_direction = 0  # -1 for left, 1 for right, 0 for no dash
        self.last_grounded_time = 0  # Track when player was last on ground
        
        # Double-tap detection
        self.last_left_press_time = 0
        self.last_right_press_time = 0
        self.double_tap_window = 300  # Time window for double-tap in milliseconds
        self.left_key_was_pressed = False
        self.right_key_was_pressed = False
    
    def update(self, keys, solid_tiles, one_way_tiles, level_width, level_height):
        """Update player position and state.

        solid_tiles: list of Rect that are full solid (ground)
        one_way_tiles: list of Rect that are one-way platforms (collide only when falling)
        level_width/level_height: pixel bounds of the level for camera/clamp
        """
        current_time = pygame.time.get_ticks()
        
        # Track previous ground state
        self.was_on_ground = self.on_ground
        
        # Handle invulnerability timer
        if self.invulnerable:
            if current_time - self.invulnerable_time > self.invulnerable_duration:
                self.invulnerable = False
        
        # Handle dash duration
        if self.is_dashing:
            if current_time - self.dash_start_time > self.dash_duration:
                self.is_dashing = False
                self.dash_direction = 0

        # Remember previous position for one-way checks
        prev_rect = self.rect.copy()

        # Check for double-tap dash (only when recently grounded and not already dashing)
        if not self.is_dashing:
            dash_available = self.can_dash()
            
            # Check for left double-tap
            left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
            if left_pressed and not self.left_key_was_pressed:
                if dash_available and (current_time - self.last_left_press_time) < self.double_tap_window:
                    # Double-tap detected!
                    self.start_dash(-1)
                self.last_left_press_time = current_time
            self.left_key_was_pressed = left_pressed
            
            # Check for right double-tap
            right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            if right_pressed and not self.right_key_was_pressed:
                if dash_available and (current_time - self.last_right_press_time) < self.double_tap_window:
                    # Double-tap detected!
                    self.start_dash(1)
                self.last_right_press_time = current_time
            self.right_key_was_pressed = right_pressed

        # Reset horizontal velocity
        self.velocity_x = 0
        
        # Handle horizontal input (normal movement or dash)
        if self.is_dashing:
            # During dash, move at dash speed in dash direction
            self.velocity_x = self.dash_direction * self.dash_speed
            # Update facing direction based on dash
            if self.dash_direction != 0:
                self.facing_direction = self.dash_direction
        else:
            # Normal movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity_x = -self.speed
                self.facing_direction = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity_x = self.speed
                self.facing_direction = 1
        
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
        
        # Move horizontally and check collisions
        self.rect.x += self.velocity_x
        # horizontal collisions only against solid tiles (not platforms)
        self.check_horizontal_collisions(solid_tiles)

        # Move vertically and check collisions
        self.rect.y += self.velocity_y
        self.check_vertical_collisions(solid_tiles, one_way_tiles, prev_rect, level_height)

        # Keep player within level bounds horizontally and vertically
        self.rect.x = max(0, min(self.rect.x, level_width - self.width))
        self.rect.y = max(0, min(self.rect.y, level_height - self.height))
        
        # Handle jumping AFTER all collision and position updates are complete
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        
        if jump_pressed and not self.jump_key_was_pressed:
            # Jump key just pressed (edge detection)
            if self.on_ground:
                # Ground jump - always works when on ground
                self.velocity_y = self.jump_speed
                self.can_jump = False
                self.jump_start_time = current_time
                self.has_landed_since_jump = False
                # Enable double jump immediately after ground jump
                self.has_double_jump = True
            elif self.has_double_jump:
                # Double jump (air jump) - within grace period after first jump
                time_since_jump = current_time - self.jump_start_time
                if time_since_jump <= self.double_jump_grace_period:
                    self.velocity_y = self.jump_speed
                    self.has_double_jump = False
        
        self.jump_key_was_pressed = jump_pressed
    
    def check_horizontal_collisions(self, tiles):
        """Check for horizontal collisions with solid tiles only (platforms have no horizontal collision)."""
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
        was_grounded = self.on_ground
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
        
        # Additional check: if velocity is 0 and we were grounded last frame, stay grounded
        # This prevents flickering when standing still
        if self.velocity_y == 0 and was_grounded and not self.on_ground:
            # Do a quick check if there's ground below us (within 1 pixel)
            test_rect = self.rect.copy()
            test_rect.y += 1
            
            for tile in solid_tiles:
                if test_rect.colliderect(tile):
                    self.on_ground = True
                    self.can_jump = True
                    break
            
            if not self.on_ground:
                for tile in one_way_tiles:
                    if test_rect.colliderect(tile):
                        self.on_ground = True
                        self.can_jump = True
                        break
        
        # Update last grounded time when touching ground
        if self.on_ground:
            self.last_grounded_time = pygame.time.get_ticks()
            
            # Only process landing logic when transitioning from air to ground
            if not self.was_on_ground:
                # Just landed - mark as landed but don't change double jump state
                self.has_landed_since_jump = True
    
    def draw(self, screen, camera_x=0, camera_y=0, total_crystals=0, collected_crystals=0):
        """Draw the player to the screen with camera offset."""
        # Flash player when invulnerable
        if self.invulnerable:
            if (pygame.time.get_ticks() // 100) % 2:  # Flash every 100ms
                return
        
        # Change color when dashing for visual feedback
        if self.is_dashing:
            self.image.fill((255, 255, 0))  # Yellow during dash
        else:
            self.image.fill((0, 128, 255))  # Normal blue color
        
        # Draw eye on player
        self.draw_eye_on_sprite()
        
        # Draw player with camera offset
        screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)
        screen.blit(self.image, screen_pos)
        
        # Draw hearts (UI elements stay in fixed position)
        self.draw_hearts(screen)
        
        # Draw crystals UI
        if total_crystals > 0:
            self.draw_crystals(screen, total_crystals, collected_crystals)
        
        # Draw dash indicator
        self.draw_dash_indicator(screen)
        
        # Draw double jump indicator
        self.draw_double_jump_indicator(screen)
    
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
    
    def draw_eye_on_sprite(self):
        """Draw a simple white square eye on the player sprite"""
        # Position eye near the head area
        eye_size = 6  # Small square
        eye_x = self.width // 2 - eye_size // 2  # Center horizontally
        eye_y = 8  # Near the top (head area)
        
        # Offset eye based on movement direction
        offset = 6  # Pixels to offset
        
        # Horizontal offset
        if self.velocity_x > 0:  # Moving right
            eye_x += offset
        elif self.velocity_x < 0:  # Moving left
            eye_x -= offset
        else:
            # Use facing direction when not moving
            if self.facing_direction > 0:
                eye_x += offset
            else:
                eye_x -= offset
        
        # Vertical offset
        if self.velocity_y < 0:  # Moving up (jumping)
            eye_y -= offset
        elif self.velocity_y > 0:  # Moving down (falling)
            eye_y += offset
        
        # Draw white square eye directly on the sprite
        pygame.draw.rect(self.image, (255, 255, 255), (eye_x, eye_y, eye_size, eye_size))
    
    def draw_crystals(self, screen, total_crystals, collected_crystals):
        """Draw crystal collection status (similar to hearts)."""
        crystal_size = 16
        crystal_spacing = 22
        start_x = 10
        start_y = 85  # Below level name
        
        for i in range(total_crystals):
            x = start_x + i * crystal_spacing
            y = start_y
            
            # Rhombus points: top, right, bottom, left
            center_x = x + crystal_size // 2
            center_y = y + crystal_size // 2
            half_size = crystal_size // 2
            
            points = [
                (center_x, center_y - half_size),      # top
                (center_x + half_size, center_y),       # right
                (center_x, center_y + half_size),       # bottom
                (center_x - half_size, center_y)        # left
            ]
            
            if i < collected_crystals:
                # Collected crystal (filled cyan)
                pygame.draw.polygon(screen, (0, 255, 255), points)
                pygame.draw.polygon(screen, (0, 150, 200), points, 2)
                # Add shine
                shine = [
                    (center_x - half_size // 3, center_y - half_size // 3),
                    (center_x, center_y - half_size // 2),
                    (center_x - half_size // 4, center_y)
                ]
                pygame.draw.polygon(screen, (200, 255, 255), shine)
            else:
                # Uncollected crystal (outline only, gray)
                pygame.draw.polygon(screen, (128, 128, 128), points, 2)
    
    def draw_dash_indicator(self, screen):
        """Draw dash availability indicator."""
        # Position below hearts and level text
        indicator_x = 10
        indicator_y = 125
        indicator_width = 80
        indicator_height = 20
        
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), 
                        (indicator_x, indicator_y, indicator_width, indicator_height))
        
        if self.can_dash():
            # Dash ready - draw full green bar with pulsing effect
            pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500.0  # 0 to 1 pulse
            brightness = int(200 + 55 * pulse)  # Pulse between 200 and 255
            color = (0, brightness, 0)
            pygame.draw.rect(screen, color, 
                           (indicator_x + 2, indicator_y + 2, indicator_width - 4, indicator_height - 4))
            
            # Draw "DASH" text
            font = pygame.font.Font(None, 18)
            text = font.render("DASH", True, (255, 255, 255))
            text_rect = text.get_rect(center=(indicator_x + indicator_width // 2, indicator_y + indicator_height // 2))
            screen.blit(text, text_rect)
        else:
            # Dash not ready - show cooldown progress or air state
            current_time = pygame.time.get_ticks()
            time_since_dash = current_time - self.last_dash_time
            
            if time_since_dash < self.dash_cooldown:
                # Show cooldown progress
                progress = time_since_dash / self.dash_cooldown
                fill_width = int((indicator_width - 4) * progress)
                pygame.draw.rect(screen, (100, 100, 0), 
                               (indicator_x + 2, indicator_y + 2, fill_width, indicator_height - 4))
            else:
                # Check if within grace period
                current_time = pygame.time.get_ticks()
                recently_grounded = (current_time - self.last_grounded_time) <= self.dash_grace_period
                
                if not recently_grounded:
                    # In air beyond grace period - show red bar
                    pygame.draw.rect(screen, (150, 0, 0), 
                                   (indicator_x + 2, indicator_y + 2, indicator_width - 4, indicator_height - 4))
                    
                    # Draw "AIR" text
                    font = pygame.font.Font(None, 18)
                    text = font.render("AIR", True, (200, 200, 200))
                    text_rect = text.get_rect(center=(indicator_x + indicator_width // 2, indicator_y + indicator_height // 2))
                    screen.blit(text, text_rect)
        
        # Draw border
        pygame.draw.rect(screen, (200, 200, 200), 
                        (indicator_x, indicator_y, indicator_width, indicator_height), 2)
    
    def draw_double_jump_indicator(self, screen):
        """Draw double jump availability indicator."""
        # Position next to dash indicator
        indicator_x = 100  # Right of dash indicator
        indicator_y = 125
        indicator_width = 80
        indicator_height = 20
        
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), 
                        (indicator_x, indicator_y, indicator_width, indicator_height))
        
        # Determine state for display only (doesn't modify player state)
        if self.has_double_jump and not self.on_ground:
            # Double jump available in air - draw full blue bar with pulsing effect
            pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500.0  # 0 to 1 pulse
            brightness = int(150 + 105 * pulse)  # Pulse between 150 and 255
            color = (0, brightness, brightness)  # Cyan color
            pygame.draw.rect(screen, color, 
                           (indicator_x + 2, indicator_y + 2, indicator_width - 4, indicator_height - 4))
            
            # Draw "JUMP" text
            font = pygame.font.Font(None, 18)
            text = font.render("JUMP", True, (255, 255, 255))
            text_rect = text.get_rect(center=(indicator_x + indicator_width // 2, indicator_y + indicator_height // 2))
            screen.blit(text, text_rect)
        elif self.on_ground:
            # On ground - show ready state
            pygame.draw.rect(screen, (0, 100, 100), 
                           (indicator_x + 2, indicator_y + 2, indicator_width - 4, indicator_height - 4))
            
            # Draw "READY" text
            font = pygame.font.Font(None, 18)
            text = font.render("READY", True, (200, 200, 200))
            text_rect = text.get_rect(center=(indicator_x + indicator_width // 2, indicator_y + indicator_height // 2))
            screen.blit(text, text_rect)
        else:
            # In air without double jump - show unavailable
            pygame.draw.rect(screen, (80, 80, 80), 
                           (indicator_x + 2, indicator_y + 2, indicator_width - 4, indicator_height - 4))
            
            # Draw "USED" text
            font = pygame.font.Font(None, 18)
            text = font.render("USED", True, (150, 150, 150))
            text_rect = text.get_rect(center=(indicator_x + indicator_width // 2, indicator_y + indicator_height // 2))
            screen.blit(text, text_rect)
        
        # Draw border
        pygame.draw.rect(screen, (200, 200, 200), 
                        (indicator_x, indicator_y, indicator_width, indicator_height), 2)
    
    def can_dash(self):
        """Check if player can currently dash."""
        current_time = pygame.time.get_ticks()
        cooldown_ready = (current_time - self.last_dash_time) > self.dash_cooldown
        recently_grounded = (current_time - self.last_grounded_time) <= self.dash_grace_period
        return recently_grounded and not self.is_dashing and cooldown_ready
    
    def can_shoot(self):
        """Check if player can shoot (cooldown check)."""
        current_time = pygame.time.get_ticks()
        return (current_time - self.last_shot_time) > self.shoot_cooldown
    
    def shoot(self):
        """Create and return a bullet. Returns None if on cooldown."""
        if not self.can_shoot():
            return None
        
        # Create bullet from player position
        bullet_x = self.rect.centerx
        bullet_y = self.rect.centery
        
        # Update last shot time
        self.last_shot_time = pygame.time.get_ticks()
        
        # Return bullet info (game will create the actual bullet)
        return {'x': bullet_x, 'y': bullet_y, 'direction': self.facing_direction}
    
    def start_dash(self, direction):
        """Start a dash in the given direction (-1 for left, 1 for right)."""
        self.is_dashing = True
        self.dash_direction = direction
        self.dash_start_time = pygame.time.get_ticks()
        self.last_dash_time = self.dash_start_time
    
    def get_rect(self):
        """Return the player's rectangle for collision detection."""
        return self.rect
    
    def take_damage(self, damage=1):
        """Reduce player hearts by damage amount."""
        # Player is immune to damage while dashing or during invulnerability frames
        if not self.invulnerable and not self.is_dashing and self.hearts > 0:
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
        self.is_dashing = False
        self.dash_direction = 0
        self.has_double_jump = False
        self.has_landed_since_jump = True
        self.jump_start_time = 0