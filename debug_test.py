import asyncio
import sys

async def run_client(name, commands):
    print(f"[{name}] Connecting...")
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 2300)
        print(f"[{name}] Connected")
    except Exception as e:
        print(f"[{name}] Connection failed: {e}")
        return

    try:
        # Read welcome message
        while True:
            line = await reader.readline()
            if not line:
                break
            decoded = line.decode().strip()
            # print(f"[{name}] Server: {decoded}")
            if "Enter your password" in decoded:
                break
        
        print(f"[{name}] Sending password 'new'")
        writer.write(b"new\n")
        await writer.drain()

        # Read character creation prompt
        while True:
            line = await reader.readline()
            if not line:
                break
            decoded = line.decode().strip()
            # print(f"[{name}] Server: {decoded}")
            if "What is your name" in decoded:
                break
        
        print(f"[{name}] Sending name '{name}'")
        writer.write(f"{name}\n".encode())
        await writer.drain()

        # Read until game start
        while True:
            line = await reader.readline()
            if not line:
                break
            decoded = line.decode().strip()
            # print(f"[{name}] Server: {decoded}")
            if ">" in decoded:
                break

        print(f"[{name}] Logged in. Executing commands...")

        for cmd in commands:
            print(f"[{name}] Sending: {cmd}")
            writer.write(f"{cmd}\n".encode())
            await writer.drain()
            
            # Read response (naive)
            try:
                line = await asyncio.wait_for(reader.readline(), timeout=1.0)
                print(f"[{name}] Response: {line.decode().strip()}")
            except asyncio.TimeoutError:
                pass
            
            await asyncio.sleep(0.5)

    except Exception as e:
        print(f"[{name}] Error: {e}")
    finally:
        print(f"[{name}] Closing connection")
        writer.close()
        await writer.wait_closed()

async def main():
    crafter_cmds = [
        "look",
        "inventory",
        "craft potion",
        "inventory"
    ]
    
    await run_client("DebugCrafter", crafter_cmds)

if __name__ == "__main__":
    asyncio.run(main())
