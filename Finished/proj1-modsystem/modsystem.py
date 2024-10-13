import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from dotenv import load_dotenv
import os
import random
from pymongo import MongoClient
from dbmods import XP

load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")
mod_log = int(os.getenv("MOD_LOG_CH"))
seer_role = int(os.getenv("SEER_R_ID"))
drewph = int(os.getenv("DREWPH"))

intents = discord.Intents.all()
token = os.getenv('DC_DREWPH_TOKEN')
bot = commands.Bot(command_prefix="/", intents=intents)

def describe_member(command):
    return  app_commands.describe(member="Enter the member's username")(command)

@bot.event
async def on_ready():
    await bot.tree.sync()
    for each_server in bot.guilds:
        print(f"Bot is in server: {each_server.name} with ID: {each_server.id}")  
    print(f'We have logged in as {bot.user}')

#Working (Final)
@bot.tree.command(name="setxp", description="Set a user's XP by adding, removing or adjusting.")  # This is the slash command
@app_commands.describe(member="Enter the member's username",option="Choose an option from add/remove/adjust",amount="Enter the amount of XP.")
async def setxp(interaction: discord.Interaction, member:discord.Member, option:str, amount:int):
    user = XP(MongoClient(mongo_uri), member)
    if option == "add":
        final_xp = user.add(amount)
    elif option == "remove":
        final_xp = user.remove(amount)
    elif option == "adjust":
        final_xp = user.set(amount)
    else:
        final_xp = "This is not an option, please try again."
    await interaction.response.send_message(final_xp)

@bot.tree.command(name="viewxp", description="View a user's XP.")
@app_commands.describe(member="Enter the member's username")
async def view_xp(interaction: discord.Interaction, member:discord.Member):
    user = XP(MongoClient(mongo_uri), member)
    display_xp = user.view()
    await interaction.response.send_message(display_xp)

@bot.tree.command(name="reset", description="Resets a user's XP.")
@app_commands.describe(member="Enter the member's username")
async def reset(interaction: discord.Interaction, member:discord.Member):
    user = XP(MongoClient(mongo_uri), member)
    resetted_xp = user.reset()
    await interaction.response.send_message(resetted_xp)

# Working (Concept Only)
class Menu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.member = None

    @discord.ui.select(cls=discord.ui.UserSelect,placeholder="Choose a mod")
    async def select_callback(self, interaction:discord.Interaction, select:discord.ui.UserSelect):
        selected_user = select.values[0]

        embed = interaction.message.embeds[0]
        embed.add_field(name="2 Points",value="- Incorrect Response\n- Deletion of Messages\n- No Response\n- No Response on Ticket (during shift)\n- Not Attending Project Meetings\n- Toolbox Call Absent\n- Toolbox Open Camera Policy\n- Toolbox No Response\n- Toolbox Unpreparedness\n- No message within an hour")
        embed.add_field(name="1 Points",value="- No Response on Ticket (during shift)\n- Late Response\n- Sentence Grammar\n- Failure to Delete Bot/Spam Messages\n- No Daily Sentiment\n- No Acknowledgment\n- Toolbox Tardiness\n- Toolbox Inappropriate Filters\n- Less than 5 messages within an hour")
        message_id = interaction.message.id
        new_view = DeductMenu(selected_user, message_id)
        await interaction.response.edit_message(embed=embed, view=new_view)
    
class DeductMenu(discord.ui.View):
    def __init__(self, user:discord.Member, m_id:int):
        super().__init__(timeout=0)
        self.discorduser = user
        self.message_id = m_id

#region
    @discord.ui.select(placeholder="Select a reason..", options=[
        discord.SelectOption(label="Incorrect Response",value="1"),
        discord.SelectOption(label="Deletion of Messages",value="2"),
        discord.SelectOption(label="No Response",value="3"),
        discord.SelectOption(label="No Response on Ticket (during shift)",value="4"),
        discord.SelectOption(label="Not Attending Project Meetings",value="5"),
        discord.SelectOption(label="Toolbox Call Absent",value="6"),
        discord.SelectOption(label="Toolbox Open Camera Policy",value="7"),
        discord.SelectOption(label="Toolbox No Response",value="8"),
        discord.SelectOption(label="Toolbox Unpreparedness",value="9"),
        discord.SelectOption(label="No Message Within an Hour",value="10"),
        discord.SelectOption(label="No Response on Ticket (next shift)",value="11"),
        discord.SelectOption(label="Late Response",value="12"),
        discord.SelectOption(label="Sentence Grammar",value="-13"),
        discord.SelectOption(label="Failure to Delete Bot/Spam Messages",value="14"),
        discord.SelectOption(label="No Daily Sentiment",value="15"),
        discord.SelectOption(label="No Acknowledgment",value="16"),
        discord.SelectOption(label="Toolbox Tardiness",value="17"),
        discord.SelectOption(label="Toolbox Inappropriate Filters",value="18"),
        discord.SelectOption(label="Less than ５ Messages Within an Hour",value="19")])
#endregion      
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        selected_value = select.values[0]
        selected_label = None
        for option in select.options:
            if option.value == selected_value:
                selected_label = option.label  # Correctly access the label of the selected option
                break
        int_value = int(selected_value)
        if int_value < 11:
            number = 2
        else:
            number = 1
        embed = discord.Embed(title="One last step...", description="Before points are deducted, please send your screenshots/s here as proof.")
        embed.set_thumbnail(url="https://64.media.tumblr.com/737385756eccd5864afd59f7e3a7990f/57a6e5a7915180f3-da/s540x810/530011bac77f7e627e15bbbefd4fe7d98f56491a.gif")
        await interaction.response.defer()
        await interaction.followup.edit_message(message_id=self.message_id, embed=embed,view=None)
        def check(m: discord.Message):
                return (
                    len(m.attachments) > 0 
                    and m.author == interaction.user
                    and m.channel == interaction.channel
                )
        tries = 0
        while True:
            try:
                message = await bot.wait_for('message',check=check,timeout=120)
                if message.content == "":
                    user = XP(MongoClient(mongo_uri), self.discorduser)
                    user.remove(number)
                    await interaction.followup.send(f"Deducted {number} point/s for {self.discorduser.name}. Reason: {selected_label}")
                    break
                elif tries < 3:
                    await message.delete()
                    await interaction.followup.send("Error: Text found. Please only send your attached screenshot/s.", ephemeral=True)
                    tries += 1
                else:
                    await message.delete()
                    await interaction.followup.send("Please use the command again and send only attached file/s.", ephemeral=True)
                    break
            except asyncio.TimeoutError:
                await interaction.followup.send("Time has run out. Please try the XP system again and prepare your files.", ephemeral=True)
                break

@bot.tree.command(name="xp", description="Uses XP system.")
async def xp(interaction: discord.Interaction):
    view = Menu()
    embed = discord.Embed(title="__Welcome to the XP System__",description="Please select a mod to be monitored, deduct points based on the given reason, and prepare the screenshot/s as proof.")
    embed.set_thumbnail(url="https://64.media.tumblr.com/737385756eccd5864afd59f7e3a7990f/57a6e5a7915180f3-da/s540x810/530011bac77f7e627e15bbbefd4fe7d98f56491a.gif")
    await interaction.response.send_message(view=view, embed=embed,ephemeral=True)

@bot.command()
async def modmessage(user:discord.Member, channel:discord.TextChannel):
    gif_list = [
        "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/3bfbc20fdd9ba64568289b6fbac9674ea678ee61-512x512.gif",
        "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExd21ucDQxYTQ0ZjRkYXZtcnliNW15ODFoeXVmZzg2Y3FpdTJuMndwaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/M51FEiXf0rhmSQekQN/giphy.gif",
        "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHQ0dmpkMTJ1emVlaGlkMGliNGNvczI4anQycTF1ZzJ1Mnh2eHRubCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/oMcYsUwreNw2l4KpSl/giphy.gif",
        "https://media.tenor.com/tvU7M82-ar8AAAAi/leona-legends-of-runeterra.gif"
    ]
    chosen_gif = random.choice(gif_list)
    embed = discord.Embed(title=f"Welcome, {user.display_name}",description="This is a designated channel to monitor your own performance through XPs. Please take note that all commendations and violations will also be notified here.", color=0x2c2c2c)
    embed.set_thumbnail(url=chosen_gif)
    await channel.send(embed=embed)

# Working (Concept Only)
# Issue: if there's a (.) in a user.name, it can create duplicate channels.
async def welcomemod(interaction: discord.Interaction, user:discord.Member):
    guild = interaction.guild
    channel_name = f"room-{user.name}"
    category = guild.get_channel(mod_log) # MOD LOG in dummy server
    admin_role = guild.get_role(seer_role) # Seer Role ID
    existing_channel = discord.utils.get(category.text_channels, name=channel_name)
    if not existing_channel:
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Deny access to everyone
            user: discord.PermissionOverwrite(view_channel=True,read_message_history=True,send_messages=False),  # Allow access to the specified user
            admin_role: discord.PermissionOverwrite(administrator=True)
        }

        for member in guild.members:
            if admin_role in member.roles:
                overwrites[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        new_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await modmessage(user, new_channel)
        await interaction.followup.send(f"Channel {channel_name} created.",ephemeral=True)
    else:
        await interaction.followup.send(f"Channel {channel_name} already exists.",ephemeral=True)

# Working (Final)
@bot.tree.command(name="leaderboard",description="Shows all the mod's leaderboard for added XPs.")
async def leaderboard(interaction:discord.Interaction):
    user = XP(MongoClient(mongo_uri))
    handles = user.sort_winners("a")
    xps = user.sort_winners("b")
    strhandles = ""
    count = 0
    for each_h in handles:
        strhandles += "{}{}\n".format("🥇 " if count == 0 else "🥈 " if count == 1 else "🥉 " if count == 2 else "", each_h)
        count += 1
    
    strxps = ""
    for each_xp in xps:
        strxps += "`{}`\n".format(each_xp)

    embed = discord.Embed(title="Leaderboard", description="*Here are the results of all moderators who have earned points* **:**")
    embed.add_field(name="__Name__",value=strhandles)
    embed.add_field(name="__Added XPs__",value=strxps)
    embed.set_thumbnail(url="https://media.tenor.com/el3gs-lJ5f0AAAAM/karen-run.gif")
    await interaction.response.send_message(embed=embed)

#Working (Final)
class VerifyMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="Proceed",style=discord.ButtonStyle.green)
    async def proceed(self, interaction: discord.Interaction, button:discord.ui.Button):
        user = XP(MongoClient(mongo_uri), interaction.user)
        user.register() #registers user to database
        await interaction.response.defer(thinking=True, ephemeral=True) #allows to think
        await welcomemod(interaction, interaction.user)

#Working (Final)
@bot.command()
@commands.check(lambda ctx: ctx.author.id == drewph)
async def verify(ctx):
    embed = discord.Embed(title="Create your own log!",description="By clicking the button below, you are sharing your Discord username to get access for certain channels within this server. **Always be careful for any FAKE messages or redirects.**",color=0xfcbf00)
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/416/416227.png")
    view = VerifyMenu()
    view.add_item(discord.ui.Button(label="Author", style=discord.ButtonStyle.link, url="https://github.com/imjakeym8"))
    await ctx.send(embed=embed,view=view)

@verify.error
async def verify_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        print(f"{ctx.author} does not have permissions to use /verify.")

bot.run(token)