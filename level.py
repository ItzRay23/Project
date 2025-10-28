"""
Level class for the pygame project.
Handles level generation, background, obstacles, and progression.
"""

import pygame
import random

class Level:
    def __init__(self, level_number=1):
        """Initialize the level."""
        self.level_number = level_number
        self.background_color = (135, 206, 235)  # Sky blue background
        
        # Level dimensions (make it much longer for scrolling)
        self.width = 2400  # 3x longer than screen width
        self.height = 600
        self.ground_height = 50
        
        # Platforms
        self.platforms = []
        self.decorations = []
        
        # Generate level content
        self.generate_platforms()
        self.generate_decorations()
    
    def generate_platforms(self):
        """Generate Mario-style platforms for the level."""
        self.platforms = []
        
        # Ground platform (full width)
        ground = pygame.Rect(0, self.height - self.ground_height, self.width, self.ground_height)
        self.platforms.append(ground)
        
        # Add floating platforms across the longer level
        platform_data = [
            # First section (0-800)
            (200, 450, 120, 20),   # Low platform
            (400, 350, 100, 20),   # Mid platform
            (150, 250, 80, 20),    # High platform left
            (550, 200, 100, 20),   # High platform right
            (350, 150, 60, 20),    # Very high platform
            (600, 400, 80, 20),    # Another low platform
            (50, 350, 100, 20),    # Left side platform
            (650, 300, 120, 20),   # Right side platform
            
            # Second section (800-1600)
            (900, 400, 100, 20),   # Entry platform
            (1100, 300, 120, 20),  # Mid platform
            (850, 200, 80, 20),    # High left
            (1250, 250, 100, 20),  # High right
            (1000, 150, 60, 20),   # Very high
            (1400, 450, 150, 20),  # Long low platform
            (1200, 100, 80, 20),   # Very high platform
            (1500, 350, 100, 20),  # End section platform
            
            # Third section (1600-2400)
            (1700, 400, 120, 20),  # Entry platform
            (1900, 300, 100, 20),  # Mid platform
            (1650, 200, 80, 20),   # High left
            (2050, 250, 120, 20),  # High right
            (1800, 150, 60, 20),   # Very high
            (2200, 400, 100, 20),  # Low platform
            (2000, 100, 80, 20),   # Very high platform
            (2300, 350, 90, 20),   # Final platform
        ]
        
        for x, y, width, height in platform_data:
            platform = pygame.Rect(x, y, width, height)
            self.platforms.append(platform)
    
    def generate_decorations(self):
        """Generate decorative elements for the level."""
        self.decorations = []
        
        # Generate clouds in the background
        num_clouds = random.randint(3, 6)
        
        for i in range(num_clouds):
            x = random.randint(0, self.width - 80)
            y = random.randint(50, 200)
            size = random.randint(30, 60)
            
            decoration = {
                'pos': (x, y),
                'size': size,
                'color': (255, 255, 255),
                'type': 'cloud'
            }
            
            self.decorations.append(decoration)
        
        # Generate some grass decorations on platforms
        for platform in self.platforms[1:]:  # Skip ground platform
            if random.random() < 0.7:  # 70% chance to have grass
                grass_x = platform.x + random.randint(0, max(1, platform.width - 20))
                grass_y = platform.y - 8
                
                decoration = {
                    'pos': (grass_x, grass_y),
                    'size': 8,
                    'color': (34, 139, 34),
                    'type': 'grass'
                }
                
                self.decorations.append(decoration)
    
    def update(self):
        """Update level state."""
        # Update any animated decorations here
        # For now, decorations are static
        pass
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the level to the screen with camera offset."""
        # Draw background
        screen.fill(self.background_color)
        
        # Draw decorations with camera offset
        for decoration in self.decorations:
            pos_x, pos_y = decoration['pos']
            # Only draw if visible on screen
            if pos_x - camera_x >= -50 and pos_x - camera_x <= 850:
                if decoration['type'] == 'cloud':
                    # Draw simple cloud shape
                    size = decoration['size']
                    color = decoration['color']
                    screen_x = pos_x - camera_x
                    screen_y = pos_y - camera_y
                    
                    # Main cloud body
                    pygame.draw.circle(screen, color, (screen_x + size//2, screen_y + size//3), size//3)
                    pygame.draw.circle(screen, color, (screen_x + size//4, screen_y + size//2), size//4)
                    pygame.draw.circle(screen, color, (screen_x + size*3//4, screen_y + size//2), size//4)
                    
                elif decoration['type'] == 'grass':
                    # Draw simple grass
                    color = decoration['color']
                    screen_x = pos_x - camera_x
                    screen_y = pos_y - camera_y
                    for i in range(3):
                        pygame.draw.line(screen, color, 
                                       (screen_x + i*3, screen_y), 
                                       (screen_x + i*3, screen_y - 5), 2)
        
        # Draw platforms with camera offset
        for platform in self.platforms:
            # Only draw platforms that are visible on screen
            if platform.right >= camera_x and platform.left <= camera_x + 800:
                # Create screen-space rectangle
                screen_rect = pygame.Rect(platform.x - camera_x, platform.y - camera_y, 
                                        platform.width, platform.height)
                
                if platform == self.platforms[0]:  # Ground platform
                    pygame.draw.rect(screen, (139, 69, 19), screen_rect)  # Brown ground
                    # Add grass on top of ground
                    grass_rect = pygame.Rect(screen_rect.x, screen_rect.y, 
                                           screen_rect.width, 5)
                    pygame.draw.rect(screen, (34, 139, 34), grass_rect)
                else:
                    pygame.draw.rect(screen, (160, 82, 45), screen_rect)  # Brown platforms
                    # Add border to platforms
                    pygame.draw.rect(screen, (101, 67, 33), screen_rect, 2)
    
    def get_platforms(self):
        """Return list of platform rectangles for collision detection."""
        return self.platforms
    
    def get_enemy_spawn_positions(self):
        """Get valid enemy spawn positions on platforms."""
        spawn_positions = []
        
        # Spawn enemies on platforms (not on ground)
        for platform in self.platforms[1:]:  # Skip ground platform
            if platform.width >= 60:  # Only on platforms wide enough
                # Create patrol area for this platform
                patrol_start = platform.x + 16
                patrol_end = platform.x + platform.width - 16
                spawn_x = platform.x + platform.width // 2
                spawn_y = platform.y - 35  # Above the platform
                
                spawn_positions.append({
                    'x': spawn_x,
                    'y': spawn_y,
                    'patrol_start': patrol_start,
                    'patrol_end': patrol_end
                })
        
        return spawn_positions
    
    def get_level_number(self):
        """Return the current level number."""
        return self.level_number