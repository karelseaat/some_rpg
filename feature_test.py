import asyncio
import sys

async def read_until_prompt(reader, name):
    buffer = ""
    while True:
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=2.0)
            if not data:
                break
            decoded = data.decode('utf-8', errors='ignore')
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
    await asyncio.sleep(1.0) # Slower pace to ensure sync

async def run_client(name, password, actions):
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 2300)
    except ConnectionRefusedError:
        print(f"[{name}] Could not connect.")
        return

    # Initial welcome
    await read_until_prompt(reader, name)
    
    # Login/Create
    await send_command(writer, "new", name)
    await read_until_prompt(reader, name)
    # Server generates password, so we don't send one. We just send the name next.
    await send_command(writer, name, name)
    await read_until_prompt(reader, name)
    
    await send_command(writer, "toggle_color", name)
    await read_until_prompt(reader, name)

    # Execute scripted actions
    for action in actions:
        if action.startswith("WAIT"):
            seconds = int(action.split()[1])
            print(f"[{name}] Waiting {seconds}s...")
            await asyncio.sleep(seconds)
        else:
            await send_command(writer, action, name)
            await read_until_prompt(reader, name)

    await send_command(writer, "quit", name)
    writer.close()
    await writer.wait_closed()

async def main():
    # Alice: The Crafter & Trader
    alice_actions = [
        "travel east", # To Market
        "buy Theron the Trader Health Potion",
        "buy Theron the Trader Health Potion",
        "craft Mega Potion",
        "inventory", # Verify craft
        "travel west", # Back to Tavern
        "WAIT 2", # Wait for everyone to be ready
        "say Here is your potion Bob",
        "give Bob Mega Potion"
    ]

    # Bob: The Receiver
    bob_actions = [
        "WAIT 5", # Wait for Alice to go shopping
        "look",
        "WAIT 5", # Wait for Alice to return
        "inventory", # Check before
        "WAIT 3", # Wait for trade
        "inventory", # Check after
        "equip Mega Potion",
        "yell I GOT THE POWER!"
    ]

    # Charlie: The Distant Observer (Global Chat Test)
    charlie_actions = [
        "travel north", # To Forest
        "WAIT 10",
        "yell Is anyone there?",
        "WAIT 5" # Should hear Bob's yell
    ]

    # Dave: The Local Observer (Local Chat Test)
    dave_actions = [
        "WAIT 10",
        "say Nice potion Bob",
        "WAIT 5"
    ]

    await asyncio.gather(
        run_client("Alice", "AlicePass", alice_actions),
        run_client("Bob", "BobPass", bob_actions),
        run_client("Charlie", "CharliePass", charlie_actions),
        run_client("Dave", "DavePass", dave_actions)
    )

if __name__ == "__main__":
    asyncio.run(main())
