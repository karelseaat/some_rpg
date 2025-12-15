#!/bin/bash
# Quick test script for SomeRPG

echo "Starting SomeRPG test..."
echo ""

cd "$(dirname "$0")" || exit 1

# Activate venv
source .venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Run integration tests
echo "Running integration tests..."
python << 'PYTEST'
import sys
sys.path.insert(0, '.')

from config import load_world_config
from models import Player
from engine import GameEngine

world = load_world_config()
player = Player(name="TestHero", location_id=world.start_location)
engine = GameEngine(world, player)

tests = [
    ("World Loading", len(world.locations) == 8),
    ("NPCs", len(world.npcs) == 6),
    ("Items", len(world.items) == 7),
    ("Player Creation", player.name == "TestHero"),
    ("Inventory", isinstance(player.inventory, list)),
]

passed = 0
for name, result in tests:
    status = "✓" if result else "✗"
    print(f"{status} {name}")
    if result:
        passed += 1

print(f"\n{passed}/{len(tests)} tests passed")
sys.exit(0 if passed == len(tests) else 1)
PYTEST

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "All tests passed!"
    echo ""
    echo "To start the server:"
    echo "  python main.py"
    echo ""
    echo "Then connect in another terminal:"
    echo "  telnet localhost 5000"
    echo "=========================================="
else
    echo "Tests failed!"
    exit 1
fi
