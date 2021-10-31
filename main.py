# THIS IS A SECONDARY INSTANCE FOR KARUTA ASSIST AND ONLY DOES EVENT PINGS/DATING QUESTIONS/POSSIBLY FRAMES

import discord
from discord.ext import commands
import math
import asyncio
from discord.ext.commands import CommandNotFound
import time
import random
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys

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

boardpossiblestr = "00000wjtwbbdddr2"
directiondict = {"u": "up",
                 "d": "down",
                 "r": "right",
                 "l": "left"}
squaredict = {"0": "0️⃣", # nothing
              "b": "🪙", # bonus
              "d": "⬇", # drop
              "r": "🔪", # robber
              "2": "📈", # doubler
              "w": "🔁", # warp
              "t": "💀", # trap
              "j": "💰" # jeff
              }


restrictedguilds = []
serversheet = []
datingsheet = gspread.Worksheet
minigamesheet = gspread.Worksheet

## INIT
@bot.event
async def on_ready():
    global serversheet
    global datingsheet
    global restrictedguilds
    global minigamesheet

    updates = bot.get_channel(816514583161602069)

    # GOOGLE SHEETS
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('karuta-assist-3fa5c4a641bf.json', scope)
        client = gspread.authorize(creds)

        sheet = client.open('Karuta Assist')

        servers = sheet.get_worksheet(1)
        datingsheet = sheet.get_worksheet(2)
        minigamesheet = sheet.get_worksheet(5)

    except:
        await updates.send("Error connecting to Google Sheets, retrying...")

    serversheet = servers.get_all_records()
    restrictedguilds = [int(i["Guild"]) for i in serversheet]

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


def rankUsers(load):
    net_correct = []
    for i in load:
        if str(i["Visitor"]) not in [k[0] for k in net_correct]:
            net_correct.append([str(i["Visitor"]), i["Result"], (1 if i["Result"] == 0 else 0)])
        else:
            net_correct[net_correct.index([m for m in net_correct if m[0] == str(i["Visitor"])][0])][1] += i[
                "Result"]
            net_correct[net_correct.index([m for m in net_correct if m[0] == str(i["Visitor"])][0])][-1] += (
                1 if i["Result"] == 0 else 0)
    ratios = []
    for i in net_correct:
        ratios.append({
            "Visitor": i[0],
            "Ratio": i[1] * (1 - len([j for j in load if str(j["Visitor"]) == str(i[0])]) / len(load))
        })
    return ratios


def subtract(x, y):
    return [i for i in x if not i in y or y.remove(i)]


def toString(d):
    return f"{d['Visitor']}; {stripURL(d['URL'])}; {d['Question']}; {d['Answer']}"


def stripURL(url):
    s = str(url).split("-")
    out = []
    for i in s:
        if i not in "01234567890":
            out.append(i)
    return "-".join(out[:-1])


def getCoins(load, id):
    return sum([int(i["Coins"]) for i in load if str(id) == str(i["ID"])])

# CLASSES
class Question:
    def __init__(self, kvi_d, url):
        splitd = kvi_d.replace("`", "").split("\n")
        self.visitor = splitd[0].split(" ")[-1][2:-1]
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
        return {"visitor": self.visitor,
                "character": self.character,
                "question": self.question,
                "answer 1": self.answer1,
                "answer 2": self.answer2,
                "answer 3": self.answer3,
                "answer 4": self.answer4}


class Board:
    def __init__(self, player):
        self.id = player
        self.boardlist = [random.choice(list(boardpossiblestr)) for i in range(25)]
        random.shuffle(self.boardlist)
        self.board2dlist = [self.boardlist[0:5],
                            self.boardlist[5:10],
                            self.boardlist[10:15],
                            self.boardlist[15:20],
                            self.boardlist[20:]]
        self.pos = [0, 0]
        self.visited = []
        self.result = []
        self.score = 0

    def up(self):
        if self.pos[-1] != 0:
            self.pos[-1] -= 1
        else:
            self.pos[-1] = 4

    def down(self):
        if self.pos[-1] != 4:
            self.pos[-1] += 1
        else:
            self.pos[-1] = 0

    def left(self):
        if self.pos[0] != 0:
            self.pos[0] -= 1
        else:
            self.pos[0] = 4

    def right(self):
        if self.pos[0] != 4:
            self.pos[0] += 1
        else:
            self.pos[0] = 0

    def move(self, str):
        for i in str:
            if self.board2dlist[self.pos[-1]][self.pos[0]] == "w":
                self.pos = [random.choice([0, 1, 2, 3, 4]), random.choice([0, 1, 2, 3, 4])]
            elif i.lower() == "d":
                self.down()
            elif i.lower() == "u":
                self.up()
            elif i.lower() == "r":
                self.right()
            elif i.lower() == "l":
                self.left()
            self.visited.append((self.board2dlist[self.pos[-1]][self.pos[0]], i.lower()))

    def moves_to_emoji(self, str):
        emoji = ""
        for i in str:
            if i.lower() == "d":
                emoji += "⬇"
            elif i.lower() == "u":
                emoji += "⬆"
            elif i.lower() == "r":
                emoji += "➡"
            elif i.lower() == "l":
                emoji += "⬅"
        return emoji

    def return_path(self):
        return self.visited

    def calculate_score(self):
        self.jeff_count = 0
        for i in self.visited:
            if self.jeff_count > 0 and i[0] == 'j':
                self.jeff_count += 1
                self.result.append(
                    f"You moved {directiondict[i[-1]]} and met Jeff Bezos. He took your other kidney and shipped you to the morgue. As the owner of Amazon, he doesn't pay shipping on anything!")
                self.result.append("You died!")
                return
            else:
                if i[0] == '0':
                    self.result.append(f"You moved {directiondict[i[-1]]} and found nothing!")
                elif i[0] == 'b':
                    bonus = 1 + round(random.random() * 5)
                    self.result.append(f"You moved {directiondict[i[-1]]} and found {bonus} coins!")
                    self.score += bonus
                elif i[0] == 'd':
                    drop = 1 + round(random.random() * 5)
                    self.result.append(f"You moved {directiondict[i[-1]]} and dropped {drop} coins!")
                    self.score -= drop
                elif i[0] == 'r':
                    if self.score >= 0:
                        self.result.append(f"You moved {directiondict[i[-1]]} and got robbed of all your coins!")
                    else:
                        self.result.append(
                            f"You moved {directiondict[i[-1]]} and met a robber! But robbers rob coins and not debt!")
                    self.score = min(self.score, 0)
                elif i[0] == '2':
                    self.result.append(
                        f"You moved {directiondict[i[-1]]} and found a special coin that doubles your coins!")
                    self.score *= 2
                elif i[0] == 'w':
                    self.result.append(f"You moved {directiondict[i[-1]]} and were warped to a random spot!")
                elif i[0] == 'j':
                    self.result.append(
                        f"You moved {directiondict[i[-1]]} and met Jeff Bezos. You gave him a kidney and he paid off your debt. As a Prime subscriber, you didn't have to pay shipping!")
                    if self.score < 0:
                        self.score = 0
                    self.jeff_count += 1
                elif i[0] == 't':
                    self.result.append(f"You moved {directiondict[i[-1]]} and fell into a trap! You died!")
                    return


# COMMANDS

# DATING QUESTIONS
@bot.command(aliases=["vi", "VI"])
async def visit(ctx):
    logs = bot.get_channel(825955683996401685)
    errors = bot.get_channel(902049222025682994)
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
    results = [i for i in datingsheet.get_all_records() if
               ((i["URL"][:-6] == url[:-6]) and i["Question"] == question.question)]
    if results:
        goodresults = [i["Answer"] for i in results if i["Result"] == 1]
        neutralresults = [i["Answer"] for i in results if i["Result"] == 0]
        badresults = [i["Answer"] for i in results if i["Result"] == -1]
        if goodresults:
            answer = discord.Embed(title="Collected Data on this Question:",
                                   description="Most likely answer to be correct",
                                   colour=0x00ff00)
            answer.add_field(name="Correct answers",
                             value=f"**Most likely answer** (`mode`)\n - {mode(goodresults) if mode(goodresults) != '' else 'None'}\n*List of all correct answers*\n - {', '.join(goodresults)}",
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
                                 value=f"**Most likely answer** (`mode`)\n - {mode(neutralresults) if mode(neutralresults) != '' else 'None'}\n*List of all neutral answers*\n - {', '.join(neutralresults)}",
                                 inline=False)
            else:
                answer = discord.Embed(title="Collected Data on this Question:",
                                       description="Most likely answer to be correct",
                                       colour=0xff0000)
                answer.add_field(name="Neutral answers",
                                 value="So far there are no neutral answers collected",
                                 inline=False)
                answer.add_field(name="Wrong answers",
                                 value=f"**List of all wrong answers**\n - {', '.join(badresults)}",
                                 inline=False)
        answer.set_thumbnail(url=question.url)
        answer.set_footer(
            text="Note that all answers contain a random element - answering correctly may not earn you AP")
        await msg.reply(embed=answer)
        await kvi.add_reaction("✅")
    else:
        norecords = await ctx.send("No records found - do your best to answer the question, and check ✅ when finished")
        await kvi.add_reaction("✅")
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
                [question.visitor, question.url, question.question, correctanswer, questionresult])
            break
        except:
            pass
    await output.edit(content="Loading the Sheet... please wait")
    tries = 0
    loads = 0
    while True:
        try:
            load = datingsheet.get_all_records()
            break
        except:
            loads += 1
            await output.edit(content=f"Loading the Sheet... please wait\nTries: {loads}")
    nonemptyanswers = [i for i in load if i["URL"] is not None]
    await output.edit(content="Waiting for Google Sheets... please wait")
    while True:
        try:
            ind = load.index({
                "Visitor": int(question.visitor),
                "URL": question.url,
                "Question": question.question,
                "Answer": correctanswer,
                "Result": questionresult
            }) + 2
            await output.delete()
            log = discord.Embed(title="Dating Answer Submitted",
                                description=f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}")
            log.set_thumbnail(url=botIcon)
            log.add_field(name="Index", value=ind, inline=False)
            log.add_field(name="Visitor",
                          value=question.visitor,
                          inline=False)
            log.add_field(name="URL",
                          value=stripURL(question.url),
                          inline=False)
            log.add_field(name="Question",
                          value=question.question, inline=False)
            log.add_field(name="Answer", value=correctanswer, inline=False)
            log.add_field(name="Result", value=questionresult, inline=False)
            await logs.send(embed=log)
            await msg.reply(
                f"Data sent! Thank you! Your response number is {ind}. For error reporting please have this number ready.")
            await resp.delete()
            break
        except:
            tries += 1
            await output.edit(content=f"Waiting for Google Sheets... please wait\nTries: {tries}")


@bot.command(aliases=["du"])
async def dateupdate(ctx, index, *args):
    msg = ctx.message
    answer = " ".join(args)
    if ctx.author.id == 166271462175408130:
        while True:
            try:
                datingsheet.update_cell(index, 4, answer)
                await msg.reply(f"Answer on row {index} changed to `{answer}`")
                break
            except:
                pass
    else:
        await msg.reply("You do not have access to this command.")


@bot.command(aliases=["dlb"])
async def dateleaderboard(ctx):
    msg = ctx.message
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
    most_answers = mode([i["Visitor"] for i in load])
    most_answers_1 = len([i for i in load if str(i["Visitor"]) == str(most_answers) and i["Result"] == 1])
    most_answers_0 = len([i for i in load if str(i["Visitor"]) == str(most_answers) and i["Result"] == 0])
    most_answers_neg1 = len([i for i in load if str(i["Visitor"]) == str(most_answers) and i["Result"] == -1])
    most_answers_num = len([i for i in load if str(i["Visitor"]) == str(most_answers)])

    most_correct = mode([i["Visitor"] for i in load if i["Result"] == 1])
    most_correct_num = len([i for i in load if str(i["Visitor"]) == str(most_correct) and i["Result"] == 1])
    most_correct_sum = len([i for i in load if str(i["Visitor"]) == str(most_correct)])

    most_incorrect = mode([i["Visitor"] for i in load if i["Result"] == -1])
    most_incorrect_num = len([i for i in load if str(i["Visitor"]) == str(most_incorrect) and i["Result"] == -1])
    most_incorrect_sum = len([i for i in load if str(i["Visitor"]) == str(most_incorrect)])

    net_correct = []
    for i in load:
        if str(i["Visitor"]) not in [k[0] for k in net_correct]:
            net_correct.append([str(i["Visitor"]), i["Result"]])
        else:
            net_correct[net_correct.index([m for m in net_correct if m[0] == str(i["Visitor"])][0])][-1] += i["Result"]
    most_net_correct = sorted(net_correct, key=lambda x: x[1], reverse=True)[0][0]
    most_net_correct_num = sum([i["Result"] for i in load if str(i["Visitor"]) == str(most_net_correct)])
    most_net_correct_1 = len([i for i in load if str(i["Visitor"]) == str(most_net_correct) and i["Result"] == 1])
    most_net_correct_0 = len([i for i in load if str(i["Visitor"]) == str(most_net_correct) and i["Result"] == 0])
    most_net_correct_neg1 = len([i for i in load if str(i["Visitor"]) == str(most_net_correct) and i["Result"] == -1])
    most_net_correct_sum = len([i for i in load if str(i["Visitor"]) == str(most_net_correct)])

    most_net_incorrect = sorted(net_correct, key=lambda x: x[1])[0][0]
    most_net_incorrect_num = sum([i["Result"] for i in load if str(i["Visitor"]) == str(most_net_incorrect)])
    most_net_incorrect_1 = len([i for i in load if str(i["Visitor"]) == str(most_net_incorrect) and i["Result"] == 1])
    most_net_incorrect_0 = len([i for i in load if str(i["Visitor"]) == str(most_net_incorrect) and i["Result"] == 0])
    most_net_incorrect_neg1 = len(
        [i for i in load if str(i["Visitor"]) == str(most_net_incorrect) and i["Result"] == -1])
    most_net_incorrect_sum = len([i for i in load if str(i["Visitor"]) == str(most_net_incorrect)])

    most_asked_question = mode([i["Question"] for i in load])
    most_correct_question = mode([i["Question"] for i in load if i["Result"] == 1])
    most_incorrect_question = mode([i["Question"] for i in load if i["Result"] == -1])
    most_given_answer = mode([i["Answer"] for i in load])

    leaderboard = discord.Embed(title="Dating Question Leaderboards", description="Statistics for the users")
    leaderboard.add_field(name="Most Answers",
                          value=f"<@{most_answers}> ({most_answers_1}/{most_answers_0}/{most_answers_neg1} out of {most_answers_num} total)",
                          inline=False)
    leaderboard.add_field(name="Most Correct Answers",
                          value=f"<@{most_correct}> ({most_correct_num} out of {most_correct_sum} total)", inline=False)
    leaderboard.add_field(name="Most Incorrect Answers",
                          value=f"<@{most_incorrect}> ({most_incorrect_num} out of {most_incorrect_sum} total)",
                          inline=False)
    leaderboard.add_field(name="Most Net Correct",
                          value=f"<@{most_net_correct}> ({most_net_correct_num} net score - {most_net_correct_1}/{most_net_correct_0}/{most_net_correct_neg1}, {most_net_correct_sum} total)",
                          inline=False)
    leaderboard.add_field(name="Most Net Incorrect",
                          value=f"<@{most_net_incorrect}> ({most_net_incorrect_num} net score - {most_net_incorrect_1}/{most_net_incorrect_0}/{most_net_incorrect_neg1}, {most_net_incorrect_sum} total))",
                          inline=False)
    leaderboard.add_field(name="Most Asked Question", value=f"{most_asked_question}", inline=False)
    leaderboard.add_field(name="Most Correctly Answered Question", value=f"{most_correct_question}", inline=False)
    leaderboard.add_field(name="Most Incorrectly Answered Question", value=f"{most_incorrect_question}", inline=False)
    leaderboard.add_field(name="Most Given Answer", value=f"{most_given_answer}", inline=False)
    leaderboard.set_thumbnail(url=botIcon)
    leaderboard.set_footer(
        text="Net Correct and Incorrect are based off the sum of answers - when an answer is right, it is recorded as +1, 0 if neutral, and -1 if wrong")
    await loadmsg.delete()
    await msg.reply(embed=leaderboard)


@bot.command(aliases=["ds"])
async def datestats(ctx, *args):
    msg = ctx.message
    if args == ():
        user = ctx.author.id
    else:
        user = args[0]
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
    try:
        userinfo = [i for i in load if str(i["Visitor"]) == str(user)]
        correct_answers = len([i for i in userinfo if i["Result"] == 1])
        wrong_answers = len([i for i in userinfo if i["Result"] == -1])
        neutral_answers = len([i for i in userinfo if i["Result"] == 0])
        net_correct = sum([i["Result"] for i in userinfo])
        total_answers = len(userinfo)

        ratio = net_correct * (1 - total_answers / len(load))

        ranks = sorted(rankUsers(load), key=lambda x: x["Ratio"], reverse=True)
        rank = ranks.index({
            "Visitor": str(user),
            "Ratio": ratio}) + 1

        stats = discord.Embed(title="Dating Stats", description=f"Showing dating answer statistics for <@{user}>")
        stats.add_field(name="Total correct answers",
                        value=f"{correct_answers} out of {total_answers} total answered ({Round(correct_answers / total_answers * 100)}%)",
                        inline=False)
        stats.add_field(name="Total neutral answers",
                        value=f"{neutral_answers} out of {total_answers} total answered ({Round(neutral_answers / total_answers * 100)}%)",
                        inline=False)
        stats.add_field(name="Total wrong answers",
                        value=f"{wrong_answers} out of {total_answers} total answered ({Round(wrong_answers / total_answers * 100)}%)",
                        inline=False)
        stats.add_field(name="Net Correct",
                        value=f"{net_correct} -> [`{correct_answers}` + `0 × {neutral_answers}` - `{wrong_answers}`] out of {total_answers} ({Round(net_correct / total_answers * 100)}%)",
                        inline=False)
        stats.add_field(name="Rank", value=f"{rank} out of {len(ranks) + 1}", inline=False)
        stats.add_field(name="Score", value=round(ratio, 2), inline=False)
        stats.set_thumbnail(url=botIcon)
        stats.set_footer(
            text="Score is calculated by Net Correct × (1 - Total Answers / All Answers)")
        await loadmsg.delete()
        await msg.reply(embed=stats)
    except:
        await msg.reply("You have 0 entries in the database.")


@bot.command(aliases=["rlb"])
async def rankleaderboard(ctx):
    msg = ctx.message
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
    ranks = sorted(rankUsers(load), key=lambda x: x["Ratio"], reverse=True)
    desc = []
    for i in range(len(ranks)):
        desc.append(f"{i + 1}. <@{ranks[i]['Visitor']}> {round(ranks[i]['Ratio'], 2)}\n")
    desclist = [desc[10 * i:10 * (i + 1)] for i in range(Round(len(desc) / 10) + 1)]
    page = 0
    rankembed = discord.Embed(title="Rank Leaderboard",
                              description=f"Top answerers by score:\n\n{''.join(desclist[page % len(desclist)])}")
    rankembed.set_thumbnail(url=botIcon)
    await loadmsg.delete()
    r = await msg.reply(embed=rankembed)
    await r.add_reaction("⬅")
    await r.add_reaction("➡")
    while True:
        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅", "➡"]

            react = await bot.wait_for("reaction_add", check=check, timeout=60)
            if str(react[0].emoji) == "⬅":
                page -= 1
            elif str(react[0].emoji) == "➡":
                page += 1
            edit = discord.Embed(title="Rank Leaderboard",
                                 description=f"Top answerers by score:\n\n{''.join(desclist[page % len(desclist)])}")
            edit.set_thumbnail(url=botIcon)
            await r.edit(embed=edit)
        except asyncio.TimeoutError:
            return


@bot.command(aliases=["sg", "mg"])
async def minigame(ctx):
    msg = ctx.message
    acc = ""
    for i in range(10):
        acc += random.choice(["u", "d", "l", "r"])
    movestr = acc
    b = Board(str(ctx.author.id))
    emojimoves = b.moves_to_emoji(movestr)
    b.move(movestr)
    b.calculate_score()
    while True:
        try:
            load = minigamesheet.get_all_records()
            break
        except:
            pass
    users = [str(i["ID"]) for i in load]
    if str(ctx.author.id) in users:
        user = [i for i in load if str(i["URL"]) == str(ctx.author.id)][0]
        ind = load.index(user)
        coins = user["Coins"]
        while True:
            try:
                minigamesheet.update_cell(ind + 2, 2, coins + b.score)
            except:
                pass
    else:
        while True:
            try:
                minigamesheet.append_row([b.id, b.score])
                break
            except:
                pass
    if b.score == 0:
        res_color = 0xf8e71c
    elif b.score > 0:
        res_color = 0x00ff00
    elif b.score < 0:
        res_color = 0xff0000
    result = "\n".join(b.result)
    desclist = []
    for i in b.board2dlist:
        desclist.append("".join([squaredict[k] for k in i]))
    res = discord.Embed(title="Minigame Result", description=f"Moves taken:\n{emojimoves}", colour=res_color)
    res.add_field(name="Results", value=result, inline=False)
    res.add_field(name="Tiles", value="".join([squaredict[i[0]] for i in b.visited]), inline=False)
    res.add_field(name="Minigame Map", value="\n".join(desclist), inline=False)
    res.add_field(name="Net Coins", value=f"{b.score} coins" + (f" - {b.jeff_count} kidney(s)" if b.jeff_count > 0 else ""), inline=False)
    res.set_thumbnail(url=botIcon)
    await msg.reply(embed=res)


@bot.command()
async def coins(ctx, *args):
    msg = ctx.message
    if args == ():
        user = ctx.author.id
    else:
        user = args[0]
    loadmsg = await ctx.send("Loading the Sheet... please wait")
    loads = 0
    while True:
        try:
            load = minigamesheet.get_all_records()
            await loadmsg.edit(content="Waiting for Google Sheets... please wait")
            break
        except:
            loads += 1
            await loadmsg.edit(content=f"Loading the Sheet... please wait\nTries: {loads}")
    coin = getCoins(load, user)
    c = discord.Embed(title="Coins", description=f"Coins owned by <@{user}>")
    c.add_field(name="Total coins", value=coin, inline=False)
    c.set_thumbnail(url=botIcon)
    await msg.reply(embed=c)


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
        step = 0
        length = len(load)
        double = []
        waitmsg = await msg.reply(f"Searching entry #{step + 1} of {length}")
        while step < length:
            try:
                if load[step] == load[step + 1]:
                    double.append(step + 2)
            except:
                pass
            step += 1
            await waitmsg.edit(content=f"Searching entry #{step + 1} of {length}")
        await waitmsg.delete()
        await msg.reply(content=f"Consecutive dupes found: {', '.join([str(i) for i in double])}")
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