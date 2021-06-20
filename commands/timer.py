from discord.ext import commands
from functions import _timer

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flag = False

    @commands.command()
    async def start(self, ctx):
        await ctx.message.delete()
        if not self.flag: 
            self.flag = True
            await _timer.initiate_timer(self.bot, ctx)
        else: await ctx.channel.send('Please stop the running timer first!')
        

    @commands.command()
    async def stop(self, ctx):
        await ctx.message.delete()
        if self.flag: 
            self.flag = False
            await _timer.delete_timer()
        else: await ctx.channel.send('Please start a timer first!')

    @commands.command()
    async def mute(self):
        await _timer.mute_sound()
        
def setup(bot):
    bot.add_cog(Timer(bot))