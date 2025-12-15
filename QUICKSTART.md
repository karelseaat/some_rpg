# Quick Start Guide for SomeRPG

## Setup (One-time)

1. Navigate to project directory:
```bash
cd /Users/aatkarelse/sourcecodes/somerpg
```

2. Activate virtual environment:
```bash
source .venv/bin/activate
```

## Running the Server

Start the server:
```bash
python main.py
```

The server will start on `localhost:5000` by default.

### Server Options

```bash
python main.py --port 3000              # Use port 3000
python main.py --config custom.toml     # Use custom config
python main.py --host 127.0.0.1         # Bind to localhost only
```

## Connecting as a Player

From another terminal:
```bash
telnet localhost 5000
```

Then:
1. Enter your character name
2. Type `look` to see your surroundings
3. Type `help` to see all commands

## Basic Game Flow

1. **Explore**: Use `travel <direction>` to move between locations
2. **Interact**: Use `talk <npc>` to speak with NPCs
3. **Shop**: Use `buy <npc> <item>` to purchase supplies from merchants
4. **Combat**: Use `encounter` to fight enemies (automatic roll-based)
5. **Rest**: Use `rest short` or `rest long` to recover
6. **Quests**: Use `quests` to see active quests

## Example Commands

```
look                    # Examine current location
travel north            # Go north
inventory               # Check inventory
rest short              # Quick rest (20 health, 30 stamina)
use health_potion       # Use an item
talk merchant           # Talk to NPC
buy merchant rope       # Buy rope from merchant
investigate             # Search for hidden items
encounter               # Try to fight something
status                  # Show character stats
help                    # Show all commands
quit                    # Exit game
```

## Customizing the World

Edit `world.toml` to add/modify:
- **Locations**: Add new areas to explore
- **NPCs**: Add characters with dialogue and quests
- **Items**: Create weapons, potions, treasure
- **Encounters**: Define enemies and their difficulty
- **Quests**: Create objectives for players

### Simple Example: Add a New Location

Edit `world.toml` and add:
```toml
[[locations]]
id = "blacksmith"
name = "Old Blacksmith's Shop"
description = "A forge with the smell of hot metal"
type = "settlement"
exits = { west = "tavern" }
npcs = ["blacksmith"]
encounters = []
dangers = []
treasure = []

[[npcs]]
id = "blacksmith"
name = "Gronk the Blacksmith"
description = "A muscular dwarf covered in soot"
dialogue = "Need weapons? I forge the finest steel!"
shop = true
offers_quest = false
inventory = ["sword", "shield"]
```

Then restart the server and players can explore it!

## Troubleshooting

**Server won't start**: Check if port 5000 is in use
```bash
lsof -i :5000  # See what's using the port
python main.py --port 3000  # Use different port
```

**Connection refused**: Make sure server is running and you're using the correct host/port

**Game freezes**: Some commands timeout after 5 minutes of inactivity

**Items not appearing**: Check item IDs match in locations and items sections

## Development Tips

- **Add combat**: Modify `engine.py` encounter system
- **Add persistence**: Save player data to a database
- **Add guilds**: Create groups of players
- **Add PvP**: Add player-vs-player combat system
- **Add events**: Time-based world events and seasonal changes

## Performance Notes

- Supports many concurrent players
- Each connection is async (non-blocking)
- Random encounters have configurable chance rates (edit engine.py)
