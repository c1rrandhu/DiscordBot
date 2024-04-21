import discord
import sqlite3
from discord.ext import commands
from discord import app_commands
from setup import TOKEN

bot_contr = False
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

db = sqlite3.connect('cars_database')
cur = db.cursor()


@bot.event
async def on_ready():
    print("Bot is ready")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


@bot.tree.command(name='start')
async def start(interaction: discord.Interaction):
    global bot_contr
    bot_contr = True
    await interaction.response.send_message("""Привет! Это бот, который помогает выбрать нужную вам машину. 
    \n/helper - для просмотра инструкции пользования ботом\n
    /search_price - для поиска по цене\n
    /search_brand - для поиска по марке авто\n
    /search_by_mask - для поиска по конкретным характеристикам (см. /helper)""", ephemeral=True)


@bot.tree.command(name='finish')
async def finish(interaction: discord.Interaction):
    global bot_contr
    bot_contr = False
    await interaction.response.send_message('Goodbye!')


@bot.tree.command(name='helper')
async def help_bot(interaction: discord.Interaction):
    if bot_contr:
        data = '\n'.join(["Soon there'll be user manual here..."])
        await interaction.response.send_message(data)


@bot.tree.command(name='search')
async def search(interaction: discord.Interaction):
    if bot_contr:
        await interaction.response.send_message('123')


@bot.tree.command(name='search_brand')
@app_commands.describe(brand="бренд, модель (на англ.):")
async def search(interaction: discord.Interaction, brand: str):
    if bot_contr:
        cars = cur.execute("""SELECT id,
                            brand,
                            model,
                            year,
                            horse_power,
                            engine,
                            drive,
                            fuel,
                            transmission,
                            country,
                            color,
                            body_type,
                            tax_per_year,
                            price,
                            condition,
                            run
                            FROM main""").fetchall()
        countries = cur.execute("""SELECT name FROM countries""").fetchall()
        types = cur.execute("""SELECT name FROM types""").fetchall()
        ans = []
        for i in cars:
            car = f'{i[1]} {i[2]}'.lower().split()
            if len(set(brand.lower().split()) & set(car)) >= 1:
                ans.append(i)
        ans1 = []
        if ans:
            for q in ans:
                s = ''

                s += f'Бренд: {q[1]}\n'

                s += f'Модель: {q[2]}\n'

                s += f'Год выпуска: {q[3]}\n'

                s += f'Лошадиные силы: {q[4]}\n'

                s += f'Объем двигателя: {q[5]}\n'

                if s[6] == 'full':
                    s += f'Привод: полный\n'

                elif s[6] == 'forward':
                    s += f'Привод: передний\n'

                elif s[6] == 'backward':
                    s += f'Привод: задний\n'

                if s[7] == 'diesel':
                    s += f'Привод: дизель\n'

                elif s[7] == 'petrol':
                    s += f'Привод: бензин\n'

                elif s[7] == 'hybrid':
                    s += f'Привод: гибрид\n'

                s += f'Трансмисссия: {q[8]}\n'

                s += f'Страна производителя: {countries[q[9] - 1][0]}\n'

                s += f'Тип кузова: {types[q[11] - 1][0]}\n'

                s += f'Годовой налог: {q[12]}\n'

                s += f'Цена: ~{q[13]} руб.\n'

                ans1.append(s)

            await interaction.response.send_message('\n------------------------\n\n'.join(ans1))
        else:
            await interaction.response.send_message("""По вашему запросу ничего не нашлось, попробуйте еще раз.
Не забывайте указывать бренд и модель автомобиля на английском!""")


@bot.listen()
async def on_message(message):
    if not message.author.bot and '/' not in message.content and bot_contr:
        await message.channel.send("I've received a message")

bot.run(TOKEN)
