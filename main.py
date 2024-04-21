# libraries import
import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from setup import TOKEN

bot_contr = False
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

db = sqlite3.connect('static/db/cars_database')
cur = db.cursor()


async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'''Привет, {member.name}! Я - бот-помощник по поиску и выбору автомобиля.
Чтобы начать со мной работать, напиши команду /start'''
    )


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
    await interaction.response.send_message("""Привет! Я - бот-помощник по поиску и выбору автомобиля.\n
Чтобы узнать, как я работаю вызови команду /helper""", ephemeral=True)


@bot.tree.command(name='finish')
async def finish(interaction: discord.Interaction):
    global bot_contr
    bot_contr = False
    await interaction.response.send_message('Goodbye!')


@bot.tree.command(name='helper')
async def help_bot(interaction: discord.Interaction):
    if bot_contr:
        data = '\n\n'.join(["""1) Все команды пишутся через / на английском языке. Список доступных команд:
/helper - для просмотра инструкции пользования ботом;
/search_price - для поиска по цене;
/search_brand - для поиска по марке авто;
/search_year - для поиска по году производства""",
                            '2) При удачно выданном запросе, бот пришлет фото автомобиля',
                            '3) Если Вы хотите произвести поиск по ценовому диапазону, '
                            'Вы можете ввести как конкретное число, как одноименное неравенство, например, >1000000, '
                            'так и сложное условие в формате {начальная цена:конечная цена};',
                            '4) Пункт 4 так же применим и к поиску по году выпуска авто;',
                            '5) Чтобы завершить мою работу, вызови команду /finish'])
        await interaction.response.send_message(data)


@bot.tree.command(name='search')
async def search(interaction: discord.Interaction):
    if bot_contr:
        await interaction.response.send_message('123')


@bot.tree.command(name='search_brand')
@app_commands.describe(brand="бренд, модель (на англ.):")
async def search_brand(interaction: discord.Interaction, brand: str):
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
                            run,
                            url
                            FROM main""").fetchall()
        countries = cur.execute("""SELECT name FROM countries""").fetchall()
        types = cur.execute("""SELECT name FROM types""").fetchall()
        ans = []
        for i in cars:
            car = f'{i[1]} {i[2]}'.lower().split()
            q = len(set(brand.lower().split()) & set(car))
            if q >= 1 and brand.lower().split()[0] in set(brand.lower().split()) & set(car):
                ans.append((i, q))
        ans.sort(key=lambda x: x[1], reverse=True)
        qqq = 0
        embedList = []

        if ans:
            for q1 in ans:
                url = ''
                q = q1[0]
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

                url = q[16]

                if qqq == 0:
                    # await interaction.response.send_message('Лучший ответ:\n\n' + s)
                    embed = discord.Embed(
                        title='Лучший ответ:',
                        description=s,
                        colour=discord.Colour.from_rgb(106, 192, 245),
                    ).set_image(url=url)
                    embedList.append(embed)
                else:
                    embed = discord.Embed(
                        title='',
                        description=s,
                        colour=discord.Colour.from_rgb(106, 192, 245)
                    ).set_image(url=url)
                    embedList.append(embed)
                print(url)
                qqq += 1

            await interaction.response.send_message(embeds=embedList[:10])
        else:
            await interaction.response.send_message("""По вашему запросу ничего не нашлось, попробуйте еще раз.
Не забывайте указывать бренд и модель автомобиля на английском!""")


@bot.tree.command(name='search_price')
@app_commands.describe(price='цена, конкретное целое число или диапазон')
async def search_by_price(interaction: discord.Interaction, price: str):
    if bot_contr:
        if '>' in price or '<' in price or '=' in price:
            pass
        elif ':' in price:
            price = price.split(':')
            price = f'>={price[0]} and price <= {price[1]}'
        else:
            price = '=' + price
        cars = cur.execute(f"""SELECT id,
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
                                    run,
                                    url
                                    FROM main 
        WHERE price {price}""").fetchall()
        countries = cur.execute("""SELECT name FROM countries""").fetchall()
        types = cur.execute("""SELECT name FROM types""").fetchall()
        cars.sort(key=lambda x: x[13])

        embedList = []
        qqq = 0

        if cars:
            for q in cars:
                url = ''
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

                url = q[16]

                if qqq == 0:
                    # await interaction.response.send_message('Лучший ответ:\n\n' + s)
                    embed = discord.Embed(
                        title='Лучший ответ:',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58),
                    ).set_image(url=url)
                    embedList.append(embed)
                else:
                    embed = discord.Embed(
                        title='',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58)
                    ).set_image(url=url)
                    embedList.append(embed)
                print(url)
                qqq += 1

            await interaction.response.send_message(embeds=embedList[:10])
        else:
            await interaction.response.send_message("""По вашему запросу ничего не нашлось.
Попробуйте поставить другую цену.""")


@bot.tree.command(name='search_year')
@app_commands.describe(year='год производства')
async def search_by_year(interaction: discord.Interaction, year: str):
    if bot_contr:
        if '>' in year or '<' in year or '=' in year:
            pass
        elif ':' in year:
            year = year.split(':')
            year = f'>= "{year[0]}" and year <= "{year[1]}"'
        else:
            year = '=' + year
        print(year)
        cars = cur.execute(f"""SELECT id,
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
                                    run,
                                    url
                                    FROM main 
        WHERE year {year}""").fetchall()
        countries = cur.execute("""SELECT name FROM countries""").fetchall()
        types = cur.execute("""SELECT name FROM types""").fetchall()
        print(cars)
        embedList = []
        qqq = 0

        if cars:
            for q in cars:
                url = ''
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

                url = q[16]

                if qqq == 0:
                    # await interaction.response.send_message('Лучший ответ:\n\n' + s)
                    embed = discord.Embed(
                        title='Лучший ответ:',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58),
                    ).set_image(url=url)
                    embedList.append(embed)
                else:
                    embed = discord.Embed(
                        title='',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58)
                    ).set_image(url=url)
                    embedList.append(embed)
                print(url)
                qqq += 1

            await interaction.response.send_message(embeds=embedList[:10])
        else:
            await interaction.response.send_message("""По вашему запросу ничего не нашлось.
Попробуйте поставить другой год производства.""")


@bot.tree.command(name='search_country')
@app_commands.describe(country='страна-производитель')
async def search_country(interaction: discord.Interaction, country: str):
    if bot_contr:
        countries = cur.execute(f"""SELECT id, name FROM countries WHERE name = "{country}" """).fetchall()[0]
        cars = cur.execute(f"""SELECT id,
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
                            run,
                            url
                            FROM main
                            WHERE country = {countries[0]}""").fetchall()

        types = cur.execute("""SELECT name FROM types""").fetchall()

        embedList = list()
        qqq = 0

        if cars:
            for q in cars:
                url = ''
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

                s += f'Страна производителя: {countries[1]}\n'

                s += f'Тип кузова: {types[q[11] - 1][0]}\n'

                s += f'Годовой налог: {q[12]}\n'

                s += f'Цена: ~{q[13]} руб.\n'

                url = q[16]

                if qqq == 0:
                    # await interaction.response.send_message('Лучший ответ:\n\n' + s)
                    embed = discord.Embed(
                        title='Лучший ответ:',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58),
                    ).set_image(url=url)
                    embedList.append(embed)
                else:
                    embed = discord.Embed(
                        title='',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58)
                    ).set_image(url=url)
                    embedList.append(embed)
                print(url)
                qqq += 1

            await interaction.response.send_message(embeds=embedList[:10])
        else:
            await interaction.response.send_message("""По вашему запросу ничего не нашлось.
Попробуйте найти другую страну-производителя.""")


@bot.tree.command(name='search_body_type')
@app_commands.describe(body_type='тип кузова')
async def search_body_type(interaction: discord.Interaction, body_type: str):
    if bot_contr:
        countries = cur.execute(f"""SELECT name FROM countries""").fetchall()
        types = cur.execute(f"""SELECT id, name FROM types WHERE name = "{body_type}" """).fetchall()[0]
        cars = cur.execute(f"""SELECT id,
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
                            run,
                            url
                            FROM main
                            WHERE body_type = "{types[0]}" """).fetchall()

        embedList = list()
        qqq = 0

        if cars:
            for q in cars:
                url = ''
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

                s += f'Тип кузова: {types[1]}\n'

                s += f'Годовой налог: {q[12]}\n'

                s += f'Цена: ~{q[13]} руб.\n'

                url = q[16]

                if qqq == 0:
                    # await interaction.response.send_message('Лучший ответ:\n\n' + s)
                    embed = discord.Embed(
                        title='Лучший ответ:',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58),
                    ).set_image(url=url)
                    embedList.append(embed)
                else:
                    embed = discord.Embed(
                        title='',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58)
                    ).set_image(url=url)
                    embedList.append(embed)
                print(url)
                qqq += 1

            await interaction.response.send_message(embeds=embedList[:10])
        else:
            await interaction.response.send_message("""По вашему запросу ничего не нашлось.
Попробуйте подобрать другой тип кузова.""")


@bot.tree.command(name='search_tax')
@app_commands.describe(tax='сумма налога в год')
async def search_by_tax(interaction: discord.Interaction, tax: str):
    if bot_contr:
        if '>' in tax or '<' in tax or '=' in tax:
            pass
        elif ':' in tax:
            tax = tax.split(':')
            tax = f'>= {tax[0]} and tax_per_year <= {tax[1]}'
        else:
            tax = '=' + tax
        cars = cur.execute(f"""SELECT id,
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
                                    run,
                                    url
                                    FROM main 
        WHERE tax_per_year {tax}""").fetchall()
        countries = cur.execute("""SELECT name FROM countries""").fetchall()
        types = cur.execute("""SELECT name FROM types""").fetchall()
        cars.sort(key=lambda x: x[12])

        embedList = []
        qqq = 0

        if cars:
            for q in cars:
                url = ''
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

                url = q[16]

                if qqq == 0:
                    # await interaction.response.send_message('Лучший ответ:\n\n' + s)
                    embed = discord.Embed(
                        title='Лучший ответ:',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58),
                    ).set_image(url=url)
                    embedList.append(embed)
                else:
                    embed = discord.Embed(
                        title='',
                        description=s,
                        colour=discord.Colour.from_rgb(52, 205, 58)
                    ).set_image(url=url)
                    embedList.append(embed)
                print(url)
                qqq += 1

            await interaction.response.send_message(embeds=embedList[:10])
        else:
            await interaction.response.send_message("""По вашему запросу ничего не нашлось.
Попробуйте поставить другую сумму налога.""")


@bot.listen()
async def on_message(message):
    if not message.author.bot and '/' not in message.content and bot_contr:
        await message.channel.send("""Не-не, я - бот, и разговаривать не умею.
Попроси меня о чем-нибудь в виде команды, и я тебе помогу. Например, /helper тебе в помощь!)""",
                                   file=discord.File('static/img/bot.jpg'))


if __name__ == '__main__':
    bot.run(TOKEN)
