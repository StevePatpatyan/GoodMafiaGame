from distutils.command.check import check
import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
import os
import config
from random import randint
from time import sleep
from emoji import demojize



bot = commands.Bot(command_prefix='^')
@bot.event
async def on_ready():
    print("ready")
@bot.command()
async def test(ctx):
    msg = await ctx.channel.send("🇦")
    sleep(5)
    msgs = await ctx.channel.history(limit = 5).flatten()
    print(demojize(str(msgs[0].reactions[0])))
@bot.command()
async def create(ctx):
    user = str(ctx.author.id)
    users = "".join(open("users.txt","r").read().split("\n")).split(",")
    if user in users:
        await ctx.author.send("You are already in an active session, so you cannot create another.")
        return
    await ctx.author.send("Please type a session password. If you don't want a password, type a single character.")
    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.channel.DMChannel)
    password = await bot.wait_for("message", check = check)
    password = password.content
    if len(password) <= 1:
        password = ""
    users = open("users.txt","a+")
    users.write(user+",\n")
    passwords = open("passwords.txt","a+")
    passwords.write(password+"\n")
    await ctx.author.send("Session successfully created. You and others in the session will be alerted when the lobby is full or when there are enough players to start.")
    await ctx.channel.send(ctx.author.mention+" has successfully started a mafia session! Type \"^join\" to join.")
@bot.command()
async def join(ctx):
    user = str(ctx.author.id)
    users =  open("users.txt","r").read().split("\n")
    if user in "".join(users).split(","):
        await ctx.author.send("You are already in an active session, so you cannot join another.")
        return
    listOfSessions = ""
    if len(users) <= 1:
        await ctx.author.send("There are no active sessions.")
        return
    for usr in users:
        usersPerSession = usr.split(",")
        for x in range(len(usersPerSession)-1):
            player = await bot.fetch_user(int(usersPerSession[x]))
            player = player.name
            listOfSessions+="**"+str((x+1))+"**: "+player+", "
        listOfSessions+="\n"
    await ctx.author.send(listOfSessions)
    await ctx.author.send("Select an active session to join by typing the number of the session.")
    def check(m):
        return m.author==ctx.author and isinstance(m.channel, discord.DMChannel) and m.content.isdigit()
    response = await bot.wait_for("message",check = check)
    response = int(response.content)
    if response <= 0 or response > len(users):
        await ctx.author.send("The session number you entered is invalid.")
        return
    password = open("passwords.txt","r").read().split("\n")[response-1]
    passwordResponse = ""
    if password != "":
        await ctx.author.send("Enter the session password: ")
        def check2(m):
            return m.author==ctx.author and isinstance(m.channel, discord.DMChannel)
        passwordResponse = await bot.wait_for("message",check=check2)
        passwordResponse = passwordResponse.content
        if passwordResponse==password:
            passwordResponse = ""
    if passwordResponse == "":
        users[response-1]+= user+","
        open("users.txt","w").write("\n".join(users))
        await ctx.author.send("Successfully joined session!")
        await ctx.channel.send(ctx.author.mention+" successfully joined Session #"+str(response)+" (<@"+str(int(users[response-1].split(",")[0]))+">'s lobby)")
        return
    await ctx.author.send("Incorrect session password")
@bot.command()
async def play(ctx):
    hosts = []
    user = str(ctx.author.id)
    users = open("users.txt","r").read().split("\n")
    for x in range(len(users)-1):
        hosts.append(users[x].split(",")[0])
    if user not in hosts:
        await ctx.author.send("You are not a host of any active session.")
        return
    usersInSession = users[hosts.index(user)].split(",")
    if len(usersInSession) <= 4:
        await ctx.channel.send("There are not enough players to begin.")
        return
    usersInSession.pop(0)
    for x in range(len(usersInSession)-1):
        usersInSession[x] = "<@"+usersInSession[x]+">"
    usersInSession = "".join(usersInSession)
    await ctx.channel.send(usersInSession+" <@"+user+"> has started the Mafia Game!")
    #################################################################################
    usersInSession = users[hosts.index(user)].split(",")
    roles = ["mafia","doctor","detective","townperson"]
    players = {}
    for x in range(len(usersInSession)-1-4):
        roles.append("townsperson")
    await ctx.channel.send("Assigning roles to players...")
    for usr in usersInSession:
        if usr == "":
            break
        roleIndex = randint(0,len(roles)-1)
        players[roles[roleIndex]] = int(usr)
        recipient = await bot.fetch_user(int(usr))
        await recipient.send("You are "+roles[roleIndex])
        roles.pop(roleIndex)
    ###############################################################################
    await ctx.channel.send("Let us begin...")
    while(len(players) >= 2):
        if len(players) > 3:
            await ctx.channel.send("Night falls upon you...")
            victim = ""
            patient = ""
            savedSelf = False
            await ctx.channel.send("Evil doings in progress...")
            while True:
                mafia = await bot.fetch_user((players["mafia"]))
                await mafia.send("Type the name of the person you want to kill.")
                def check3(m):
                    return m.author == mafia and isinstance(m.channel, discord.DMChannel)
                victim = await bot.wait_for("message",check=check3)
                victim = await MemberConverter().convert(ctx,victim.content)
                victim = victim.id
                if victim in players.values():
                    if victim == players["mafia"]:
                        await mafia.send("Your life is worth it. Don't do it.")
                    else:
                        break
                else:
                    await mafia.send("That is not a player.")
            while True:
                doctor = await bot.fetch_user((players["doctor"]))
                await doctor.send("Type the name of the person you want to save.")
                def check4(m):
                    return m.author == doctor and isinstance(m.channel, discord.DMChannel)
                patient = await bot.wait_for("message",check=check4)
                patient = await MemberConverter().convert(ctx,patient.content)
                patient = patient.id
                if patient in players.values():
                    if patient == players["doctor"]:
                        if savedSelf:
                            await doctor.send("Policies say you can't be selfish.")
                        else:
                            savedSelf = True
                            break
                    else:
                        break
                else:
                    await doctor.send("That is not a player.")
            while True:
                detective = await bot.fetch_user((players["detective"]))
                await detective.send("Type the name of the person you want to accuse.")
                def check5(m):
                    return m.author == detective and isinstance(m.channel, discord.DMChannel)
                suspect = await bot.wait_for("message",check=check5)
                suspect = await MemberConverter().convert(ctx,detective.content)
                suspect = suspect.id
                detective = detective.id
                if suspect in players.values():
                    if suspect == players["detective"]:
                        await detective.send("You're obviously not the mafia... right?")
                    else:
                        break
                else:
                    await mafia.send("That is not a player.")
##################################################################################################################
            for x in range(len(usersInSession)-1):
                usersInSession[x] = "<@"+usersInSession[x]+">"
            usersInSession = "".join(usersInSession)
            await ctx.channel.send(usersInSession,"Wake up! There is some news!")
            sleep(3)
            expos = open("expositions.txt","r").read().split("\n")
            deaths = open("deaths.txt","r").read().split("\n")
            revivals = open("revivals.txt","r").read().split("\n")                
            chosenExpo = expos[randint(len(expos))].replace("[VIC]", "<@" + str(suspect) + ">")
            chosenDeath = deaths[randint(len(deaths))].replace("[VIC]", "<@" + str(suspect) + ">")
            chosenRevival = revivals[randint(len(revivals))].replace("[VIC]", "<@" + str(suspect) + ">")
            await ctx.channel.send(chosenExpo)
            sleep(7)
            if patient == victim:
                await ctx.channel.send(chosenRevival)
            else:
                players = {role:player for role, player in players.items() if player != victim}
                await ctx.channel.send(chosenDeath)
            sleep(7)
##################################################################################################################################
        await ctx.channel.send("Get ready to vote gang!")
        sleep(3)
        voteLetters = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]
        voteCount = {}
        for num in range(len(players.values())):
            voteCount[voteLetters[num]] = 0
            await ctx.channel.send(voteLetters[num] + ": <@" + str(players.values()[num]) + ">")
        await ctx.channel.send("React to this message with the number of the person you suspect of being the mafia...")
        msgs = await ctx.channel.history(limit = 200).flatten()
        msgs = [msg for msg in msgs if msg.author.id == 1117512903315169320]
        msg = [message for message in msgs if message.content == "React to this message with the number of the person you suspect of being the mafia..."]
        votes = msg[0].reactions
        while len(votes) < len(players):
            msgs = await ctx.channel.history(limit = 200).flatten()
            msgs = [msg for msg in msgs if msg.author.id == 1117512903315169320]
            msg = [message for message in msgs if message.content == "React to this message with the number of the person you suspect of being the mafia..."]
            votes = msg[0].reactions
        for vote in votes:
            if demojize(vote) in voteCount:
                voteCount[demojize(vote)] += 1
        if voteCount.values().count(voteCount.values()[0]) == len(voteCount.values()):
            await ctx.channel.send("Vote tied evenly... Nobody was eliminated.")
            sleep(2)
        else:
            for vote in voteCount.values():
                tiebreakers = []
                if voteCount.values().count(vote) > 1:
                    tiebreakers.append(vote)
            if len(tiebreakers) > 0:    
                subPlayers = [players[x] for x in range(len(players.values())) if voteCount.values()[x] == max(tiebreakers)]
                await ctx.channel.send("Tiebreaker vote!")
                sleep(2)
                voteCount = {}
                for num in range(len(players.values())):
                    voteCount[voteLetters[num]] = 0
                    await ctx.channel.send(voteLetters[num] + ": <@" + str(subPlayers.values()[num]) + ">")
                await ctx.channel.send("React to this message with the number of the person you suspect of being the mafia...")
                msgs = await ctx.channel.history(limit = 200).flatten()
                msgs = [msg for msg in msgs if msg.author.id == 1117512903315169320]
                msg = [message for message in msgs if message.content == "React to this message with the number of the person you suspect of being the mafia..."]
                votes = msg[0].reactions
                while len(votes) < len(subPlayers):
                    msgs = await ctx.channel.history(limit = 200).flatten()
                    msgs = [msg for msg in msgs if msg.author.id == 1117512903315169320]
                    msg = [message for message in msgs if message.content == "React to this message with the number of the person you suspect of being the mafia..."]
                    votes = msg[0].reactions
                for vote in votes:
                    if demojize(vote) in voteCount:
                        voteCount[demojize(vote)] += 1
                if votes.count(votes[0]) == len(votes):
                    await ctx.channel.send("Vote tied evenly... Nobody was eliminated.")
                else:
                    players = {role:player for role, player in players if player != subPlayers[voteCount.values().index(max(voteCount.values()))]}
                    await ctx.channel.send(str(subPlayers[voteCount.values().index(max(voteCount.values()))]) + " was eliminated")
            else:
                players = {role:player for role, player in players if player != players[voteCount.values().index(max(voteCount.values()))]}
                await ctx.channel.send(str(players[voteCount.values().index(max(voteCount.values()))]) + " was eliminated")
#####################################################################################################################################################################################
        if "mafia" not in players:
            await ctx.channel.send("Mafia eliminated! The town has became victorious!")
            return
    await ctx.channel.send("Game over. The mafia was <@" + str(players["mafia"]) + ">")

@bot.command()
async def leave(ctx):
    with open("users.txt", "w+") as usersFile:
        users = usersFile.read().split("\n")
        for x in range(users):
            group = users[x].split(",")
            if str(ctx.author.id) in group:
                group.remove(str(ctx.author.id))
                users[x] = ",".join(group)
                usersFile.write("\n".join(users))
                await ctx.channel.send("<@" + str(ctx.author.id) + "> you successfully left <@" + str(group[x]) + "'s session.")
                return
    await ctx.channel.send("<@" + str(ctx.author.id) + "> you are not in a session.")

        

@bot.command()
async def shutdown(ctx):
bot.run(config.botToken)
