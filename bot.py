import discord
from discord.ext import commands
import json
import os
import random
import time

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

# 🛒 SHOP SYSTEM
shop_items = {
    "knife": 5000,
    "pistol": 15000,
    "zastita": 20000
}

user_inventory = {}

business_owner = {}
business_last_pay = {}
# ---------------- LOAD ----------------
def load_data():
    global cash_data, bank, dirty_money, registered_users
    global crime_cooldown, work_cooldown, daily_cooldown, credit_cooldown, rob_cooldown
    global user_inventory
    global business_owner, business_last_pay

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

                # 🎒 INVENTORY
                user_inventory = data.get("user_inventory", {})

                # 🏢 BUSINESS
                business_owner = data.get("business_owner", {})
                business_last_pay = data.get("business_last_pay", {})

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

            user_inventory = {}

            business_owner = {}
            business_last_pay = {}

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

        user_inventory = {}

        business_owner = {}
        business_last_pay = {}

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
            "rob_cooldown": rob_cooldown,

            # 🎒 INVENTORY
            "user_inventory": user_inventory,

            # 🏢 BUSINESS SYSTEM
            "business_owner": business_owner,
            "business_last_pay": business_last_pay

        }, f, indent=4)
# ---------------- USER INIT ----------------
def ensure_user(user):
    if user not in cash_data:
        cash_data[user] = 100

    if user not in bank:
        bank[user] = 0

    if user not in dirty_money:
        dirty_money[user] = 0

    
    if user not in user_inventory:
        user_inventory[user] = []

    
    if user not in business_owner:
        business_owner[user] = None

    if user not in business_last_pay:
        business_last_pay[user] = 0

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
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

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
        return await ctx.reply(
            "❌ Moraš prvo otvoriti račun sa `!prijava` da bi koristio banku!",
            mention_author=False
        )

    ensure_user(user)

    embed = discord.Embed(title="🏦 Vaš račun", color=discord.Color.gold())

    # 💰 1. RED
    embed.add_field(
        name="💰 Novčanik",
        value=f"`{cash_data[user]:,}$`",
        inline=True
    )

    embed.add_field(
        name="🏦 Banka",
        value=f"`{bank[user]:,}$`",
        inline=True
    )

    embed.add_field(
        name="🕵️ Prljav novac",
        value=f"`{dirty_money[user]:,}$`",
        inline=True
    )

    # 📦 INVENTORY (2. RED)
    items = user_inventory.get(user, [])

    if items:
        names = {
            "pistol": "Pištolj",
            "knife": "Nož",
            "zastita": "Zaštita"
        }

        pretty_items = [names.get(i, i) for i in items]
        inv_text = "\n".join(f"`{i}`" for i in pretty_items)
    else:
        inv_text = "`Prazno`"

    embed.add_field(
        name="📦 Inventory",
        value=inv_text,
        inline=True
    )

    # 🏢 BIZNIS
    biznis = business_owner.get(user)

    if biznis:
        biz_names = {
            "fabrikabudjavoggraza": "Fabrika budjavog graza",
            "kiosk": "Kiosk",
            "autopraonica": "Autopraonica"
        }

        biz_text = biz_names.get(biznis, biznis)
    else:
        biz_text = "Nemaš biznis"

    embed.add_field(
        name="🏢 Biznis",
        value=f"`{biz_text}`",
        inline=True
    )

    await ctx.reply(embed=embed)
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

    now = int(time.time())

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

    crime_cooldown[user] = now

    # 📦 INVENTORY
    if user not in user_inventory:
        user_inventory[user] = []

    inv = user_inventory[user]

    # ❌ mora imati pištolj
    if "pistol" not in inv:
        return await ctx.reply("❌ Treba ti pištolj za crime!", mention_author=False)

    # 💰 25k - 40k PRLJAVOG NOVCA
    earnings = random.randint(25000, 40000)

    if user not in dirty_money:
        dirty_money[user] = 0

    dirty_money[user] += earnings

    # 🔫 pištolj se troši
    inv.remove("pistol")

    save_data()

    embed = discord.Embed(
        title="💀 Kriminal uspješan",
        color=discord.Color.dark_red()
    )

    embed.add_field(name="🕵️ Prljav novac", value=f"```+{earnings:,}$```", inline=False)
    embed.add_field(name="🧾 Ukupno", value=f"```{dirty_money[user]:,}$```", inline=False)
    embed.add_field(name="🔫 Status", value="Izgubio si pištolj", inline=False)

    await ctx.reply(embed=embed, mention_author=False)

#------------------PRANJE PARA-------------------
@bot.command()
async def operipare(ctx):
    user = str(ctx.author.id)

    if user not in registered_users:
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

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
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

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
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

    if target not in registered_users:
        return await ctx.reply("❌ Taj korisnik nema račun!", mention_author=False)

    if user == target:
        return await ctx.reply("❌ Ne možeš sebe opljačkati!", mention_author=False)

    ensure_user(user)
    ensure_user(target)

    now = int(time.time())

    # ⏳ cooldown 10 min
    if user in rob_cooldown and now - rob_cooldown[user] < 600:
        left = 600 - (now - rob_cooldown[user])
        return await ctx.reply(f"⏳ Čekaj još {left//60}m {left%60}s", mention_author=False)

    rob_cooldown[user] = now

    # 📦 INVENTORY
    if user not in user_inventory:
        user_inventory[user] = []

    if target not in user_inventory:
        user_inventory[target] = []

    attacker_items = user_inventory[user]
    target_items = user_inventory[target]

    # ❌ mora imati nož
    if "knife" not in attacker_items:
        return await ctx.reply("❌ Treba ti nož za pljačku!", mention_author=False)

    # 🛡️ zaštita
    if "zastita" in target_items:
        target_items.remove("zastita")
        attacker_items.remove("knife")

        save_data()

        embed = discord.Embed(
            title="🛡️ ZAŠTIĆEN",
            color=discord.Color.blue()
        )

        embed.add_field(name="Info", value="Korisnik je imao zaštitu!", inline=False)
        embed.add_field(name="Rezultat", value="Izgubio si nož", inline=False)

        return await ctx.reply(embed=embed, mention_author=False)

    success = random.randint(1, 100) <= 60

    # ❌ nema para
    if cash_data[target] <= 0:
        attacker_items.remove("knife")
        save_data()
        return await ctx.reply("❌ Nema para! Izgubio si nož.", mention_author=False)

    # ✔️ USPJEH
    if success:
        percent = 30
        stolen = int(cash_data[target] * percent / 100)

        cash_data[target] -= stolen
        cash_data[user] += stolen

        attacker_items.remove("knife")

        save_data()

        embed = discord.Embed(
            title="💰 PLJAČKA USPJEŠNA",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Rezultat",
            value=f"```PLJAČKAŠ: {ctx.author}\nŽRTVA: {member}\nUKRADENO: {stolen:,}$```",
            inline=False
        )

    # ❌ FAIL
    else:
        fine = random.randint(1000, 3000)
        cash_data[user] = max(0, cash_data[user] - fine)

        attacker_items.remove("knife")

        save_data()

        embed = discord.Embed(
            title="💀 PLJAČKA NEUSPJEŠNA",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Rezultat",
            value=f"```PLJAČKAŠ: {ctx.author}\nŽRTVA: {member}\nKAZNA: {fine:,}$```",
            inline=False
        )

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
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

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
        return await ctx.reply("❌ Moraš prvo otvoriti račun sa `!prijava`", mention_author=False)

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
            "`!banka` - vidi stanje novca i inventory\n"
            "`!pay @user <iznos>` - šalje novac igraču\n"
            "`!shop` - lista itema za kupovinu\n"
            "`!kupi <item>` - kupi oružje / zaštitu"
            "`!daily` - dnevna nagrada\n"
        ),
        inline=False
    )

    embed.add_field(
        name="💀 Rizik/ Crime",
        value=(
            "`!pljackaj @user` - pljačka igrača\n"
            "`!crime` - kriminal (pištolj treba)\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🏢 Biznis sistem",
        value=(
            "`!biznisi` - lista biznisa\n"
            "`!kupibiz <ime>` - kupi biznis\n"
            "`!uzmipare` - uzmi pare iz biznisa\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🏆 Statistika",
        value=(
            "`!top10` - najbogatiji igrači"
        ),
        inline=False
    )

    await ctx.reply(embed=embed)

#----------------SHOP----------------
@bot.command()
async def shop(ctx):
    embed = discord.Embed(
        title="🛒 SHOP",
        description="Dostupni itemi:",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="🔫 Pištolj",
        value=f"`{shop_items['pistol']:,}`",
        inline=False
    )

    embed.add_field(
        name="🔪 Nož",
        value=f"`{shop_items['knife']:,}`",
        inline=False
    )


    embed.add_field(
        name="Zaštita",
        value=f"`{shop_items['zastita']:,}`",
        inline=False
    )
    embed.set_footer(text="Kupovina: !kupi <pistolj/noz>")

    await ctx.reply(embed=embed)
#------------------BUY-----------------
@bot.command()
async def kupi(ctx, item: str):
    user = str(ctx.author.id)

    # ❌ mora prijava
    if user not in registered_users:
        return await ctx.reply(
            f"❌ {ctx.author.mention} moraš prvo otvoriti račun sa `!prijava`",
            mention_author=False
        )

    ensure_user(user)

    item = item.lower()

    # 🔁 MAPIRANJE
    aliases = {
        "pistol": "pistol",
        "pištolj": "pistol",
        "pistolj": "pistol",

        "knife": "knife",
        "noz": "knife",
        "nož": "knife",

        "zastita": "zastita",
        "zaštita": "zastita"
    }

    names = {
        "pistol": "Pištolj",
        "knife": "Nož",
        "zastita": "Zaštita"
    }

    if item not in aliases:
        return await ctx.reply("❌ Item ne postoji! Koristi: pistolj/noz/zastita")

    item = aliases[item]

    if item not in shop_items:
        return await ctx.reply("❌ Taj item nije u shopu!")

    price = shop_items[item]

    if cash_data[user] < price:
        return await ctx.reply("❌ Nemaš dovoljno novca!")

    cash_data[user] -= price

    if user not in user_inventory:
        user_inventory[user] = []

    user_inventory[user].append(item)

    save_data()

    embed = discord.Embed(
        title="🛒 KUPOVINA USPJEŠNA",
        color=discord.Color.green()
    )

    embed.add_field(
        name="User",
        value=f"{ctx.author.mention}",
        inline=False
    )

    embed.add_field(
        name="Item",
        value=f"`{names[item]}`",
        inline=False
    )

    embed.add_field(
        name="Cijena",
        value=f"`{price:,}`",
        inline=False
    )

    embed.add_field(
        name="Status",
        value="`Kupljeno ✔️`",
        inline=False
    )

    await ctx.reply(embed=embed)
# ---------------- BIZNISI ----------------
@bot.command()
async def biznisi(ctx):
    embed = discord.Embed(
        title="🏢 DOSTUPNI BIZNISI",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🏭 Fabrika budjavog graza",
        value="💰 Cijena: `100,000$`\n💸 Zarada: `30,000$ / 24h`",
        inline=False
    )

    embed.add_field(
        name="🏪 Kiosk",
        value="💰 Cijena: `50,000$`\n💸 Zarada: `10,000$ / 24h`",
        inline=False
    )

    embed.add_field(
        name="🚗 Autopraonica",
        value="💰 Cijena: `75,000$`\n💸 Zarada: `20,000$ / 24h`",
        inline=False
    )

    embed.add_field(
        name="🛒 Kupovina",
        value="Koristi: `!kupibiz <ime>`\nPrimjer: `!kupibiz kiosk`",
        inline=False
    )

    await ctx.reply(embed=embed)

# ---------------- KUPI BIZNIS ----------------
@bot.command()
async def kupibiz(ctx, *, biznis: str):
    user = str(ctx.author.id)

    ensure_user(user)

    biznis = biznis.lower().replace(" ", "")

    # 🏢 BIZNISI
    biz = {
        "fabrikabudjavoggraza": 100000,
        "kiosk": 50000,
        "autopraonica": 75000
    }

    names = {
        "fabrikabudjavoggraza": "Fabrika budjavog graza",
        "kiosk": "Kiosk",
        "autopraonica": "Autopraonica"
    }

    if biznis not in biz:
        return await ctx.reply("❌ Taj biznis ne postoji! Koristi !biznisi")

    if cash_data[user] < biz[biznis]:
        return await ctx.reply("❌ Nemaš dovoljno novca!")

    # ❌ već ima biznis
    if business_owner.get(user):
        return await ctx.reply("❌ Već posjeduješ biznis!")

    cash_data[user] -= biz[biznis]

    business_owner[user] = biznis
    business_last_pay[user] = 0

    save_data()

    embed = discord.Embed(
        title="🏢 KUPOVINA USPJEŠNA",
        color=discord.Color.green()
    )

    embed.add_field(
        name="Biznis",
        value=f"`{names[biznis]}`",
        inline=False
    )

    embed.add_field(
        name="Status",
        value="Kupljeno ✔️",
        inline=False
    )

    await ctx.reply(embed=embed)

# ---------------- UZMI PARE ----------------
@bot.command()
async def uzmipare(ctx):
    user = str(ctx.author.id)

    ensure_user(user)

    if user not in business_owner or not business_owner[user]:
        return await ctx.reply("❌ Nemaš biznis!")

    now = int(time.time())

    # ⏳ 24h cooldown
    if user in business_last_pay and now - business_last_pay[user] < 86400:
        left = 86400 - (now - business_last_pay[user])
        hours = left // 3600
        minutes = (left % 3600) // 60

        return await ctx.reply(
            f"⏳ Čekaj još **{hours}h {minutes}m**",
            mention_author=False
        )

    biznis = business_owner[user]

    earnings_map = {
        "fabrikabudjavoggraza": 30000,
        "kiosk": 10000,
        "autopraonica": 20000
    }

    earnings = earnings_map.get(biznis, 0)

    cash_data[user] += earnings
    business_last_pay[user] = now

    save_data()

    embed = discord.Embed(
        title="💰 DNEVNA ZARADA",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Biznis",
        value=f"`{biznis}`",
        inline=False
    )

    embed.add_field(
        name="Zarada",
        value=f"```+{earnings:,}$```",
        inline=False
    )

    await ctx.reply(embed=embed)

# ---------------- PAY ----------------
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    sender = str(ctx.author.id)
    receiver = str(member.id)

    # ❌ mora prijava
    if sender not in registered_users:
        return await ctx.reply(
            f"❌ {ctx.author.mention} moraš prvo otvoriti račun sa `!prijava`",
            mention_author=False
        )

    if receiver not in registered_users:
        return await ctx.reply("❌ Taj korisnik nema račun!")

    ensure_user(sender)
    ensure_user(receiver)

    if amount <= 0:
        return await ctx.reply("❌ Unesi validan iznos!")

    if cash_data[sender] < amount:
        return await ctx.reply("❌ Nemaš dovoljno novca!")

    # 💸 transfer
    cash_data[sender] -= amount
    cash_data[receiver] += amount

    save_data()

    embed = discord.Embed(
        title="💸 TRANSFER NOVCA",
        color=discord.Color.green()
    )

    embed.add_field(
        name="📤 Pošiljaoc",
        value=f"{ctx.author.mention}",
        inline=False
    )

    embed.add_field(
        name="📥 Primalac",
        value=f"{member.mention}",
        inline=False
    )

    embed.add_field(
        name="💰 Iznos",
        value=f"`{amount:,}$`",
        inline=False
    )

    await ctx.reply(embed=embed)
# ---------------- RUN ----------------


import os

bot.run(os.getenv("DISCORD_TOKEN"))
