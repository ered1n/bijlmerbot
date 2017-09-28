import discord
from discord.ext import commands
from methods import permission
import time
import json

class Moderation:

    def __init__(self, bot):
        self.bot = bot
    
    async def purgeMessage(self, ctx, amount):
        purgeEmbed = discord.Embed(title="Messages deleted", description="Deleted " + str(amount) + " message(s)", colour=0x00ff00)
        date = time.strftime("%d/%m/%Y %H:%M")
        purgeEmbed.set_footer(text=date)
        await ctx.send(embed=purgeEmbed)
        
    async def checkCmd(self, ctx, cmd):
        if(cmd in self.bot.permCommands):
            return True
        else:
            await ctx.send("Error, command doesn't require permission or doesn't exist")
            return False
            
    async def checkRoleOrUser(self, ctx, roleOrUser):
        try:
            return await commands.MemberConverter().convert(ctx, roleOrUser)
        except commands.BadArgument:
            pass
        try:
            return await commands.RoleConverter().convert(ctx, roleOrUser)
        except commands.BadArgument:
            await ctx.send("Error, invalid user or role")
            pass
            
    #purge
    @commands.command()
    @commands.check(permission.checkPermission)
    async def purge(self, ctx, amount: int, member: discord.Member=None):
        messages = []
        await ctx.channel.purge(limit=1)
        if member:
            async for message in ctx.channel.history():
                if message.author.id == member.id:
                    messages.append(message)
                if len(messages) == amount:
                    break
        else:
            async for message in ctx.channel.history():
                messages.append(message)
                if len(messages) == amount:
                    break
        await ctx.channel.delete_messages(messages)
        await self.purgeMessage(ctx, len(messages))
    
    #permission
    @commands.group()
    async def perm(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument
    
    @perm.command()
    async def add(self, ctx, cmd, roleOrUser):
        if ctx.author.id == ctx.guild.owner.id or permission.checkPermission(ctx):
            if await self.checkCmd(ctx, cmd):
                roleOrUser = await self.checkRoleOrUser(ctx, roleOrUser)
                if not permission.findPermission(permission.getPermissions(self.bot.permissionJSON), cmd, ctx.guild.id, roleOrUser):
                    rule = {"command": cmd, "server": ctx.guild.id, "role/user": roleOrUser.id}
                    with open(self.bot.permissionJSON, "r+") as data:
                        perms = json.load(data)
                        perms.append(rule)
                        data.seek(0)
                        json.dump(perms, data)
                    await ctx.send("Permission added :ok_hand: :100:")
                else:
                    await ctx.send("Error, this rule already exists :smirk:")
        else:
            await ctx.send("Error, you don't have permission to use the perm command :joy:")
        
    @perm.command()
    async def remove(self, ctx, cmd, roleOrUser):
        if ctx.author.id == ctx.guild.owner.id or permission.checkPermission(ctx):
            if await self.checkCmd(ctx, cmd):
                roleOrUser = await self.checkRoleOrUser(ctx, roleOrUser)
                rule = permission.findPermission(permission.getPermissions(self.bot.permissionJSON), cmd, ctx.guild.id, roleOrUser)
                if(rule):
                    with open(self.bot.permissionJSON, "r+") as data:
                        perms = json.load(data)
                        perms.pop(perms.index(rule))
                        data.seek(0)
                        json.dump(perms, data)
                        data.truncate()
                    await ctx.send("Permission removed :worried:")
                else:
                    await ctx.send("Error, rule doesn't exist :rage:")
        else:
            await ctx.send("Error, you don't have permission to use the perm command :joy:")
            
def setup(bot):
    bot.add_cog(Moderation(bot))