import json
import discord
from discord import app_commands
from discord.ext import commands
import shelve
from sys import exit
import ansicon

ansicon.load()

config = json.load(open('config.json'))

bot = commands.Bot(command_prefix = '$', help_command = None, intents=discord.Intents.none())

try:
    print("[Shelve] loading data...")
    DB = shelve.open("Medals")
    print("[Shelve] data loaded in!")
    DB.close()
except Exception as e:
    exit(f"[Shelve] critical error: {e}")


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)

@bot.tree.command(name = "check", description="Lists all of the medals you or user has")
async def check(interaction: discord.Interaction, user: discord.Member = None):
    if user == None:
        userid = str(interaction.user.id)
    else:
        userid = str(user.id)
    DB = shelve.open("Medals")
    try:
        userMedals = DB[userid]
        print("[Shelve] Called")
        await interaction.response.send_message(f"{userMedals}")
        DB.close()
    except Exception as e:
        await interaction.response.send_message(f"can't send | {e}")
        DB.close()


@bot.tree.command(name = "award", description = "Award a medal to a user")
@app_commands.choices(medals=[
	discord.app_commands.Choice(name='🥇TestMedal1', value = 1),
	discord.app_commands.Choice(name='🥈TestMedal2', value = 2),
	discord.app_commands.Choice(name='🥉TestMedal3', value = 3)])
async def award(interaction: discord.Interaction, awardee: discord.Member, medals: discord.app_commands.Choice[int]):
    await interaction.response.send_message(f"awardee: {awardee.name}\nmedal: {medals.name}/{medals.value}")
    DB = shelve.open("Medals")
    try:
        awardeeID = str(awardee.id)
        DB[awardeeID]
    except:
        DB[awardeeID] = []
    tempDict = DB[awardeeID]
    tempDict.append(medals.value)
    DB[awardeeID] = tempDict
    DB.close()
    print("[Shelve] Stored")
    

bot.run(config['TOKEN'])