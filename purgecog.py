import discord
from discord.ext import commands
import os
import datetime
import roleutils
import main

purge_message = None
end_date = None
mod_chan = 889617374922289152

# 141 Guild ID 468278941652746241
# moderator chat ID 889617374922289152



class PurgeCog(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(name="initpurge")
  async def purge(self, ctx):

    author = ctx.author
    if not roleutils.is_officer(author):
      await ctx.reply("You do not have permissions for this command.")
      return

    global purge_message
    global end_date

    if purge_message is not None:
      await ctx.reply("A purge has already been initiated. You may not start another")
      return

    end_date = (datetime.datetime.now() + (datetime.timedelta(days=7))).strftime('%m/%d/%Y')

    for member in self.client.get_guild(main.guild).members:
      if member.bot: continue
      if roleutils.has_role(member, "[141CR]"):
        role = discord.utils.get(self.client.get_guild(
        main.guild).roles,name="Purge")
        print(member.name)
        await member.add_roles(role)

    embed = discord.Embed(title="IMPORTANT: MUST READ", description="141 Colonial Rangers Member Purge", color=0xff0000)
    embed.add_field(
            name="Intent",
            value="High command has designated a member purge commence. By reacting to this message with the reaction role below, you will be exempt. Failure to follow will result in your removal from regiment.",
            inline=False)
    embed.add_field(name="Start Date",
                    value=datetime.datetime.now().strftime('%m/%d/%Y'),
                    inline=False)
    embed.add_field(name="End Date", value=end_date, inline=False)
    embed.set_thumbnail(url="https://i.imgur.com/3AtXglX.png")
    await ctx.message.delete()
    msg = await ctx.send(embed=embed)

    emoji = '✅'
    await msg.add_reaction(emoji)
    purge_message = str(msg.id)

    await self.client.get_guild(main.guild).get_channel(mod_chan).send("Purge has been started by " +ctx.author.mention)

    with open("purgemsg.txt", "w") as file:
        file.write(str(msg.id) + "\n" + end_date + datetime.datetime.now().strftime('%m/%d/%Y'))

    main.purge_loop.start()

  @commands.command(name="cancelpurge")
  async def cancel_purge(self, ctx):
    global purge_message
    global end_date

    if not roleutils.is_officer(ctx.author):
      await ctx.reply("You do not have permissions for this command.")
      return

    if purge_message is not None:
      await ctx.send("Cancelling purge...")
      main.purge_loop.cancel()
      purge_message = None
      end_date = None
      dir_path = os.path.dirname(os.path.realpath(__file__))
      os.remove(dir_path + '/purgemsg.txt')
      for member in self.client.get_guild(main.guild).members:
        role = discord.utils.get(self.client.get_guild(main.guild).roles,name="Purge")
        await member.remove_roles(role)
      await ctx.send("Purge stopped")
      await self.client.get_guild(main.guild).get_channel(mod_chan).send("Purge has been cancelled by " + ctx.author.mention)
    else:
      await ctx.send("There is currently no purge happening.")

  def set_message(self, msg):
    global purge_message
    purge_message = msg

  def set_date(seld, date):
    global end_date
    end_date = date

  def get_msg(self):
    global purge_message
    return purge_message

  def get_date(self):
    global end_date
    return end_date

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    message = payload.message_id
    member = payload.member
    if member.bot: return
    global purge_message
    if str(message) == purge_message and payload.emoji.name == "✅":
      role = discord.utils.get(self.client.get_guild(payload.guild_id).roles,name="Purge")
      await member.remove_roles(role)

  async def start_purge(self):
    remove_roles = [
      "Master Sergeant", "Staff Sergeant", "Corporal", "NCO",
      "Specialist", "Private 1st Class", "Private", "Recruit",
      "Enlisted", "[141CR]", "Ground Combat", "Rifleman", "Medic",
      "Grenadier", "Heavy Weapons Operator", "Partisan", "Marine",
      "Armor", "Artillery", "Logistics", "Engineer", "Strategic/Recon",
      "Pathfinder", "QRF", "Purge", "Collie"
      ]

    removed_members = []

    for member in self.client.get_guild(main.guild).members:
      if roleutils.has_role(member, "[141CR]") and roleutils.has_role(member, "Purge"):
        for role_has in member.roles:
          if role_has.name in remove_roles:
            print(member.name)
            role = discord.utils.get(self.client.get_guild(main.guild).roles, name=role_has.name)
            await member.remove_roles(role)
            removed_members.append(member.name)

    with open("purgemembers.txt", "w") as file:
      for elem in removed_members:
        file.write(elem + "\n")\

    global purge_message
    purge_message = None
    global end_date
    end_date = None
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.remove(dir_path + '/purgemsg.txt')
    main.purge_loop.cancel()
    await self.client.get_guild(main.guild).get_channel(mod_chan).send(
            "@everyone Purge has been completed. Message Jarkyc to get list of members purged.")


def setup(client):
  client.add_cog(PurgeCog(client))
