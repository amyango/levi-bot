import discord
import os
import random

client = discord.Client()

fortunes = ["You will injure your most precious body part in the near future", 
        "Your fifth great grandchild will be really good at ping pong",
        "You will grow an eye inside your mind that can predict the next taco bell special",
        "Tomorrow you will wake up",
        "3564543999 seconds from now you will blink",
        "You will meet someone with a curtain fetish",
        "There is a pastrami sandwich in your future",
        "Your next thought will be about how delicious potatoes are",
        "Tomorrow you will do the thing you've been meaning to do",
        "5 years from today, you will unknowingly cross paths with a clown wrangler",
        "You will be betrayed by your own insecurities",
        "The next chicken you encouner will possess the soul of a lasagna",
        "If you ever have to pick between your first and second child, clip your 3rd toenail for guidance"]

greetings = ["Yo",
        "Lol nerd",
        "Uhhh who are you",
        "Aloha",
        "Commencing ban",
        "hi"
        ]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send(greetings[random.randint(0,len(greetings)-1)])

    if message.content.startswith('$fortune'):
        await message.channel.send(fortunes[random.randint(0,len(fortunes)-1)])

client.run('ODE1NDU3NTA5NzU0MDExNjY5.GTiJrW.MZLl2eRDos2eik3pcAbtPf2o6hR33-zWrzDzSs')

