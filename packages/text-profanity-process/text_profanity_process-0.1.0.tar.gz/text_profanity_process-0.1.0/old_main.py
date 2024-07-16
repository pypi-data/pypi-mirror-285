from logging import exception
import os

import discord
import requests

#my_secret = os.getenv('TOKEN')
my_secret = "MTI1MDQyODUwMTAzMTM4NzE0Ng.GsNzup.0nagmF3T_RnpErfJsAoED0V4zvrwwMYhiBw_34"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
client = discord.Client(intents=intents)


def call_api(message):
  url = "https://hmphuoc-toxic.hf.space/checkplus"
  try:
    response = requests.post(url, json={"comment": message.content})
    if response.status_code == 200:
      data = response.json()
      if(data[0]>=0.7):
        return ["Lời lẽ có tính độc hại cao","😡"]
      if(data[0]>=0.5):
        return ["Lời lẽ có tính độc hại","😱"]
      if(data[0]>=0.4):
        return ["Cẩn thận lời nói","😒"]
  except(exception):
    print(exception)
    return ["Xảy ra lỗi trong quá trình xử lý","🤒"]

@client.event
async def on_ready():
  print("The bot {0.user} is ready!".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith("!hello"):
    await message.channel.send("Hello!")

  if message.content.startswith("!intro"):
    await message.channel.send("I'm Comment Dection Bot, I'm here to help you with your comments!")

  if message.content.startswith("!help"):
    await message.channel.send("!hello: Greeting\n!intro: Introduction\n!help: You alreay know what it is")

  else:
    result = call_api(message)
    if(result):
      await message.reply(result[0])
      await message.add_reaction(result[1])