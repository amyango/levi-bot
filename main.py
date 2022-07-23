import discord
import os
import random

###############################################################################
# IDs
###############################################################################
# Found by toggling developer mode on your raspberry pi
# They are recommended when identifying a user, since people
# can change their usernames/nicknames
amaid=206298476802342912
jenid=250073550478639104

client = discord.Client()

###############################################################################
# Create a list of quotes from fortunes.txt
###############################################################################
fortunes = open("/home/pi/git/levi-bot/fortunes.txt", "r").readlines()

###############################################################################
# List of greetings
###############################################################################
greetings = ["Lol nerd",
        "Who are you",
        "Aloha",
        "Commencing ban",
        "hi"
        ]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    # Ignore the message if we're the one that sent it
    if message.author == client.user:
        return

    ###########################################################################
    # Greeting command
    ###########################################################################
    if message.content.startswith('$hello'):
        if message.author.id == jenid:
            await message.channel.send("Hello Mistress")
        else:
            await message.channel.send(greetings[random.randint(0,len(greetings)-1)])

    ###########################################################################
    # Fortune command
    ###########################################################################
    if message.content.startswith('$fortune'):
        await message.channel.send(fortunes[random.randint(0,len(fortunes)-1)])

    ###########################################################################
    # Infraction command
    ###########################################################################
    if message.content.startswith('$infraction'):
        if message.author.id != jenid:
            await message.channel.send("I don't take orders from you.")
            return
        taggedUser = message.mentions[0];
        await message.channel.send('infracting ' + taggedUser.name)
        
token=open("/home/pi/git/levi-bot/token.txt").readline().rstrip()
client.run(token)
