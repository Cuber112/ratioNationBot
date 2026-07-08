import json
import os
import random
import re
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

MEMORY_FILE = "memory.json"
END_TOKEN = "__END__"


async def on_ready():
    print(0)


def clean_text(text):
    text = re.sub(r"http\S+", "", text)  # Remove links
    text = re.sub(r"<@!?\d+>", "", text)  # Remove user pings
    return text.strip().split()


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return {}

    return data if isinstance(data, dict) else {}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=2)


def generate_reply(text):
    memory = load_memory()
    transitions = memory.get("transitions", {})

    if not transitions:
        return None

    words = clean_text(text)
    if not words:
        return None

    start_word = words[-1].lower()
    if start_word not in transitions:
        start_word = random.choice(list(transitions.keys()))

    chain = [start_word]
    for _ in range(8):
        next_words = transitions.get(chain[-1], [])
        if not next_words:
            break

        next_word = random.choice(next_words)
        if next_word in {"", END_TOKEN}:
            break

        chain.append(next_word)

    if not chain:
        return None

    return " ".join(chain)


def update_markov_memory(words):
    memory = load_memory()
    transitions = memory.setdefault("transitions", {})

    if not words:
        save_memory(memory)
        return

    for i in range(len(words) - 1):
        state = words[i].lower()
        next_state = words[i + 1].lower()
        transitions.setdefault(state, []).append(next_state)

    last_word = words[-1].lower()
    transitions.setdefault(last_word, []).append(END_TOKEN)

    save_memory(memory)
    print(f"Updated memory with {len(words) - 1} transitions")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    words = clean_text(message.content)
    if words:
        update_markov_memory(words)

        if not message.content.startswith("!"):
            reply = generate_reply(message.content)
            if reply:
                await message.channel.send(reply)

    await client.process_commands(message)

client.run(open("KEY").readline())