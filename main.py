import discord
import os
import sys
import random
import time
import json
from datetime import datetime
from json.decoder import JSONDecodeError
import pokebase as pb

# Function to print log messages
def log(msg):
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + msg, flush=True)

# Safe open json file
def openjson(filename):
    try:
        result = json.load(open(filename, 'r'))
    except JSONDecodeError:
        result = {}
    return result

###############################################################################
# IDs
###############################################################################
# Found by toggling developer mode on discord
# They are recommended when identifying a user, since people
# can change their usernames/nicknames
amaid=206298476802342912
jenid=250073550478639104

###############################################################################
# Discord Initialization
###############################################################################
# Setting intents will pre-load some discord information
# The members and reaction initializations are added so that the reaction
# listeners will work.
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
client = discord.Client(intents=intents)

usage='Commands: $hello $fortune $infraction $roll $tothefarm $slots $points'

###############################################################################
# Opening Files
###############################################################################
projectdir = '/home/pi/git/levi-bot/'
datadir = projectdir + 'data/'

fortunefile = projectdir + "fortunes.txt"
greetingfile = projectdir + "greetings.txt"

infractfile = datadir + "infractions.json"
pokefile = datadir + "pokemon.json"
berryfile = datadir + "berries.json"
poketeamsfile = datadir + "poketeams.json"
pointsfile = datadir + "points.json"

fortunes = open(fortunefile, "r").readlines()
greetings = open(greetingfile, "r").readlines()
infractions = openjson(infractfile)
pokemon = openjson(pokefile)
poketeams = openjson(poketeamsfile)
points = openjson(pointsfile)
berries = openjson(berryfile)

###############################################################################
# Pokemon
###############################################################################

###############################################################################
# main
###############################################################################
@client.event
async def on_ready():
    log('We have logged in as {0.user}'.format(client))

@client.event
async def on_reaction_add(reaction, user):
    log('reaction on message by ' + reaction.message.author.name)

    # Levi doesn't care about points
    if reaction.message.author == client.user:
        return

    # Don't let people give themselves points
    # Cuz that's sad
    if reaction.message.author == user:
        return

    add_points(reaction.message.author.id, 1)

@client.event
async def on_reaction_remove(reaction, user):
    log('reaction removed on message by ' + reaction.message.author.name)
    add_points(reaction.message.author.id, -1)

async def do_greeting(message):
    if message.author.id == jenid:
        await message.channel.send("Hello Mistress")
    else:
        await message.channel.send(greetings[random.randint(0,len(greetings)-1)])

@client.event
async def on_message(message):
# Levi doesn't want to talk to himself # That's lame
    if message.author == client.user:
        return

    ###########################################################################
    # Help command
    ###########################################################################
    if message.content.startswith('$help'):
        await message.channel.send(usage)
        return

    ###########################################################################
    # Greeting command
    ###########################################################################
    if message.content.startswith('$hello'):
        do_greeting(message)
        return

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

        taggedUser = message.mentions[0]

        if str(taggedUser.id) in infractions:
            infractions[str(taggedUser.id)] += 1
        else:
            infractions[str(taggedUser.id)] = 1

        with open(infractfile, 'w') as outfile:
            json.dump(infractions, outfile)

        msg="" + taggedUser.name + " infractions: " + str(infractions[str(taggedUser.id)])
        await message.channel.send(msg)

    ###########################################################################
    # Points command
    ###########################################################################
    if message.content.startswith('$points'):

        if not str(message.author.id) in points:
            points[str(message.author.id)] = 0

        msg="" + message.author.name + " points: " + str(points[str(message.author.id)])
        await message.channel.send(msg)

    ###########################################################################
    # Gatcha
    ###########################################################################
    if message.content.startswith('$roll'):

        team = get_poketeam(message.author.id)

        if len(team) == 0:
            newpokeid = random.randint(1, 898)
        elif len(team) >= 6:
            await message.channel.send('You already have 6 pokemon you greedy bitch')
            await message.channel.send('hint: $tothefarm <pokemon> to release')
            return
        else:
            pts = get_points(message.author.id)
            if pts < 10:
                await message.channel.send('You have insufficient points (10 per roll): ' + str(pts))
                return
            add_points(message.author.id, -10)
            newpokeid = random.randint(1, 898)

        await message.channel.send(':game_die: R O L L I N G :game_die:')

        newpoke = {}
        newpoke['id'] = newpokeid
        newpoke['name'] = pb.pokemon(newpokeid).name
        newpoke['basepic'] = pb.SpriteResource('pokemon', newpokeid).url
        team.append(newpoke)
        set_poketeam(message.author.id, team)

        log(message.author.name + ' new pokemon ' + newpoke['name'])

        await message.channel.send('Welcome ' + newpoke['name'] + ' to your team!')
        await message.channel.send(newpoke['basepic'])

    if message.content.startswith('$team'):

        if len(message.mentions) > 0:
            user = message.mentions[0];
        else:
            user = message.author

        team = get_poketeam(user.id)

        i = 0
        secs = 0

        for pokemon in team:
            embed = poke_embed(pokemon)
            await message.channel.send(embed=embed)
        #await message.add_reaction('⬅')
        #await message.add_reaction('➡')

    if message.content.startswith('$tothefarm'):
        words = message.content.split(" ")
        if len(words) > 1:
            # look for the pokemon send to the farm
            team = get_poketeam(message.author.id)

            if words[1] == "allthembitches":
                await message.channel.send('Goodbye bitches!')
                nberries = 0
                for i in range(len(team)):
                    nberries += random.randint(1, 10)
                    await message.channel.send(team[i]['basepic'])
                team = []
                set_poketeam(message.author.id, team)
                return

            for i in range(len(team)):
                if team[i]['name'] == words[1]:
                    nberries = random.randint(1, 10)
                    await message.channel.send('Goodbye ' + team[i]['name'] + '!')
                    await message.channel.send('The farm sent you back ' + str(nberries) + ' ~~soylent chunks~~ berries')
                    del team[i]
                    add_berries(message.author.id, nberries)
                    set_poketeam(message.author.id, team)
                    return
        await message.channel.send('Usage: $tothefarm <pokemon name/allthembitches>') 

    if message.content.startswith('$berry'):
        nberries = get_berries(message.author.id)
        msg="" + message.author.name + " berries: " + str(nberries)
        await message.channel.send(msg)

    if message.content.startswith('$slots'):

        pts = get_points(message.author.id)

        if pts < 1:
            await message.channel.send('You have insufficient points (1 per spin): ' + str(pts))
            return

        await message.channel.send(':game_die: S L O T S :game_die:')


def pull_slot(message):
    icons = [':fire:', ':leaves:', ':ocean:', ':cherries:', ':coin:']
    ncols = 3
    result = [None] * ncols
    pts = -1

    string = ''

    for i in range(0, ncols):
        result[i] = random.randint(0, len(icons)-1)
        string = string + icons[result[i]]
    await message.channel.send(string)

    max_icon = 0
    max_matches = 1

    for i in range(0, len(icons)):
        if result[i] == i:

    string = ''
    if (result[0] == result[1]) and (result[0] == result[2]):
        pts = (result[0] + 1) * 10
        string = string + '\n    J A C K P O T    \n***' + str(pts) + '***'
    elif result[0] == result[1] or result[0] == result[2]: 
        pts = ((result[0] + 1) // 2) + 1
        string = string + '\nSmall Winner!\n***' + str(pts) + '***'
    elif result[1] == result[2]:
        pts = ((result[1] + 1) // 2) + 1
        string = string + '\nSmall Winner!\n***' + str(pts) + '***'
    else:
        string = string + '\n***' + 'Try again' + '***' + ' :grimacing:'

    await message.channel.send(string)
    add_points(message.author.id, pts)

    

def poke_embed(pokemon):
    embed = discord.Embed(title=pokemon['name'].capitalize())
    embed.set_thumbnail(url=pokemon['basepic'])
    if not 'lvl' in pokemon:
        pokemon['lvl'] = 1
    embed.add_field(name='Level', value=pokemon['lvl'], inline=True)
    return embed


def get_berries(uid):
    if not str(uid) in berries:
        berries[str(uid)] = 0
    return berries[str(uid)]

def add_berries(uid, pts):
    if not str(uid) in berries:
        berries[str(uid)] = 0
    else:
        berries[str(uid)] += pts

    with open(berryfile, 'w') as outfile:
        json.dump(berries, outfile)

def get_points(uid):
    if not str(uid) in points:
        points[str(uid)] = 0
    return points[str(uid)]

def add_points(uid, pts):
    if not str(uid) in points:
        points[str(uid)] = 0
    else:
        points[str(uid)] += pts

    with open(pointsfile, 'w') as outfile:
        json.dump(points, outfile)

    return points[str(uid)]

#def set_pokemon(uid, team):
#    pokemon[str(uid)] = team
#    with open(pokefile, 'w') as outfile:
#        json.dump(pokemon, outfile)
    
#def get_pokemon(uid):
#    if not str(uid) in pokemon:
#        pokemon[str(uid)] = []
#    return pokemon[str(uid)]

def get_poketeam(uid):
    if not str(uid) in poketeams:
        poketeams[str(uid)] = []
    return poketeams[str(uid)]

def set_poketeam(uid, team):
    poketeams[str(uid)] = team
    with open(poketeamsfile, 'w') as outfile:
        json.dump(poketeams, outfile)
 
token=open("/home/pi/git/levi-bot/token.txt").readline().rstrip()
client.run(token)
