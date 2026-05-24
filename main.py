import discord
from discord.ext import commands
import re

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

async def on_ready():
    print(botKey)

def clean_text(text):
    # Strip out whatever here
    text = re.sub(r'http\S+', '', text)  # Remove links
    text = re.sub(r'<@!?\d+>', '', text)  # Remove user pings
    return text.strip().split()

def update_markov_memory(words):
    # Break words into pairs and save them to your database.
    if len(words) < 2:
        return
    
    for i in range(len(words) - 1):
        state = words[i]
        next_state = words[i+1]

        # Make a fucking database this doesn't do shit
        print(f"Learning: {state} -> {next_state}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    words = clean_text(message.content)  
    if words:
        update_markov_memory(words)

    await client.process_commands(message)

with open("KEY", 'r') as file:
    botKey = file.readline()

client.run(botKey)