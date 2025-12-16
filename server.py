"""Telnet server for the RPG game."""

import asyncio
import socket
from typing import Optional
from models import Player, World
from engine import GameEngine
from game import Game
from color import title, success, error, info, bold, dim, warning
from commands import COMMANDS


class TelnetPlayer:
    """Represents a telnet connection to a player."""

    def __init__(self, reader, writer, world: World):
        self.reader = reader
        self.writer = writer
        self.world = world
        self.game: Optional[Game] = None
        self.in_combat = False
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
            if line and self.game:
                self.game.player.command_history.append(line)
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

    async def process_command(self, command: str) -> bool:
        """Process a player command."""
        command_lower = command.lower().strip()
        if not command_lower:
            return True

        if command_lower.startswith('!'):
            # The `!N` command should not be added to history
            if self.game and self.game.player.command_history and self.game.player.command_history[-1] == command_lower:
                self.game.player.command_history.pop()

            if len(command_lower) > 1 and command_lower[1:].isdigit():
                try:
                    idx = int(command_lower[1:]) - 1
                    if 0 <= idx < len(self.game.player.command_history):
                        cmd = self.game.player.command_history[idx]
                        await self.send(info(f"Recalled: {cmd}"))
                    else:
                        await self.send(error("History index out of range"))
                except ValueError:
                    await self.send(error("Invalid history command. Use !N where N is a number."))
            else:
                await self.send(info("History:"))
                for i, cmd in enumerate(self.game.player.command_history[-10:], 1):
                    await self.send(info(f"{i}. {cmd}"))
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
        await self.character_creation()
        
        # Show initial location
        desc = self.game.engine.get_location_description()
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
