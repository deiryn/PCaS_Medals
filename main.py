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

def getMedal(id):
    match id:
        case 1:
            return "🥇 medal1"
        case 2:
            return "🥈 medal2"
        case 3:
            return "🥉 medal3"
        case _:
            return

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
        getUserMedals = DB[userid]
        print("[Shelve] Called")
        userMedals = []
        for medal in getUserMedals:
            userMedals.append(getMedal(medal))
        embed = discord.Embed(title="Medals:", description="Listing all of your medals...")
        for item in userMedals:
            embed.add_field(name="\u200b", value=item, inline=False)
        await interaction.response.send_message(embed=embed)
        DB.close()
    except Exception as e:
        await interaction.response.send_message(f"can't send | {e}")
        DB.close()


@bot.tree.command(name = "award", description = "Award a medal to a user")
@app_commands.choices(medals=[
	discord.app_commands.Choice(name='<:True:930898578963062795> TestMedal1', value = 1),
	discord.app_commands.Choice(name='<:True:930898578963062795> TestMedal2', value = 2),
	discord.app_commands.Choice(name='<:True:930898578963062795> TestMedal3', value = 3)])
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