import json
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
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
        medalAmount = []
        for medal, amount in getUserMedals.items():
            userMedals.append(getMedal(medal))
            medalAmount.append(amount)
        print(userMedals)
        print(medalAmount)
        embed = discord.Embed(title="Medals:", description="Listing all of your medals...")
        for medal, amount in zip(userMedals, medalAmount):
                embed.add_field(name="\u200b", value=f"{medal} x{amount}", inline=False)
        await interaction.response.send_message(embed=embed)
        DB.close()
    except Exception as e:
        await interaction.response.send_message(f"No medals were found or an error happened.", ephemeral=True)
        print(f"CHECK ERROR: {e}")
        DB.close()


@bot.tree.command(name = "award", description = "Award a medal to a user")
@app_commands.choices(medals=[
	discord.app_commands.Choice(name='<:True:930898578963062795> TestMedal1', value = 1),
	discord.app_commands.Choice(name='<:True:930898578963062795> TestMedal2', value = 2),
	discord.app_commands.Choice(name='<:True:930898578963062795> TestMedal3', value = 3)])
async def award(interaction: discord.Interaction, awardee: discord.Member, medals: discord.app_commands.Choice[int]):
    DB = shelve.open("Medals")
    try:
        awardeeID = str(awardee.id)
        DB[awardeeID]
    except:
        DB[awardeeID] = {}
    tempDict = DB[awardeeID]
    if medals.value in tempDict:
        medalAmount = tempDict[medals.value]
        tempDict[medals.value] = medalAmount + 1
    else:
        tempDict[medals.value] = 1
    DB[awardeeID] = tempDict
    print(tempDict)
    DB.close()
    await interaction.response.send_message(f"awardee: {awardee.name}\nmedal: {medals.name}/{medals.value}")
    print("[Shelve] Stored")


@bot.tree.command(name = "strip", description="Takes away ALL medals")
async def strip(interaction: discord.Interaction, target: discord.Member):
    proceedButton = Button(label="Proceed", style=discord.ButtonStyle.red)
    try:
        view = View()
        view.add_item(proceedButton)
    except Exception as e:
        print(e)

    async def proceedInteraction(interaction: discord.Interaction):
        DB = shelve.open("Medals")
        try:
            targetID = str(target.id)
            DB[targetID]
        except:
            await interaction.response.send_message("User not found.")
            return
        del DB[targetID]
        embed = discord.Embed(title="Success!", description=f"{target.name} is cleared of medals.", colour = discord.Colour.red())
        DB.close()
        await interaction.response.send_message(embed=embed)
        print("[Shelve] Deleted value")
    proceedButton.callback = proceedInteraction

    embed = discord.Embed(title="Halt!", description="This action will clear **ALL** user medals.\n__You cannot reverse it!__", colour=discord.Color.red())
    try:
        await interaction.response.send_message(embed=embed, view=view)
    except Exception as e:
        print(e)
    

bot.run(config['TOKEN'])