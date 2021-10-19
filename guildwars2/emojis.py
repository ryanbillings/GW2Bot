import re

import discord
from discord.ext import commands


class EmojiMixin:
    async def prepare_emojis(self):
        doc = await self.bot.database.get_cog_config(self)
        self.emojis = doc.get("emojis", {})

    def get_emoji(self,
                  ctx,
                  emoji,
                  *,
                  fallback=False,
                  fallback_fmt="{}",
                  return_obj=False):
        if isinstance(ctx, (discord.Message, discord.TextChannel)):
            if ctx.guild:
                me = ctx.guild.me
            else:
                me = self.bot.user
        elif ctx:
            me = ctx.me
        else:
            me = None
        if ctx:
            if isinstance(ctx, discord.TextChannel):
                channel = ctx
            elif ctx.channel:
                channel = ctx.channel
            else:
                channel = None
            if channel:
                can_use = channel.permissions_for(me).external_emojis
            else:
                can_use = True
            if can_use:
                search_str = emoji.lower().replace(" ", "_")
                # Remove illegal emoji characters
                search_str = re.sub('[\.,\,,\',\:,\;,!\?]', '', search_str)
                emoji_id = self.emojis.get(search_str)
                if emoji_id:
                    emoji_obj = self.bot.get_emoji(emoji_id)
                    if emoji_obj:
                        if return_obj:
                            return emoji_obj
                        return str(emoji_obj)
        if fallback:
            return fallback_fmt.format(emoji)
        return ""

    @commands.group(name="emojis", case_insensitive=True)
    @commands.guild_only()
    @commands.is_owner()
    async def emojis_management(self, ctx):
        """Commands related to emoji management"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @emojis_management.command(name="register")
    async def emojis_register(self, ctx):
        """Register emojis present in the current server"""
        registered = []
        for emoji in ctx.guild.emojis:
            name = emoji.name
            await self.bot.database.set_cog_config(
                self, {"emojis." + name.lower(): emoji.id})
            registered.append(emoji.name)
        if not registered:
            return await ctx.send("No emojis were registered")
        await ctx.send("Registered {} emojis:\n```{}```".format(
            len(registered), ", ".join(registered)))
        await self.prepare_emojis()
