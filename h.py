"""
TERMINALX999 - Modern Slash Command Bot (Python)
Dependencies: pip install discord.py requests
"""

import discord
import requests
import datetime
from discord import app_commands
from discord.ext import commands

# --- CONFIGURATION ---
API_KEY = 'TX999-1ED943E0-39A19E27'
API_BASE = 'https://terminalx999.live/api.php'
ROLE_ID = '1509195631426535616' 
CHANNEL_ID = '1509195425964363877'
BOT_TOKEN = 'MTUwOTE5NzMzMTA5MjczODEwOA.GP1Aac.mbGpwZ08FS9Dg4SvOHI0TiGDJPdvIcRKP9vDJQ'

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("🔄 Syncing Slash Commands...")
        await self.tree.sync()
        print("✅ Commands Synced!")

bot = MyBot()

def create_embed(title, description, color=0x0062ff):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text="Made By Ishu • Modern Slash API", icon_url="https://media.discordapp.net/attachments/1233881503923179572/1508508525733613768/f5a065de3c18e183c40f9e0acc24d53b.png?ex=6a17c5cb&is=6a16744b&hm=6afbbd33e8631da72962e5eaa57952de3d27b3a97a2ee4ce765ac9bd523e5f80&=&format=webp&quality=lossless&width=815&height=815")
    return embed

async def check_security(interaction: discord.Interaction):
    if CHANNEL_ID and str(interaction.channel_id) != str(CHANNEL_ID):
        await interaction.response.send_message(embed=create_embed("❌ Wrong Channel", f"This bot only works in <#{CHANNEL_ID}>.", 16727296), ephemeral=True)
        return False
    if ROLE_ID and discord.utils.get(interaction.user.roles, id=int(ROLE_ID)) is None:
        await interaction.response.send_message(embed=create_embed("❌ Access Denied", "You don't have the required role.", 16727296), ephemeral=True)
        return False
    return True

@bot.event
async def on_ready():
    print(f'🚀 {bot.user} is online!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))

@bot.tree.command(name="add", description="Whitelist a new UID")
@app_commands.describe(uid="The UID to whitelist", days="Expiry days (default 30)")
async def add(interaction: discord.Interaction, uid: str, days: int = 30):
    if not await check_security(interaction): return
    await interaction.response.defer()
    
    try:
        url = f"{API_BASE}?action=reseller_add&api_key={API_KEY}&uid={uid}&days={days}"
        res = requests.get(url).json()
        if res.get('success'):
            fetched_name = res.get('name', 'Unknown')
            embed = create_embed("✅ Success", f"UID `{uid}` has been whitelisted.", 51283)
            embed.add_field(name="🕒 Expiry", value=f"{days} Days", inline=True)
            embed.add_field(name="👤 Player", value=fetched_name, inline=True)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=create_embed("❌ Failed", res.get('error', 'Unknown error (Player name might be invalid)'), 16727296))
    except Exception as e:
        await interaction.followup.send("❌ **API Connection Error**")

@bot.tree.command(name="remove", description="Delete a UID from whitelist")
async def remove(interaction: discord.Interaction, uid: str):
    if not await check_security(interaction): return
    await interaction.response.defer()
    try:
        url = f"{API_BASE}?action=reseller_remove&api_key={API_KEY}&uid={uid}"
        res = requests.get(url).json()
        if res.get('success'):
            await interaction.followup.send(embed=create_embed("🗑️ Removed", f"UID `{uid}` deleted.", 51283))
        else:
            await interaction.followup.send(embed=create_embed("❌ Error", "UID not found.", 16727296))
    except:
        await interaction.followup.send("❌ **API Error**")

@bot.tree.command(name="list", description="Show your whitelisted UIDs")
async def list_uids(interaction: discord.Interaction):
    if not await check_security(interaction): return
    await interaction.response.defer()
    try:
        url = f"{API_BASE}?action=reseller_list&api_key={API_KEY}"
        res = requests.get(url).json()
        if res.get('success'):
            uids = "\n".join([f"🔹 `{e['uid']}` - {e.get('name', 'N/A')}" for e in res.get('data', [])]) or "Empty list."
            await interaction.followup.send(embed=create_embed("📜 Whitelist", uids[:4000]))
    except:
        await interaction.followup.send("❌ **API Error**")

@bot.tree.command(name="credits", description="Check your balance")
async def credits(interaction: discord.Interaction):
    if not await check_security(interaction): return
    try:
        url = f"{API_BASE}?action=get_my_api_key&api_key={API_KEY}"
        res = requests.get(url).json()
        bal = res.get('data', {}).get('credits', 0)
        await interaction.response.send_message(embed=create_embed("💳 Balance", f"You have **{bal}** credits remaining."))
    except:
        await interaction.response.send_message("❌ **Error**")

@bot.tree.command(name="help", description="Show bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = create_embed("🛠️ Commands", "Modern Slash Command Menu")
    embed.add_field(name="/add", value="Add a new UID", inline=False)
    embed.add_field(name="/remove", value="Delete a UID", inline=False)
    embed.add_field(name="/list", value="Show your UIDs", inline=False)
    embed.add_field(name="/credits", value="Check balance", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(BOT_TOKEN)