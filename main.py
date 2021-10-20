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

        servers = sheet.get_worksheet(1)
        datingsheet = sheet.get_worksheet(2)
        eventsheet = sheet.get_worksheet(3)
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
                value=f"This is the 2nd instance of Karuta Assist, you will be able to use both normally", inline=False)
    e.set_thumbnail(url=botIcon)
    e.set_footer(text="Check kinfo for help!")
    await updates.send(embed=e)
    await bot.change_presence(activity=discord.Game(name="kinfo"))
    print("Bot is Ready")


@bot.command(aliases=["d2"])
async def die2(ctx):
    msg = ctx.message
    if ctx.author.id == 166271462175408130:
        await msg.reply("Dying... :skull:")
        sys.exit()
    else:
        await msg.reply("You do not have access to this command")


@bot.command(aliases=["rc"])
async def rollcall(ctx):
    msg = ctx.message
    if ctx.author.id == 166271462175408130:
        await msg.reply("Instance 2 o7")
    else:
        await msg.reply("You do not have access to this command")


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
    return [int(i["Channel"]) for i in serversheet if int(i["Guild"]) == guild]


def mode(arr):
    counts = {k: arr.count(k) for k in set(arr)}
    modes = sorted(dict(filter(lambda x: x[1] == max(counts.values()), counts.items())).keys())
    if modes == arr:
        return ""
    else:
        return "\n".join([str(i) for i in modes])


def rankUsers(load):
    net_correct = []
    for i in load:
        if str(i["Visitor"]) not in [k[0] for k in net_correct]:
            net_correct.append([str(i["Visitor"]), i["Result"], (1 if i["Result"] == 1 else 0)])
        else:
            net_correct[net_correct.index([m for m in net_correct if m[0] == str(i["Visitor"])][0])][1] += i[
                "Result"]
            net_correct[net_correct.index([m for m in net_correct if m[0] == str(i["Visitor"])][0])][-1] += (
                1 if i["Result"] == 1 else 0)
    ratios = []
    for i in net_correct:
        ratios.append({
            "Visitor": i[0],
            "Ratio": (i[1]/i[-1] if i[-1] != 0 else 0) * (1 - 1 / len([j for j in load if str(j["Visitor"]) == str(i[0])]))
        })
    return ratios


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
            await norecords.delete()
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
            send = await ctx.send("Sending data to Google Sheets... please wait")
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
    await send.delete()
    loadmsg = await ctx.send("Loading the Sheet... please wait")
    tries = 0
    loads = 0
    while True:
        try:
            load = datingsheet.get_all_records()
            await loadmsg.delete()
            break
        except:
            loads += 1
            await loadmsg.edit(content=f"Loading the Sheet... please wait\nTries: {loads}")
    trymsg = await ctx.send("Waiting for Google Sheets... please wait")
    while True:
        try:
            ind = load.index({
                "Visitor": int(question.visitor),
                "URL": question.url,
                "Question": question.question,
                "Answer": correctanswer,
                "Result": questionresult
            })
            await trymsg.delete()
            await msg.reply(
                f"Data sent! Thank you! Your response number is {ind + 2}. For error reporting please having this number ready.")
            await resp.delete()
            break
        except:
            tries += 1
            await trymsg.edit(content=f"Waiting for Google Sheets... please wait\nTries: {tries}")


@bot.command(aliases=["dlb"])
async def dateleaderboard(ctx):
    loadmsg = await ctx.send("Loading the Sheet... please wait")
    loads = 0
    while True:
        try:
            load = datingsheet.get_all_records()
            await loadmsg.delete()
            trymsg = await ctx.send("Waiting for Google Sheets... please wait")
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
    most_net_incorrect_neg1 = len([i for i in load if str(i["Visitor"]) == str(most_net_incorrect) and i["Result"] == -1])
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
    await trymsg.delete()
    await ctx.send(embed=leaderboard)


@bot.command(aliases=["ds"])
async def datestats(ctx, *args):
    if args == ():
        user = ctx.author.id
    else:
        user = args[0]
    loadmsg = await ctx.send("Loading the Sheet... please wait")
    loads = 0
    while True:
        try:
            load = datingsheet.get_all_records()
            await loadmsg.delete()
            trymsg = await ctx.send("Waiting for Google Sheets... please wait")
            break
        except:
            loads += 1
            await loadmsg.edit(content=f"Loading the Sheet... please wait\nTries: {loads}")
    userinfo = [i for i in load if str(i["Visitor"]) == str(user)]
    correct_answers = len([i for i in userinfo if i["Result"] == 1])
    wrong_answers = len([i for i in userinfo if i["Result"] == -1])
    neutral_answers = len([i for i in userinfo if i["Result"] == 0])
    net_correct = sum([i["Result"] for i in userinfo])
    total_answers = len(userinfo)

    ratio = (net_correct/correct_answers if correct_answers != 0 else 0) * (1 - 1 / total_answers)

    ranks = sorted(rankUsers(load), key=lambda x: x["Ratio"], reverse=True)
    rank = ranks.index({
        "Visitor": str(user),
        "Ratio": ratio}) + 1

    stats = discord.Embed(title="Dating Stats", description=f"Showing dating answer statistics for <@{user}>")
    stats.add_field(name="Total correct answers", value=f"{correct_answers} out of {total_answers} total answered ({Round(correct_answers/total_answers * 100)}%)", inline=False)
    stats.add_field(name="Total neutral answers", value=f"{neutral_answers} out of {total_answers} total answered ({Round(neutral_answers/total_answers * 100)}%)", inline=False)
    stats.add_field(name="Total wrong answers", value=f"{wrong_answers} out of {total_answers} total answered ({Round(wrong_answers/total_answers * 100)}%)", inline=False)
    stats.add_field(name="Net Correct", value=f"{net_correct} -> [`{correct_answers}` + `0 × {neutral_answers}` - `{wrong_answers}`] out of {total_answers} ({Round(net_correct/total_answers * 100)}%)", inline=False)
    stats.add_field(name="Rank", value=f"{rank} out of {len(ranks) + 1}", inline=False)
    stats.add_field(name="Score", value=round(ratio, 2), inline=False)
    stats.set_thumbnail(url=botIcon)
    stats.set_footer(text="Score is calculated by Net Correct / Total Correct × (max(total_answers, 10)) / All Answers")
    await trymsg.delete()
    await ctx.send(embed=stats)


@bot.command(aliases=["rlb"])
async def rankleaderboard(ctx):
    loadmsg = await ctx.send("Loading the Sheet... please wait")
    loads = 0
    while True:
        try:
            load = datingsheet.get_all_records()
            await loadmsg.delete()
            trymsg = await ctx.send("Waiting for Google Sheets... please wait")
            break
        except:
            loads += 1
            await loadmsg.edit(content=f"Loading the Sheet... please wait\nTries: {loads}")
    ranks = sorted(rankUsers(load), key=lambda x: x["Ratio"], reverse=True)
    desc = []
    for i in range(len(ranks)):
        desc.append(f"{i+1}. <@{ranks[i]['Visitor']}> {round(ranks[i]['Ratio'], 2)}\n")
    desclist = [desc[10 * i:10 * (i + 1)] for i in range(Round(len(desc) / 10) + 1)]
    page = 0
    rankembed = discord.Embed(title="Rank Leaderboard", description=f"Top answerers by score:\n\n{''.join(desclist[page % len(desclist)])}")
    rankembed.set_thumbnail(url=botIcon)
    await trymsg.delete()
    r = await ctx.send(embed=rankembed)
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
            edit = discord.Embed(title="Rank Leaderboard", description=f"Top answerers by score:\n\n{''.join(desclist[page % len(desclist)])}")
            edit.set_thumbnail(url=botIcon)
            await r.edit(embed=edit)
        except asyncio.TimeoutError:
            return

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
            await bot.process_commands(message)
    else:
        await bot.process_commands(message)


bot.run(token)
