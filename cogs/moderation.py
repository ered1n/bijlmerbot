import discord
import time
import json
import io
import textwrap
import traceback
import config
import asyncio

from discord.ext import commands
from methods import permission
from contextlib import redirect_stdout

class Moderation:

    def __init__(self, bot):
        self.bot = bot
    
    async def purgeMessage(self, ctx, amount):
        purgeEmbed = discord.Embed(title="Messages deleted", description="Deleted " + str(amount) + " message(s)", colour=0x00ff00)
        date = time.strftime("%d/%m/%Y %H:%M")
        purgeEmbed.set_footer(text=date)
        await ctx.send(embed=purgeEmbed, delete_after=10)
        
    async def checkCmd(self, ctx, cmd):
        if(cmd in self.bot.permCommands):
            return True
        else:
            await ctx.send("Error, command doesn't require permission or doesn't exist", delete_after=10)
            return False
            
    async def checkRoleOrUser(self, ctx, roleOrUser):
        try:
            return await commands.MemberConverter().convert(ctx, roleOrUser)
        except commands.BadArgument:
            pass
        try:
            return await commands.RoleConverter().convert(ctx, roleOrUser)
        except commands.BadArgument:
            await ctx.send("Error, invalid user or role", delete_after=10)
            pass

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')
            
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

    # ban
    @commands.command()
    @commands.check(permission.checkPermission)
    async def ban(self, ctx, user: discord.Member, *, reason: str):
        await user.send("You have been banned from " + ctx.guild.name + " because of the following reason: '" + reason + "'")
        await user.ban(reason=reason)

    # kick
    @commands.command()
    @commands.check(permission.checkPermission)
    async def kick(self, ctx, user: discord.Member, *, reason: str):
        await user.send("You have been kicked from " + ctx.guild.name + " because of the following reason: '" + reason + "'")
        await user.kick(reason=reason)

    # warn
    @commands.command()
    @commands.check(permission.checkPermission)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        await user.send("You have been warned on " + ctx.guild.name + " because of the following reason: '" + reason + "'")

    #permission
    @commands.group(usage="<add/remove> <cmd> <roleOrUser>")
    async def perm(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument
    
    @perm.command(hidden=True)
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
                    await ctx.send("Permission added :ok_hand: :100:", delete_after=10)
                else:
                    await ctx.send("Error, this rule already exists :smirk:", delete_after=10)
        else:
            await ctx.send("Error, you don't have permission to use the perm command :joy:", delete_after=10)
        
    @perm.command(hidden=True)
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
                    await ctx.send("Permission removed :worried:", delete_after=10)
                else:
                    await ctx.send("Error, rule doesn't exist :rage:", delete_after=10)
        else:
            await ctx.send("Error, you don't have permission to use the perm command :joy:")

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def eval(self, ctx, *, body: str):
        if ctx.author.id in config.owners:
            """Evaluates a code"""

            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message
            }

            env.update(globals())

            body = self.cleanup_code(body)
            stdout = io.StringIO()

            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

            try:
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction('\u2705')
                except:
                    pass

                if ret is None:
                    if value:
                        await ctx.send(f'```py\n{value}\n```')
                else:
                    self._last_result = ret
                    await ctx.send(f'```py\n{value}{ret}\n```')
        else:
            await ctx.send("Error, you don't have permission to use the eval command :rage:", delete_after=10)

def setup(bot):
    bot.add_cog(Moderation(bot))