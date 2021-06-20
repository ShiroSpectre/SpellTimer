# import
import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# environment variables
load_dotenv()
TOKEN = os.getenv('discord_token')
PREFIX = os.getenv('prefix')

bot = commands.Bot(command_prefix=PREFIX)

print('> Loading Commandclasses')
for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        bot.load_extension(f'commands.{os.path.splitext(filename)[0]}')
        print(f'{os.path.splitext(filename)[0]} loaded')
print()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('-'*30)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='!start'))

bot.run(TOKEN)