import asyncio
import sys

async def read_until_prompt(reader):
    buffer = ""
    while True:
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=2.0)
            if not data:
                break
            decoded = data.decode('utf-8', errors='ignore')
            # Print to stdout so we can see what's happening
            sys.stdout.write(decoded)
            sys.stdout.flush()
            buffer += decoded
            if ">" in buffer.splitlines()[-1]: # Check if prompt is at the end
                return buffer
        except asyncio.TimeoutError:
            break
    return buffer

async def send_command(writer, command):
    print(f"\n[Client Sending]: {command}")
    writer.write((command + "\n").encode('utf-8'))
    await writer.drain()
    await asyncio.sleep(1)

async def main():
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 2300)
    except ConnectionRefusedError:
        print("Could not connect to server. Is it running?")
        return

    # Initial welcome
    await read_until_prompt(reader)
    
    # New game
    await send_command(writer, "new")
    await read_until_prompt(reader)
    
    # Name
    await send_command(writer, "DemoHero")
    await read_until_prompt(reader)
    
    # Toggle color to make logs cleaner
    await send_command(writer, "toggle_color")
    await read_until_prompt(reader)

    # 1. Test Market (East)
    print("\n--- Testing Market ---")
    await send_command(writer, "travel east") # To Market
    await read_until_prompt(reader)
    
    await send_command(writer, "look")
    response = await read_until_prompt(reader)
    
    # Try to buy something
    await send_command(writer, "buy Theron the Trader Health Potion")
    await read_until_prompt(reader)

    # Go back to Tavern (West)
    await send_command(writer, "travel west")
    await read_until_prompt(reader)

    # 2. Test Combat (North)
    print("\n--- Testing Combat ---")
    await send_command(writer, "equip Rusty Sword")
    await read_until_prompt(reader)
    
    await send_command(writer, "travel north") # To Forest
    response = await read_until_prompt(reader)
    
    # Hunt for enemies
    turns = 0
    while "encountered" not in response and "attacked" not in response and turns < 5:
        print(f"[Client]: Searching for trouble... (Turn {turns})")
        await send_command(writer, "travel south")
        await read_until_prompt(reader)
        await send_command(writer, "travel north")
        response = await read_until_prompt(reader)
        turns += 1

    if "encountered" in response or "attacked" in response:
        print("[Client]: Enemy found! Engaging combat.")
        # Fight loop
        while True:
            await send_command(writer, "attack")
            combat_log = await read_until_prompt(reader)
            if "defeated" in combat_log or "Game Over" in combat_log:
                break
            if "not in combat" in combat_log:
                break
    else:
        print("[Client]: Could not find an enemy after multiple attempts.")

    # Quit
    await send_command(writer, "quit")
    
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
