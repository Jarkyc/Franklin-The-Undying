import keepalive
keepalive.keep_alive()
import asyncio
import os
import discord
from discord.ext import commands, tasks
from gtts import gTTS
import nacl
import datetime
import roleutils
from dotenv import load_dotenv
load_dotenv
token = os.getenv('token')

intents = discord.Intents.default()
intents.members = True
Bot = commands.Bot(intents=intents, command_prefix="~")
guild = 468278941652746241
last_remind = None

Bot.load_extension('purgecog')
Bot.load_extension('errorhandler')
Bot.load_extension('recomcog')
Bot.load_extension('recordcog')

def main():
  pass

if __name__ == "__main__":
  main()  

@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Everything"))
    purgecog = Bot.get_cog("PurgeCog")

    try:
        file = open("purgemsg.txt", "r")
        lines = file.readlines()

        global last_remind
        msg = lines[0].replace('\n', '')
        enddate = lines[1].replace('\n', '')
        last_remind = lines[2].replace('\n', '')
        print(last_remind)
        if msg != "":
            purgecog.set_message(msg)
            purgecog.set_date(enddate)
            purge_loop.start()
        else:
            print("Purge not happening. Continuing...")
        file.close()
    except FileNotFoundError:
        print("Purge not happening. Continuing...")


@tasks.loop(seconds=5.0)
async def purge_loop():
  date = datetime.datetime.now().strftime('%m/%d/%Y')
  purgecog = Bot.get_cog("PurgeCog")
  global guild
  global last_remind
  if last_remind == (datetime.datetime.now() + (datetime.timedelta(days=-1))).strftime("%m/%d/%Y"):
    print(last_remind)
    print((datetime.datetime.now() + (datetime.timedelta(days=-1))).strftime("%m/%d/%Y"))
    with open("purgemsg.txt", "r+") as file:
      lines = file.readlines()
      lines[2] = date
      file.seek(0)
      file.writelines(lines)
    last_remind = date
    channel = Bot.get_channel(500123421716381725)
    message = await channel.fetch_message(purgecog.get_msg())
    await Bot.get_channel(500123421716381725).send("<@&915334666029006898> daily reminder to react with :white_check_mark: on the following message to prevent removal from regiment: " + message.jump_url)

  if date == purgecog.get_date():

    await purgecog.start_purge()


@Bot.command()
async def recruit(ctx, member: discord.Member = None):
  if not roleutils.is_officer(ctx.author):
    await ctx.send("You do not have permissions for this command")
    return

  if member == None:
    await ctx.send("Please enter a member to set to recruit")
    return

  if roleutils.has_role(member, "[141CR]"):
    await ctx.send("This person is already in 141!")
    return

  roles = ["Recruit", "Collie", "Community", "[141CR]"]

  global guild
  for role in roles:
    role = discord.utils.get(Bot.get_guild(guild).roles, name=role)
    await member.add_roles(role)
  unver = discord.utils.get(Bot.get_guild(guild).roles, name="Unverified")
  await member.remove_roles(unver)
  await ctx.send(ctx.author.mention + " you have added " + member.mention + " to recruit status")
  name = "[RCT] " + member.display_name
  await member.edit(nick=name)


@Bot.command()
async def validate(ctx):
  if not roleutils.is_officer(ctx.author): return
  purgecog = Bot.get_cog("PurgeCog")
  global guild
  channel = Bot.get_channel(500123421716381725)
  message = await channel.fetch_message(purgecog.get_msg())
  await ctx.send("Users who reacted but still are in purge:")
  for reaction in message.reactions:
    async for user in reaction.users():
      if roleutils.has_role(user, "Purge"):
        await ctx.send(user.mention)


@Bot.command()
async def importantactive(ctx):
  if not roleutils.is_officer(ctx.author): return
  global guild
  await ctx.send("The following members are NCOs+ who have not verrified activity:")
  for member in Bot.get_guild(guild).members:

    if (roleutils.has_role(member, "Purge") and roleutils.has_role(member, "Officer")) or (roleutils.has_role(member, "Purge") and roleutils.has_role(member, "Senior Officer")) or (roleutils.has_role(member, "Purge") and roleutils.has_role(member, "NCO")):
      await ctx.send(member.mention)


@Bot.command()
async def connect(ctx):
  voice_channel = ctx.author.voice.channel
  global guild
  voice = ctx.voice_client
  if voice == None:
    await voice_channel.connect()
  else:
    await ctx.send("I am already connected to a voice channel")

@Bot.command()
async def say(ctx, * args):
  if not roleutils.is_officer(ctx.author):
    await ctx.send("You do no have permission for this")
    return
  vc = ctx.voice_client
  end = " ".join(args)
  message = ctx.author.name + " says " + end
  language = 'en'
  myObj = gTTS(text=message, lang=language, slow=False)
  myObj.save("voice.mp3")
  vc.play(discord.FFmpegPCMAudio("voice.mp3"))

@Bot.command()
async def klausrap(ctx, * args):
  if ctx.author.id != 160882467090333696: 
    await ctx.send("You do not have permission for this")
    return
  vc = ctx.voice_client
  vc.play(discord.FFmpegPCMAudio("vonklaus.mp3"))

  while vc.is_playing:
    await asyncio.sleep(.1)

@Bot.command()
async def react(ctx, * args):
  if roleutils.is_officer(ctx.author):
    roleid = int(args[0])
    msg = ' '.join(args)
    message = msg.split(' ', 1)[1]
    role = discord.utils.get(Bot.get_guild(guild).roles, id=roleid)
    await ctx.message.delete()
    sent = await ctx.send(message)
    with open("reactmessages.txt", "r+") as file:
      file.seek(0,2)
      file.write(str(sent.id) + ":" + str(role.id) + "\n")

@Bot.event
async def on_raw_reaction_add(payload):
  with open("reactmessages.txt", "r+") as file:
    lines = file.readlines()
    for line in lines:
      line.replace("\n", "")
      storedids = line.split(":")
      storedmessage = storedids[0]
      if storedmessage == str(payload.message_id):
        roleid = int(storedids[1])
        role = discord.utils.get(Bot.get_guild(guild).roles, id=roleid)
        await payload.member.add_roles(role)

@Bot.event
async def on_raw_reaction_remove(payload):
  with open("reactmessages.txt", "r+") as file:
    lines = file.readlines()
    for line in lines:
      line.replace("\n", "")
      storedids = line.split(":")
      storedmessage = storedids[0]
      if storedmessage == str(payload.message_id):
        roleid = int(storedids[1])
        role = discord.utils.get(Bot.get_guild(guild).roles, id=roleid)
        member = Bot.get_guild(guild).get_member(payload.user_id)
        await member.remove_roles(role)
         
@Bot.event
async def on_message(message):
  if message.guild is None and not message.author.bot:
    print(message.author.name+ ": " + message.content)
  await Bot.process_commands(message)

@Bot.command()
async def sudo(ctx, * args):
  if roleutils.is_officer(ctx.author):
    await ctx.message.delete()
    await ctx.send(' '.join(args))

@Bot.command()
async def leave(ctx):
  await ctx.voice_client.disconnect()



Bot.run(token)
