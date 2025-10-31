# 2D Platformer Game

A 2D platformer game built with pygame featuring physics-based movement, multiple enemy types, and CSV-based level design.

## Project Structure

- `main.py` - Main game class with game loop, camera system, and collision handling
- `player.py` - Player class with platformer physics, heart-based health, and invulnerability frames
- `enemy.py` - Base enemy class with three specialized enemy types and AI behaviors
- `level.py` - CSV-based level loader with tile system and decoration generation
- `levels/level1.csv` - Level data file defining platforms, enemies, and collectibles
- `requirements.txt` - Python dependencies

## Features Implemented

### Player System (`player.py`)

- **Movement**: WASD/Arrow keys with acceleration-based physics
- **Jumping**: Space/Up/W keys with ground detection and jump buffering
- **Health System**: 3 hearts with visual heart display in top-left
- **Damage System**: 1-second invulnerability frames with flashing effect
- **Physics**: Gravity, maximum fall speed, and ground collision detection
- **Platform Support**: Distinguishes between solid ground and one-way platforms
- **Camera Integration**: Player position drives camera movement

### Enemy System (`enemy.py`)

Three distinct enemy types with inheritance-based design:

- **BasicEnemy**: Simple red enemies that patrol left-right, reversing on collisions
- **JumpingEnemy**: Cyan enemies that jump periodically while patrolling (1.5-2.5 second intervals)
- **AmbushEnemy**: Dark magenta enemies that patrol platforms and jump down to attack when player is detected within range (80 pixels detection, 100 pixel attack range)

**Shared Enemy Features**:

- Physics-based movement with gravity and collision detection
- Health system with visual health bars when damaged
- Platform collision (treat one-way platforms as solid)
- Screen boundary detection with direction reversal

### Level System (`level.py`)

- **CSV-Based Design**: Levels defined in CSV files with tile codes
- **Tile Types**:
  - `G` = Solid ground (full collision)
  - `P` = One-way platforms (collision only from above, 8px thick)
  - `C` = Collectible items (gold coins)
  - `B/J/A` = Enemy spawn points (Basic/Jumping/Ambush)
- **Visual Elements**:
  - Brown ground tiles with green grass tops
  - Wooden-textured platforms with borders
  - Procedurally generated cloud decorations
  - Small grass decorations on solid tiles
- **Collectible System**: Gold coin pickups with collection tracking

### Main Game System (`main.py`)

- **Camera System**: Smooth camera following with level boundary constraints
- **Game States**: Running, game over, and restart functionality
- **Collision Detection**: Player-enemy damage system with invulnerability frames
- **UI Elements**:
  - Heart-based health display (fixed position)
  - Collectible counter (e.g., "Collected: 2/3")
  - Game over screen with restart option
- **Performance**: 60 FPS with efficient rendering and collision detection

## How to Run

1. Make sure you have Python installed
2. Install pygame: `pip install pygame`
3. Run the game: `python main.py`

## Controls

- **Movement**: WASD keys or Arrow keys
- **Jump**: Spacebar, Up arrow, or W key
- **Quit**: ESC key or close window
- **Restart**: R key (when game over)

## Game Mechanics

<<<<<<< Updated upstream
- Green square is the player
- Health bars appear above entities when damaged
- 3 Different Enemy types (normal, jumpy, and ambush)
- 
=======
- **Player**: Blue rectangle (32x48 pixels) with 3 hearts of health
- **Enemies**:
  - Red squares (BasicEnemy)
  - Cyan squares (JumpingEnemy)
  - Dark magenta squares (AmbushEnemy)
- **Environment**: Brown ground tiles, wooden platforms, gold collectibles
- **Physics**: Realistic gravity, one-way platform support, collision boundaries
- **Camera**: Follows player with smooth scrolling within level bounds
>>>>>>> Stashed changes

## Level Design Notes

- Levels are designed in CSV format for easy editing
- 64x64 pixel tile grid system
- Current level (`level1.csv`) is 80 tiles wide × 11 tiles tall (5120×704 pixels)
- Mix of solid ground, one-way platforms, and strategic enemy placement
- Collectibles placed on elevated platforms to encourage exploration

## Technical Implementation

- **Object-Oriented Design**: Separate classes for different game systems
- **Sprite-Based Rendering**: Efficient drawing with camera offset calculations  
- **Physics Engine**: Custom gravity and collision detection for platformer feel
- **State Management**: Clean separation of update/render cycles
- **Modular Architecture**: Easy to extend with new enemy types or level features
