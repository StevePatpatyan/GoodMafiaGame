import rsa
from distutils.command.check import check
import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
import os
import config



bot = commands.Bot(command_prefix='^')
@bot.event
async def on_ready():
    print("ready")
@bot.command()
async def create(ctx):
    print("h")
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
            print(usersPerSession[x])
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
    
bot.run(config.botToken)
