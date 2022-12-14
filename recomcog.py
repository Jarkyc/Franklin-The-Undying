import discord
from discord.ext import commands, tasks
import main
import datetime
import roleutils

channel = 823535219155927111
globalchan = 912531337901125642
readychan = 919290727660417024
readymsg = 925801984638984202

processors = {}

class RecomCog(commands.Cog):
  
  def __init__(self, client):
    self.client = client
  
  @tasks.loop(minutes=30)
  async def remind_loop(self):
    global channel
    global globalchan
    with open("recommendations.txt", "r+") as file:
      lines = file.readlines()
      if len(lines) != 0: 
        global channel
        for line in lines:
          if line == '\n': continue
          line = int(line.replace('\n', ""))
          if line == '': continue
          chan = self.client.get_channel(channel)
          print(line)
          message = await chan.fetch_message(line) 
          first = message.created_at + (datetime.timedelta(days = 1))
          second = datetime.datetime.now()
          if (second - first).total_seconds() >= 0:
            for reaction in message.reactions:
              emoji = self.client.get_emoji(835258590645715085)
              if reaction.emoji == emoji and reaction.count >= 4:
                modifymessage = await self.client.get_channel(readychan).fetch_message(readymsg)
                content = modifymessage.content 
                newcon = content + "\n" + "--" + message.jump_url  
                await modifymessage.edit(content=newcon)
                try:
                  lines.remove(str(line) + '\n')
                except ValueError:
                  lines.remove(str(line))
      file.seek(0)
      file.truncate(0)
      for line in lines:
        line.replace("\n", "")
        if line == ' ' or line == None: continue
        file.write(line)
    with open("preprocessed.txt", "r+") as file:
      lines = file.readlines()
      if len(lines) != 0: 
        for line in lines:
          line = int(line.replace('\n', ""))
          if line == '' or line == "\n": continue
          chan = self.client.get_channel(globalchan)
          print(line)
          message = await chan.fetch_message(line) 
          first = message.created_at + (datetime.timedelta(days = 1))
          second = datetime.datetime.now()
          if (second - first).total_seconds() >= 0:
            for reaction in message.reactions:
              emoji = self.client.get_emoji(835258590645715085)
              if reaction.emoji == emoji and reaction.count >= 4:
                embed = message.embeds[0]
                officerchannel = self.client.get_channel(channel)
                newmessage = await officerchannel.send(embed=embed)
                emoji = '✅'
                await message.add_reaction(emoji)
                with open("recommendations.txt", "r+") as ofile:
                  ofile.seek(0, 2)
                  ofile.write(str(newmessage.id) + '\n')
                try:
                  lines.remove(str(line) + '\n')
                except ValueError:
                  lines.remove(str(line))
      file.seek(0)
      file.truncate(0)
      for line in lines:
        line.replace("\n", "")
        if line == ' ' or line == None: continue
        file.write(line)
  
  @commands.command()
  async def recommend(self, ctx):
    processors[ctx.author.id] = []
    await ctx.send("Please send a message containing the names of the people you wish to recommend. Make sure you do not tag said individuals")


    
  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author == self.client.user or message.content.startswith("~"):
      return
    author = message.author.id
    global processors
    if author in processors.keys():
      ls = processors[author]
      if len(ls) == 0:
        ls.append(message.content)
        await message.channel.send("Please enter in the rank or medals you wish to recommend them for")
      elif len(ls) == 1:
        ls.append(message.content)
        await message.channel.send("Please enter in the reason for your recommendation")
      elif len(ls) == 2:
        if len(message.content) >= 1024:
          await message.channel.send("Your message exceeds 1024 characters. Discord embeds cannot process more than this. Please shorten your message and try again")
          return
        ls.append(message.content)
        await message.channel.send("Your recommendation has been processed.")
        await self.addrec(author=author, content=processors[author])
        processors.pop(author)

  async def addrec(self, author, content):
    global channel
    global globalchan
    people = content[0]
    ranks = content[1]
    reason = content[2]
    user = self.client.get_guild(main.guild).get_member(author)
    embed = discord.Embed(title="Recommendation", description="Recommendation sent by: " + user.display_name, color=0xffee00)
    embed.add_field(name="Users: ", value=people, inline=False)
    embed.add_field(name="Ranks:", value=ranks, inline=False)
    embed.add_field(name="Reason:", value=reason, inline=False)
    if roleutils.is_officer(user):
      chan = self.client.get_channel(channel)
      message = await chan.send(embed=embed)
      with open("recommendations.txt", "r+") as file:
        file.seek(0, 2)
        file.write(str(message.id) + '\n')
    else: 
      chan = chan = self.client.get_channel(globalchan)
      message = await chan.send(embed=embed)
      with open("preprocessed.txt", "r+") as file:
        file.seek(0, 2)
        file.write(str(message.id) + '\n')
    
  
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    global channel
    sentin = self.client.get_channel(payload.channel_id)
    if sentin == self.client.get_channel(channel):
      message = await sentin.fetch_message(payload.message_id)
      embeds = message.embeds
      if len(embeds) != 0:
        if roleutils.is_officer(payload.member) and payload.emoji.name == "✅":
          id = message.id
          with open("recommendations.txt", "r+") as file:
            lines = file.readlines()
            for line in lines:
              print(line)
              if str(id) in line:
                lines.remove(str(line))
            await message.delete()
            file.seek(0)
            file.truncate(0)
            file.writelines(lines)
          readymessage = await self.client.get_channel(readychan).fetch_message(readymsg)
          conlist = readymessage.content.split("\n")
          for row in conlist:
            if row == "--https://discord.com/channels/" + str(main.guild) + "/" + str(channel) + "/" + str(id):
              conlist.remove(row)
          "\n".join(conlist)
          m = await self.client.get_channel(readychan).fetch_message(readymsg)
          newcontent = "\n".join(conlist)
          await m.edit(content=newcontent)



  @commands.Cog.listener()
  async def on_ready(self):
    self.remind_loop.start()

    
def setup(client):
  client.add_cog(RecomCog(client))
