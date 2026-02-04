import discord
from discord import app_commands
import io
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

ALLOWED_ROLE_ID = 1317228890976161936  

@client.event
async def on_ready():
    await tree.sync() 
    print(f"Logged in as {client.user}")

@tree.command(name="generate", description="Generate a custom bot script")
@app_commands.describe(mainusername="Your main Roblox username", prefix="The command prefix (Default is !)")
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.user.id)) 
async def generate(interaction: discord.Interaction, mainusername: str, prefix: str = "!"):
    
    has_role = any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles)
    
    if not has_role:
        await interaction.response.send_message("❌ Error: You do not have permission.", ephemeral=True)
        return

    script_template = f"""getgenv().Owner = "{mainusername}"
ggetgenv().Bot = {
    Config = {},
    State = {},
    Runtime = {}
}
Bot.Config = {
    Command = { Prefix = "!" },
    Guns = { Enabled = true, List = { "aug", "rifle" } },
    Strafe = { Enabled = true, Mode = "random2", Distance = 12, Speed = 1.25 },
    AntiStomp = { Enabled = true, Delay = 0.15 },
    AutoArmor = { Enabled = true, Threshold = 120, CheckInterval = 0.5 },
    Dance = { Enabled = true, Default = "Floss" },
    AutoMask = { Enabled = false, Type = "Ninja Mask"},
    Skybox = { 
        Enabled = true, 
        Default = "Neptune" -- "Neptune" | "Purple Nebula" | "Minecraft" | "Night Sky" | "Aesthetic Night"
    },
    FPS = { 
        Cap = 240, 
        WhiteScreen = false
    }
}
loadstring(game:HttpGet("https://raw.githubusercontent.com/yuvic123/Skidov1.2-stand/refs/heads/main/Skido-Sniper-Bot"))()"""

    file_data = io.BytesIO(script_template.encode())
    discord_file = discord.File(file_data, filename="script.txt")

    await interaction.response.send_message(
        content=f"✅ Done {interaction.user.mention}! Script for `{mainusername}` generated below:", 
        file=discord_file
    )

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⏳ Wait **{error.retry_after:.1f}s**.", ephemeral=True)
    else:
        print(f"Error: {error}")

keep_alive()
token = os.getenv("DISCORD_TOKEN") 

if token:
    client.run(token)
else:
    print("Error: DISCORD_TOKEN environment variable is missing.")

