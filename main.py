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
    add_points(reaction.message.author.id, -1)

###############################################################################
# $hello
###############################################################################
async def do_greeting(message):
    if message.author.id == jenid:
        await message.channel.send("Hello Mistress")
    else:
        await message.channel.send(greetings[random.randint(0,len(greetings)-1)])

###############################################################################
# $infraction
###############################################################################
async def do_infraction(message):

    # Only Jen can use this function
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

###############################################################################
# $roll
###############################################################################
async def do_pokeroll(message):

    # Messages
    greedybitch='You already have 6 pokemon you greedy bitch\n'
    greedybitch+='hint: $tothefarm <pokemon> to release'
    poorbitch='You have insufficient points (10 per roll): '

    team = get_poketeam(message.author.id)

    # Get a free pokemon if team is empty
    if len(team) == 0:
        newpokeid = random.randint(1, 898)
    elif len(team) >= 6:
        await message.channel.send(greedybitch)
        return
    else:
        pts = get_points(message.author.id)
        if pts < 10:
            await message.channel.send(poorbitch + str(pts))
            return
        add_points(message.author.id, -10)
        newpokeid = random.randint(1, 898)

    await message.channel.send(':game_die: R O L L I N G :game_die:')

    newpoke = newpokemon(newpokeid)
    team.append(newpoke)
    set_poketeam(message.author.id, team)

    log(message.author.name + ' new pokemon ' + newpoke['name'])

    await message.channel.send('Welcome ' + newpoke['name'] + ' to your team!')
    await message.channel.send(newpoke['basepic'])

###############################################################################
# Create new pokemon
###############################################################################
def newpokemon(pid):
    newpokemon = {}
    newpokemon['id'] = pid
    newpokemon['name'] = pb.pokemon(pid).name
    newpokemon['basepic'] = pb.SpriteResource('pokemon', pid).url
    return newpokemon

###############################################################################
# $roll
###############################################################################
async def do_poketeam(message):
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

###############################################################################
# $tothefarm <pokemon/allthembitches>
###############################################################################
async def do_murder(message):

    murderusage='Usage: $tothefarm <pokemon name/allthembitches>'

    words = message.content.split(" ")

    # Argument checking
    if len(words) < 2:
        await message.channel.send(murderusage)
        return

    # Look for the pokemon send to the farm
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
        if team[i]['name'] == lower(words[1]):
            nberries = random.randint(1, 10)
            await message.channel.send('Goodbye ' + team[i]['name'] + '!')
            await message.channel.send(team[i]['basepic'])
            await message.channel.send('The farm sent you back ' + str(nberries) + ' ~~soylent chunks~~ berries')
            del team[i]
            add_berries(message.author.id, nberries)
            set_poketeam(message.author.id, team)
            return

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
        await do_greeting(message)
        return

    ###########################################################################
    # Fortune command
    ###########################################################################
    if message.content.startswith('$fortune'):
        await message.channel.send(fortunes[random.randint(0,len(fortunes)-1)])
        return

    ###########################################################################
    # Infraction command
    ###########################################################################
    if message.content.startswith('$infraction'):
        await do_infraction(message)
        return

    ###########################################################################
    # Points command
    ###########################################################################
    if message.content.startswith('$points'):
        msg="" + message.author.name + " points: " + str(get_points(message.author.id))
        await message.channel.send(msg)
        return

    ###########################################################################
    # Gatcha
    ###########################################################################
    if message.content.startswith('$roll'):
        await do_pokeroll(message)
        return

    if message.content.startswith('$team'):
        await do_poketeam(message)
        return

    if message.content.startswith('$tothefarm'):
        await do_murder(message)
        return

    if message.content.startswith('$berry'):
        msg = message.author.name + " berries: " 
        msg += str(get_berries(message.author.id))
        await message.channel.send(msg)

    if message.content.startswith('$slots'):
        await do_slots(message)
        return

async def do_slots(message):

    words = message.content.split(" ")
    poorbitch='You have insufficient points (1 per spin): '
    await message.channel.send(':game_die: S L O T S :game_die:')

    nspins = 1

    # If they provided a number that's the number of spins
    # Max 10 spins at a time
    try:
        nspins = int(words[1]) 
        if nspins > 10:
            nspins = 10 
        await message.channel.send('Spinning ' + str(nspins) + ' times')
    except:
        nspins = 1
        await message.channel.send('NOT A NUMBER ')


    while nspins > 0:
        nspins -= 1
        pts = get_points(message.author.id)
        if pts < 1:
            await message.channel.send(poorbitch + str(pts))
            return
        await pull_slot(message)

async def pull_slot(message):

    pts = -1
    ncols = 3
    string = ''
    result = [None] * ncols
    icons = [':fire:', ':leaves:', ':ocean:', ':cherries:', ':coin:']

    for i in range(0, ncols):
        result[i] = random.randint(0, len(icons)-1)
        string = string + icons[result[i]]
    await message.channel.send(string)

    max_icon = 0
    max_matches = 1
    matches = 0

    # Check for matches
    for i in range(0, len(icons)):
        matches = 0
        for j in result:
            if j == i:
                matches += 1
        if matches > max_matches:
            max_icon = i
            max_matches = matches

    string=''

    if max_matches == ncols:
        pts = (max_icon + 1) * 10
        string = string + '\n    J A C K P O T    \n***' + str(pts) + '***'
    elif max_matches > 1:
        pts = ((max_icon + 1) // 2) + 1
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
