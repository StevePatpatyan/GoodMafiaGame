import rsa
from distutils.command.check import check
import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
import os
import config



bot = commands.Bot(command_prefix='^')
publicKey, privateKey = rsa.newkeys(512)
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
    else:
        password = str(rsa.encrypt(password.encode(),publicKey))
    users = open("users.txt","a+")
    users.write(user+",\n")
    passwords = open("passwords.txt","a+")
    passwords.write(password+"\n")
    await ctx.author.send("Session successfully created. You and others in the session will be alerted when the lobby is full or when there are enough players to start.")
    await ctx.channel.send(ctx.author.mention+" has successfully started a mafia session! Type \"^join\" to join.")
@bot.command()
async def join(ctx):
    user = str(ctx.author.id)
    users = "".join(open("users.txt","r").read().split("\n")).split(",")
    if user in users:
        await ctx.author.send("You are already in an active session, so you cannot join another.")
        return
    await ctx.author.send("")
    
bot.run(config.botToken)
