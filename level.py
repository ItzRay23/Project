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
    P -> platform (one-way: collides only from above)
    C -> collectible (placed on top of tile)
    B -> BasicEnemy spawn point
    J -> JumpingEnemy spawn point
    A -> AmbushEnemy spawn point

    The level is a grid of tiles. Tile size can be adjusted using `tile_size`.
    """

    def __init__(self, csv_path="levels/level1.csv", tile_size=64):
        self.csv_path = csv_path
        self.tile_size = tile_size
        self.background_color = (135, 206, 235)  # Sky blue

        # Storage for tiles
        self.tiles = []  # 2D list of tile codes
        self.solid_tiles = []  # list of pygame.Rect for G (ground)
        self.one_way_tiles = []  # list of pygame.Rect for P (platform)
        self.collectibles = []  # list of dicts: {'rect': Rect, 'collected': False}
        self.enemy_spawns = []  # list of dicts: {'x': x, 'y': y, 'type': enemy_type}

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
        self.one_way_tiles = []
        self.collectibles = []
        self.enemy_spawns = []

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

        # Small grass decorations above solid tiles
        for rect in self.solid_tiles:
            if random.random() < 0.2:
                decoration = {'pos': (rect.x + 8, rect.y - 8), 'size': 6, 'color': (34, 139, 34), 'type': 'grass'}
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

        # Draw tiles (solid ground and one-way platforms)
        for rect in self.solid_tiles:
            if rect.right >= camera_x and rect.left <= camera_x + self.tile_size * 12:
                screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
                pygame.draw.rect(screen, (139, 69, 19), screen_rect)
                grass_rect = pygame.Rect(screen_rect.x, screen_rect.y, screen_rect.width, 4)
                pygame.draw.rect(screen, (34, 139, 34), grass_rect)

        for rect in self.one_way_tiles:
            if rect.right >= camera_x and rect.left <= camera_x + self.tile_size * 12:
                screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
                pygame.draw.rect(screen, (160, 82, 45), screen_rect)
                pygame.draw.rect(screen, (101, 67, 33), screen_rect, 2)

        # Draw collectibles
        for item in self.collectibles:
            if item['collected']:
                continue
            rect = item['rect']
            if rect.right >= camera_x and rect.left <= camera_x + self.tile_size * 12:
                screen_rect = pygame.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)
                pygame.draw.ellipse(screen, (255, 215, 0), screen_rect)  # Gold coin
        
        # Draw enemy spawn points (for debugging/development)
        # Uncomment this section if you want to see spawn markers visually
        for spawn in self.enemy_spawns:
            spawn_x = spawn['x'] - camera_x
            spawn_y = spawn['y'] - camera_y
            if -16 <= spawn_x <= 816 and -16 <= spawn_y <= 616:  # On screen check
                color = {'basic': (255, 100, 100), 'jumping': (100, 255, 255), 'ambush': (255, 100, 255)}.get(spawn['type'], (255, 255, 255))
                pygame.draw.circle(screen, color, (spawn_x, spawn_y), 8)
                pygame.draw.circle(screen, (255, 255, 255), (spawn_x, spawn_y), 8, 2)
    
    def get_platforms(self):
        """Return two lists: solid tiles and one-way tiles (platforms)."""
        return self.solid_tiles, self.one_way_tiles
    
    def get_enemy_spawn_positions(self):
        """Return enemy spawn positions from CSV markers."""
        return self.enemy_spawns.copy()  # Return a copy to prevent external modification
    
    def get_level_number(self):
        """Return the current level number."""
        return self.level_number