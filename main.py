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
            return "<:order_of_hollo55:1030766918291951656> Order of hollo55"
        case 2:
            return "<:order_of_nitro:1030767000127012935> Order of Nitro"
        case 3:
            return "<:clownery_medal:1003662400513388554> Official Medal of Clownery"
        case 4:
            return "<:veterans_award:1030767334727622719> PCaS Veteran' Award"
        case 5:
            return "<:winner_of_p2:1030767529091674113> Winner of the PCaS Challenge (P2)"
        case 6:
            return "<:winner_of_p1:1030767598687748176> Winner of the PCaS Challenge (P1)"
        case 7:
            return "Merit"
        case 8:
            return "<:merit_VI_medal:1030768469605621822> Meritorious Merit of Meritness"
        case 9:
            return "<:conduct:1030767684436115537> Medal of Conduct"
        case 10:
            return "<:activity:1030767651590508584> Medal of Activity"
        case 11:
            return "<:development_excellence:1030767088048033822> Medal of Development Excellence"
        case 12:
            return "<:event_excellence:1030767160450105446> Medal of Event Excellence"
        case 13:
            return "<:security_excellence:1030767207405334598> Medal of Security Excellence"
        case 14:
            return "<:food_excellence:1030767250514395156> Medal of Food Excellence"
        case 15:
            return "<:loser_of_p2:1030769136906809375> Loser of the PCaS Challenge"
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
        #print(userMedals)
        #print(medalAmount)
        embed = discord.Embed(title="Medals:", description="Listing all of your medals...")
        for medal, amount in zip(userMedals, medalAmount):
                embed.add_field(name="\u200b", value=f"**{medal}** x{amount}", inline=False)
        await interaction.response.send_message(embed=embed)
        DB.close()
    except Exception as e:
        print(f"CHECK ERROR: {e}")
        await interaction.response.send_message(f"No medals were found or an error happened.", ephemeral=True)


@bot.tree.command(name = "award", description = "Award a medal to a user")
@app_commands.choices(medal=[
	discord.app_commands.Choice(name='Order of hollo55', value = 1),
	discord.app_commands.Choice(name='Order of Nitro', value = 2),
	discord.app_commands.Choice(name='Official Medal of Clownery', value = 3),
    discord.app_commands.Choice(name='PCaS Veteran\' Award', value = 4),
    discord.app_commands.Choice(name='Winner of the PCaS Challenge (P2)', value = 5),
    discord.app_commands.Choice(name='Winner of the PCaS Challenge (P1)', value = 6),
    discord.app_commands.Choice(name='Merit', value = 7),
    discord.app_commands.Choice(name='Meritorious Merit of Meritness', value = 8),
    discord.app_commands.Choice(name='Medal of Conduct', value = 9),
    discord.app_commands.Choice(name='Medal of Activity', value = 10),
    discord.app_commands.Choice(name='Medal of Development Excellence', value = 11),
    discord.app_commands.Choice(name='Medal of Event Excellence', value = 12),
    discord.app_commands.Choice(name='Medal of Security Excellence', value = 13),
    discord.app_commands.Choice(name='Medal of Food Excellence', value = 14),
    discord.app_commands.Choice(name='Loser of the PCaS Challenge', value = 15)])
async def award(interaction: discord.Interaction, awardee: discord.Member, medal: discord.app_commands.Choice[int]):
    DB = shelve.open("Medals")
    try:
        awardeeID = str(awardee.id)
        DB[awardeeID]
    except:
        DB[awardeeID] = {}
    tempDict = DB[awardeeID]
    if medal.value in tempDict:
        medalAmount = tempDict[medal.value]
        tempDict[medal.value] = medalAmount + 1
    else:
        tempDict[medal.value] = 1
    DB[awardeeID] = tempDict
    #print(tempDict)
    DB.close()
    embed= discord.Embed(title="Awarded!", description=f"**{getMedal(medal.value)}** was awarded to {awardee.name}!", color=discord.Colour.green())
    await interaction.response.send_message(embed=embed)
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
            await interaction.response.send_message("User not found or the user has no medals.", ephemeral=True)
            return
        del DB[targetID]
        embed = discord.Embed(title="Success!", description=f"**{target.name} is cleared of medals.**", colour = discord.Colour.red())
        DB.close()
        await interaction.response.send_message(embed=embed)
        print("[Shelve] Deleted value")
    proceedButton.callback = proceedInteraction

    embed = discord.Embed(title="Halt!", description="This action will clear **ALL** user medals.\n__You cannot reverse it!__", colour=discord.Color.red())
    try:
        await interaction.response.send_message(embed=embed, view=view)
    except Exception as e:
        print(e)


@bot.tree.command(name = "seize", description="Take away a medal of a user")
@app_commands.choices(medal=[
	discord.app_commands.Choice(name='Order of hollo55', value = 1),
	discord.app_commands.Choice(name='Order of Nitro', value = 2),
	discord.app_commands.Choice(name='Official Medal of Clownery', value = 3),
    discord.app_commands.Choice(name='PCaS Veteran\' Award', value = 4),
    discord.app_commands.Choice(name='Winner of the PCaS Challenge (P2)', value = 5),
    discord.app_commands.Choice(name='Winner of the PCaS Challenge (P1)', value = 6),
    discord.app_commands.Choice(name='Merit', value = 7),
    discord.app_commands.Choice(name='Meritorious Merit of Meritness', value = 8),
    discord.app_commands.Choice(name='Medal of Conduct', value = 9),
    discord.app_commands.Choice(name='Medal of Activity', value = 10),
    discord.app_commands.Choice(name='Medal of Development Excellence', value = 11),
    discord.app_commands.Choice(name='Medal of Event Excellence', value = 12),
    discord.app_commands.Choice(name='Medal of Security Excellence', value = 13),
    discord.app_commands.Choice(name='Medal of Food Excellence', value = 14),
    discord.app_commands.Choice(name='Loser of the PCaS Challenge', value = 15)])
async def seize(interaction: discord.Interaction, target: discord.Member, medal: discord.app_commands.Choice[int]):
    DB = shelve.open("Medals")
    try:
        targetID = str(target.id)
        DB[targetID]
    except Exception as e:
        print(e)
        await interaction.response.send_message("User not found or the user has no medals.", ephemeral=True)
        return
    try:
        DB[targetID][medal.value]
    except:
       await interaction.response.send_message("Medal not found in user inventory.", ephemeral=True)
       return
    
    tempDict = DB[targetID]

    if tempDict[medal.value] > 1:
        medalAmount = tempDict[medal.value]
        tempDict[medal.value] = medalAmount - 1
    else:
        del tempDict[medal.value]

    embed = discord.Embed(title="Seized!", description=f"The **{getMedal(medal.value)}** was seized from {target.name}.\nOne medal was removed (more medals may remain).")
    DB[targetID] = tempDict
    print("[Shelve] Stored")
    await interaction.response.send_message(embed=embed)

bot.run(config['TOKEN'])