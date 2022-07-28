import discord
import os
import random
import json
from json.decoder import JSONDecodeError

###############################################################################
# IDs
###############################################################################
# Found by toggling developer mode on discord
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

###############################################################################
# infractions list
###############################################################################
projectdir = "/home/pi/git/levi-bot/"
infractfile = projectdir + "infractions.json"
infractions = {}
try: # Add try-catch in case the infractions.json file is empty
    infractions = json.load(open(infractfile, 'r'))
except JSONDecodeError:
    pass

###############################################################################
# bingo command
###############################################################################

# Readonly variables
x = ':x:'
o = ':green_circle:'
usage = 'Usage: $bingo <board/respin/list/stamp #>'

# Global variables
bingo = {}
bingo_stat = {}
bingo_items = open(projectdir + "bingo.txt").readlines()

# Initialize Stamps
for item in bingo_items:
    bingo_stat[item] = x

# Function that prints the list of stamps
async def bingo_list(message):
    bingo_prt = ''
    for item in bingo_items:
        bingo_prt = bingo_prt + bingo_stat[item] + item
    await message.channel.send(bingo_prt)

# Main function for the $bingo command
async def dobingo(message):
    global bingo_stat
    words = message.content.split(" ")
    subcmd = ""

    if len(words) > 1:
        subcmd = words[1]

    if subcmd == "board":
        await bingo_init(message, False)
    elif subcmd == "respin":
        await bingo_init(message, True)
    elif subcmd == "list":
        await bingo_list(message)
    elif subcmd == "stamp":
        await bingo_stamp(message, words)
    elif subcmd == "clear":
        await bingo_clear(message)
    else:
        await message.channel.send(usage)

# Stamp an item off the list
async def bingo_stamp(message, words):
    if len(words) >= 3:

        try:
            idx = int(words[2]) - 1
        except ValueError:
            await message.channel.send("NOT A NUMBER.\n" + usage)
            return

        if idx > 23 or idx < 1:
            await message.channel.send("Number out of range.\n" + usage)
            return

        bingo_stat[bingo_items[idx]] = o
        await message.channel.send(bingo_stat[bingo_items[idx]] + bingo_items[idx])
    else:
        await message.channel.send("NO NUMBER PROVIDED\n" + usage)

# Clear the list of stamps
async def bingo_clear(message):
        if message.author.id != jenid and message.author.id != amaid:
            await message.channel.send("I don't take orders from you.")
            return
        for item in bingo_items:
            bingo_stat[item] = x
        await message.channel.send("Stamps have been cleaned.")

# Create a board or show a board
async def bingo_init(message, new):
    if new or not message.author.id in bingo:
        await message.channel.send("Generating board for " + message.author.name)
        # Fill out the bingo board with 1-24 randomly
        numbers = []
        for i in range(1, 25):
            numbers.append(i)
        random.shuffle(numbers)
        numbers.insert(12, 0)

        print(numbers)

        bingo[message.author.id] = numbers

    await bingo_board_print(message)

# Print the user's board
# Each 'space' is a 2x2 grid of emojis:
#   :one: :four:   for     1 4
#   :x:   :x:              x x
async def bingo_board_print(message):
    output = ''

    numbers = [':zero:', ':one:', ':two:', ':three:', ':four:',
               ':five:', ':six:', ':seven:', ':eight:', ':nine:']

    statstring = ''
    count = 0
    for space in bingo[message.author.id]:
        if space == 0:
            stat = o
        else:
            stat = bingo_stat[bingo_items[space-1]]

        output = output + numbers[space // 10] + numbers[space % 10] + ' '
        statstring = statstring + stat + stat + ' '
        if (count + 1) % 5 == 0:
            output = output + '\n'
            output = output + statstring + '\n'
            statstring = ''
        count += 1

    await message.channel.send(output)

###############################################################################
# main
###############################################################################
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

        if str(taggedUser.id) in infractions:
            infractions[str(taggedUser.id)] += 1
        else:
            infractions[str(taggedUser.id)] = 1

        with open(infractfile, 'w') as outfile:
            json.dump(infractions, outfile)

        msg="" + taggedUser.name + " infractions: " + str(infractions[str(taggedUser.id)])
        await message.channel.send(msg)

    ###########################################################################
    # Bingo
    ###########################################################################
    if message.content.startswith('$bingo'):
        await dobingo(message)
        
token=open("/home/pi/git/levi-bot/token.txt").readline().rstrip()
client.run(token)
