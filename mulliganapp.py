import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

intents = discord.Intents.all()
token = os.getenv('DC_JOLLIEB_TOKEN')
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    for each_server in bot.guilds:
        print(f"Bot is in server: {each_server.name} with ID: {each_server.id}")  
    print(f'We have logged in as {bot.user}')

class FeedbackModal(discord.ui.Modal, title="Please input how many counters."):
    counter_1k = discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 1000", required=False)
    counter_2k = discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 2000", required=False)
    counter_n = discord.ui.TextInput(style=discord.TextStyle.short, label="No Counter", required=False) 

    async def on_submit(self, interaction: discord.Interaction):
        # Process the values as needed. Here's an example message:
        feedback = (
            f"Counter 1000: {self.counter_1k.value or 'None'}\n"
            f"Counter 2000: {self.counter_2k.value or 'None'}\n"
            f"No Counter: {self.counter_n.value or 'None'}"
        )
        await interaction.response.send_message(feedback, ephemeral=True)

@bot.tree.command(name="build", description="Build your deck.")
async def build(interaction: discord.Interaction):
    buttonguide = discord.Embed(title="Mulligan Simulator", description="Please build your deck first given the options below.")
    myview = DeckButton()
    await interaction.response.send_message(embed=buttonguide, view=myview)

class MyButton(discord.ui.Button):
    def __init__(self, label, callback, style=discord.ButtonStyle.primary):
        super().__init__(label=label, style=style)
        self.custom_callback = callback

    async def callback(self, interaction:discord.Interaction):
        await self.custom_callback(interaction)

class DeckButton(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.character = []
        self.event = []
        self.stage = []
        self.add_item(MyButton(label="Character", callback=self.trigger_callback))
        self.add_item(MyButton(label="Event", callback=self.trigger_callback))
        self.add_item(MyButton(label="Stage", callback=self.trigger_callback))

    async def trigger_callback(self, interaction: discord.Interaction):
        trigger = TriggerButton()
        await interaction.response.edit_message(view=trigger)


class TriggerButton(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.add_item(MyButton(label="Has Trigger", callback=self.modal_callback))
        self.add_item(MyButton(label="No Trigger", callback=self.modal_callback))

    async def modal_callback(self, interaction: discord.Interaction):
        feedbackmodal = FeedbackModal()
        await interaction.response.send_modal(feedbackmodal)   


#class NumberSelectView(discord.ui.View):
#    def __init__(self):
#        super().__init__(timeout=None)
#        
#        # Generate options from 1 to 50
#        options = [discord.SelectOption(label=str(i), value=str(i)) for i in range(1, 26)]
#        
#        # Create the dropdown menu
#        self.select = discord.ui.Select(
#            placeholder="Select a number between 1 and 50...",
#            options=options,
#            min_values=1,
#            max_values=1  # Allow only single selection
#        )
#        
#        # Set callback for selection
#        self.select.callback = self.select_callback
#        self.add_item(self.select)
#
#    async def select_callback(self, interaction: discord.Interaction):
#        selected_value = self.select.values[0]  # Retrieve the selected value
#        await interaction.response.send_message(f"You selected number: {selected_value}", ephemeral=True)
#
## Command to trigger the number selection
#@bot.command(name="select_number")
#async def select_number(ctx):
#    view = NumberSelectView()
#    await ctx.send("Choose a number between 1 and 50:", view=view)

# Run the bot
bot.run(token)