# Level Editor Guide - Echoes of Lyra

Welcome to the level editor! You can create and modify levels using CSV files.

## How to Edit Levels

1. Open any `.csv` file in this folder with a text editor (Notepad, VS Code, Excel, etc.)
2. Edit the grid using the tile codes below
3. Save the file
4. Run the game to see your changes!

## Tile Codes

Each character in the CSV represents a tile in the game:

### Empty Space

- `.` - Empty space (no collision)

### Ground & Platforms

- `G` - Ground (brown with grass on top, full collision)
- `D` - Dirt (plain brown block, full collision)
- `S` - Cobblestone (stone with cracks, full collision)
- `R` - Removable wooden planks (removed after boss is defeated)
- `P` - Platform (one-way platform, collision only from above)

### Items

- `C` - Collectible crystal (must collect all to unlock exit)
- `E` - Exit door (level completion point)

### Spawn Points

- `X` - Player spawn point (where the player starts)
- `B` - BasicEnemy spawn point (simple ground enemy)
- `J` - JumpingEnemy spawn point (enemy that jumps around)
- `A` - AmbushEnemy spawn point (hangs from ceiling, drops on player)
- `Z` - BossEnemy spawn point (powerful boss enemy)

## Tips for Creating Levels

1. **Grid Size**: Each tile is 64x64 pixels. Keep your levels reasonable size (20-100 columns wide, 10-30 rows tall)

2. **Player Spawn**: Always include one `X` for the player spawn point. If you don't, the game will spawn the player at a default location.

3. **Exit**: Include one `E` (exit door) where you want the level to end.

4. **Collectibles**: Add `C` tiles for crystals. Players must collect all crystals before the exit unlocks.

5. **Enemies**: Place enemy spawn points strategically:
   - `B` enemies patrol on the ground
   - `J` enemies jump around
   - `A` enemies hang from platforms/ground and drop on players
   - `Z` is for boss enemies (use sparingly!)

6. **Level Design**: 
   - Build ground with `G` or `D` tiles
   - Use `P` for platforms players can jump through
   - Create challenges with enemy placement
   - Hide crystals in interesting locations

## Example Level Snippet

```
.,.,.,.,.,.,.,.,.,.,
.,.,C,.,.,.,.,.,.,.,
.,.,G,G,G,.,.,.,.,.,
.,.,.,.,.,.,P,P,P,.,
B,.,.,.,.,.,.,.,.,E
G,G,G,G,G,G,G,G,G,G
```

This creates:

- Ground at the bottom
- A collectible crystal floating above
- A platform in the middle
- A basic enemy on the left
- An exit door on the right

## Testing Your Levels

1. Save your CSV file
2. Make sure the filename is `levelN.csv` (where N is the level number)
3. Run the game
4. Select your level from the level select screen
5. Test and refine!

Happy Level Creating! 🎮✨
