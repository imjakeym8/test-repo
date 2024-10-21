import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from pymongo import MongoClient

import mulligan

intents = discord.Intents.all()
token = os.getenv('DC_JOLLIEB_TOKEN')
local_uri = os.getenv('MONGODB_LOCAL_URI')
bot = commands.Bot(command_prefix="/", intents=intents)

cardtype = mulligan.Card()

@bot.event
async def on_ready():
    await bot.tree.sync()
    for each_server in bot.guilds:
        print(f"Bot is in server: {each_server.name} with ID: {each_server.id}")  
    print(f'We have logged in as {bot.user}')

@bot.tree.command(name="build", description="Build your deck.")
async def build(interaction: discord.Interaction):
    buttonguide = discord.Embed(title="Mulligan Simulator", description="Please build your deck first given the options below.")
    myview = DeckButton()
    await interaction.response.send_message(embed=buttonguide, view=myview)

class EmbedGuide(discord.Embed):
    def __init__(self, title="Mulligan Simulator", description="Please build your deck first given the options below."):
        super().__init__(title=title,description=description)


class MyButton(discord.ui.Button):
    def __init__(self, label, callback, style=discord.ButtonStyle.primary):
        super().__init__(label=label, style=style)
        self.custom_callback = callback

    async def callback(self, interaction:discord.Interaction):
        await self.custom_callback(interaction)

class FinalButton(discord.ui.Button):
    def __init__(self, callback, label="Save", style=discord.ButtonStyle.success):
        super().__init__(label=label, style=style)
        self.custom_callback = callback

    async def callback(self, interaction:discord.Interaction):
        await self.custom_callback(interaction)

class TriggerButton(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)

class FeedbackModal(discord.ui.Modal):
    def __init__(self, title="Please input how many cards are included.", text_inputs: list[discord.ui.TextInput] = None, parent_view = None):
        super().__init__(title=title)
        self.text_inputs = text_inputs if text_inputs else []
        self.parent_view = parent_view if parent_view else None
        self.sum = [ parent_view.character + parent_view.event + parent_view.stage if parent_view else None ]
        for text_input in self.text_inputs:
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        answers = [ text_input.value for text_input in self.text_inputs ]
    
        if getattr(self, 'update_character', False):
            self.parent_view.character.extend([cardtype.C1T] * int(answers[0]))
            self.parent_view.character.extend([cardtype.C2T] * int(answers[1]))
            self.parent_view.character.extend([cardtype.CT] * int(answers[2]))
            print(self.parent_view.character)
        elif getattr(self, 'update_characternt', False):
            self.parent_view.character.extend([cardtype.C1] * int(answers[0]))
            self.parent_view.character.extend([cardtype.C2] * int(answers[1]))
            self.parent_view.character.extend([cardtype.C] * int(answers[2]))
            print(self.parent_view.character)
        elif getattr(self, 'update_event', False):  
            self.parent_view.event.extend([cardtype.E1T] * int(answers[0]))
            self.parent_view.event.extend([cardtype.E2T] * int(answers[1]))
            self.parent_view.event.extend([cardtype.E3T] * int(answers[2]))
            self.parent_view.event.extend([cardtype.E4T] * int(answers[3]))
            self.parent_view.event.extend([cardtype.ET] * int(answers[4]))
            print(self.parent_view.event)
        elif getattr(self, 'update_eventnt', False):  
            self.parent_view.event.extend([cardtype.E1] * int(answers[0]))
            self.parent_view.event.extend([cardtype.E2] * int(answers[1]))
            self.parent_view.event.extend([cardtype.E3] * int(answers[2]))
            self.parent_view.event.extend([cardtype.E4] * int(answers[3]))
            self.parent_view.event.extend([cardtype.E] * int(answers[4]))
            print(self.parent_view.event)
        elif getattr(self, 'update_stage', False):
            self.parent_view.stage.extend([cardtype.ST] * int(answers[0]))
            print(self.parent_view.stage)
        elif getattr(self, 'update_stagent', False):
            self.parent_view.stage.extend([cardtype.S] * int(answers[0]))
            print(self.parent_view.stage)

        embed = EmbedGuide()
        embed.add_field(name="Characters",value=str(len(self.parent_view.character)))
        embed.add_field(name="Events",value=str(len(self.parent_view.event)))
        embed.add_field(name="Stages",value=str(len(self.parent_view.stage)))

        sum = len(self.parent_view.character) + len(self.parent_view.event) + len(self.parent_view.stage)
        if sum == 50:
            self.parent_view.add_item(FinalButton(callback=self.save_callback))
        await interaction.edit_original_response(embed=embed,view=self.parent_view)

    async def save_callback(self, interaction:discord.Interaction):
        await interaction.response.defer()
        client = MongoClient(local_uri)
        db = client.mulligan
        coll = db.decks
        print(self.sum)
        try:
            ans = coll.find_one({"uid":discord.Interaction.user.id},{"_id":0})
            if ans is None:
                coll.insert_one({{"uid":discord.Interaction.user.id},{"deck":self.sum}})
                print("Added.")
                await interaction.followup.send("Done!")
        except Exception as e:
            return f"An error occured: {e}"         

class DeckButton(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.character = []
        self.event = []
        self.stage = []
        self.add_item(MyButton(label="Character", callback=self.ctrigger_callback))
        self.add_item(MyButton(label="Event", callback=self.etrigger_callback))
        self.add_item(MyButton(label="Stage", callback=self.strigger_callback))

    def generate_cmodal_text_inputs(self):
        return [
            discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 1000", default="0", required=False),
            discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 2000", default="0", required=False),
            discord.ui.TextInput(style=discord.TextStyle.short, label="No Counter", default="0", required=False)
        ]

    def generate_emodal_text_inputs(self):
        return [
            discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 1000", default="0", required=False),
            discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 2000", default="0", required=False),
            discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 3000", default="0", required=False),
            discord.ui.TextInput(style=discord.TextStyle.short, label="Counter: 4000", default="0", required=False),
            discord.ui.TextInput(style=discord.TextStyle.short, label="No Counter", default="0", required=False)
        ]

    async def ctrigger_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        trigger = TriggerButton()
        trigger.add_item(MyButton(label="Has Trigger", callback=self.cmodal_callback))
        trigger.add_item(MyButton(label="No Trigger", callback=self.cntmodal_callback))
        trigger.add_item(MyButton(label="Back", callback=self.back_callback))
        await interaction.edit_original_response(view=trigger)
    
    async def etrigger_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        trigger = TriggerButton()
        trigger.add_item(MyButton(label="Has Trigger", callback=self.emodal_callback))
        trigger.add_item(MyButton(label="No Trigger", callback=self.entmodal_callback))
        trigger.add_item(MyButton(label="Back", callback=self.back_callback))
        await interaction.edit_original_response(view=trigger)   

    async def strigger_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        trigger = TriggerButton()
        trigger.add_item(MyButton(label="Has Trigger", callback=self.smodal_callback))
        trigger.add_item(MyButton(label="No Trigger", callback=self.sntmodal_callback))
        trigger.add_item(MyButton(label="Back", callback=self.back_callback))
        await interaction.edit_original_response(view=trigger)
    
    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(view=self)

    async def cmodal_callback(self, interaction: discord.Interaction):
        text_inputs = self.generate_cmodal_text_inputs()
        feedbackmodal = FeedbackModal(text_inputs=text_inputs, parent_view=self)
        feedbackmodal.update_character = True
        await interaction.response.send_modal(feedbackmodal)
    
    async def cntmodal_callback(self, interaction: discord.Interaction):
        text_inputs = self.generate_cmodal_text_inputs()
        feedbackmodal = FeedbackModal(text_inputs=text_inputs, parent_view=self)
        feedbackmodal.update_characternt = True
        await interaction.response.send_modal(feedbackmodal)

    async def emodal_callback(self, interaction: discord.Interaction):
        text_inputs = self.generate_emodal_text_inputs()
        feedbackmodal = FeedbackModal(text_inputs=text_inputs, parent_view=self)
        feedbackmodal.update_event = True
        await interaction.response.send_modal(feedbackmodal)

    async def entmodal_callback(self, interaction: discord.Interaction):
        text_inputs = self.generate_emodal_text_inputs()
        feedbackmodal = FeedbackModal(text_inputs=text_inputs, parent_view=self)
        feedbackmodal.update_eventnt = True
        await interaction.response.send_modal(feedbackmodal)
    
    async def smodal_callback(self, interaction: discord.Interaction):
        text_inputs = [
            discord.ui.TextInput(style=discord.TextStyle.short, label="No Counter", default="0", required=False)
        ]
        feedbackmodal = FeedbackModal(text_inputs=text_inputs, parent_view=self)
        feedbackmodal.update_stage = True
        await interaction.response.send_modal(feedbackmodal)

    async def sntmodal_callback(self, interaction: discord.Interaction):
        text_inputs = [
            discord.ui.TextInput(style=discord.TextStyle.short, label="No Counter", default="0", required=False)
        ]
        feedbackmodal = FeedbackModal(text_inputs=text_inputs, parent_view=self)
        feedbackmodal.update_stagent = True
        await interaction.response.send_modal(feedbackmodal)

#    async def on_submit(self, interaction: discord.Interaction):
#        # Process the values as needed. Here's an example message:
#        feedback = (
#            f"Counter 1000: {self.counter_1k.value or 'None'}\n"
#            f"Counter 2000: {self.counter_2k.value or 'None'}\n"
#            f"No Counter: {self.counter_n.value or 'None'}"
#        )
#        await interaction.response.send_message(feedback, ephemeral=True)
#
#        if counter_1k is not None:
#
#        if counter_2k is not None:
#        if counter_n is not None:

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