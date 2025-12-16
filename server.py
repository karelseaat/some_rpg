"""Telnet server for the RPG game."""

import asyncio
import socket
from typing import Optional, List
from models import Player, World, Enemy
from engine import GameEngine
from game import Game
from color import title, success, error, info, bold, dim, warning
from commands import COMMANDS

ACTIVE_GAMES: List["TelnetPlayer"] = []

class TelnetPlayer:
    """Represents a telnet connection to a player."""

    def __init__(self, reader, writer, world: World):
        self.reader = reader
        self.writer = writer
        self.world = world
        self.game: Optional[Game] = None
        self.in_combat = False
        self.current_enemy: Optional[Enemy] = None
        self.last_action = None

    async def send(self, message: str):
        """Send a message to the player."""
        if message:
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
        
        self.game = Game(self.world, name)
        
        await self.send(success(f"\nWelcome, {self.game.player.name}!"))
        await self.send(info("You awaken in a tavern, unsure how you got here..."))
        await self.send("")

    async def process_combat_command(self, command: str) -> bool:
        """Process a player command during combat."""
        command_lower = command.lower().strip()
        if not command_lower:
            return True

        parts = command_lower.split()
        action = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # In combat, only some commands are allowed
        if action not in ["attack", "skill", "item", "flee", "status", "look"]:
            await self.send(error("You are in combat! You can only attack, use skills or items, or flee."))
            return True

        handler = COMMANDS.get(action)
        if handler:
            try:
                message = await handler(self.game, args)
                await self.send(message)
            except Exception as e:
                await self.send(error(f"An error occurred: {e}"))
        else:
            await self.send(error(f"Unknown command: {action}"))

        # Enemy's turn
        if self.game.in_combat and self.game.current_enemy.health > 0:
            enemy_damage = self.game.current_enemy.attack
            self.game.player.take_damage(enemy_damage)
            await self.send(warning(f"{self.game.current_enemy.name} attacks you for {enemy_damage} damage!"))

        # Check for combat end
        if self.game.player.health <= 0:
            # The game over message is handled in the main loop
            return True 
        
        if self.game.current_enemy and self.game.current_enemy.health <= 0:
            await self.send(success(f"You have defeated {self.game.current_enemy.name}!"))
            self.game.player.add_gold(self.game.current_enemy.reward_gold)
            self.game.player.gain_experience(self.game.current_enemy.reward_exp)
            await self.send(success(f"You gain {self.game.current_enemy.reward_gold} gold and {self.game.current_enemy.reward_exp} experience."))
            self.game.in_combat = False
            self.game.current_enemy = None

        return True

    async def process_command(self, command: str) -> bool:
        """Process a player command."""
        if self.game.in_combat:
            return await self.process_combat_command(command)

        command_lower = command.lower().strip()
        if not command_lower:
            return True

        if command_lower.startswith('!'):
            await self.send(error("History commands are disabled."))
            return True

        parts = command_lower.split()
        action = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        handler = COMMANDS.get(action)
        if handler:
            try:
                message = await handler(self.game, args)
                if message == "QUIT":
                    await self.send(info("Goodbye, adventurer!"))
                    return False
                await self.send(message)
            except Exception as e:
                await self.send(error(f"An error occurred: {e}"))
        else:
            await self.send(error(f"Unknown command: {action}. Type 'help' for commands."))
        
        return True

    async def game_loop(self):
        """Main game loop."""
        await self.show_welcome()

        loaded_player = GameEngine.load_game(self.world)
        if loaded_player:
            self.game = Game(self.world, loaded_player.name)
            self.game.player = loaded_player
            self.game.engine = GameEngine(self.world, self.game.player)
            await self.send(success(f"\nWelcome back, {self.game.player.name}!"))
        else:
            await self.character_creation()
        
        # Show initial location
        desc = self.game.engine.get_location_description()
        await self.send(info(desc))
        
        # Main game loop
        while True:
            try:
                if self.game.in_combat and self.game.current_enemy:
                    prompt = bold(f"\n({self.game.player.health} HP) vs ({self.game.current_enemy.health} HP) > ")
                else:
                    prompt = bold("\n> ")
                await self.send_raw(prompt)
                
                line = await self.read_line()
                
                if line is None:
                    break
                
                if not line:
                    continue
                
                result = await self.process_command(line)
                if result is False:
                    break
                
                # Check if player is dead
                if self.game.player.health <= 0:
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
    ACTIVE_GAMES.append(player)
    await player.handle_connection()
    ACTIVE_GAMES.remove(player)


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

def save_all_games():
    """Save all active games."""
    print("Saving all games...")
    for player in ACTIVE_GAMES:
        if player.game and player.game.engine:
            player.game.engine.save_game()
    print("All games saved.")

def run_server(world: World, port: int = 2300):
    """Run the telnet server (blocking)."""
    asyncio.run(start_server(world, port=port))
