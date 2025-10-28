# Pygame Project

A basic pygame project structure with player, enemy, and level management.

## Project Structure

- `main.py` - Main driver file that runs the game loop
- `player.py` - Player class with movement and health management
- `enemy.py` - Enemy class with AI behavior and different enemy types
- `level.py` - Level class for background, obstacles, and level progression
- `requirements.txt` - Python dependencies

## Features

### Player Class

- WASD or arrow key movement
- Health system with hearts as HP
- Collision detection
- Screen boundary constraints

### Enemy Class

- Multiple enemy types (basic, jumping, ambush)
- Health system with visual indicator
- Screen boundary collision

### Level Class

- Dynamic background colors based on level
- Level progression system
- Spawn position management

### Main Game Loop

- Event handling (quit, escape key)
- Game state management
- Collision detection between player and enemies
- 60 FPS frame rate control

## How to Run

1. Make sure you have Python installed
2. Install pygame: `pip install pygame`
3. Run the game: `python main.py`

## Controls

- **Movement**: WASD keys or Arrow keys
- **Quit**: ESC key or close window

## Game Mechanics

- Green square is the player
- Red squares are enemies
- Gray rectangles are obstacles
- Health bars appear above entities when damaged
- Level number is displayed in the top-left corner

## Development Environment

The project is set up with a Python virtual environment in `.venv/` with pygame installed
