"""
Level class for the pygame project.
Handles level generation, background, obstacles, and progression.
"""

import pygame
import csv
import os
import random


class Level:
    """Tile-based level loaded from a CSV.

    CSV tile codes:
    . -> empty
    G -> ground (solid, full collision)
    D -> dirt (solid, full collision, plain dirt appearance)
    P -> platform (one-way: collides only from above)
    C -> collectible (placed on top of tile)
    E -> exit door (level completion point)
    B -> BasicEnemy spawn point
    J -> JumpingEnemy spawn point
    A -> AmbushEnemy spawn point
    Z -> BossEnemy spawn point

    The level is a grid of tiles. Tile size can be adjusted using `tile_size`.
    """

    def __init__(self, csv_path="levels/level1.csv", tile_size=64):
        self.csv_path = csv_path
        self.tile_size = tile_size
        self.background_color = (135, 206, 235)  # Sky blue

        # Storage for tiles
        self.tiles = []  # 2D list of tile codes
        self.solid_tiles = []  # list of pygame.Rect for G and D (ground and dirt)
        self.ground_tiles = []  # list of pygame.Rect for G (ground) specifically
        self.dirt_tiles = []  # list of pygame.Rect for D (dirt) specifically
        self.cobblestone_tiles = []  # list of pygame.Rect for S (cobblestone) specifically
        self.removable_tiles = []  # list of pygame.Rect for R (removable wooden planks)
        self.one_way_tiles = []  # list of pygame.Rect for P (platform)
        self.collectibles = []  # list of dicts: {'rect': Rect, 'collected': False}
        self.enemy_spawns = []  # list of dicts: {'x': x, 'y': y, 'type': enemy_type}
        self.exit_rect = None  # pygame.Rect for E (exit door)
        
        # Boss defeat tracking
        self.boss_defeated = False

        # Level pixel dimensions (computed after loading CSV)
        self.width = 0
        self.height = 0

        # Load CSV and build tile lists
        self.load_from_csv(self.csv_path)

        # Decorations (clouds/grass) are optional
        self.decorations = []
        self.generate_decorations()
    
    def load_from_csv(self, csv_path):
        """Load the tile grid from a CSV file.

        Each row in the CSV is a row of tiles. Files should be stored in `levels/`.
        """
        # Clear previous
        self.tiles = []
        self.solid_tiles = []
        self.ground_tiles = []
        self.dirt_tiles = []
        self.cobblestone_tiles = []
        self.removable_tiles = []
        self.one_way_tiles = []
        self.collectibles = []
        self.enemy_spawns = []
        self.exit_rect = None

        # Allow relative path
        base = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base, csv_path)

        if not os.path.exists(full_path):
            # If CSV is missing, create a very small default flat level
            cols = 40
            rows = 10
            for r in range(rows):
                row = ['.'] * cols
                if r == rows - 1:
                    row = ['G'] * cols
                self.tiles.append(row)
        else:
            with open(full_path, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    # strip spaces
                    self.tiles.append([cell.strip() for cell in row])

        # Compute grid and pixel dimensions
        self.rows = len(self.tiles)
        self.cols = max((len(r) for r in self.tiles), default=0)

        # Pad shorter rows with empty tiles so the grid is rectangular
        for r in self.tiles:
            if len(r) < self.cols:
                r.extend(['.'] * (self.cols - len(r)))

        # Update pixel dimensions from grid size
        self.width = self.cols * self.tile_size
        self.height = self.rows * self.tile_size

        # Build rect lists
        for r_index, row in enumerate(self.tiles):
            for c_index, code in enumerate(row):
                x = c_index * self.tile_size
                y = r_index * self.tile_size
                if code == 'G':
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    self.solid_tiles.append(rect)
                    self.ground_tiles.append(rect)
                elif code == 'D':
                    # Dirt block - same collision as ground but different appearance
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    self.solid_tiles.append(rect)
                    self.dirt_tiles.append(rect)
                elif code == 'S':
                    # Cobblestone - solid tile with cracked stone appearance
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    self.solid_tiles.append(rect)
                    self.cobblestone_tiles.append(rect)
                elif code == 'R':
                    # Removable wooden planks - removed after boss defeat
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    self.solid_tiles.append(rect)
                    self.removable_tiles.append(rect)
                elif code == 'P':
                    # Make platforms thin - only 8 pixels thick at the top
                    platform_thickness = 8
                    rect = pygame.Rect(x, y, self.tile_size, platform_thickness)
                    self.one_way_tiles.append(rect)
                elif code == 'C':
                    # collectible sits centered on tile
                    rect = pygame.Rect(x + self.tile_size//4, y + self.tile_size//4,
                                       self.tile_size//2, self.tile_size//2)
                    self.collectibles.append({'rect': rect, 'collected': False})
                elif code == 'B':
                    # BasicEnemy spawn point
                    spawn_x = x + self.tile_size // 2
                    spawn_y = y + self.tile_size // 2
                    self.enemy_spawns.append({'x': spawn_x, 'y': spawn_y, 'type': 'basic'})
                elif code == 'J':
                    # JumpingEnemy spawn point
                    spawn_x = x + self.tile_size // 2
                    spawn_y = y + self.tile_size // 2
                    self.enemy_spawns.append({'x': spawn_x, 'y': spawn_y, 'type': 'jumping'})
                elif code == 'A':
                    # AmbushEnemy spawn point
                    spawn_x = x + self.tile_size // 2
                    spawn_y = y + self.tile_size // 2
                    self.enemy_spawns.append({'x': spawn_x, 'y': spawn_y, 'type': 'ambush'})
                elif code == 'Z':
                    # BossEnemy spawn point
                    spawn_x = x + self.tile_size // 2
                    spawn_y = y + self.tile_size // 2
                    self.enemy_spawns.append({'x': spawn_x, 'y': spawn_y, 'type': 'boss'})
                elif code == 'E':
                    # Exit door - full tile size
                    self.exit_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
    
    def generate_decorations(self):
        """Generate simple clouds and grass decorations."""
        self.decorations = []
        num_clouds = random.randint(3, 6)
        for i in range(num_clouds):
            x = random.randint(0, max(0, self.width - 80))
            y = random.randint(50, 200)
            size = random.randint(30, 60)
            decoration = {'pos': (x, y), 'size': size, 'color': (255, 255, 255), 'type': 'cloud'}
            self.decorations.append(decoration)

        # Small grass decorations above ground tiles only (not dirt)
        for rect in self.ground_tiles:
            if random.random() < 0.2:
                decoration = {'pos': (rect.x + 8, rect.y - 8), 'size': 6, 'color': (34, 139, 34), 'type': 'grass'}
                self.decorations.append(decoration)
    
    def remove_boss_tiles(self):
        """Remove all removable tiles after boss is defeated."""
        if not self.boss_defeated:
            self.boss_defeated = True
            # Remove all removable tiles from solid_tiles
            for tile in self.removable_tiles:
                if tile in self.solid_tiles:
                    self.solid_tiles.remove(tile)
            print("Boss defeated! Removable tiles have been removed.")
    
    def update(self):
        """Update level state."""
        # Update any animated decorations here
        # For now, decorations are static
        pass
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the entire level to the screen with camera offset (no visibility culling)."""
        # Draw background
        screen.fill(self.background_color)

        # Decorations
        for decoration in self.decorations:
            pos_x, pos_y = decoration['pos']
            screen_x = pos_x - camera_x
            screen_y = pos_y - camera_y
            if decoration['type'] == 'cloud':
                size = decoration['size']
                pygame.draw.circle(screen, decoration['color'], (screen_x + size//2, screen_y + size//3), size//3)
                pygame.draw.circle(screen, decoration['color'], (screen_x + size//4, screen_y + size//2), size//4)
                pygame.draw.circle(screen, decoration['color'], (screen_x + size*3//4, screen_y + size//2), size//4)
            elif decoration['type'] == 'grass':
                for i in range(3):
                    pygame.draw.line(screen, decoration['color'], (screen_x + i*3, screen_y), (screen_x + i*3, screen_y - 5), 2)

        # Draw ground tiles (brown with grass on top)
        for rect in self.ground_tiles:
            screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
            pygame.draw.rect(screen, (139, 69, 19), screen_rect)
            grass_rect = pygame.Rect(screen_rect.x, screen_rect.y, screen_rect.width, 4)
            pygame.draw.rect(screen, (34, 139, 34), grass_rect)

        # Draw dirt tiles (plain brown, no grass)
        for rect in self.dirt_tiles:
            screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
            pygame.draw.rect(screen, (139, 69, 19), screen_rect)  # Darker brown for dirt
        
        # Draw cobblestone tiles (stone with cracks)
        for rect in self.cobblestone_tiles:
            screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
            
            # Base stone color (gray)
            pygame.draw.rect(screen, (120, 120, 130), screen_rect)
            
            # Draw darker border for depth
            pygame.draw.rect(screen, (80, 80, 90), screen_rect, 3)
            
            # Draw cracks for cobbled look
            crack_color = (70, 70, 80)
            
            # Vertical crack (left side)
            pygame.draw.line(screen, crack_color, 
                           (screen_rect.x + 8, screen_rect.y + 5),
                           (screen_rect.x + 6, screen_rect.y + 25), 2)
            
            # Diagonal crack (middle)
            pygame.draw.line(screen, crack_color,
                           (screen_rect.x + 20, screen_rect.y + 10),
                           (screen_rect.x + 45, screen_rect.y + 30), 2)
            
            # Horizontal crack (bottom)
            pygame.draw.line(screen, crack_color,
                           (screen_rect.x + 15, screen_rect.y + 50),
                           (screen_rect.x + 40, screen_rect.y + 48), 2)
            
            # Small crack (top right)
            pygame.draw.line(screen, crack_color,
                           (screen_rect.x + 50, screen_rect.y + 8),
                           (screen_rect.x + 55, screen_rect.y + 15), 2)
            
            # Add subtle texture spots
            texture_color = (100, 100, 110)
            pygame.draw.circle(screen, texture_color, 
                             (screen_rect.x + 30, screen_rect.y + 20), 3)
            pygame.draw.circle(screen, texture_color,
                             (screen_rect.x + 15, screen_rect.y + 40), 2)
            pygame.draw.circle(screen, texture_color,
                             (screen_rect.x + 50, screen_rect.y + 35), 2)
        
        # Draw removable wooden plank tiles (only if not removed yet)
        if not self.boss_defeated:
            for rect in self.removable_tiles:
                screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
                
                # Base wood color (light brown)
                pygame.draw.rect(screen, (160, 120, 80), screen_rect)
                
                # Draw darker wood grain lines (horizontal planks)
                plank_color = (120, 90, 60)
                for i in range(4):
                    y_offset = i * 16
                    pygame.draw.line(screen, plank_color,
                                   (screen_rect.x, screen_rect.y + y_offset),
                                   (screen_rect.x + screen_rect.width, screen_rect.y + y_offset), 2)
                
                # Draw vertical wood grain details
                for i in range(5):
                    x_offset = i * 13
                    pygame.draw.line(screen, plank_color,
                                   (screen_rect.x + x_offset, screen_rect.y),
                                   (screen_rect.x + x_offset, screen_rect.y + screen_rect.height), 1)
                
                # Draw nails/bolts at corners
                nail_color = (80, 80, 80)
                pygame.draw.circle(screen, nail_color,
                                 (screen_rect.x + 8, screen_rect.y + 8), 3)
                pygame.draw.circle(screen, nail_color,
                                 (screen_rect.x + screen_rect.width - 8, screen_rect.y + 8), 3)
                pygame.draw.circle(screen, nail_color,
                                 (screen_rect.x + 8, screen_rect.y + screen_rect.height - 8), 3)
                pygame.draw.circle(screen, nail_color,
                                 (screen_rect.x + screen_rect.width - 8, screen_rect.y + screen_rect.height - 8), 3)
                
                # Draw border for temporary look
                pygame.draw.rect(screen, (100, 70, 40), screen_rect, 2)

        # Draw platform tiles (one-way platforms)
        for rect in self.one_way_tiles:
            screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
            pygame.draw.rect(screen, (160, 82, 45), screen_rect)
            pygame.draw.rect(screen, (101, 67, 33), screen_rect, 2)

        # Draw exit door
        if self.exit_rect:
            screen_rect = pygame.Rect(self.exit_rect.x - camera_x, self.exit_rect.y - camera_y, 
                                     self.exit_rect.width, self.exit_rect.height)
            
            # Check if all collectibles are collected
            total = len(self.collectibles)
            collected = sum(1 for it in self.collectibles if it['collected'])
            all_collected = (total == 0) or (collected == total)
            
            # Draw door frame (dark wood)
            pygame.draw.rect(screen, (101, 67, 33), screen_rect)
            
            # Draw door (lighter wood or locked gray)
            door_inner = pygame.Rect(screen_rect.x + 4, screen_rect.y + 4, 
                                    screen_rect.width - 8, screen_rect.height - 8)
            if all_collected:
                pygame.draw.rect(screen, (139, 90, 43), door_inner)  # Unlocked - brown
            else:
                pygame.draw.rect(screen, (100, 100, 100), door_inner)  # Locked - gray
            
            # Draw door handle
            handle_x = screen_rect.x + screen_rect.width - 15
            handle_y = screen_rect.y + screen_rect.height // 2
            handle_color = (218, 165, 32) if all_collected else (150, 150, 150)
            pygame.draw.circle(screen, handle_color, (handle_x, handle_y), 4)
            
            # Draw lock icon or "EXIT" text
            font = pygame.font.Font(None, 24)
            if all_collected:
                text = font.render("EXIT", True, (255, 255, 255))
            else:
                # Draw lock symbol
                text = font.render("LOCKED", True, (200, 200, 200))
            text_rect = text.get_rect(center=(screen_rect.centerx, screen_rect.centery))
            screen.blit(text, text_rect)
        
        # Draw collectibles (crystals)
        for item in self.collectibles:
            if item['collected']:
                continue
            rect = item['rect']
            # Draw rhombus crystal
            center_x = rect.centerx - camera_x
            center_y = rect.centery - camera_y
            half_w = rect.width // 2
            half_h = rect.height // 2
            
            # Rhombus points: top, right, bottom, left
            crystal_points = [
                (center_x, center_y - half_h),  # top
                (center_x + half_w, center_y),   # right
                (center_x, center_y + half_h),   # bottom
                (center_x - half_w, center_y)    # left
            ]
            # Draw filled crystal (cyan/light blue)
            pygame.draw.polygon(screen, (0, 255, 255), crystal_points)
            # Draw crystal outline (darker blue)
            pygame.draw.polygon(screen, (0, 150, 200), crystal_points, 2)
            # Add shine effect
            shine_points = [
                (center_x - half_w // 3, center_y - half_h // 3),
                (center_x, center_y - half_h // 2),
                (center_x - half_w // 4, center_y)
            ]
            pygame.draw.polygon(screen, (200, 255, 255), shine_points)
        
        # Draw enemy spawn points (for debugging/development)
        # Uncomment this section if you want to see spawn markers visually
        # for spawn in self.enemy_spawns:
        #     spawn_x = spawn['x'] - camera_x
        #     spawn_y = spawn['y'] - camera_y
        #     color = {'basic': (255, 100, 100), 'jumping': (100, 255, 255), 'ambush': (255, 100, 255)}.get(spawn['type'], (255, 255, 255))
        #     pygame.draw.circle(screen, color, (spawn_x, spawn_y), 8)
        #     pygame.draw.circle(screen, (255, 255, 255), (spawn_x, spawn_y), 8, 2)
    
    def get_platforms(self):
        """Return two lists: solid tiles and one-way tiles (platforms)."""
        return self.solid_tiles, self.one_way_tiles
    
    def get_enemy_spawn_positions(self):
        """Return enemy spawn positions from CSV markers."""
        return self.enemy_spawns.copy()  # Return a copy to prevent external modification
    
    def is_exit_unlocked(self):
        """Check if all collectibles are collected to unlock the exit."""
        total = len(self.collectibles)
        collected = sum(1 for it in self.collectibles if it['collected'])
        return (total == 0) or (collected == total)
    
    def get_highest_ground_y(self, x_position):
        """Get the Y position of the highest ground or platform near the given x position.
        
        Returns the top Y coordinate of the highest tile within a reasonable range of x_position.
        If no ground is found, returns a default value near the bottom of the level.
        """
        search_range = 200  # Search within 200 pixels horizontally
        highest_y = self.height - 100  # Default fallback position
        
        # Check solid tiles (ground and dirt)
        for rect in self.solid_tiles:
            if abs(rect.centerx - x_position) <= search_range:
                if rect.top < highest_y:
                    highest_y = rect.top
        
        # Check one-way platforms
        for rect in self.one_way_tiles:
            if abs(rect.centerx - x_position) <= search_range:
                if rect.top < highest_y:
                    highest_y = rect.top
        
        return highest_y
    
    def get_level_number(self):
        """Return the current level number."""
        return self.level_number