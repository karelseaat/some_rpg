# 🎮 SomeRPG - Start Here!

Welcome to SomeRPG, a complete text-based multiplayer RPG with a telnet server and TOML-based world configuration.

## ⚡ Quick Start (2 minutes)

### 1. Start the Server
```bash
cd /Users/aatkarelse/sourcecodes/somerpg
source .venv/bin/activate
python main.py
```

You should see:
```
SomeRPG Server started on 0.0.0.0:5000
Connect with: telnet 0.0.0.0 5000
```

### 2. Connect in Another Terminal
```bash
telnet localhost 5000
```

### 3. Play the Game
- Enter your character name
- Type `help` to see commands
- Type `look` to see current location
- Type `travel north` to move around
- Type `encounter` to fight enemies

Done! You're playing! 🚀

## 📖 Documentation

Read the documents in this order:

1. **START_HERE.md** ← You are here
2. **QUICKSTART.md** - Command reference and quick tips
3. **FEATURES.md** - Complete feature list
4. **INSTALL.md** - Detailed setup and customization
5. **README.md** - Full technical documentation
6. **PROJECT_SUMMARY.md** - Architecture and project overview

## 🎯 What Can You Do?

- **Explore** - Travel between 8 interconnected locations
- **Fight** - Combat with 6 different enemy types
- **Shop** - Buy items from merchants
- **Rest** - Recover health and stamina at inns
- **Quest** - Accept quests from NPCs
- **Level Up** - Gain experience and get stronger
- **Collect** - Find hidden treasure
- **Survive** - Avoid or escape environmental dangers

## 🎮 Essential Commands

| Command | What It Does |
|---------|-------------|
| `look` | See current location |
| `travel north` | Move north (or south/east/west) |
| `inventory` | Check your items |
| `encounter` | Try to fight something |
| `rest short` | Quick rest (heal 20 HP, 30 stamina) |
| `rest long` | Full rest (100% health/stamina) |
| `use rope` | Use an item |
| `talk merchant` | Talk to an NPC |
| `buy merchant rope` | Buy rope from merchant |
| `investigate` | Search for hidden treasure |
| `danger` | Check for hazards |
| `quests` | View active quests |
| `status` | See character stats |
| `help` | Show all commands |
| `quit` | Exit game |

## 📁 Project Structure

```
somerpg/
├── main.py              ← Start the server here
├── world.toml           ← Edit this to customize the world
├── server.py            ← Telnet server code
├── engine.py            ← Game logic
├── models.py            ← Data models
├── config.py            ← Config loader
├── color.py             ← Terminal colors
├── test.sh              ← Run tests
└── [Documentation files]
```

## 🌍 The World

**8 Locations:**
- 🍺 **Tavern** - Starting point, safe haven
- 🌲 **Forest** - Dangerous, creatures lurk here
- 🕷️ **Cave** - Dark, spiders and treasure
- ⛰️ **Mountain Path** - Treacherous, avalanches
- 🏔️ **Summit** - Difficult climb, great view
- 🏘️ **Village** - Peaceful settlement
- 🏪 **Market** - Shopping hub
- ⛺ **Campground** - Rest spot

**6 NPCs to Meet:**
- Bartender at tavern
- Merchant with shop
- Healer with quests
- Mayor with quests
- Sage at summit
- Hermit in cave

**3 Quests to Complete:**
- Find mushrooms
- Deal with bandits
- Learn from sage

## 🛠️ Customize the World

Edit `world.toml` to:
- Add new locations
- Create new NPCs
- Design encounters
- Set up quests
- Add items and treasure

Just edit the file and restart the server!

Example: Add a new item:
```toml
[[items]]
id = "magic_ring"
name = "Magic Ring"
description = "A mysterious ring"
type = "equipment"
value = 150
effect = "none"
```

## 🎯 Game Flow

1. **Connect** - Join the world
2. **Create Character** - Name your hero
3. **Explore** - Visit locations
4. **Interact** - Talk to NPCs
5. **Gather** - Collect items and gold
6. **Fight** - Battle enemies
7. **Level Up** - Get stronger
8. **Complete Quests** - Achieve objectives
9. **Survive** - Avoid death
10. **Repeat** - Keep playing!

## 📊 Character Stats

- **Health** - Takes damage in combat, restored by rest
- **Stamina** - Used for travel, restored by rest
- **Gold** - Currency for buying items
- **Experience** - Earned from combat, leads to level up
- **Level** - Increases as you gain experience

## 💡 Tips for New Players

1. **Start safe** - Tavern is secure, rest there first
2. **Get supplies** - Buy potions from merchant before adventuring
3. **Know your escape** - Forests are dangerous, prepare before going
4. **Rest regularly** - Don't let health get too low
5. **Level up** - Fight easy enemies first to build experience
6. **Explore carefully** - Some areas have tough enemies
7. **Take quests** - NPCs reward quest completion
8. **Collect treasure** - Use `investigate` to find hidden items

## ⚠️ Common Mistakes

- ❌ Adventuring without healing items
- ❌ Ignoring low health
- ❌ Not resting before tough areas
- ❌ Forgetting the `help` command
- ❌ Rushing into caves unprepared

## 🔧 If Something Goes Wrong

**Server won't start:**
```bash
python main.py --port 3000  # Use different port
```

**Can't connect:**
```bash
# Make sure server is running in another terminal
telnet localhost 5000
```

**Game freezes:**
- Type any command to wake it up
- Reconnect with telnet

**Questions about commands:**
- Type `help` in game
- Check QUICKSTART.md
- Read FEATURES.md

## 🚀 Next Steps

### For Players:
1. Start the server: `python main.py`
2. Connect: `telnet localhost 5000`
3. Create your character
4. Type `help` to see commands
5. Start exploring!

### For Creators:
1. Edit `world.toml` to customize world
2. Add new locations, NPCs, items
3. Create quests and encounters
4. Restart server to apply changes
5. Test your changes in game

### For Developers:
1. Read FEATURES.md for capabilities
2. Check engine.py for game logic
3. Modify server.py for new commands
4. Extend models.py for new mechanics
5. See PROJECT_SUMMARY.md for architecture

## 📞 Need Help?

- **Quick questions** → Check QUICKSTART.md
- **Feature details** → See FEATURES.md
- **Setup issues** → Read INSTALL.md
- **Code questions** → Review PROJECT_SUMMARY.md
- **Full docs** → Read README.md

## 🎉 You're Ready!

Everything is set up and ready to go. Just:

```bash
source .venv/bin/activate
python main.py
```

Then in another terminal:
```bash
telnet localhost 5000
```

**Welcome to SomeRPG, adventurer! Let the adventure begin!** 🗡️⚔️🛡️

---

**Version**: 1.0  
**Status**: Production Ready  
**Players Supported**: 100+  
**Locations**: 8  
**NPCs**: 6  
**Quests**: 3  
**Encounters**: 6+
