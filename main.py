import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import CommandNotFound
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys
from collections import Counter

token = "Nzc5NTAwNjAyNDg0MTk1MzI4.X7hcgg.y4STLPtvCoHYr7lHI3EmE029nbI"
bot = commands.Bot(command_prefix=["k", "K"])

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('karuta-assist-3fa5c4a641bf.json', scope)
client = gspread.authorize(creds)

botIcon = "https://cdn.discordapp.com/attachments/783771457468628996/902034363863146566/unknown.png"
hfp = open("hina.png", "rb")
sfp = open("sayo.png", "rb")
hina = hfp.read()
sayo = sfp.read()

boardpossiblestr = "0wjtwbdr2"
directiondict = {"u": "up",
                 "d": "down",
                 "r": "right",
                 "l": "left"}
squaredict = {"0": "0️⃣",  # nothing
              "b": "🪙",  # bonus
              "d": "⬇",  # drop
              "r": "🔪",  # robber
              "2": "📈",  # doubler
              "w": "🔁",  # warp
              "t": "💀",  # trap
              "j": "💰"  # jeff
              }

restrictedguilds = []
serversheet = []
datingsheet = gspread.Worksheet
datinganswers = []
characters = []
curr_ind = 0

## INIT
@bot.event
async def on_ready():
    global serversheet
    global datingsheet
    global restrictedguilds
    global datinganswers
    global characters
    global curr_ind

    updates = bot.get_channel(816514583161602069)

    # GOOGLE SHEETS
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('karuta-assist-3fa5c4a641bf.json', scope)
        client = gspread.authorize(creds)

        sheet = client.open('Karuta Assist')

        servers = sheet.get_worksheet(1)
        datingsheet = sheet.get_worksheet(2)

    except:
        await updates.send("Error connecting to Google Sheets, retrying...")
    serversheet = servers.get_all_records()
    datinganswers = datingsheet.get_all_records()
    restrictedguilds = [int(i["Guild"]) for i in serversheet]

    if serversheet == [] or datinganswers == [] or restrictedguilds == []:
        try:
            serversheet = servers.get_all_records()
            datinganswers = datingsheet.get_all_records()
            restrictedguilds = [int(i["Guild"]) for i in serversheet]
        except:
            await updates.send("Error initializing data")

    updateChars()
    curr_ind = len(datinganswers)

    while True:
        try:
            load = datingsheet.get_all_records()
            break
        except:
            pass
    listload = [tuple(i.values()) for i in load]
    setload = list(set(listload))
    alldupes = list((Counter(listload) - Counter(setload)).elements())
    dupes = list(set(alldupes))
    indexes = []
    for i in dupes:
        indexes += [k for k in allindex(listload, i)]
    sortind = sorted(indexes)
    consdupes = []
    for i in range(len(sortind)):
        try:
            if load[sortind[i]] == load[sortind[i + 1]]:
                consdupes += [sortind[i], sortind[i + 1]]
        except:
            pass
    actualdupes = []
    for i in range(len(consdupes)):
        try:
            if consdupes[i] == consdupes[i + 1] - 1:
                actualdupes += [consdupes[i] + 2, consdupes[i + 1] + 2]
        except:
            pass
    final = sorted(list(set(actualdupes)))
    if final != []:
        duos = [final[i * 2:(i + 1) * 2] for i in range((len(final) + 2 - 1) // 2)]
        marked = [i[0] for i in duos]
        markedshift = [i - marked.index(i) for i in marked]
        for i in markedshift:
            while True:
                try:
                    datingsheet.delete_rows(i)
                    break
                except:
                    pass

    e = discord.Embed(title=f"2nd instance status as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                      description="Active and inactive commands")
    e.add_field(name="Active commands",
                value="- Dating Questions", inline=False)
    e.add_field(name="Inactive commands", value="-Event pings",
                inline=False)
    e.add_field(name="Other info",
                value=f"This is the 2nd instance of Karuta Assist, you will be able to use all instances normally",
                inline=False)
    e.set_thumbnail(url=botIcon)
    e.set_footer(text="Check kinfo for help!")
    await updates.send(embed=e)
    await bot.change_presence(activity=discord.Game(name="kinfo"))
    print("Bot is Ready")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.event
async def on_command(ctx):
    try:
        if 6 < datetime.datetime.now().hour < 19:
            await bot.user.edit(avatar=hina)
        else:
            await bot.user.edit(avatar=sayo)
    except:
        pass


# KILLSWITCH
@bot.command(aliases=["d2"])
async def die2(ctx):
    msg = ctx.message
    if ctx.author.id == 166271462175408130:
        await msg.reply("Dying... :skull:")
        sys.exit()
    else:
        await msg.reply("You do not have access to this command")


# ROLL CALL
@bot.command(aliases=["rc"])
async def rollcall(ctx):
    msg = ctx.message
    if ctx.author.id == 166271462175408130:
        await msg.reply("Instance 2 o7")
    else:
        await msg.reply("You do not have access to this command")


# BOT WAIT FOR CHECKS
def containsEmbed(ch):
    def inner(message):
        return message.embeds != [] and message.channel == ch and message.author.id == 646937666251915264

    return inner


def isRightUser(reaction):
    def inner(message):
        return message.author.user in reaction.users()

    return inner


def isCallerAndCorrect(msg, content):
    def inner(message):
        return message.author == msg.author and message.content.lower()[
                                                :3] == content and message.channel == msg.channel

    return inner


# HELPERS
# Fuck Python rounding
def Round(fl):
    s = str(fl)
    if s.split(".")[-1] == "5":
        return int(s.split(".")[0]) + 1
    else:
        return round(fl)


# Fuck list.index()
def allindex(l, item):
    indexes = []
    for i, j in enumerate(l):
        if j == item:
            indexes.append(i)
    return indexes


def allowedChannels(guild):
    return [int(i["Channel"]) for i in serversheet if int(i["Guild"]) == guild]


def mode(arr):
    counts = {k: arr.count(k) for k in set(arr)}
    modes = sorted(dict(filter(lambda x: x[1] == max(counts.values()), counts.items())).keys())
    if modes == arr:
        return ""
    elif arr == 1:
        return arr[0]
    else:
        return "\n".join([str(i) for i in modes])


def stripURL(url):
    s = str(url).split("-")
    out = []
    for i in s:
        if i not in "01234567890":
            out.append(i)
    return "-".join(out[:-1]).replace("/versioned", "")


def removeURL(question):
    return {"Question": question["Question"],
            "Answer": question["Answer"],
            "Result": question["Result"]}


def updateChars():
    for url in list(set([i["URL"] for i in datinganswers])):
        characters.append(Character(url, [removeURL(k) for k in datinganswers if k["URL"] == url]))


# CLASSES
class Question:
    def __init__(self, kvi_d, url):
        splitd = kvi_d.replace("`", "").split("\n")
        self.character = " ".join(splitd[1].split(" ")[2:-1]).replace("*", "")
        self.code = splitd[1].split(" ")[-1].replace("(", "").replace(")", "")
        self.question = splitd[6].replace("*", "")[1:-1]
        self.url = url
        self.answer1 = " ".join(splitd[8].split(" ")[1:])
        self.answer2 = " ".join(splitd[9].split(" ")[1:])
        try:
            self.answer3 = " ".join(splitd[10].split(" ")[1:])
        except:
            self.answer3 = ""
        try:
            self.answer4 = " ".join(splitd[11].split(" ")[1:])
        except:
            self.answer4 = ""

    def toDict(self):
        return {"character": self.character,
                "question": self.question,
                "answer 1": self.answer1,
                "answer 2": self.answer2,
                "answer 3": self.answer3,
                "answer 4": self.answer4}


class Character:
    def __init__(self, url, questions):
        self.url = url
        self.questions = questions


# COMMANDS

# DATING QUESTIONS
@bot.command(aliases=["vi", "VI"])
async def visit(ctx):
    global curr_ind
    logs = bot.get_channel(825955683996401685)
    msg = ctx.message
    while True:
        try:
            kvi = await bot.wait_for("message", check=containsEmbed(ctx.channel), timeout=10)
            kvi_e = kvi.embeds[0]
            if kvi_e.title == "Visit Character":
                await kvi.add_reaction("❓")
                break
        except asyncio.TimeoutError:
            return
        except IndexError:
            pass
    while True:
        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "❓"

            await bot.wait_for("reaction_add", check=check, timeout=60)
            kvi_e = kvi.embeds[0]
            if kvi_e.title == "Visit Character" and "1️⃣" in kvi_e.description:
                kvi_d = kvi_e.description
                url = kvi_e.thumbnail.url
                question = Question(kvi_d, url)
                break
        except asyncio.TimeoutError:
            return
    if [i for i in characters if i.url[:-6] == url[:-6]][0]:
        c = [i for i in characters if i.url[:-6] == url[:-6]][0]
        results = [i for i in c.questions if question.question == i["Question"]]
    else:
        results = []
    if results:
        goodresults = [i["Answer"] for i in results if i["Result"] == 1]
        neutralresults = [i["Answer"] for i in results if i["Result"] == 0]
        badresults = [i["Answer"] for i in results if i["Result"] == -1]
        if goodresults:
            answer = discord.Embed(title="Collected Data on this Question:",
                                   description="Most likely answer to be correct",
                                   colour=0x00ff00)
            answer.add_field(name="Correct answers",
                             value=f"**Most likely answer** (`mode`)\n - {mode(goodresults) if mode(goodresults) != '' else 'None'}\n*List of all correct answers*\n - {', '.join(list(set(goodresults)))}",
                             inline=False)
        else:
            answer = discord.Embed(title="Collected Data on this Question:",
                                   description="Most likely answer to be correct",
                                   colour=0xf8e71c)
            answer.add_field(name="Correct answers",
                             value="So far there are no correct answers collected",
                             inline=False)
            if neutralresults:
                answer.add_field(name="Neutral answers",
                                 value=f"**Most likely answer** (`mode`)\n - {mode(neutralresults) if mode(neutralresults) != '' else 'None'}\n*List of all neutral answers*\n - {', '.join(list(set(neutralresults)))}",
                                 inline=False)
            else:
                answer = discord.Embed(title="Collected Data on this Question:",
                                       description="Most likely answer to be correct",
                                       colour=0xff0000)
                answer.add_field(name="Neutral answers",
                                 value="So far there are no neutral answers collected",
                                 inline=False)
                answer.add_field(name="Wrong answers",
                                 value=f"**List of all wrong answers**\n - {', '.join(list(set(badresults)))}",
                                 inline=False)
        answer.set_thumbnail(url=question.url)
        answer.set_footer(
            text="Note that all answers contain a random element - answering correctly may not earn you AP")
        await msg.reply(embed=answer)
        await kvi.add_reaction("✅")
    else:
        emb = discord.Embed(title="No records found", description="Do your best to answer the question, and check ✅ when finished")
        emb.add_field(name="Answers from other characters", value="Click the reaction below to get more data on this question, but for all characters instead", inline=False)
        emb.set_footer(text="Note that this data may not be accurate")
        norecords = await ctx.send(embed=emb)
        await norecords.add_reaction("📈")
        await kvi.add_reaction("✅")
        while True:
            try:
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) == "📈"
                await bot.wait_for("reaction_add", check=check, timeout=15)
                gquery = [i["Answer"] for i in datinganswers if i["Question"] == question.question and i["Result"] == 1]
                nquery = [i["Answer"] for i in datinganswers if i["Question"] == question.question and i["Result"] == 0]
                bquery = [i["Answer"] for i in datinganswers if i["Question"] == question.question and i["Result"] == -1]
                if gquery:
                    qanswer = discord.Embed(title="Collected Data on this Question:",
                                       description="Most likely answer to be correct",
                                       colour=0x00ff00)
                    qanswer.add_field(name="Correct answers",
                                 value=f"**Most likely answer** (`mode`)\n - {mode(gquery) if mode(gquery) != '' else 'None'}\n*List of all correct answers*\n - {', '.join(list(set(gquery)))}",
                                 inline=False)
                else:
                    qanswer = discord.Embed(title="Collected Data on this Question:",
                                       description="Most likely answer to be correct",
                                       colour=0xf8e71c)
                    qanswer.add_field(name="Correct answers",
                                 value="So far there are no correct answers collected",
                                 inline=False)
                    if nquery:
                        qanswer.add_field(name="Neutral answers",
                                     value=f"**Most likely answer** (`mode`)\n - {mode(nquery) if mode(nquery) != '' else 'None'}\n*List of all neutral answers*\n - {', '.join(list(set(nquery)))}",
                                     inline=False)
                    else:
                        qanswer = discord.Embed(title="Collected Data on this Question:",
                                           description="Most likely answer to be correct",
                                           colour=0xff0000)
                        qanswer.add_field(name="Neutral answers",
                                     value="So far there are no neutral answers collected",
                                     inline=False)
                        qanswer.add_field(name="Wrong answers",
                                     value=f"**List of all wrong answers**\n - {', '.join(list(set(bquery)))}",
                                     inline=False)
                qanswer.set_thumbnail(url=question.url)
                qanswer.set_footer(
                text="Note that all answers contain a random element - answering correctly may not earn you AP")
                await norecords.edit(embed=qanswer)
                break
            except asyncio.TimeoutError:
                break
            except:
                pass
    while True:
        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "✅"

            await bot.wait_for("reaction_add", check=check, timeout=60)
            kvi_e = kvi.embeds[0]
            color = str(kvi_e.color)
            if color == "#ff0000":
                embedcolor = 0xff0000
                questionresult = -1
            elif color == "#f8e71c":
                embedcolor = 0xf8e71c
                questionresult = 0
            elif color == "#00ff00":
                embedcolor = 0x00ff00
                questionresult = 1
            if question.answer4 != "":
                numquestions = 4
            elif question.answer3 != "":
                numquestions = 3
            else:
                numquestions = 2
            if not results:
                await norecords.delete()
            response = discord.Embed(
                title=f"You answered this question {['with a neutral result.', 'correctly!', 'incorrectly.'][questionresult]}",
                description="Which answer did you put?",
                colour=embedcolor)
            response.add_field(name="Answer 1", value=question.answer1, inline=False)
            response.add_field(name="Answer 2", value=question.answer2, inline=False)
            if numquestions >= 3:
                response.add_field(name="Answer 3", value=question.answer3, inline=False)
            if numquestions == 4:
                response.add_field(name="Answer 4", value=question.answer4, inline=False)
            response.set_thumbnail(url=question.url)
            resp = await msg.reply(embed=response)

            await resp.add_reaction("1️⃣")
            await resp.add_reaction("2️⃣")
            if numquestions >= 3:
                await resp.add_reaction("3️⃣")
            if numquestions == 4:
                await resp.add_reaction("4️⃣")
            break
        except:
            await ctx.send("Timed out")
            return
    while True:
        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

            r = await bot.wait_for("reaction_add", check=check, timeout=60)
            if r[0].emoji == "4️⃣":
                correctanswer = question.answer4
            elif r[0].emoji == "3️⃣":
                correctanswer = question.answer3
            elif r[0].emoji == "2️⃣":
                correctanswer = question.answer2
            elif r[0].emoji == "1️⃣":
                correctanswer = question.answer1
            output = await ctx.send("Sending data to Google Sheets... please wait")
            break
        except asyncio.TimeoutError:
            await ctx.send("Timed out")
            return
    while True:
        try:
            datingsheet.append_row(
                [question.url, question.question, correctanswer, questionresult])
            break
        except:
            pass
    curr_ind += 1
    log = discord.Embed(title="Dating Answer Submitted",
                        description=f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}")
    log.set_thumbnail(url=botIcon)
    log.add_field(name="Index", value=curr_ind, inline=False)
    log.add_field(name="URL",
                  value=stripURL(question.url),
                  inline=False)
    log.add_field(name="Question",
                  value=question.question, inline=False)
    log.add_field(name="Answer", value=correctanswer, inline=False)
    log.add_field(name="Result", value=questionresult, inline=False)
    await logs.send(embed=log)
    await output.delete()
    await msg.reply(
        f"Data sent! Thank you! Your response number is {curr_ind}. For error reporting please have this number ready.")
    await resp.delete()


@bot.command(aliases=["du"])
async def dateupdate(ctx, index, *args):
    error = bot.get_channel(902049222025682994)
    msg = ctx.message
    answer = " ".join(args)
    while True:
        try:
            datingsheet.update_cell(index, 4, answer)
            await msg.reply(f"Answer on row {index} changed to `{answer}`")
            break
        except:
            pass
    log = discord.Embed(title="Answer Update", description="Due to a misclick or other errors, this answer was changed")
    log.add_field(name="Index", value=index, inline=False)
    log.add_field(name="Editor", value=f"<@{ctx.author.id}>", inline=False)
    log.add_field(name="Answer", value=answer, inline=False)
    log.set_thumbnail(url=botIcon)
    await error.send(embed=log)


@bot.command(aliases=["fd"])
async def finddupes(ctx):
    msg = ctx.message
    if ctx.author.id == 166271462175408130:
        loadmsg = await ctx.send("Loading the Sheet... please wait")
        loads = 0
        while True:
            try:
                load = datingsheet.get_all_records()
                await loadmsg.edit(content="Waiting for Google Sheets... please wait")
                break
            except:
                loads += 1
                await loadmsg.edit(content=f"Loading the Sheet... please wait\nTries: {loads}")
        listload = [tuple(i.values()) for i in load]
        setload = list(set(listload))
        alldupes = list((Counter(listload) - Counter(setload)).elements())
        dupes = list(set(alldupes))
        indexes = []
        for i in dupes:
            indexes += [k for k in allindex(listload, i)]
        sortind = sorted(indexes)
        consdupes = []
        for i in range(len(sortind)):
            try:
                if load[sortind[i]] == load[sortind[i + 1]]:
                    consdupes += [sortind[i], sortind[i + 1]]
            except:
                pass
        actualdupes = []
        for i in range(len(consdupes)):
            try:
                if consdupes[i] == consdupes[i + 1] - 1:
                    actualdupes += [consdupes[i] + 2, consdupes[i + 1] + 2]
            except:
                pass
        final = sorted(list(set(actualdupes)))
        if final != []:
            duos = [final[i * 2:(i + 1) * 2] for i in range((len(final) + 2 - 1) // 2)]
            marked = [i[0] for i in duos]
            markedshift = [i - marked.index(i) for i in marked]
            for i in markedshift:
                while True:
                    try:
                        datingsheet.delete_rows(i)
                        break
                    except:
                        pass
        await loadmsg.delete()
        if final != []:
            out = await msg.reply(f"Deleted rows: {', '.join([str(i) for i in marked]) if final != [] else 'None'}")
        else:
            out = await msg.reply(f"Consecutive dupes found: None")
        updateChars()
        await out.edit("Sheet refreshed!")
    else:
        await msg.reply("You do not have access to this command")


@bot.command(aliases=["r2", "2r"])
async def restart2(ctx):
    msg = ctx.message
    if ctx.author.id == 166271462175408130:
        await msg.reply("Restarting...")
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    else:
        await msg.reply("You do not have access to this command")


# EVENTS
@bot.event
async def on_message(message):
    ch = message.channel
    guild = int(message.guild.id)
    # CHANNEL LIMITING
    if guild in restrictedguilds:
        if int(ch.id) in allowedChannels(guild):
            await bot.process_commands(message)
    else:
        await bot.process_commands(message)


bot.run(token)
