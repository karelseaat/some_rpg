# SomeRPG - Text-Based Multiplayer RPG

A telnet-based text adventure RPG with colored terminal output, configurable world via TOML, and multiple gameplay mechanics.

## Features

- **Telnet Server**: Connect multiple players simultaneously via telnet
- **Colored Terminal Output**: ANSI color codes for enhanced visual experience
- **TOML World Config**: Define locations, NPCs, items, quests, and encounters in a simple TOML file
- **Player Actions**:
  - `travel` - Move between locations
  - `look` - Examine current location
  - `rest` - Restore health and stamina
  - `use` - Use items from inventory
  - `talk` - Converse with NPCs
  - `buy` - Purchase items from merchants
  - `investigate` - Search for hidden treasures
  - `encounter` - Fight enemies or interact with creatures
  - `danger` - Face random dangers
  - `inventory` - Check items
  - `status` - View character stats
  - `quests` - View active quests

## Installation

1. Create virtual environment:
```bash
cd /path/to/somerpg
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install tomli
```

## Running the Server

```bash
python main.py [--config world.toml] [--port 5000] [--host 0.0.0.0]
```

Examples:
```bash
python main.py                              # Default config, port 5000
python main.py --port 3000                  # Custom port
python main.py --config custom_world.toml   # Custom config file
```

## Connecting as a Client

From another terminal:
```bash
telnet localhost 5000
```

## Configuration

Edit `world.toml` to define your world:

### World Metadata
```toml
[world]
name = "Your World Name"
start_location = "tavern"
```

### Locations
```toml
[[locations]]
id = "tavern"
name = "The Rusty Ale Tavern"
description = "A warm tavern..."
type = "inn"  # inn, wilderness, settlement, landmark
exits = { north = "forest", east = "market" }
npcs = ["bartender"]
encounters = ["goblin_scout"]
dangers = []
treasure = []
```

### NPCs
```toml
[[npcs]]
id = "merchant"
name = "Theron"
description = "A sharp-eyed merchant"
dialogue = "Looking for supplies?"
shop = true
offers_quest = false
inventory = ["health_potion", "rope"]
```

### Items
```toml
[[items]]
id = "health_potion"
name = "Health Potion"
description = "Restores vitality"
type = "consumable"  # consumable, food, tool, treasure, equipment
value = 50
effect = "heal"  # heal, stamina, light, none
amount = 1
```

### Quests
```toml
[[quests]]
id = "mushroom_hunt"
name = "The Mushroom Hunt"
description = "Find rare mushrooms"
giver = "healer"  # NPC id
location = "cave"
objectives = ["Find 3 glowing mushrooms", "Return to Sister Mara"]
reward = 100
reward_item = "health_potion"
```

### Encounters
```toml
[[encounters]]
id = "goblin_scout"
name = "Goblin Scout"
description = "A small goblin with a mischievous grin"
type = "combat"  # combat, interaction, obstacle
difficulty = "easy"  # easy, medium, hard
reward = 25
```

### Dangers
```toml
[[dangers]]
id = "lost_in_forest"
name = "Lost in the Woods"
description = "You've become disoriented"
damage = 5
escape_difficulty = "medium"
```

## Game Mechanics

### Player Stats
- **Health**: Reduced by dangers and combat, restored by rest and items
- **Stamina**: Used for traveling, restored by rest and items
- **Gold**: Earned from encounters, spent on items
- **Experience**: Gained from combat, levels player up
- **Level**: Increases when enough experience is gained

### Combat
When encountering an enemy, success depends on:
- Player level and random luck
- Enemy difficulty (easy, medium, hard)
- Rewards scale with difficulty

### Healing & Items
- Consumables can restore health or stamina
- Food items provide healing
- Tools can be collected (rope, torch)
- Treasure can be found through investigation

### Dangers
Each location can have dangers that trigger randomly:
- Damage varies by danger
- Escape difficulty affects chance of avoiding damage

## Project Structure

```
somerpg/
├── .venv/                 # Virtual environment
├── main.py               # Entry point
├── server.py             # Telnet server
├── engine.py             # Game logic
├── models.py             # Data models
├── config.py             # Config loader
├── color.py              # Color utilities
├── world.toml            # World definition
└── README.md             # This file
```

## Extending the Game

1. **Add Locations**: Add new `[[locations]]` blocks in `world.toml`
2. **Add NPCs**: Create new `[[npcs]]` blocks and link them to locations
3. **Add Encounters**: Define `[[encounters]]` and reference in locations
4. **Add Quests**: Create `[[quests]]` with objectives and rewards
5. **Add Items**: Define `[[items]]` for shops or treasures

## Tips

- Start players with some gold in `world.toml` (adjust Player initialization in models.py)
- Use descriptive location descriptions to set atmosphere
- Balance encounter difficulty with rewards
- Create quest chains by having NPCs reference each other
- Use dangers to encourage caution in wilderness areas

## License

Public domain - feel free to modify and use as you wish!
