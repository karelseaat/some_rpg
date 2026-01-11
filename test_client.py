"""A telnet client that uses an LLM to play the game."""
import asyncio
import ollama
import argparse
import random
import re

class GameClient:
    def __init__(self, host, port, model='llama2'):
        self.host = host
        self.port = port
        self.model = model
        self.reader = None
        self.writer = None

    async def connect(self):
        """Connect to the telnet server."""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        print(f"Connected to {self.host}:{self.port}")

    async def close(self):
        """Close the connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        print("Connection closed.")

    async def read_until_prompt(self):
        """Read from the server until a prompt is found, or until a timeout."""
        buffer = ""
        print("Reading from server...")
        while True:
            try:
                # Read data with a short timeout
                data = await asyncio.wait_for(self.reader.read(1024), timeout=1.0)
                if not data: # Connection closed
                    print("Connection closed by server.")
                    break
                decoded_data = data.decode('utf-8')
                print(f"Received raw data: {decoded_data!r}")
                buffer += decoded_data
                
                # If a prompt is found, return everything before it.
                if ">" in buffer:
                    print("Prompt found.")
                    parts = buffer.rsplit('>', 1)
                    return parts[0].strip()
                    
            except asyncio.TimeoutError:
                # If a timeout occurs, and no prompt is found, return whatever we have.
                print("Read timeout. Returning buffered data.")
                return buffer.strip()
            except UnicodeDecodeError:
                print("UnicodeDecodeError. Continuing to read.")
                # In case of partial character, continue reading
                continue
        return buffer.strip() # Return whatever is left if connection closes


    async def send_command(self, command):
        """Send a command to the server."""
        self.writer.write((command + '\n').encode('utf-8'))
        await self.writer.drain()

    async def get_llm_command(self, context):
        """Get a command from the LLM."""
        # Only send the last ~2000 characters of the context
        context = context[-2000:]
        
        system_prompt = (
            "You are an AI player in a text-based RPG. Your sole function is to output valid game commands."
            "Your goal is to explore the world, interact, and progress. You are currently in a location within the game."
            "\n\n"
            "**CRITICAL INSTRUCTIONS:**"
            "1. **OUTPUT ONLY COMMANDS:** Your response MUST contain ONLY ONE command, wrapped in `[COMMAND]` and `[/COMMAND]` tags."
            "   - **NO NARRATIVE, NO EXPLANATIONS, NO CHAT.** Just the command."
            "   - For example: `[COMMAND]travel north[/COMMAND]` or `[COMMAND]talk Old Harv[/COMMAND]`."
            "\n"
            "2. **EXPLORE & INTERACT:**"
            "   - Use `look` to get information about your current location and available 'Exits:'."
            "   - Use `travel <direction>` (e.g., `travel north`) to move. Prioritize new directions."
            "   - Use `talk <npc name>` to speak with people. Look for information about quests or items."
            "   - Use `buy <npc name> <item name>` to purchase items (e.g., `buy Theron the Trader Health Potion`)."
            "\n"
            "3. **QUESTS:** If an NPC offers a quest (e.g., 'They have a quest for you: <Quest Name>'), accept it using `accept_quest <npc name>`."
            "4. **COMBAT:** If an enemy appears, engage it using `attack` or `skill <skillname>`."
            "5. **AVOID REPETITION:** Do not issue the exact same command repeatedly unless specifically instructed by the game (e.g., during combat)."
            "6. **USE 'HELP':** If you are truly stuck, use `help`."
            "\n\n"
            "Analyze the game's output and decide your single best next action."
        )
        
        response = ollama.chat(
            model=self.model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': context},
            ]
        )
        
        llm_response = response['message']['content']
        print(f"LLM raw response: {llm_response}")

        # Extract command from between the tags
        command = ""
        try:
            start_tag = "[COMMAND]"
            end_tag = "[/COMMAND]"
            start_index = llm_response.index(start_tag) + len(start_tag)
            end_index = llm_response.index(end_tag, start_index)
            command = llm_response[start_index:end_index].strip()
        except ValueError:
            # Fallback if the LLM doesn't follow instructions (this should ideally not happen now)
            print("LLM did not use command tags. Attempting to extract first line as command.")
            command = llm_response.strip().split('\n')[0]
        
        # Additional cleaning for commands like "look around"
        if command.lower().startswith("look around"):
            command = "look"
        elif command.lower().startswith("look"):
            command = "look"

        # Final cleaning
        command = ''.join(c for c in command if c.isalnum() or c == ' ').strip()
        return command


async def main(host, port, model):
    """Main function."""
    client = GameClient(host, port, model)
    await client.connect()

    try:
        full_context = ""
        latest_location_description = "" # Store the latest location description separately
        last_command = ""
        repeat_count = 0
        
        # Read the welcome message first
        initial_response = await client.read_until_prompt()
        print(initial_response)
        full_context += initial_response + "\n\n"

        # Let's start with a password. Always start a new game for testing.
        start_command = "new"
        print(f"CLI command: {start_command}")
        await client.send_command(start_command)
        await asyncio.sleep(0.5) # Give server a moment
        
        # Read the response to the 'new' command (new password, character creation prompt)
        response = await client.read_until_prompt()
        print(response)
        full_context += response + "\n\n"
        
        # The game now asks for a character name.
        name_prompt = "The game is asking for a character name. Please provide ONLY a single-word name, without any command tags or extra text."
        llm_name_response = await client.get_llm_command(full_context + name_prompt)
        
        # Remove command tags first, then extract the name
        cleaned_llm_response = llm_name_response.replace("[COMMAND]", "").replace("[/COMMAND]", "").strip()
        character_name = cleaned_llm_response.split()[0].strip() if cleaned_llm_response else ""
            
        # Final cleaning to ensure it's alphanumeric and remove 'name' if LLM hallucinated
        if character_name.lower().startswith("name"):
            character_name = character_name[4:].strip() # Remove "name" prefix
        
        character_name = ''.join(c for c in character_name if c.isalnum())
        if not character_name: # Fallback if cleaning leaves an empty string
            character_name = "BotPlayer"
        
        print(f"LLM command (name): {character_name}")
        await client.send_command(character_name)
        await asyncio.sleep(0.5) # Give server a moment

        # Read the response after entering the name (welcome message, initial location desc)
        response = await client.read_until_prompt()
        print(response)
        full_context += response + "\n\n"
        latest_location_description = response # Store the first location description

        # Send toggle_color command to disable colors for the LLM
        toggle_command = "toggle_color"
        print(f"CLI command: {toggle_command}")
        await client.send_command(toggle_command)
        await asyncio.sleep(0.5)

        # Read the response from the toggle_color command
        response = await client.read_until_prompt()
        print(response)
        full_context += response + "\n\n"
        
        while True:
            # Get the next command from the LLM based on the latest server output
            command = await client.get_llm_command(full_context)

            # Loop-breaking logic
            if command == last_command:
                repeat_count += 1
            else:
                repeat_count = 0
            
            if repeat_count > 1:
                print("LLM is stuck in a loop. Forcing a different command.")
                # Try to force exploration by traveling, using the stored latest_location_description
                if "Exits:" in latest_location_description:
                    try:
                        exits_line = [line for line in latest_location_description.split('\n') if "Exits:" in line][-1]
                        # Remove color codes if they somehow made it here (shouldn't with toggle_color)
                        clean_exits_line = re.sub(r'\x1b\[[0-9;]*m', '', exits_line)
                        exits = clean_exits_line.split(":")[1].strip().split(", ")
                        command = f"travel {random.choice(exits)}"
                        print(f"Forcing travel to: {command}")
                    except (IndexError, AttributeError, ValueError) as e:
                        print(f"Error parsing exits for forced travel: {e}. Falling back to help.")
                        command = "help" # Fallback if parsing exits fails
                else:
                    command = "help"
                repeat_count = 0 # Reset counter

            print(f"LLM command: {command}")

            # Send the command to the server
            await client.send_command(command)
            last_command = command # Store the last command
            await asyncio.sleep(1) # Be a bit more human

            # Read the server's response
            response = await client.read_until_prompt()
            print(response)
            
            # Update the full context for the LLM
            full_context += response + "\n\n"
            # Also update the latest_location_description if the response contains one
            if "Exits:" in response and "People here:" in response: # Heuristic for a location description
                latest_location_description = response

            # Keep the full context from growing indefinitely, but keep enough for exits
            num_responses = full_context.count('\n\n')
            if num_responses > 5:
                # Find the start of the 5th-to-last response
                indices = [i for i, char in enumerate(full_context) if full_context.startswith('\n\n', i)]
                if len(indices) > 5:
                    full_context = full_context[indices[-5]:]


    except (EOFError, ConnectionResetError):
        print("Connection closed by server.")
    finally:
        await client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM-powered telnet game client.")
    parser.add_argument("--host", type=str, default="localhost", help="Host of the game server.")
    parser.add_argument("--port", type=int, default=2300, help="Port of the game server.")
    parser.add_argument("--model", type=str, default="llama2", help="Ollama model to use.")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port, args.model))
    except KeyboardInterrupt:
        print("Exiting.")
