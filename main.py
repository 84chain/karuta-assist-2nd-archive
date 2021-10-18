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

botIcon = "https://cdn.discordapp.com/attachments/783771457468628996/881774334916591636/Screenshot_1295_1.png"
botInvite = "https://discord.com/api/oauth2/authorize?client_id=779500602484195328&permissions=116800&scope=bot"
serverInvite = "https://discord.gg/Z3XQ28AUxu"

restrictedguilds = []
serversheet = []
datingsheet = []
eventsheet = []


## INIT
@bot.event
async def on_ready():
    global serversheet
    global datingsheet
    global restrictedguilds
    global eventsheet
    updates = bot.get_channel(816514583161602069)

    # GOOGLE SHEETS
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('karuta-assist-3fa5c4a641bf.json', scope)
        client = gspread.authorize(creds)

        sheet = client.open('Karuta Assist')

        serversheet = sheet.get_worksheet(1)
        datingsheet = sheet.get_worksheet(2)
        eventsheet = sheet.get_worksheet(3)
    except:
        updates.send("Error connecting to Google Sheets, restarting...")
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    restrictedguilds = [int(i["Guild"]) for i in serversheet.get_all_records()]

    e = discord.Embed(title=f"2nd instance status as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                      description="Active and inactive commands")
    e.add_field(name="Active commands",
                value="- Dating Questions", inline=False)
    e.add_field(name="Inactive commands", value="-Event pings",
                inline=False)
    e.add_field(name="Other info",
                value=f"This is the 2nd instance of Karuta Assist, you will be able to use both normally", inline=False)
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
    return [int(i["Channel"]) for i in serversheet.get_all_records() if int(i["Guild"]) == guild]


def mode(arr):
    counts = {k: arr.count(k) for k in set(arr)}
    modes = sorted(dict(filter(lambda x: x[1] == max(counts.values()), counts.items())).keys())
    if modes == arr:
        return ""
    else:
        return ", ".join([str(i) for i in modes])


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


# COMMANDS

# DATING QUESTIONS
@bot.command(aliases=["vi"])
async def visit(ctx):
    while True:
        try:
            kvi = await bot.wait_for("message", check=containsEmbed(ctx.channel), timeout=10)
            kvi_e = kvi.embeds[0]
            if kvi_e.title == "Visit Character":
                await kvi.add_reaction("❓")
                break
        except asyncio.TimeoutError:
            await ctx.send("The `kvi` embed was not found")
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
            await ctx.send(":question: was not given")
            return
    results = [i for i in datingsheet.get_all_records() if
               ((i["URL"][:-6] == url[:-6]) and i["Question"] == question.question)]
    if results:
        goodresults = [i["Answer"] for i in results if i["Result"] == 1]
        neutralresults = [i["Answer"] for i in results if i["Result"] == 0]
        badresults = [i["Answer"] for i in results if i["Result"] == -1]
        answer = discord.Embed(title="Collected Data on this Question:", description="Most likely answer to be correct")
        if goodresults:
            answer.add_field(name="Correct answers",
                             value=f"**Most likely answer** (`mode`)\n - {mode(goodresults)}\n*List of all answers*\n - {goodresults}",
                             inline=False)
        else:
            answer.add_field(name="Correct answers",
                             value="So far there are no correct answers collected",
                             inline=False)
            if neutralresults:
                answer.add_field(name="Neutral answers",
                                 value=f"**Most likely answer** (`mode`)\n - {mode(neutralresults)}\n*List of all answers*\n - {neutralresults}",
                                 inline=False)
            else:
                answer.add_field(name="Neutral answers",
                                 value="So far there are no neutral answers collected",
                                 inline=False)
                answer.add_field(name="Wrong answers",
                                 value=f"**List of all wrong answers**\n - {badresults}",
                                 inline=False)
        answer.set_thumbnail(url=botIcon)
        answer.set_footer(
            text="Note that all answers contain a random element - answering correctly may not earn you AP")
        await ctx.send(answer)
        await kvi.add_reaction("✅")
    else:
        await ctx.send("No records found - do your best to answer the question, and check ✅ when finished")
        await kvi.add_reaction("✅")
    while True:
        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "✅"

            await bot.wait_for("reaction_add", check=check, timeout=60)
            kvi_e = kvi.embeds[0]
            color = str(kvi_e.color)
            if color == "#ff0000":
                questionresult = -1
            elif color == "#f8e71c":
                questionresult = 0
            elif color == "#00ff00":
                questionresult = 1
            if question.answer4 != "":
                numquestions = 4
            elif question.answer3 != "":
                numquestions = 3
            else:
                numquestions = 2

            response = discord.Embed(
                title=f"You answered this question {['with a neutral result.', 'correctly!', 'incorrectly.'][questionresult]}",
                description="Which answer did you put?")
            response.add_field(name="Answer 1", value=question.answer1, inline=False)
            response.add_field(name="Answer 2", value=question.answer2, inline=False)
            if numquestions >= 3:
                response.add_field(name="Answer 3", value=question.answer3, inline=False)
            if numquestions == 4:
                response.add_field(name="Answer 4", value=question.answer4, inline=False)
            response.set_thumbnail(url=botIcon)
            resp = await ctx.send(embed=response)

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
            await ctx.send("Sending data to Google Sheets... please wait")
            break
        except asyncio.TimeoutError:
            await ctx.send("Timed out")
            return
    try:
        datingsheet.append_row(
            [question.visitor, question.url, question.question, correctanswer, questionresult])
        indexes = []
        for i in datingsheet.get_all_records():
            if (str(i["Visitor"]) == str(question.visitor)
                and str(i["URL"]) == str(question.url)
                and str(i["Question"]) == str(question.question)
                and str(i["Answer"]) == str(correctanswer)
                and str(i["Result"]) == str(questionresult)):
                indexes.append(datingsheet.get_all_records().index(i))
        index = indexes[-1]
        await ctx.send(f"Data sent! Thank you! Your response number is {index}. For error reporting please having this number ready.")
    except Exception as e:
        ex = discord.Embed(title="An Exception has occurred...",
                           description=f"Exception on https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}")
        ex.add_field(name="Reason", value=e)
        ex.set_thumbnail(url=botIcon)
        await ctx.send(embed=ex)


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
    msg = message.content
    ch = message.channel
    guild = int(message.guild.id)
    egg = bot.get_channel(826680875637800961)
    # CHANNEL LIMITING
    if guild in restrictedguilds:
        if int(ch.id) in allowedChannels(guild):
            if message.attachments == []:
                await bot.process_commands(message)
            else:
                if int(message.author.id) == 646937666251915264:
                    if message.reactions != []:
                        await egg.send(f"https://discord.com/channels/{message.guild.id}/{ch.id}/{message.id}")
                        time.sleep(int([i["Grace Period"] for i in eventsheet.get_all_records() if
                                        str(i["Server"]) == str(message.guild.id)][0]))
                        for i in message.reactions:
                            if str(i.emoji) == "🍬" or str(i.emoji) == "🍫":
                                await ch.send(
                                    f"<@&{[i['Role ID'] for i in eventsheet.get_all_records() if str(i['Server']) == str(message.guild.id)][0]}>")
                else:
                    await bot.process_commands(message)
    else:
        if message.attachments == []:
            await bot.process_commands(message)
        else:
            if int(message.author.id) == 646937666251915264:
                if message.reactions != []:
                    await egg.send(f"https://discord.com/channels{message.guild.id}/{ch.id}/{message.id}")
                    time.sleep(int([i["Grace Period"] for i in eventsheet.get_all_records() if
                                    str(i["Server"]) == str(message.guild.id)][0]))
                    for i in message.reactions:
                        if str(i.emoji) == "🍬" or str(i.emoji) == "🍫":
                            await ch.send(
                                f"<@&{[i['Role ID'] for i in eventsheet.get_all_records() if str(i['Server']) == str(message.guild.id)][0]}>")
            else:
                await bot.process_commands(message)


bot.run(token)
