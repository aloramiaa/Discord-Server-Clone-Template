"""
Discord Server Cloning Bot

A utility bot for cloning Discord server structure including roles, channels, and permissions.

Features:
- Copies roles with attributes (name, color, permissions, hoist, mentionable)
- Maintains role hierarchy/positioning
- Replicates category and channel structure
- Handles permission overwrites
- Preserves channel positions and settings

Requirements:
- Bot token with administrator privileges
- Bot added to both source and target servers
- Privileged gateway intents enabled:
  * Server Members Intent
  * Message Content Intent

Usage:
1. Replace YOUR_BOT_TOKEN_HERE with actual token
2. Run the script
3. Follow console prompts to input server IDs
4. Confirm operation

WARNING: This will DELETE ALL existing roles/channels in target server!
"""
import discord
from discord.ext import commands
import asyncio

# IMPORTANT: Replace with your bot token
TOKEN = "YOUR_BOT_TOKEN_HERE"

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")

    try:
        # Get user input for source & target guild IDs
        source_id = int(input("Enter SOURCE Guild ID to copy from: ").strip())
        target_id = int(input("Enter TARGET Guild ID to copy to: ").strip())

        source_guild = bot.get_guild(source_id)
        target_guild = bot.get_guild(target_id)

        if not source_guild or not target_guild:
            print("❌ Bot must be in BOTH servers.")
            await bot.close()
            return

        confirm = input(
            f"⚠️ Are you sure you want to CLEAR target server and CLONE '{source_guild.name}' to '{target_guild.name}'? (yes/no): "
        ).strip().lower()
        
        if confirm != "yes":
            print("❌ Operation aborted.")
            await bot.close()
            return

        # Check bot permissions in target server
        if not target_guild.me.guild_permissions.administrator:
            print("❌ Bot requires Administrator permissions in target server")
            await bot.close()
            return

        print(f"\n🚀 Starting clone from '{source_guild.name}' to '{target_guild.name}'...\n")

        # -------------------- CLEAR TARGET SERVER --------------------
        print("🔨 Clearing channels in target guild...")
        for channel in list(target_guild.channels):  # Use list to avoid mutation during iteration
            try:
                await channel.delete()
                print(f"✅ Deleted channel: {channel.name}")
            except discord.Forbidden:
                print(f"❌ Missing permissions to delete channel: {channel.name}")
            except discord.HTTPException as e:
                print(f"⚠️ HTTP error deleting channel '{channel.name}': {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error deleting channel '{channel.name}': {e}")

        print("🔨 Clearing roles in target guild...")
        for role in list(target_guild.roles):  # Use list to avoid mutation during iteration
            if role.name == "@everyone":
                continue
            try:
                await role.delete()
                print(f"✅ Deleted role: {role.name}")
            except discord.Forbidden:
                print(f"❌ Missing permissions to delete role: {role.name}")
            except discord.HTTPException as e:
                print(f"⚠️ HTTP error deleting role '{role.name}': {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error deleting role '{role.name}': {e}")

        # -------------------- COPY ROLES --------------------
        print("\n📦 Copying roles (name, color, permissions, hoist, mentionable)...")
        role_mapping = {}
        for role in source_guild.roles:
            if role.name == "@everyone":
                role_mapping[role.id] = target_guild.default_role
                continue
            try:
                new_role = await target_guild.create_role(
                    name=role.name,
                    colour=role.colour,
                    permissions=role.permissions,
                    hoist=role.hoist,
                    mentionable=role.mentionable,
                    reason=f"Cloned from {source_guild.name}"
                )
                role_mapping[role.id] = new_role
                print(f"Created role: {new_role.name}")
            except Exception as e:
                print(f"⚠️ Failed to create role '{role.name}': {e}")

        # -------------------- ROLE POSITION SYNCHRONIZATION --------------------
        print("\n🔧 Adjusting role positions to match source server...")
        role_positions = []
        for source_role in source_guild.roles:
            if source_role.name == "@everyone":
                continue
            target_role = role_mapping.get(source_role.id)
            if target_role:
                role_positions.append((target_role, source_role.position))

        positions_dict = {role.id: position for role, position in role_positions}
        
        try:
            await target_guild.edit_role_positions(positions_dict)
            print("✅ Role stacking order adjusted.")
        except Exception as e:
            print(f"⚠️ Failed to adjust role positions: {e}")

        # -------------------- COPY CATEGORIES & CHANNELS --------------------
        print("\n📂 Copying categories with permission overwrites...")
        for category in source_guild.categories:
            try:
                overwrites = {}
                for target, perms in category.overwrites.items():
                    if isinstance(target, discord.Role) and target.id in role_mapping:
                        overwrites[role_mapping[target.id]] = perms

                new_category = await target_guild.create_category(
                    name=category.name,
                    overwrites=overwrites,
                    position=category.position
                )
                print(f"Created category: {new_category.name}")

                # Copy channels within category
                for channel in category.channels:
                    await copy_channel(channel, new_category, role_mapping, target_guild)

            except Exception as e:
                print(f"⚠️ Failed to copy category '{category.name}': {e}")

        # -------------------- COPY UNCATEGORIZED CHANNELS --------------------
        print("\n📁 Copying uncategorized channels...")
        for channel in source_guild.channels:
            if not isinstance(channel, discord.CategoryChannel) and channel.category is None:
                await copy_channel(channel, None, role_mapping, target_guild)

        print("\n✅ Clone complete! Your target server is now an exact structural copy.")
        await bot.close()

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        await bot.close()

async def copy_channel(channel, new_category, role_mapping, target_guild):
    overwrites = {}
    for target, perms in channel.overwrites.items():
        if isinstance(target, discord.Role) and target.id in role_mapping:
            overwrites[role_mapping[target.id]] = perms

    try:
        if isinstance(channel, discord.TextChannel):
            new_chan = await target_guild.create_text_channel(
                name=channel.name,
                topic=channel.topic,
                position=channel.position,
                slowmode_delay=channel.slowmode_delay,
                nsfw=channel.nsfw,
                category=new_category,
                overwrites=overwrites
            )
            print(f"  Created text channel: {new_chan.name}")

        elif isinstance(channel, discord.VoiceChannel):
            new_chan = await target_guild.create_voice_channel(
                name=channel.name,
                position=channel.position,
                bitrate=channel.bitrate,
                user_limit=channel.user_limit,
                category=new_category,
                overwrites=overwrites
            )
            print(f"  Created voice channel: {new_chan.name}")

    except Exception as e:
        print(f"⚠️ Failed to create channel '{channel.name}': {e}")

bot.run(TOKEN)
