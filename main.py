import discord
import sqlite3
from discord.ext import commands

bot_contr = False
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='#!', intents=intents)

db = sqlite3.connect('cars_database')
cur = db.cursor()


@bot.command(name='start')
async def start(ctx):
    global bot_contr
    bot_contr = True
    await ctx.send('Hello!')


@bot.command(name='finish')
async def finish(ctx):
    global bot_contr
    bot_contr = False
    await ctx.send('Goodbye!')


@bot.command(name='helper')
async def help_bot(ctx):
    if bot_contr:
        data = '\n'.join(["Soon there'll be user manual here..."])
        await ctx.send(data)


@bot.command(name='search')
async def search(ctx):
    if bot_contr:
        await ctx.send('123')


@bot.listen()
async def on_message(message):
    if not message.author.bot and '#!' not in message.content:
        await message.channel.send("I've received a message")

bot.run(TOKEN)
