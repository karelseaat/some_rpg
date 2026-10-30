"""Telnet server for the RPG game."""

import asyncio
import socket
from typing import Optional, List
from models import Player, World, Enemy
from GameEngineFacade import GameEngineFacade as GameEngine
from game import Game
from color import title, success, error, info, bold, dim, warning
from commands import COMMANDS
from logger import logger
from session_manager import session_manager, Session

ACTIVE_GAMES: List["TelnetPlayer"] = []

from events import event_bus, Event

def on_notification(event: Event):
    """Handle notification events."""
    player_name = event.data["player_name"]
    message = event.data["message"]
    for tp in ACTIVE_GAMES:
        if tp.game and tp.game.player.name == player_name:
            asyncio.create_task(tp.send(success(message, game=tp.game)))

# Subscribe to notifications
event_bus.subscribe("notification", on_notification)

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

    async def send(self, message: str, game: Optional[Game] = None):
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
        except (asyncio.TimeoutError, UnicodeDecodeError):
            return None

    async def show_welcome(self):
        """Show welcome screen."""
        await self.send("")
        await self.send(title("=" * 60, game=self.game))
        await self.send(title("    Welcome to SomeRPG - Text Adventure", game=self.game))
        await self.send(title("=" * 60, game=self.game))
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
            await self.send(error("You are in combat! You can only attack, use skills or items, or flee.", game=self.game))
            return True

        handler = COMMANDS.get(action)
        if handler:
            try:
                message = await handler(self.game, args)
                await self.send(message)
            except Exception as e:
                await self.send(error(f"An error occurred: {e}", game=self.game))
        else:
            await self.send(error(f"Unknown command: {action}", game=self.game))

        # Enemy's turn
        if self.game.in_combat and self.game.current_enemy.health > 0:
            enemy_damage = self.game.current_enemy.attack
            self.game.player.take_damage(enemy_damage)
            await self.send(warning(f"{self.game.current_enemy.name} attacks you for {enemy_damage} damage!", game=self.game))

        # Check for combat end
        if self.game.player.health <= 0:
            # The game over message is handled in the main loop
            return True 
        
        if self.game.current_enemy and self.game.current_enemy.health <= 0:
            await self.send(success(f"You have defeated {self.game.current_enemy.name}!", game=self.game))
            self.game.player.add_gold(self.game.current_enemy.reward_gold)
            self.game.engine.add_experience(self.game.current_enemy.reward_exp)
            await self.send(success(f"You gain {self.game.current_enemy.reward_gold} gold and {self.game.current_enemy.reward_exp} experience.", game=self.game))
            
            # Loot
            loot = self.game.engine.get_loot(self.game.current_enemy)
            if loot:
                loot_msg = "The enemy dropped: "
                location = self.game.world.get_location(self.game.player.location_id)
                for item in loot:
                    # Add to location items
                    location.items.append(item)
                    loot_msg += f"{item.name}, "
                await self.send(success(loot_msg.strip(", "), game=self.game))
            
            # Emit EnemyKilled event
            event_bus.publish(Event("enemy_killed", {
                "player": self.game.player,
                "enemy_id": self.game.current_enemy.id,
                "enemy_name": self.game.current_enemy.name
            }))

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
            await self.send(error("History commands are disabled.", game=self.game))
            return True

        parts = command_lower.split()
        action = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        handler = COMMANDS.get(action)
        if handler:
            try:
                message = await handler(self.game, args)
                await self.send(message)
            except Exception as e:
                await self.send(error(f"An error occurred: {e}", game=self.game))
        else:
            await self.send(error(f"Unknown command: {action}. Type 'help' for commands.", game=self.game))
        
        # After any action, check for danger
        danger_msg = self.game.engine.trigger_danger()
        if danger_msg:
            await self.send(warning(danger_msg, game=self.game))

        trap_msg = self.game.engine.trigger_hidden_dangers()
        if trap_msg:
            await self.send(warning(trap_msg, game=self.game))
        
        return True

    async def character_creation(self, password: str):
        """Create a new character."""
        await self.send(info("Let's create your character!", game=self.game))
        
        await self.send(info("\nWhat is your name, adventurer? ", game=self.game), )
        await self.send_raw("")
        name = await self.read_line()
        
        if not name or len(name) < 1:
            name = "Adventurer"
        
        self.game = Game(self.world, name, password)
        
        await self.send(success(f"\nWelcome, {self.game.player.name}!", game=self.game))
        await self.send(info("You awaken in a tavern, unsure how you got here...", game=self.game))
        await self.send("")

    async def game_loop(self):
        """Main game loop."""
        await self.show_welcome()

        await self.send(info("Enter your password to load a character, or type 'new' to create a new one: ", game=self.game))
        await self.send_raw("")
        password = await self.read_line()

        if not password:
            return

        if password.lower() == 'new':
            password = GameEngine.generate_password()
            await self.send(info(f"Your new password is: {password}", game=self.game))
            await self.send(warning("Write it down! You will need it to log in next time.", game=self.game))
            await self.character_creation(password)
            
            # Register session
            if self.game:
                session = Session(self.game.player.name, self.game, self)
                session_manager.add_session(session)
        else:
            loaded_player = await GameEngine.load_game(self.world, password)
            if loaded_player:
                self.game = Game(self.world, loaded_player.name, password)
                self.game.player = loaded_player
                self.game.engine = GameEngine(self.world, self.game.player)
                
                # Register session
                session = Session(self.game.player.name, self.game, self)
                session_manager.add_session(session)
                
                await self.send(success(f"\nWelcome back, {self.game.player.name}!", game=self.game))
            else:
                await self.send(info("Password not found. Creating a new character with this password.", game=self.game))
                await self.character_creation(password)
                
                # Register session (character_creation sets self.game)
                if self.game:
                    session = Session(self.game.player.name, self.game, self)
                    session_manager.add_session(session)

        # Show initial location
        desc = self.game.engine.get_location_description(game=self.game)
        await self.send(info(desc, game=self.game))
        
        # Main game loop
        while True:
            try:
                if self.game.in_combat and self.game.current_enemy:
                    prompt = bold(f"\n({self.game.player.health} HP) vs ({self.game.current_enemy.health} HP) > ", game=self.game)
                else:
                    prompt = bold("\n> ", game=self.game)
                await self.send_raw(prompt)
                
                line = await self.read_line()
                
                if line is None:
                    break
                
                if not line:
                    continue
                
                result = await self.process_command(line)
                if result is False:
                    break
                
                # Save game after every command
                await self.game.engine.save_game()
                
                # Check if player is dead
                if self.game.player.health <= 0:
                    await self.send(error("You have been defeated... Game Over", game=self.game))
                    
                    # Drop all items
                    location = self.game.world.get_location(self.game.player.location_id)
                    if self.game.player.inventory:
                        drop_msg = "You dropped your inventory:\n"
                        for item in self.game.player.inventory:
                            location.items.append(item)
                            drop_msg += f"  - {item.name} (x{item.amount})\n"
                        self.game.player.inventory = [] # Clear inventory
                        await self.send(info(drop_msg, game=self.game))
                        
                    # Save empty inventory state
                    await self.game.engine.save_game()
                    break

            except Exception as e:
                await self.send(error(f"Error: {str(e)}", game=self.game))
                break

    async def handle_connection(self):
        """Handle a client connection."""
        try:
            await self.game_loop()
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            # Unregister session if it exists
            if self.game:
                session = session_manager.get_session_by_name(self.game.player.name)
                if session:
                    session_manager.remove_session(session)
            
            self.writer.close()
            await self.writer.wait_closed()


async def handle_client(reader, writer, world: World):
    """Handle a new client connection."""
    addr = writer.get_extra_info('peername')
    logger.info(f"New connection from {addr}")
    player = TelnetPlayer(reader, writer, world)
    ACTIVE_GAMES.append(player)
    await player.handle_connection()
    ACTIVE_GAMES.remove(player)
    logger.info(f"Connection closed from {addr}")


async def world_tick_loop(world: World):
    """Background task to advance world time."""
    while True:
        await asyncio.sleep(60) # 1 minute real time = 1 hour game time
        world.time_tick += 1
        
        # Notify all players of time change (optional, but nice)
        # We would need a way to broadcast. For now, let's just log it.
        if world.time_tick % 12 == 0: # Phase change
            phase = "Day" if world.is_day else "Night"
            logger.info(f"World time advanced. It is now {phase}.")
            await session_manager.broadcast(info(f"The sun {'rises' if world.is_day else 'sets'}.", game=None))

async def start_server(world: World, host: str = "0.0.0.0", port: int = 2300):
    """Start the telnet server."""
    
    # Start the world tick loop
    asyncio.create_task(world_tick_loop(world))
    
    async def client_connected(reader, writer):
        await handle_client(reader, writer, world)
    
    server = await asyncio.start_server(client_connected, host, port)
    
    addr = server.sockets[0].getsockname()
    logger.info(f"SomeRPG Server started on {addr[0]}:{addr[1]}")
    print(f"\n{title('=' * 60)}")
    print(f"{success(f'SomeRPG Server started on {addr[0]}:{addr[1]}')}") 
    print(f"{info('Connect with: telnet ' + addr[0] + ' ' + str(addr[1]))}")
    print(f"{title('=' * 60)}\n")
    
    async with server:
        await server.serve_forever()

def save_all_games():
    """Save all active games."""
    logger.info("Saving all games...")
    # Since this is called from a signal handler or shutdown hook, we might need to run it in a loop
    # But for simplicity in this architecture, we'll just try to run it if there's a loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def save_async():
        for player in ACTIVE_GAMES:
            if player.game and player.game.engine:
                await player.game.engine.save_game()
    
    if loop.is_running():
        # If loop is running, we can't block it. This function is likely called from sync context.
        # This is tricky. Ideally, shutdown should be async.
        # For now, let's assume this is called at exit where we can run_until_complete if loop is not running
        # or create a task if it is.
        asyncio.create_task(save_async())
    else:
        loop.run_until_complete(save_async())
        
    logger.info("All games saved.")

def run_server(world: World, port: int = 2300):
    """Run the telnet server (blocking)."""
    asyncio.run(start_server(world, port=port))

if __name__ == "__main__":
    from config import load_world_config
    try:
        world = load_world_config()
        run_server(world)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        save_all_games()
