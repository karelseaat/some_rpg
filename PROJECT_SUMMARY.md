# SomeRPG - Project Summary

## What Was Built

A complete **text-based multiplayer RPG** accessible via telnet with the following features:

### Core Features
✅ **Telnet Server** - Multiple concurrent players via async networking  
✅ **Colored Terminal Output** - ANSI color codes for visual appeal  
✅ **TOML Config System** - Entire world defined in editable TOML file  
✅ **Virtual Environment** - Python 3 venv at `.venv/`  
✅ **Async Game Engine** - Scalable to many concurrent connections  

### Game Systems
- **Player Stats**: Health, Stamina, Gold, Experience, Level
- **Inventory System**: Collect and use items
- **NPCs & Shops**: Talk to characters, buy supplies
- **Combat System**: Encounter-based battles with difficulty scaling
- **Danger System**: Random hazards with damage and escape chances
- **Quest System**: Accept and track quests from NPCs
- **Location System**: Navigate between interconnected locations
- **Item System**: Consumables, food, tools, treasure

### Available Commands
```
look, travel, inventory, use, rest, talk, buy, investigate
encounter, danger, status, quests, help, quit
```

## Project Structure

```
/Users/aatkarelse/sourcecodes/somerpg/
├── .venv/                    # Python 3 virtual environment (isolated)
├── main.py                   # Entry point - starts server
├── server.py                 # Telnet server (async)
├── engine.py                 # Game logic (10KB+)
├── models.py                 # Data models (Player, World, Location, etc.)
├── config.py                 # TOML config loader
├── color.py                  # ANSI color utilities
├── world.toml                # World definition (7KB+ config)
├── requirements.txt          # Dependencies (tomli)
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide
├── world_extended_example.toml # Example additions
└── .gitignore               # Git ignore rules
```

## Technology Stack

- **Language**: Python 3.14 (via .venv)
- **Async Framework**: asyncio (built-in)
- **Config Format**: TOML (tomli library)
- **Terminal**: ANSI colors (built-in)
- **Protocol**: Telnet (RFC 854)

## How to Use

### Initial Setup (One-time)
```bash
cd /Users/aatkarelse/sourcecodes/somerpg
source .venv/bin/activate
```

### Running the Server
```bash
python main.py
# Server starts on localhost:5000
```

### Connecting as Player
```bash
telnet localhost 5000
```

### Custom Configuration
```bash
# Use custom port
python main.py --port 3000

# Use custom world config
python main.py --config custom_world.toml

# Bind to specific host
python main.py --host 127.0.0.1
```

## Configuration (world.toml)

The entire game world is defined in `world.toml`:

### Sections
- `[world]` - Game metadata
- `[[locations]]` - Places to explore (8 included)
- `[[npcs]]` - Characters to interact with (6 included)
- `[[items]]` - Equipment and consumables (7 included)
- `[[quests]]` - Objectives for players (3 included)
- `[[encounters]]` - Enemies and interactions (6 included)
- `[[dangers]]` - Hazards and traps (4 included)

### Example: Adding a Location
```toml
[[locations]]
id = "blacksmith"
name = "Blacksmith's Shop"
description = "A forge with hot metal..."
type = "settlement"
exits = { west = "tavern" }
npcs = ["blacksmith"]
encounters = []
dangers = []
treasure = []
```

## Game Flow

1. **Connect** via telnet to server
2. **Create** a character (enter name)
3. **Explore** locations using `travel` command
4. **Interact** with NPCs via `talk`
5. **Trade** with merchants via `buy`
6. **Combat** using `encounter` command
7. **Manage** health/stamina via rest and consumables
8. **Collect** treasure through investigation
9. **Level up** by gaining experience from combat

## Key Game Mechanics

### Health & Stamina
- Travel costs 10 stamina
- Resting restores health/stamina
- Potions and food provide healing
- Taking damage from encounters/dangers

### Combat
- Roll-based system (player level + luck vs enemy difficulty)
- Rewards scale with difficulty (easy/medium/hard)
- Experience gain and level progression
- Stats improve on level up

### Economy
- Start with 50 gold
- Gain gold from encounters
- Spend gold on items
- Treasure has value

### Progression
- Experience points from combat
- Level ups grant stat increases
- Better equipment and quests available
- Quest completion for NPCs

## Testing & Verification

✅ All systems tested and working:
- Config loading from TOML
- World instantiation with 8 locations
- NPC and item systems
- Player mechanics (damage, healing, gold, inventory)
- Async telnet server and client connections
- Command processing
- Game loop functionality

## Extensibility

### Easy to Extend
- **Add Locations**: Just add `[[locations]]` to world.toml
- **Add NPCs**: Add `[[npcs]]` with dialogue and shop inventory
- **Add Items**: Add `[[items]]` for shops or treasures
- **Add Encounters**: Create new `[[encounters]]` for combat variety
- **Add Dangers**: Create `[[dangers]]` for environmental hazards
- **Add Quests**: Define `[[quests]]` for player objectives

### Advanced Customization
- Modify combat difficulty formulas (engine.py)
- Add new command actions (server.py)
- Adjust healing amounts and stat costs (models.py)
- Add persistence/database (modify engine.py)
- Add guilds/groups (extend models.py)
- Add PvP combat (add to engine.py)

## Performance Notes

- **Async Design**: Handles many concurrent players
- **No Blocking I/O**: All operations non-blocking
- **Scalable**: Limited mainly by system resources
- **Configuration**: Fast TOML parsing on startup

## Included World

The default `world.toml` includes:

**Locations** (8):
- Tavern (starting point)
- Forest
- Cave
- Mountain Path
- Mountain Summit
- Village
- Market
- Campground

**NPCs** (6):
- Bartender
- Merchant (with shop)
- Healer (quest giver)
- Mayor (quest giver)
- Sage (quest giver)
- Hermit

**Quests** (3):
- Mushroom Hunt
- Bandit Trouble
- Sage's Wisdom

## Files Summary

| File | Purpose | Size |
|------|---------|------|
| main.py | Entry point | ~1.2 KB |
| server.py | Telnet server | ~10 KB |
| engine.py | Game logic | ~11 KB |
| models.py | Data models | ~5.6 KB |
| config.py | Config loader | ~4.2 KB |
| color.py | Colors | ~2.1 KB |
| world.toml | World config | ~7.2 KB |
| README.md | Full docs | ~5.1 KB |
| QUICKSTART.md | Quick start | ~3.5 KB |

**Total Python Code**: ~34 KB (excluding world config)

## Dependencies

Only one required dependency:
- **tomli** (2.0.0+) - TOML parser for Python < 3.11
  - Python 3.11+ has built-in tomllib

## Getting Started Next Steps

1. **Play the game**:
   ```bash
   source .venv/bin/activate
   python main.py
   # In another terminal: telnet localhost 5000
   ```

2. **Customize the world**:
   - Edit world.toml
   - Add new locations, NPCs, items
   - Reload server to apply changes

3. **Extend functionality**:
   - Add new commands to server.py
   - Implement new game mechanics in engine.py
   - Extend models.py for new features

4. **Deploy**:
   - Change `host="0.0.0.0"` in main.py for network access
   - Set `--port` appropriately
   - Run in screen/tmux for persistent server

## Notes

- Colors work on all terminals supporting ANSI codes
- Telnet clients available on all major platforms
- No external databases required (add as needed)
- Fully functional for single-player or small groups
- Easy to scale with persistence layer
- No graphics/GUI - pure text-based experience
