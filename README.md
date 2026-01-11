# SomeRPG - Text-Based Multiplayer RPG

Welcome to SomeRPG, a complete text-based multiplayer RPG with a telnet server, colored terminal output, and a TOML-based world configuration.

## ⚡ Quick Start

### 1. Start the Server
```bash
# Navigate to the project directory
cd /path/to/somerpg

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the server
python main.py
```
You should see: `SomeRPG Server started on 0.0.0.0:5000`

### 2. Connect
In a separate terminal window:
```bash
telnet localhost 5000
```

### 3. Play
*   Enter your character name.
*   Type `help` to see commands.
*   Type `look` to see your surroundings.
*   Type `travel north` (or other directions) to move.

---

## 🎮 Features

*   **Multiplayer Telnet Server:** Async architecture supporting multiple concurrent players.
*   **Rich World:** 8 interconnected locations, from taverns to mountain summits.
*   **Configurable:** Entire game world defined in a simple `world.toml` file.
*   **Colored Output:** ANSI color codes for an atmospheric experience.
*   **Comprehensive Systems:**
    *   **Stats:** Health, Stamina, Gold, Experience, Level.
    *   **Inventory:** Manage consumables, food, tools, and treasure.
    *   **Combat:** Turn-based encounters with difficulty scaling and rewards.
    *   **Quests:** Accept and track objectives from NPCs.
    *   **NPCs & Shops:** Interact with characters and trade gold for items.
    *   **Dangers:** Environmental hazards with escape mechanics.

## 🕹️ Game Mechanics

### Player Stats
*   **Health:** Reduced by combat/dangers, restored by resting or items.
*   **Stamina:** Consumed by traveling, restored by resting or items.
*   **Gold:** Earned from encounters, spent at shops.
*   **Experience & Level:** XP from combat leads to level ups (+Health, +Stamina).

### Commands
*   **Navigation:** `look`, `travel <direction>` (north, south, east, west)
*   **Interaction:** `talk <npc>`, `buy <npc> <item>`, `use <item>`
*   **Action:** `investigate` (search for treasure), `encounter` (trigger combat), `danger` (check hazards)
*   **Character:** `status`, `inventory`, `quests`, `rest <short|long>`
*   **System:** `help`, `quit`

### Combat & Dangers
*   **Encounters:** Success depends on Player Level + Luck vs. Enemy Difficulty.
*   **Dangers:** Random environmental hazards (e.g., "Lost in Forest") that deal damage based on escape difficulty.

---

## ⚙️ Configuration (`world.toml`)

The entire world is defined in `world.toml`. You can edit this file to expand the game without touching Python code.

### Structure
```toml
[world]          # Metadata (name, start location)
[[locations]]    # Define areas (id, description, exits)
[[npcs]]         # Define characters (dialogue, shop inventory)
[[items]]        # Define objects (consumables, equipment)
[[quests]]       # Define objectives and rewards
[[encounters]]   # Define enemies (difficulty, rewards)
[[dangers]]      # Define environmental hazards
```

### Example: Adding a Location
```toml
[[locations]]
id = "blacksmith"
name = "Blacksmith's Forge"
description = "The air is hot and smells of soot."
type = "settlement"
exits = { west = "market" }
npcs = ["blacksmith_npc"]
encounters = []
dangers = []
treasure = ["hammer"]
```

---

## 🛠️ Installation & Setup

### Requirements
*   Python 3.9+
*   Standard Telnet client (pre-installed on most OSs)

### Manual Setup
If you need to reinstall dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
*(Note: `tomli` is the only dependency for Python < 3.11)*

### Server Options
```bash
python main.py --port 3000              # Run on port 3000
python main.py --config my_world.toml   # Load custom world file
python main.py --host 127.0.0.1         # Bind to localhost only
```

### Advanced: Run in Background
```bash
nohup python main.py > server.log 2>&1 &
```

---

## 📂 Project Structure

```
somerpg/
├── .venv/               # Virtual environment
├── main.py              # Entry point
├── server.py            # Async Telnet server & I/O
├── engine.py            # Core game logic & mechanics
├── models.py            # Data classes (Player, Location, etc.)
├── config.py            # TOML configuration loader
├── color.py             # ANSI color utilities
├── world.toml           # Game world definition
└── requirements.txt     # Project dependencies
```

## 🐛 Troubleshooting

*   **"Address already in use"**: Another process is using port 5000. Try `python main.py --port 3001`.
*   **"Connection refused"**: Ensure the server is running. If on a remote machine, check firewalls.
*   **Game Freezes**: Connections may timeout after inactivity. Reconnect via telnet.
*   **Import Errors**: Ensure the virtual environment is activated (`source .venv/bin/activate`).

## 💡 Tips
*   **Start Safe:** The Tavern is safe. Rest there before venturing out.
*   **Stock Up:** Buy potions from the merchant before long journeys.
*   **Watch Health:** Don't ignore low health; hazards can be deadly.
*   **Explore:** Use `investigate` in new areas to find hidden items.

## License
Public Domain - Feel free to modify and use as you wish!