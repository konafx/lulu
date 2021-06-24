import discord
from dispander import dispand, delete_dispand
import os

intents = discord.Intents.none()
intents.guild_messages = True
intents.reactions = True
# message.guild 取得に必要
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author.bot:
        return
    await dispand(message)

@client.event
async def on_raw_reaction_add(payload):
    await delete_dispand(client, payload=payload)

print("running...")
token = os.environ['DISCORD_BOT_TOKEN']
client.run(token)
