import asyncio
import random
import sys

async def read_until_prompt(reader, name, log=True):
    buffer = ""
    while True:
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=2.0)
            if not data:
                break
            decoded = data.decode('utf-8', errors='ignore')
            if log:
                for line in decoded.splitlines():
                    if line.strip():
                        print(f"[{name} Recv]: {line}")
            buffer += decoded
            if ">" in buffer.splitlines()[-1]:
                return buffer
        except asyncio.TimeoutError:
            break
    return buffer

async def send_command(writer, command, name):
    print(f"[{name} Send]: {command}")
    writer.write((command + "\n").encode('utf-8'))
    await writer.drain()
    await asyncio.sleep(0.5)

async def run_bot(name, duration_seconds):
    print(f"[{name}] Connecting...")
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 2300)
    except ConnectionRefusedError:
        print(f"[{name}] Connection failed.")
        return

    # Initial welcome
    await read_until_prompt(reader, name)
    
    # Login Flow
    await send_command(writer, "new", name)
    # Server sends password and asks for name
    await read_until_prompt(reader, name)
    
    # Send Name
    await send_command(writer, name, name)
    await read_until_prompt(reader, name)
    
    await send_command(writer, "toggle_color", name)
    await read_until_prompt(reader, name, log=False)

    # Wait for everyone to log in
    await asyncio.sleep(5.0)

    # Give bots quest items for testing
    if name == "SimBot4":
        # Give crystal shard for Mushroom Hunt
        await send_command(writer, "cheat_add_item crystal_shard 1", name)

    # Simulation Loop
    end_time = asyncio.get_event_loop().time() + duration_seconds
    
    actions = ["look", "inventory", "rest short", "status", "investigate", "disarm"]
    directions = ["north", "south", "east", "west"]
    craftable_items = ["Mega Potion"]
    
    # Other bots to interact with
    other_bots = [b for b in ["SimBot1", "SimBot2", "SimBot3", "SimBot4"] if b != name]
    
    while asyncio.get_event_loop().time() < end_time:
        # Randomly choose an activity type
        roll = random.random()
        
        if roll < 0.3: # 30% chance to move
            cmd = f"travel {random.choice(directions)}"
        elif roll < 0.5: # 20% chance to do basic action
            cmd = random.choice(actions)
        elif roll < 0.6: # 10% chance to chat/yell
            if random.random() < 0.5:
                cmd = f"say Hello from {name}!"
            else:
                cmd = f"yell {name} is exploring the world!"
        elif roll < 0.7: # 10% chance to craft
            cmd = f"craft {random.choice(craftable_items)}"
        elif roll < 0.8: # 10% chance to trade/give
            target = random.choice(other_bots)
            # Try to give a potion (might fail if they don't have one, but that's fine for sim)
            cmd = f"give {target} potion"
        elif roll < 0.9: # 10% chance to check map or skills
            cmd = random.choice(["map", "skills"])
        else: # 10% chance to interact with NPCs or Items
            sub_roll = random.random()
            if sub_roll < 0.2:
                cmd = "buy merchant health_potion"
            elif sub_roll < 0.4:
                cmd = "equip rusty_sword"
            elif sub_roll < 0.7:
                cmd = "quest accept healer"
            else:
                cmd = "quest complete The Mushroom Hunt"
            
        await send_command(writer, cmd, name)
        response = await read_until_prompt(reader, name, log=True)
        
        # Handle Combat
        if "attacked by" in response or "vs" in response:
            print(f"[{name}] In Combat!")
            while True:
                # Simple combat AI
                if random.random() < 0.8:
                    await send_command(writer, "attack", name)
                else:
                    await send_command(writer, "flee", name)
                    
                combat_log = await read_until_prompt(reader, name, log=True)
                if "defeated" in combat_log or "Game Over" in combat_log or "fled" in combat_log:
                    break
                if "not in combat" in combat_log:
                    break
                await asyncio.sleep(1)
        
        # Handle Death
        if "Game Over" in response:
            print(f"[{name}] Died. Respawning...")
            # In this simple server, death disconnects or breaks loop. 
            # We'll just exit the bot.
            break

        await asyncio.sleep(random.uniform(2.0, 5.0))

    print(f"[{name}] Simulation finished. Quitting.")
    await send_command(writer, "quit", name)
    writer.close()
    await writer.wait_closed()

async def main():
    # Run 4 bots for 60 seconds (1 minute) for verification
    duration = 60 
    
    await asyncio.gather(
        run_bot("SimBot1", duration),
        run_bot("SimBot2", duration),
        run_bot("SimBot3", duration),
        run_bot("SimBot4", duration)
    )

if __name__ == "__main__":
    asyncio.run(main())
