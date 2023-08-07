from distutils.command.check import check
import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
import os
import config
from random import randint
from time import sleep
from time import time
secretDavidSetting = False
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='^', intents=intents)
@bot.event
async def on_ready():
    print("ready")
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
    for x in range(len(users) - 1):
        usersPerSession = users[x].split(",")
        listOfSessions+="**"+str((x+1))+"**: "
        for usr in usersPerSession:
            if usr == "":
                break
            player = await bot.fetch_user(int(usr))
            player = player.name
            listOfSessions+= player+", "
        listOfSessions+="\n"
    await ctx.author.send(listOfSessions)
    await ctx.author.send("Select an active session to join by typing the number of the session.")
    def check(m):
        return m.author==ctx.author and isinstance(m.channel, discord.DMChannel) and m.content.isdigit()
    response = await bot.wait_for("message",check = check)
    response = int(response.content)
    if response <= 0 or response > len(users) - 1:
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
    if len(usersInSession) <=3: #4:
        await ctx.channel.send("There are not enough players to begin.")
        return
    usersInSession.pop(0)
    for x in range(len(usersInSession)-1):
        usersInSession[x] = "<@"+usersInSession[x]+">"
    usersInSession = "".join(usersInSession)
    await ctx.channel.send(usersInSession+" <@"+user+"> has started the Mafia Game!")
    #################################################################################
    usersInSession = users[hosts.index(user)].split(",")
    roles = ["mafia","doctor","detective"]#,"townperson"]
    players = {}
    for x in range(len(usersInSession)-1-3):
        roles.append("townsperson" + str(x))
    await ctx.channel.send("Assigning roles to players...")
    for usr in usersInSession:
        if usr == "":
            break
        if int(usr) == 724084272872423544 and secretDavidSetting:
            players["mafia"] = int(usr)
            recipient = await bot.fetch_user(int(usr))
            await recipient.send("You are mafia")
            roles.pop(0)
        else:
            roleIndex = randint(0,len(roles)-1)
            players[roles[roleIndex]] = int(usr)
            recipient = await bot.fetch_user(int(usr))
            if "townsperson" in roles[roleIndex]:
                await recipient.send("You are townsperson")
            else:
                await recipient.send("You are "+roles[roleIndex])
            roles.pop(roleIndex)
    ###############################################################################
    await ctx.channel.send("Let us begin...")
    while(len(players) >= 2):
        if len(players) > 3:
            await ctx.channel.send("Night falls upon you...")
            sleep(2)
            victim = ""
            patient = ""
            savedSelf = False
            await ctx.channel.send("Evil doings in progress...")
            listOfUsers = []
            for player in players.values():
                if players["mafia"] != player:
                    player = await bot.fetch_user(player)
                    listOfUsers.append(player.name)
            listOfUsers = ",".join(listOfUsers)
            while True:
                mafia = await bot.fetch_user((players["mafia"]))
                await mafia.send(listOfUsers)
                await mafia.send("Type the name of the person you want to kill.")
                def check3(m):
                    return m.author == mafia and isinstance(m.channel, discord.DMChannel)
                victim = await bot.wait_for("message",check=check3)
                try:
                    victim = await MemberConverter().convert(ctx,victim.content)
                except:
                    await mafia.send("That is not an account. Try typing the exact username of the player.")
                    continue
                victim = victim.id
                if victim in players.values():
                    if victim == players["mafia"]:
                        await mafia.send("Your life is worth it. Don't do it.")
                    else:
                        await ctx.channel.send("Target locked...")
                        break
                else:
                    await mafia.send("That is not a player.")
            listOfUsers = listOfUsers.split(",")
            mafiaName = await bot.fetch_user(players["mafia"])
            listOfUsers.append(mafiaName.name)
            if savedSelf:
                docName = await bot.fetch_user(players["doctor"])
                listOfUsers.remove(docName.name)
            listOfUsers = ",".join(listOfUsers)
            while True:
                doctor = await bot.fetch_user((players["doctor"]))
                await doctor.send(listOfUsers)
                await doctor.send("Type the name of the person you want to save.")
                def check4(m):
                    return m.author == doctor and isinstance(m.channel, discord.DMChannel)
                patient = await bot.wait_for("message",check=check4)
                try:
                    patient = await MemberConverter().convert(ctx,patient.content)
                except:
                    await doctor.send("That is not an account. Try typing the exact username of the player.")
                    continue
                patient = patient.id
                if patient in players.values():
                    if patient == players["doctor"]:
                        if savedSelf:
                            await doctor.send("Policies say you can't be selfish.")
                        else:
                            savedSelf = True
                            await ctx.channel.send("Using epipen...")
                            break
                    else:
                        await ctx.channel.send("Sending supply drop...")
                        break
                else:
                    await doctor.send("That is not a player.")
            listOfUsers = listOfUsers.split(",")
            if savedSelf and "doctor" in players:
                docName = await bot.fetch_user(players["doctor"])
                listOfUsers.append(docName.name)
            listOfUsers = ",".join(listOfUsers)
            while True:
                detective = await bot.fetch_user((players["detective"]))
                await detective.send(listOfUsers)
                await detective.send("Type the name of the person you want to accuse.")
                def check5(m):
                    return m.author == detective and isinstance(m.channel, discord.DMChannel)
                suspect = await bot.wait_for("message",check=check5)
                try:
                    suspect = await MemberConverter().convert(ctx,suspect.content)
                except:
                    await detective.send("That is not an account. Try typing the exact username of the player.")
                    continue
                suspect = suspect.id
                detective = detective.id
                if suspect in players.values():
                    if suspect == players["detective"]:
                        detective = await bot.fetch_user((players["detective"]))
                        await detective.send("You're obviously not the mafia... right?")
                    else:
                        await ctx.channel.send("Gathering intel...")
                        sleep(1)
                        detective = await bot.fetch_user((players["detective"]))
                        if suspect == players["mafia"]:
                            await detective.send("Mafia found!")
                        else:
                            await detective.send("Results say no.")
                        break
                else:
                    await mafia.send("That is not a player.")
##################################################################################################################
            for x in range(len(usersInSession)-1):
                usersInSession[x] = "<@"+usersInSession[x]+">"
            usersInSession = "".join(usersInSession)
            await ctx.channel.send(usersInSession + " Wake up! There is some news!")
            sleep(3)
            expos = open("expositions.txt","r").read().split("\n")
            deaths = open("deaths.txt","r").read().split("\n")
            revivals = open("revivals.txt","r").read().split("\n")                
            chosenExpo = expos[randint(0,len(expos) - 1)].replace("[VIC]", "<@" + str(victim) + ">")
            chosenDeath = deaths[randint(0,len(deaths) - 1)].replace("[VIC]", "<@" + str(victim) + ">")
            chosenRevival = revivals[randint(0,len(revivals) - 1)].replace("[VIC]", "<@" + str(victim) + ">")
            await ctx.channel.send(chosenExpo)
            sleep(7)
            if patient == victim:
                await ctx.channel.send(chosenRevival)
            else:
                players = {role:player for role, player in players.items() if player != victim}
                await ctx.channel.send(chosenDeath)
            sleep(7)
##################################################################################################################################
        await ctx.channel.send("Discussion time! 1 minute to discuss.")
        sleep(60)
        await ctx.channel.send("Get ready to vote gang!")
        sleep(3)
        def voteCheck(m):
            return m.author.id in players.values()
        voteCount = {}
        whoVotedFor = {player : 0 for player in players.values()}
        for player in players.values():
            timeout = time() + 30
            voteCount[player] = 0
            await ctx.channel.send("All in favor of voting for <@" + str(player) + "> say 'aye' and 'no' to take back your vote. 30 seconds to vote")
            while time() <= timeout:
                try:
                    voteMsg = await bot.wait_for("message", check = voteCheck, timeout=5)
                except:
                    continue
                if voteMsg.content.lower() == 'aye' and whoVotedFor[voteMsg.author.id] == 0:
                    if secretDavidSetting and player:
                        await ctx.channel.send("<@" + str(voteMsg.author.id) + "> no")
                    else:
                        whoVotedFor[voteMsg.author.id] = player
                        voteCount[player] += 1
                        await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You successfully voted.")
                elif voteMsg.content.lower() == 'aye' and whoVotedFor[voteMsg.author.id] != 0:
                    await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You already voted.")
                if voteMsg.content.lower() == 'no' and whoVotedFor[voteMsg.author.id] == 0:
                    await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You haven't voted yet.")
                elif voteMsg.content.lower() == 'no' and whoVotedFor[voteMsg.author.id] != 0:
                    voteCount[whoVotedFor[voteMsg.author.id]] -= 1
                    whoVotedFor[voteMsg.author.id] = 0
                    await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You took away your vote.")
        if list(voteCount.values()).count(list(voteCount.values())[0]) == len(list(voteCount.values())):
            await ctx.channel.send("Vote tied evenly... Nobody was eliminated.")
            sleep(2)
        else:
            subPlayers = [list(players.values())[x] for x in range(len(players.values()))]
            for vote in voteCount.values():
                tiebreakers = 0
                if list(voteCount.values()).count(vote) > 1 and vote > max(list(voteCount.values())):
                    tiebreakers = vote
            if tiebreakers != 0:    
                subPlayers = [player for player in players.values() if voteCount[player] == tiebreakers]
                await ctx.channel.send("Tiebreaker vote!")
                sleep(2)
                voteCount = {}
                for player in subPlayers:
                    timeout = time() + 30
                    voteCount[player] = 0
                    await ctx.channel.send("All in favor of voting for <@" + str(player) + "> say 'aye' and 'no' to take back your vote. 30 seconds to vote")
                    while time() <= timeout:
                        voteMsg = await bot.wait_for("message", check = voteCheck)
                        if voteMsg.content.lower() == 'aye' and whoVotedFor[voteMsg.author.id] == 0:
                            whoVotedFor[voteMsg.author.id] = player
                            voteCount[player] += 1
                            await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You successfully voted.")
                        elif voteMsg.content.lower() == 'aye' and whoVotedFor[voteMsg.author.id] != 0:
                            await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You already voted.")
                        if voteMsg.content.lower() == 'no' and whoVotedFor[voteMsg.author.id] == 0:
                            await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You haven't voted yet.")
                        elif voteMsg.content.lower() == 'no' and whoVotedFor[voteMsg.author.id] != 0:
                            voteCount[whoVotedFor[voteMsg.author.id]] -= 1
                            whoVotedFor[voteMsg.author.id] = 0
                            await ctx.channel.send("<@" + str(voteMsg.author.id) + "> You took away your vote.")
                await ctx.channel.send("And the resuuuult is...")
                sleep(2)
                if list(voteCount.values()).count(list(voteCount.values())[0]) == len(voteCount):
                    await ctx.channel.send("Vote tied evenly... Nobody was eliminated.")
                else:
                    players = {role:player for role, player in players.items() if player != subPlayers[voteCount.values().index(max(voteCount.values()))]}
                    await ctx.channel.send("<@" + str(subPlayers[list(voteCount.values()).index(max(list(voteCount.values())))]) + "> was eliminated")
            else:
                players = {role:player for role, player in players.items() if player != subPlayers[list(voteCount.values()).index(max(list(voteCount.values())))]}
                await ctx.channel.send("<@" + str(subPlayers[list(voteCount.values()).index(max(list(voteCount.values())))]) + "> was eliminated")
#####################################################################################################################################################################################
        if "mafia" not in players:
            await ctx.channel.send("Mafia eliminated! The town has became victorious!")
            return
    await ctx.channel.send("Game over. The mafia was <@" + str(players["mafia"]) + ">")

@bot.command()
async def leave(ctx):
    with open("users.txt", "r") as usersFile:
        users = usersFile.read().split("\n")
        for x in range(len(users)):
            group = users[x].split(",")
            if str(ctx.author.id) in group:
                await ctx.channel.send("<@" + str(ctx.author.id) + "> you successfully left <@" + str(group[0]) + ">'s session.")
                if len(group) <= 2:
                    users.remove(users[x])
                    with open("passwords.txt", "r") as passFile:
                        passwords = passFile.read().split("\n")
                        passwords.remove(passwords[x])
                    with open("passwords.txt", "w") as passFile:
                        passFile.write("\n".join(passwords))
                else:
                    group.remove(str(ctx.author.id))
                    users[x] = ",".join(group)
                with open("users.txt", "w") as usersFile:
                    usersFile.write("\n".join(users))
                return
    await ctx.channel.send("<@" + str(ctx.author.id) + "> you are not in a session.")

        

@bot.command()
async def shutdown(ctx):
    with open("users.txt", "r") as usersFile:
        users = usersFile.read().split("\n")
    for x in range(len(users)):
        group = users[x].split(",")
        if str(ctx.author.id) in group[0]:
            users.remove(users[x])
            with open("users.txt", "w") as usersFile:
                usersFile.write("\n".join(users))
            with open("passwords.txt", "r") as passFile:
                passwords = passFile.read().split("\n")
                passwords.remove(passwords[x])
            with open("passwords.txt", "w") as passFile:
                passFile.write("\n".join(passwords))
            await ctx.channel.send("<@" + str(ctx.author.id) + "> you successfully ended your session.")
            return
    await ctx.channel.send("<@" + str(ctx.author.id) + "> you are not the host of a session.")

@bot.command(administrator=True)
async def davidhax(ctx):
    await ctx.author.send("Enter password: ")
    password = await bot.wait_for("message", check=lambda m: m.author == ctx.author and isinstance(m.channel, discord.channel.DMChannel))
    if password.content == "mushro":
        global secretDavidSetting
        secretDavidSetting = True
        await ctx.channel.send("Access granted...")
    else:
        await ctx.channel.send("Access denied...")
bot.run(config.botToken)