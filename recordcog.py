import discord
from discord.ext import commands
import os
import roleutils

rec_dir = None

class RecordCog(commands.Cog):

  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    global rec_dir
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder = dir_path + "/records"
    if not os.path.exists(folder):
      os.makedirs(folder)
    rec_dir = folder
  
  @commands.command()
  async def getrecords(self, ctx, member: discord.Member = None):
    if member == None:
      await ctx.send("Please enter a member to request the records of")
      return

    if member.id != ctx.author.id and not roleutils.is_officer(ctx.author):
      await ctx.send("You do not have permission to request records that are not yours")
      return

    record = rec_dir + "/" + str(member.id)
    if not os.path.exists(record):
      await ctx.send("This person has no current records")
      return
    
  
  def addrecord(self, user, type, content):
    
    dir = os.path.dirname(os.path.realpath(__file__)) + "/records/" + str(user)
    type_letter = None
    
    if type == "medal":
      type_letter = "M"
    elif type == "infraction":
      type_letter = "I"
    elif type == "note":
      type_letter = "N"
    elif type == "promotion":
      type_letter = "P"

    with open(dir + "/ " + type_letter + self.getlastnum(type) + ".txt", "w+") as file:
      file.writelines(content)
  
  def getlastnum(self, type):
    num = None
    for folder in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/records/"):
      for file in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/records/" + folder):
        filename = file.replace(".txt", "")
        print(filename)
        if filename.startswith(type):
          if num == None:
            num = (filename.replace(type, ""))
          else:
            if int(filename.replace(type, "")) > num:
              num = (filename.replace(type, ""))
    if num == None:
      return ("1")

    return(num)
  
  @commands.command()
  async def getrecord(self, ctx, arg):
     for folder in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/records/"):
      for file in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/records/" + folder):
        filename = file.replace(".txt", "")
        if filename == arg:
          with open(os.path.dirname(os.path.realpath(__file__)) + "/records/" + folder + "/" + file, "r") as recordfile:
            lines = recordfile.readlines()
            date = lines[0].replace("\n", "")
            giver = lines[1].replace("\n","")
            reason = lines[2].replace("\n","")
            exten = lines[3].replace("\n","")
            user = await self.client.fetch_user(folder)
            name = user.display_name

            title = None
            if(arg.startswith("M")):
              title = "Medal Record"
            elif arg.startswith("I"):
              title = "Infraction Record"
            elif arg.startswith("N"):
              title = "Note Record"
            elif arg.startswith("P"):
              title = "Promotion Record"
            
            pfp = user.avatar_url

            embed = discord.Embed(title=title, description="", color=0x9B06C4)
            embed.set_thumbnail(url=(pfp))
            embed.add_field(name="Date Given", value=date, inline=False)
            embed.add_field(name="Recipient", value=name, inline=False)
            embed.add_field(name="Author", value=giver, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Context", value=exten, inline=False)

            await ctx.send(embed=embed)
  
def setup(client):
  client.add_cog(RecordCog(client))

# take a user and put them in a dict with a list 
# list contains the data being collected
# listener checking if someone talks, are they in the current list of data collection, see what step they are on based on list length
# take their message and add it to the list
# on last message, send compiled data