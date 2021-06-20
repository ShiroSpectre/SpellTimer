from discord.ext import commands
from functions import _timer
import asyncio

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc = None

    @commands.command()
    async def hello(self, ctx):
        member = ctx.author
        await ctx.channel.send(f'Hello {member}!')

    @commands.command()
    async def join(self, ctx):
        await ctx.message.delete()
        if ctx.author.voice and not self.vc:
            channel = ctx.author.voice.channel
            self.vc = await channel.connect()
            await _timer.enable_sound(self.vc)
        elif not self.vc:
            msg = await ctx.channel.send(f'Please join a voice channel first {ctx.author}!')
            await asyncio.sleep(2)
            await msg.delete()
        else:
            msg = await ctx.channel.send(f'Already connected!')
            await asyncio.sleep(2)
            await msg.delete()

    @commands.command()
    async def leave(self, ctx):
        await ctx.message.delete()
        if self.vc:
            await ctx.voice_client.disconnect()
        else:
            msg = await ctx.channel.send('I am not connected to a voice channel!')
            await asyncio.sleep(2)
            await msg.delete()
            

def setup(bot):
    bot.add_cog(General(bot))