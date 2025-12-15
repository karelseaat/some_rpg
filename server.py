"""Telnet server for the RPG game."""

import asyncio
import socket
from typing import Optional
from models import Player, World
from engine import GameEngine
from color import title, success, error, info, bold, dim, warning


class TelnetPlayer:
    """Represents a telnet connection to a player."""

    def __init__(self, reader, writer, world: World):
        self.reader = reader
        self.writer = writer
        self.world = world
        self.player: Optional[Player] = None
        self.engine: Optional[GameEngine] = None
        self.in_combat = False
        self.last_action = None
        self.command_history = []
        self.history_index = -1
        self.current_input = ""

    async def send(self, message: str):
        """Send a message to the player."""
        self.writer.write((message + "\r\n").encode('utf-8'))
        await self.writer.drain()

    async def send_raw(self, message: str):
        """Send raw data without newline."""
        self.writer.write(message.encode('utf-8'))
        await self.writer.drain()

    async def read_line(self) -> Optional[str]:
        """Read a line from the player."""
        try:
            data = await asyncio.wait_for(self.reader.readline(), timeout=300)
            if not data:
                return None
            line = data.decode('utf-8').strip()
            if line:
                if not self.command_history or self.command_history[-1] != line:
                    self.command_history.append(line)
            return line
        except asyncio.TimeoutError:
            return None

    async def show_welcome(self):
        """Show welcome screen."""
        await self.send("")
        await self.send(title("=" * 60))
        await self.send(title("    Welcome to SomeRPG - Text Adventure"))
        await self.send(title("=" * 60))
        await self.send("")

    async def character_creation(self):
        """Create a new character."""
        await self.send(info("Let's create your character!"))
        
        await self.send(info("\nWhat is your name, adventurer? "), )
        await self.send_raw("")
        name = await self.read_line()
        
        if not name or len(name) < 1:
            name = "Adventurer"
        
        self.player = Player(
            name=name,
            location_id=self.world.start_location
        )
        self.engine = GameEngine(self.world, self.player)
        
        await self.send(success(f"\nWelcome, {name}!"))
        await self.send(info("You awaken in a tavern, unsure how you got here..."))
        await self.send("")

    async def show_help(self):
        """Show help menu."""
        help_text = """
Commands:
  look         - Look around current location
  travel <dir> - Travel in a direction (north, south, east, west)
  inventory    - Check your inventory
  use <item>   - Use an item from your inventory
  rest <type>  - Rest (short/long)
  talk <npc>   - Talk to an NPC
  buy <npc> <item> - Buy an item from an NPC
  investigate  - Search location for treasure
  encounter    - Try to encounter something (if available)
  danger       - Trigger a danger check
  status       - Show character status
  quests       - Show active quests
  !            - Show command history
  !N           - Execute command N from history
  help         - Show this message
  quit         - Exit the game
"""
        await self.send(info(help_text))

    async def process_command(self, command: str):
        """Process a player command."""
        command_lower = command.lower().strip()
        if not command_lower:
            return
        
        # Handle !N style commands (e.g., !1, !2)
        if command_lower.startswith('!') and len(command_lower) > 1 and command_lower[1].isdigit():
            action = "!"
            args = [command_lower[1:]]
        else:
            parts = command_lower.split()
            action = parts[0]
            args = parts[1:] if len(parts) > 1 else []

        try:
            if action == "!":
                if not args:
                    await self.send(info("History:"))
                    for i, cmd in enumerate(self.command_history[-10:], 1):
                        await self.send(info(f"{i}. {cmd}"))
                else:
                    try:
                        idx = int(args[0]) - 1
                        if 0 <= idx < len(self.command_history):
                            cmd = self.command_history[-(len(self.command_history) - idx)]
                            await self.send(info(f"Executing: {cmd}"))
                            return await self.process_command(cmd)
                        else:
                            await self.send(error("History index out of range"))
                    except ValueError:
                        await self.send(error("Usage: ! [number] - ! to show history, !N to run command N"))

            elif action == "help":
                await self.show_help()

            elif action == "look":
                desc = self.engine.get_location_description()
                await self.send(info(desc))

            elif action == "status":
                status = self.engine.get_player_status()
                await self.send(info(status))

            elif action == "travel":
                if not args:
                    await self.send(error("Travel where? (north, south, east, west)"))
                    return
                
                location = self.world.get_location(self.player.location_id)
                direction = args[0]
                
                if direction not in location.exits:
                    await self.send(error(f"You can't go {direction}"))
                    return
                
                dest_id = location.exits[direction]
                err = self.engine.move_to_location(dest_id)
                
                if err:
                    await self.send(error(err))
                else:
                    dest = self.world.get_location(dest_id)
                    await self.send(success(f"You travel {direction} to {dest.name}"))
                    await self.send(info(self.engine.get_location_description()))
                    
                    # Random danger chance
                    import random
                    if random.random() < 0.15:  # 15% chance
                        msg = self.engine.trigger_danger()
                        await self.send(warning(msg))

            elif action == "inventory":
                inv = self.engine.get_inventory()
                await self.send(info(inv))

            elif action == "use":
                if not args:
                    await self.send(error("Use what?"))
                    return
                
                item_id = args[0]
                msg = self.engine.use_item(item_id)
                await self.send(success(msg) if "restored" in msg or "eat" in msg else info(msg))

            elif action == "rest":
                duration = args[0] if args else "short"
                msg = self.engine.rest(duration)
                await self.send(success(msg))
                status = self.engine.get_player_status()
                await self.send(info(status))

            elif action == "talk":
                if not args:
                    await self.send(error("Talk to whom?"))
                    return
                
                npc_id = " ".join(args)
                msg = self.engine.talk_to_npc(npc_id)
                await self.send(info(msg))

            elif action == "buy":
                if len(args) < 2:
                    await self.send(error("Usage: buy <npc> <item>"))
                    return
                
                npc_id = args[0]
                item_id = args[1]
                msg = self.engine.buy_from_npc(npc_id, item_id)
                await self.send(success(msg) if "bought" in msg else error(msg))

            elif action == "investigate":
                msg = self.engine.investigate_location()
                await self.send(success(msg) if "treasure" in msg else info(msg))

            elif action == "encounter":
                msg, gold = self.engine.encounter_enemy()
                await self.send(success(msg) if "defeated" in msg or "peacefully" in msg else warning(msg))

            elif action == "danger":
                msg = self.engine.trigger_danger()
                await self.send(warning(msg))

            elif action == "quests":
                if not self.player.active_quests:
                    await self.send(info("You have no active quests"))
                else:
                    quests_text = "Active Quests:\n"
                    for quest_id in self.player.active_quests:
                        quest = self.world.get_quest(quest_id)
                        if quest:
                            quests_text += f"\n{quest.name}\n{quest.description}\n"
                    await self.send(info(quests_text))

            elif action == "quit":
                await self.send(info("Goodbye, adventurer!"))
                return False

            else:
                await self.send(error(f"Unknown command: {action}. Type 'help' for commands."))

        except Exception as e:
            await self.send(error(f"Error: {str(e)}"))
        
        return True

    async def game_loop(self):
        """Main game loop."""
        await self.show_welcome()
        await self.character_creation()
        
        # Show initial location
        desc = self.engine.get_location_description()
        await self.send(info(desc))
        
        # Main game loop
        while True:
            try:
                await self.send_raw(bold("\n> "))
                line = await self.read_line()
                
                if line is None:
                    break
                
                if not line:
                    continue
                
                result = await self.process_command(line)
                if result is False:
                    break
                
                # Check if player is dead
                if self.player.health <= 0:
                    await self.send(error("You have been defeated... Game Over"))
                    break

            except Exception as e:
                await self.send(error(f"Error: {str(e)}"))
                break

    async def handle_connection(self):
        """Handle a client connection."""
        try:
            await self.game_loop()
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.writer.close()
            await self.writer.wait_closed()


async def handle_client(reader, writer, world: World):
    """Handle a new client connection."""
    player = TelnetPlayer(reader, writer, world)
    await player.handle_connection()


async def start_server(world: World, host: str = "0.0.0.0", port: int = 2300):
    """Start the telnet server."""
    
    async def client_connected(reader, writer):
        await handle_client(reader, writer, world)
    
    server = await asyncio.start_server(client_connected, host, port)
    
    addr = server.sockets[0].getsockname()
    print(f"\n{title('=' * 60)}")
    print(f"{success(f'SomeRPG Server started on {addr[0]}:{addr[1]}')}") 
    print(f"{info('Connect with: telnet ' + addr[0] + ' ' + str(addr[1]))}")
    print(f"{title('=' * 60)}\n")
    
    async with server:
        await server.serve_forever()


def run_server(world: World, port: int = 2300):
    """Run the telnet server (blocking)."""
    asyncio.run(start_server(world, port=port))
