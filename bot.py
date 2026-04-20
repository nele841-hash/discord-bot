import discord
from discord.ext import commands
import json
import os
import random
import time
import asyncio

if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({}, f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

DATA_FILE = "data.json"

cash_data = {}
bank = {}
dirty_money = {}
registered_users = set()

work_cooldown = {}
crime_cooldown = {}
daily_cooldown = {}
credit_cooldown = {}
rob_cooldown = {}

# ---------------- LOAD ----------------
def load_data():
    global cash_data, bank, dirty_money, registered_users, crime_cooldown, work_cooldown, daily_cooldown, credit_cooldown, rob_cooldown

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

                cash_data = data.get("cash", {})
                bank = data.get("bank", {})
                dirty_money = data.get("dirty", {})
                registered_users = set(data.get("registered", []))

                crime_cooldown = {str(k): int(v) for k, v in data.get("crime_cooldown", {}).items()}
                work_cooldown = {str(k): int(v) for k, v in data.get("work_cooldown", {}).items()}
                daily_cooldown = {str(k): int(v) for k, v in data.get("daily_cooldown", {}).items()}
                credit_cooldown = {str(k): int(v) for k, v in data.get("credit_cooldown", {}).items()}
                rob_cooldown = {str(k): int(v) for k, v in data.get("rob_cooldown", {}).items()}

        except:
            cash_data = {}
            bank = {}
            dirty_money = {}
            registered_users = set()
            crime_cooldown = {}
            work_cooldown = {}
            daily_cooldown = {}
            credit_cooldown = {}  
            rob_cooldown = {}  

    else:
        cash_data = {}
        bank = {}
        dirty_money = {}
        registered_users = set()
        crime_cooldown = {}
        work_cooldown = {}
        daily_cooldown = {}
        credit_cooldown = {}
        rob_cooldown = {} 

load_data()

# ---------------- SAVE ----------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "cash": cash_data,
            "bank": bank,
            "dirty": dirty_money,
            "registered": list(registered_users),
            "crime_cooldown": crime_cooldown,
            "work_cooldown": work_cooldown,
            "daily_cooldown": daily_cooldown,
            "credit_cooldown": credit_cooldown,
            "rob_cooldown": rob_cooldown
        }, f, indent=4)
# ---------------- USER INIT ----------------
def ensure_user(user):
    if user not in cash_data:
        cash_data[user] = 100
    if user not in bank:
        bank[user] = 0
    if user not in dirty_money:
        dirty_money[user] = 0

# ---------------- BOT READY ----------------
@bot.event
async def on_ready():
    print(f"Bot je online kao {bot.user}")

# ---------------- PRIJAVA ----------------
@bot.command()
async def prijava(ctx):
    user = str(ctx.author.id)

    if user in registered_users:
        return await ctx.reply("❌ Već imaš račun!", mention_author=False)

    registered_users.add(user)
    ensure_user(user)
    save_data()

    await ctx.reply(f"✅ {ctx.author.mention} tvoj račun je uspješno kreiran!", mention_author=False)

# ---------------- RADI ----------------
@bot.command()
async def radi(ctx):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    ensure_user(user)

    now = int(time.time())

    if user in work_cooldown and now - work_cooldown[user] < 3600:
        left = int(3600 - (now - work_cooldown[user]))
        minutes = left // 60
        seconds = left % 60

        embed = discord.Embed(
            title="Posao",
            description=f"Moraš čekati **{minutes}m {seconds}s** prije ponovnog rada.",
            color=discord.Color.orange()
        )

        return await ctx.reply(embed=embed, mention_author=False)

    # ✅ OVO MORA BITI OVDJE
    work_cooldown[user] = now

    earnings = random.randint(500, 1500)
    cash_data[user] += earnings
    save_data()

    embed = discord.Embed(
        title="💼 Posao završen",
        color=discord.Color.blue()
    )

    embed.add_field(name="💰 Zarada", value=f"```{earnings}$```", inline=False)
    embed.add_field(name="💵 Novo stanje", value=f"```{cash_data[user]}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

# ---------------- BANKA ----------------
@bot.command()
async def banka(ctx):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

    ensure_user(user)

    embed = discord.Embed(title="🏦 Vaš račun", color=discord.Color.gold())

    embed.add_field(name="💰 Novčanik", value=f"```{cash_data[user]:,}$```", inline=True)
    embed.add_field(name="🏦 Banka", value=f"```{bank[user]:,}$```", inline=True)
    embed.add_field(name="🕵️ Prljav novac", value=f"```{dirty_money[user]:,}$```", inline=True)

    await ctx.reply(embed=embed, mention_author=False)

# ---------------- PREBACI ----------------
@bot.command()
async def prebaci(ctx, amount: int):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

    ensure_user(user)

    if amount < 1:
        return await ctx.reply("❌ Minimalan iznos je 1$", mention_author=False)

    if cash_data[user] < amount:
        return await ctx.reply("❌ Nemaš dovoljno novca!", mention_author=False)

    cash_data[user] -= amount
    bank[user] += amount

    save_data()

    embed = discord.Embed(title="Transakcija", color=discord.Color.green())
    embed.add_field(name="💸 Prebačeno", value=f"```{amount}$```", inline=True)
    embed.add_field(name="🏦 Banka", value=f"```{bank[user]}$```", inline=True)

    await ctx.reply(embed=embed, mention_author=False)

# ---------------- PODIGNI ----------------
@bot.command()
async def podigni(ctx, amount: int):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

    ensure_user(user)

    if amount < 1:
        return await ctx.reply("❌ Minimalan iznos je 1$", mention_author=False)

    if bank[user] < amount:
        return await ctx.reply("❌ Nemaš dovoljno novca u banci!", mention_author=False)

    bank[user] -= amount
    cash_data[user] += amount

    save_data()

    embed = discord.Embed(title="Transakcija", color=discord.Color.red())
    embed.add_field(name="💸 Podignuto", value=f"```{amount}$```", inline=True)
    embed.add_field(name="💵 Novčanik", value=f"```{cash_data[user]}$```", inline=True)

    await ctx.reply(embed=embed, mention_author=False)

# ---------------- CRIME ----------------
@bot.command()
async def crime(ctx):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    ensure_user(user)

    now = time.time()

    # 24h cooldown
    if user in crime_cooldown and now - crime_cooldown[user] < 86400:
        left = int(86400 - (now - crime_cooldown[user]))
        hours = left // 3600
        minutes = (left % 3600) // 60

        embed = discord.Embed(
            title="Kriminal",
            description=f"Moraš čekati **{hours}h {minutes}m**",
            color=discord.Color.orange()
        )

        return await ctx.reply(embed=embed, mention_author=False)

    crime_cooldown[user] = int(now)

    earnings = random.randint(10000, 15000)
    dirty_money[user] += earnings

    save_data()

    embed = discord.Embed(
        title="💀 Kriminal završen",
        color=discord.Color.dark_red()
    )

    embed.add_field(name="🕵️ Prljav novac", value=f"```{earnings}$```", inline=False)
    embed.add_field(name="🧾 Ukupno", value=f"```{dirty_money[user]}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

#------------------PRANJE PARA-------------------
@bot.command()
async def operipare(ctx):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    ensure_user(user)

    dirty = dirty_money.get(user, 0)

    if dirty <= 0:
        return await ctx.reply("❌ Nemaš prljavog novca!", mention_author=False)

    # 10% taksa
    tax = int(dirty * 0.10)
    cleaned = dirty - tax

    # update
    dirty_money[user] = 0
    cash_data[user] += cleaned

    save_data()

    embed = discord.Embed(
        title="PRANJE PARA",
        color=discord.Color.green()
    )
    embed.add_field(name="Prljav novac:", value=f"```{dirty}$```", inline=False)
    embed.add_field(name="Oprano:", value=f"```{cleaned}$```", inline=False)
    embed.add_field(name="Taksa (10%):", value=f"```{tax}$```", inline=False)
    

    await ctx.reply(embed=embed, mention_author=False)

@bot.command()
async def daily(ctx):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    ensure_user(user)

    now = int(time.time())

    # 24h cooldown
    if user in daily_cooldown and now - daily_cooldown[user] < 86400:
        left = 86400 - (now - daily_cooldown[user])
        hours = left // 3600
        minutes = (left % 3600) // 60

        embed = discord.Embed(
            title="DAILY",
            description=f"⏳ Moraš čekati **{hours}h {minutes}m**",
            color=discord.Color.orange()
        )

        return await ctx.reply(embed=embed, mention_author=False)

    # set cooldown
    daily_cooldown[user] = now

    # reward
    reward = random.randint(1000, 5000)
    cash_data[user] += reward

    save_data()

    embed = discord.Embed(
        title="DAILY REWARD",
        color=discord.Color.green()
    )

    embed.add_field(name="Dobio si:", value=f"```{reward}$```", inline=False)
    embed.add_field(name="Novo stanje:", value=f"```{cash_data[user]}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

#----------KREDIT--------------
@bot.command()
async def kredit(ctx):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    ensure_user(user)

    now = int(time.time())

    # 3 dana cooldown (259200 sekundi)
    if user in credit_cooldown and now - credit_cooldown[user] < 259200:
        left = 259200 - (now - credit_cooldown[user])
        hours = left // 3600
        minutes = (left % 3600) // 60

        embed = discord.Embed(
            title="KREDIT",
            description=f"⏳ Moraš čekati **{hours}h {minutes}m**",
            color=discord.Color.orange()
        )
        return await ctx.reply(embed=embed, mention_author=False)

    credit_cooldown[user] = now

    amount = 10000
    cash_data[user] += amount

    save_data()

    embed = discord.Embed(
        title="KREDIT",
        color=discord.Color.green()
    )

    embed.add_field(name="Dobio si:", value=f"```{amount}$```", inline=False)
    embed.add_field(name="Novo stanje:", value=f"```{cash_data[user]}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

#-----------------pljackaj---------------
@bot.command()
async def pljackaj(ctx, member: discord.Member):
    user = str(ctx.author.id)
    target = str(member.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    if target not in registered_users:
        return await ctx.reply("❌ Taj korisnik nema račun!", mention_author=False)

    if user == target:
        return await ctx.reply("❌ Ne možeš sebe opljačkati!", mention_author=False)

    ensure_user(user)
    ensure_user(target)

    now = int(time.time())

    # ⏳ cooldown 10 minuta
    if user in rob_cooldown and now - rob_cooldown[user] < 600:
        left = 600 - (now - rob_cooldown[user])
        minutes = left // 60
        seconds = left % 60

        embed = discord.Embed(
            title="PLJAČKA",
            description=f"⏳ Moraš čekati **{minutes}m {seconds}s**",
            color=discord.Color.orange()
        )
        return await ctx.reply(embed=embed, mention_author=False)

    rob_cooldown[user] = now

    success = random.randint(1, 100) <= 60

    if success:
        if cash_data[target] <= 0:
            return await ctx.reply("❌ Osoba nema novca!", mention_author=False)

        percent = random.randint(20, 40)
        stolen = int(cash_data[target] * percent / 100)

        cash_data[target] -= stolen
        cash_data[user] += stolen

        save_data()

        embed = discord.Embed(
            title="PLJAČKA",
            color=discord.Color.green()
        )
        embed.add_field(name="PLJAČKAŠ:", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="ŽRTVA:", value=f"{member.mention}", inline=False)
        embed.add_field(name="UKRADENO:", value=f"```{stolen}$```", inline=False)

    else:
        fine = random.randint(1000, 3000)
        cash_data[user] = max(0, cash_data[user] - fine)

        save_data()

        embed = discord.Embed(
            title="PLJAČKA",
            color=discord.Color.red()
        )
        embed.add_field(name="PLJAČKAŠ:", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="ŽRTVA:", value=f"{member.mention}", inline=False)
        embed.add_field(name="KAZNA:", value=f"```{fine}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

#-------------------SET-----------------------
@bot.command()
async def set(ctx, member: discord.Member, amount: int):
    OWNER_ID = 973286491306487838

    if ctx.author.id != OWNER_ID:
        return await ctx.reply("❌ Nemaš dozvolu!", mention_author=False)

    user = str(member.id)

    ensure_user(user)

    cash_data[user] = amount
    save_data()

    embed = discord.Embed(
        title="SET NOVCA",
        color=discord.Color.gold()
    )

    embed.add_field(name="Korisnik:", value=f"{member.mention}", inline=False)
    embed.add_field(name="Novo stanje:", value=f"```{amount}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

#-----------------SLOT-----------------
@bot.command()
async def slot(ctx, amount: int):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    ensure_user(user)

    if amount < 1:
        return await ctx.reply("❌ Minimalan ulog je 1$", mention_author=False)

    if cash_data[user] < amount:
        return await ctx.reply("❌ Nemaš dovoljno novca!", mention_author=False)

    symbols = ["🍒", "🍋", "🍇", "💎", "7️⃣"]

    r1 = random.choice(symbols)
    r2 = random.choice(symbols)
    r3 = random.choice(symbols)

    result = f"{r1} | {r2} | {r3}"

    # 🎰 WIN / LOSS LOGIKA
    if r1 == r2 == r3:
        if r1 == "💎":
            win = amount * 7
        elif r1 == "7️⃣":
            win = amount * 4
        else:
            win = amount * 2

        cash_data[user] += win

        title = "Dobitak"
        color = discord.Color.green()
        change_text = f"+{win:,}$"

    elif r1 == r2 or r1 == r3 or r2 == r3:
        win = int(amount * 1.5)
        cash_data[user] += win

        title = "Dobitak"
        color = discord.Color.gold()
        change_text = f"+{win:,}$"

    else:
        cash_data[user] -= amount

        title = "Gubitak"
        color = discord.Color.red()
        change_text = f"-{amount:,}$"

    save_data()

    embed = discord.Embed(
        title=title,
        color=color
    )

    embed.add_field(name="🎲 Rezultat", value=f"```{result}```", inline=False)
    embed.add_field(name="💸 Dob/Gub", value=f"```{change_text}```", inline=False)
    embed.add_field(name="💰 Stanje", value=f"```{cash_data[user]:,}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

#-----------------RULET---------------
@bot.command()
async def rulet(ctx, choice: str, amount: int):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo uraditi !prijava", mention_author=False)

    ensure_user(user)

    if amount < 1:
        return await ctx.reply("❌ Minimalan ulog je 1$", mention_author=False)

    if cash_data[user] < amount:
        return await ctx.reply("❌ Nemaš dovoljno novca!", mention_author=False)

    # 🎲 spin
    number = random.randint(0, 36)

    red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    black_numbers = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

    if number == 0:
        color = "green"
    elif number in red_numbers:
        color = "red"
    else:
        color = "black"

    choice = choice.lower()

    win = 0

    # 🎯 NUMBER BET
    if choice.isdigit():
        if int(choice) == number:
            win = amount * 35
            cash_data[user] += win
            outcome = "🎯 JACKPOT BROJ!"
        else:
            cash_data[user] -= amount
            outcome = "❌ GUBITAK"

    # 🎯 COLOR BET
    else:
        if choice == color:
            if color == "green":
                win = amount * 14
            else:
                win = amount * 2

            cash_data[user] += win
            outcome = "🎯 POBJEDA!"
        else:
            cash_data[user] -= amount
            outcome = "❌ GUBITAK"

    save_data()

    # 💥 FORMATIRANJE REZULTATA (kako si tražio)
    result_text = f"```{number}, {color}```"

    embed = discord.Embed(
        title="RULET",
        description=result_text,
        color=discord.Color.green() if win > 0 else discord.Color.red()
    )

    if win > 0:
        embed.add_field(name="Dobitak", value=f"```+{win:,}$```", inline=False)
    else:
        embed.add_field(name="Gubitak", value=f"```-{amount:,}$```", inline=False)

    embed.add_field(name="Stanje", value=f"```{cash_data[user]:,}$```", inline=False)

    await ctx.reply(embed=embed, mention_author=False)
#---------------------TOP10---------------------
@bot.command()
async def top10(ctx):
    if not bank:
        return await ctx.reply("Nema podataka.")

    # sortiranje po banci
    sorted_users = sorted(bank.items(), key=lambda x: x[1], reverse=True)

    embed = discord.Embed(
        title="TOP 10 NAJBOGATIJIH",
        color=discord.Color.gold()
    )

    desc = ""

    for i, (user_id, money) in enumerate(sorted_users[:10], start=1):
        member = await bot.fetch_user(int(user_id))

        # format broja (100000 -> 100,000)
        formatted = f"{money:,}"

        desc += f"**{i}. {member.name}** — `{formatted}$`\n"

    embed.description = desc

    await ctx.reply(embed=embed)

#-----------------HELP----------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="CASINO KOMANDE",
        description="Lista svih dostupnih komandi",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="💼 Osnovne komande",
        value=(
            "`!prijava` - otvara račun\n"
            "`!radi` - radi posao i zarađuješ\n"
            "`!banka` - vidi stanje novca\n"
            "`!prebaci <iznos>` - šalje novac u banku\n"
            "`!podigni <iznos>` - uzima novac iz banke"
        ),
        inline=False
    )

    embed.add_field(
        name="🎰 Casino igre",
        value=(
            "`!slot <ulog>` - slot mašina\n"
            "`!rulet <crvena/crna/broj> <ulog>` - rulet igra\n"
            "`!pljackaj @user` - pljačka igrača\n"
            "`!crime` - kriminal (prljav novac)\n"
            "`!operipare` - pere prljav novac\n"
            "`!kredit` - dobiješ 10k svakih 3 dana"
        ),
        inline=False
    )

    embed.add_field(
        name="🏆 Statistika",
        value=(
            "`!top10` - najbogatiji igrači\n"
            "`!daily` - dnevna nagrada"
        ),
        inline=False
    )

    embed.add_field(
        name="⚙️ Admin",
        value="`!set @user <iznos>` - mijenja novac (samo owner)",
        inline=False
    )

    await ctx.reply(embed=embed) 
#------------gg--------------------
class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.entries = []

    @discord.ui.button(label="🎉 Join", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = interaction.user

        if user.id in self.entries:
            await interaction.response.send_message("❌ Već si u giveaway-u!", ephemeral=True)
            return

        self.entries.append(user.id)
        await interaction.response.send_message("✅ Ušao si!", ephemeral=True)
#-----------------GW-----------------
@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, time: int, *, prize: str):

    view = GiveawayView()

    embed = discord.Embed(
        title="🎁 GIVEAWAY",
        description=f"""
🏆 Nagrada: **{prize}**
👥 Učesnici: **0**
⏳ Vrijeme: **{time}s**
        """,
        color=discord.Color.gold()
    )

    msg = await ctx.send(embed=embed, view=view)

    while time > 0:
        await asyncio.sleep(5)
        time -= 5

        embed.description = f"""
🏆 Nagrada: **{prize}**
👥 Učesnici: **{len(view.entries)}**
⏳ Vrijeme: **{time}s**
        """

        await msg.edit(embed=embed, view=view)

    if len(view.entries) == 0:
        await ctx.send("❌ Nema učesnika!")
        return

    winner_id = random.choice(view.entries)
    winner = await ctx.guild.fetch_member(winner_id)

    await ctx.send(f"🏆 Pobjednik je: {winner.mention} 🎉")
# ---------------- RUN ----------------

import os

bot.run(os.getenv("DISCORD_TOKEN"))
