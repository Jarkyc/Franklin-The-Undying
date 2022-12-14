from discord.ext import commands


class ErrorHandeler(commands.Cog):
  """A cog for global error handling"""

  def __init__(self, bot: commands.Bot):
   self.bot = bot

  @commands.Cog.listener()
  async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MemberNotFound):
      await ctx.send("Please input a valid user")
    if isinstance(error, commands.UnexpectedQuoteError):
      await ctx.send("Your message must be surrounded by quotes.")
      
def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandeler(bot))
