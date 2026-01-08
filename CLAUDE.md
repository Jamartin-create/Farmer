# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python script repository for "The Farmer Was Replaced" game automation. The game involves programming a farming drone to harvest and plant crops across a grid-based farm. The codebase implements advanced strategies for resource management, crop optimization, and maze navigation.

## Core Architecture

### Entry Point
- `main.py`: Initializes the local map cache and starts the main movement/planting loop
  - Calls `map_manage.init_map()` to set up local caching
  - Calls `do_move.lets_move()` to begin the infinite automation loop

### Key Modules

#### do_plant.py (Core Planting Logic)
The main strategy engine containing all crop-specific logic. This is the most complex module and contains:

- **Zone-based farm layout**:
  - Pumpkin merge zone: Top-left m×m area (where m = n - floor(n/2), n = world size)
  - Support ring: Single-width border around pumpkin zone for carrots
  - Cactus zone: Right of pumpkin zone (m+1 ≤ x < min(2*m+1, n), 0 ≤ y < m)
  - Maze zone: Bottom-right corner (n/2 × n/2 area)
  - Tree/Sunflower/Grass zones: Remaining areas using checkerboard patterns

- **State caches**: Global state for pumpkins, sunflowers, companions, and mazes
  - These are 2D arrays that track crop-specific information
  - Automatically rebuild when world size (n) changes
  - All cache variables are module-level globals

- **Critical game mechanics** (from .cursorrules):
  - `till()` is a **toggle**: Grassland ↔ Soil (avoid calling twice!)
  - Dead pumpkins: Cannot be harvested, block merging, auto-removed by planting
  - Sunflower 8x energy: Need 10+ sunflowers, only harvest max petal count
  - Tree adjacency: Each adjacent tree doubles growth time (up to 16x slowdown)

#### do_move.py (Movement Controller)
- `lets_move()`: Main infinite loop with mode switching
  - **Normal mode**: Column-by-column traversal (North direction, then East)
  - **Maze mode**: Uses DFS navigation from `get_maze_nav_direction()`
  - Automatically switches modes based on `is_in_maze_mode()`
- `move_and_scan()`: Wrapper for `move()` that updates local map cache

#### map_manage.py (Local Map Cache)
- Maintains `type_map[][]` and `ground_map[][]` arrays
- `init_map()`: Initializes cache arrays to world size
- `check_neighbor_has(entity)`: Checks if any of the 4 neighbors has specified entity
  - Used primarily to avoid planting trees adjacent to other trees

#### consts.py (Configuration Constants)
Centralized parameters for easy tuning:
- `WATER_THRESHOLD = 0.5`: Auto-water below this level
- `FERTILIZER_MIN_STOCK = 10`: Minimum fertilizer reserve
- `CARROT_LOW_WATERMARK = 500`: Trigger fertilizer use when carrots low
- `FERTILIZER_USE_THRESHOLD = 25`: Aggressive fertilizer use above this
- `SUNFLOWER_MIN_COUNT_FOR_8X = 10`: Minimum sunflowers for 8x energy strategy
- `DIRECTION`: Movement vectors for neighbor checking

## Critical Game Rules

### Tilling (Most Common Error Source)
```python
# CORRECT: Check ground type first
if get_ground_type() == Grounds.Grassland:
    till()

# WRONG: Blind tilling (will toggle back to grass!)
till()
till()  # Now it's grass again!
```

### Pumpkin Mechanics
- Merge when all pumpkins in square region are fully grown
- 20% chance to die → becomes Dead_Pumpkin (blocks merging)
- Dead pumpkins: `can_harvest()` always returns `False`
- Solution: Plant new crop over dead pumpkin (auto-removes it)
- Optimal merge size: 6×6 (yields n²×6 for n≥6)

### Sunflower 8x Energy Strategy
1. Need ≥10 sunflowers on farm
2. Use `measure()` to track petal count (7-15 petals)
3. Only harvest sunflowers with current max petal count
4. Harvesting non-max petals breaks the 8x bonus for next harvest
5. Implementation: `sunflower_petals_map[][]` tracks all sunflowers

### Fertilizer Strategy
- Using fertilizer "infects" plants: 50% of harvest becomes Weird_Substance
- Current strategy: Actively use on carrots/cacti when stock > threshold
- Weird_Substance is needed for maze generation (n × 2^(maze_level-1) items)
- Never use on sunflowers (reduces energy output)

### Companion Planting (Polyculture)
- `get_companion()` returns `(plant_type, (x, y))` or `None`
- Grass/Bush/Tree/Carrot can request companion plants
- `companion_need_map[][]` tracks requested plants per tile
- Priority system: Tree (40) > Bush (30) > Carrot (20) > Grass (10)
- Companions can request tiles within pumpkin zone → ignore to protect merges

### Maze Navigation
- Generate with `use_item(Items.Weird_Substance, n × 2^(level-1))` on Bush
- Never harvest Hedge (destroys maze!)
- `measure()` returns treasure coordinates from anywhere in maze
- DFS navigation in `_navigate_to_treasure()` returns direction
- Harvest Treasure when reached, then reset `maze_generated = False`

## Development Workflow

### Running the Game
The game uses a custom scripting language (not true Python) executed by the game engine. There is no command-line build/test process. Code is loaded when you run the game.

### Type Definitions
`__builtins__.py` provides type hints for IDE support but is **not executed** by the game. It documents the game's API surface.

### Strategy Documentation
The `docs/` folder contains detailed strategy guides:
- `pumpkin_strategy.md`: Dynamic merge zone sizing with formula m = n - floor(n/2)
- `cactus_strategy.md`: Sorted cactus chains for exponential yields
- `companion_mixed_planting.md`: Polyculture system for yield bonuses
- `maze_strategy.md`: DFS-based treasure navigation
- `water_fertilizer_sunflower.md`: Resource management and energy optimization
- `farm_layout.md`: Overall zone allocation strategy

## Common Development Patterns

### Adding a New Crop Zone
1. Define zone check function in `do_plant.py`: `_in_newcrop_zone(x, y, m, n)`
2. Create handler function: `_handle_newcrop_zone_cell()`
3. Add zone check to `_handle_support_cell()` with appropriate priority
4. Initialize state cache if needed (follow pattern of `_init_sunflower_state()`)

### Modifying Planting Logic
1. Locate the zone handler (e.g., `_handle_pumpkin_zone_cell()`)
2. Check for state cache dependencies (pumpkin_ready_map, sunflower_petals_map, etc.)
3. Remember: `_ensure_soil()` for crops requiring Soil, not for Grass/Bush/Tree
4. Use `_replant_as(entity)` for harvest+replant (handles fertilizer timing)

### State Cache Management
All state caches follow this pattern:
```python
# Global variables
cache_map = None
cache_memo_n = None

# Initialize in plant_something()
if cache_map == None or cache_memo_n != n:
    _init_cache_state(n)
```

### Fertilizer Integration
Fertilizer is applied in `_replant_as()` immediately after planting:
```python
def _replant_as(target_entity):
    if target_entity == Entities.Carrot:
        _plant_carrot_here()
        _maybe_use_fertilizer(Entities.Carrot)  # Right after planting!
```

## Important Constraints from .cursorrules

When modifying planting code:
1. **Always check ground type before calling `till()`** (it's a toggle, not idempotent!)
2. **Never try to harvest Dead_Pumpkin** (`can_harvest()` is always False)
3. **Plant over Dead_Pumpkin to remove it** (don't harvest/clear separately)
4. **For 8x sunflower energy**: Ensure ≥10 sunflowers AND only harvest max petals
5. **Tree spacing**: Use `check_neighbor_has(Entities.Tree)` to avoid adjacency
6. **Pumpkin merge zones**: Any dead pumpkin blocks the entire merge
7. **Maze navigation**: Never harvest Hedge entities (destroys the maze)

## Common Pitfalls

1. **Double-tilling**: Most common bug. Always check `get_ground_type() == Grounds.Grassland` first
2. **Sunflower premature harvest**: Breaks 8x bonus. Must check petal count and count ≥10
3. **Pumpkin zone contamination**: Dead pumpkins block merges. Detect and replant quickly
4. **Tree clustering**: Adjacent trees multiply growth time. Use checkerboard + neighbor check
5. **Maze destruction**: Harvesting non-Treasure entities destroys maze. Only harvest Treasure
6. **Cache invalidation**: World size changes require rebuilding all state caches
7. **Resource deadlock**: Ensure carrot production sustains pumpkin planting rate
