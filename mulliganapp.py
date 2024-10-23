import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import mulligan

load_dotenv()
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
    buttonguide = EmbedGuide()
    myview = DeckButton()
    await interaction.response.send_message(embed=buttonguide, view=myview,ephemeral=True)

class EmbedGuide(discord.Embed):
    def __init__(self, title="Deck Builder", description="Please build your deck first given the options below."):
        super().__init__(title=title,description=description)

class MyButton(discord.ui.Button):
    def __init__(self, label, callback, style=discord.ButtonStyle.primary):
        super().__init__(label=label, style=style)
        self.custom_callback = callback

    async def callback(self, interaction:discord.Interaction):
        await self.custom_callback(interaction)

class FinalButton(discord.ui.Button):
    def __init__(self, callback, label, style=discord.ButtonStyle.success):
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
        self.sum = None
        self.ratios = None
        for text_input in self.text_inputs:
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        answers = [ text_input.value for text_input in self.text_inputs ]
    
        if getattr(self, 'update_character', False):
            self.parent_view.character.extend([cardtype.C1T] * int(answers[0]))
            self.parent_view.character.extend([cardtype.C2T] * int(answers[1]))
            self.parent_view.character.extend([cardtype.CT] * int(answers[2]))
            # print(self.parent_view.character)
        elif getattr(self, 'update_characternt', False):
            self.parent_view.character.extend([cardtype.C1] * int(answers[0]))
            self.parent_view.character.extend([cardtype.C2] * int(answers[1]))
            self.parent_view.character.extend([cardtype.C] * int(answers[2]))
            # print(self.parent_view.character)
        elif getattr(self, 'update_event', False):  
            self.parent_view.event.extend([cardtype.E1T] * int(answers[0]))
            self.parent_view.event.extend([cardtype.E2T] * int(answers[1]))
            self.parent_view.event.extend([cardtype.E3T] * int(answers[2]))
            self.parent_view.event.extend([cardtype.E4T] * int(answers[3]))
            self.parent_view.event.extend([cardtype.ET] * int(answers[4]))
            # print(self.parent_view.event)
        elif getattr(self, 'update_eventnt', False):  
            self.parent_view.event.extend([cardtype.E1] * int(answers[0]))
            self.parent_view.event.extend([cardtype.E2] * int(answers[1]))
            self.parent_view.event.extend([cardtype.E3] * int(answers[2]))
            self.parent_view.event.extend([cardtype.E4] * int(answers[3]))
            self.parent_view.event.extend([cardtype.E] * int(answers[4]))
            # print(self.parent_view.event)
        elif getattr(self, 'update_stage', False):
            self.parent_view.stage.extend([cardtype.ST] * int(answers[0]))
            # print(self.parent_view.stage)
        elif getattr(self, 'update_stagent', False):
            self.parent_view.stage.extend([cardtype.S] * int(answers[0]))
            # print(self.parent_view.stage)
        else:
            await interaction.followup.send("An error occured.")

        # Totals the currently added cards on submit.
        self.sum = self.parent_view.character + self.parent_view.event + self.parent_view.stage

        if len(self.sum) == 50:
            embed = EmbedGuide(description="Congratulations, you've now built your deck. Press `Save` to register your deck or `Stats` to check your deck's stats.")
            embed.add_field(name="Characters",value=str(len(self.parent_view.character)))
            embed.add_field(name="Events",value=str(len(self.parent_view.event)))
            embed.add_field(name="Stages",value=str(len(self.parent_view.stage)))
            embed.set_footer(text="Credits: https://github.com/imjakeym8",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTvgBPvdDUKd0ffWXnQKSuyyYNGy1Sxa-DAmA&s")
            self.parent_view.clear_items()
            self.parent_view.add_item(FinalButton(label="Save",callback=self.save_callback))
            self.parent_view.add_item(FinalButton(label="Stats",callback=self.checkstats))
        else:
            embed = EmbedGuide()
            embed.add_field(name="Characters",value=str(len(self.parent_view.character)))
            embed.add_field(name="Events",value=str(len(self.parent_view.event)))
            embed.add_field(name="Stages",value=str(len(self.parent_view.stage)))

        await interaction.edit_original_response(embed=embed,view=self.parent_view)

    async def checkstats(self, interaction:discord.Interaction):
        # Calculate percentage of bricks, counters 1k, counter 2k, counters inc. events, event counters, triggers.
        await interaction.response.defer()
        brick_list = [ each["counter"] for each in self.sum if each["counter"] < 1000 ]
        counter_list = [ each["counter"] for each in self.sum if each["counter"] >= 1000 ]
        counter1k_list = [ each["counter"] for each in self.sum if each["counter"] == 1000 and each["type"] == "character" ]
        counter2k_list = [ each["counter"] for each in self.sum if each["counter"] == 2000 and each["type"] == "character" ]
        event_list = [ each["counter"] for each in self.sum if each["counter"] >= 2000 and each["type"] == "event"]
        trigger_list = [ each["trigger"] for each in self.sum if each["trigger"] is True]

        brick_ratio = len(brick_list) / 50 * 100 if brick_list != [] else 0
        counter_ratio = len(counter_list) / 50 * 100 if counter_list != [] else 0
        counter1k_ratio = len(counter1k_list) / 50 * 100 if counter1k_list != [] else 0
        counter2k_ratio = len(counter2k_list) / 50 * 100 if counter2k_list != [] else 0
        event_ratio = len(event_list) / 50 * 100 if event_list != [] else 0      
        trigger_ratio = len(trigger_list) / 50 * 100 if trigger_list != [] else 0
        
        self.ratios = [
            {"category": "Bricks", "ratio": brick_ratio, "count": len(brick_list)},
            {"category": "1000 Counters", "ratio": counter1k_ratio, "count": len(counter1k_list)},
            {"category": "2000 Counters", "ratio": counter2k_ratio, "count": len(counter2k_list)},
            {"category": "Event Counters", "ratio": event_ratio, "count": len(event_list)},
            {"category": "Total Counters", "ratio": counter_ratio, "count": len(counter_list)},
            {"category": "Triggers", "ratio": trigger_ratio, "count": len(trigger_list)},
        ]

        embed = EmbedGuide(description="Here are your deck's stats.\n\nPress `Save` to register your deck.")
        embed.add_field(name="Characters",value=str(len(self.parent_view.character)))
        embed.add_field(name="Events",value=str(len(self.parent_view.event)))
        embed.add_field(name="Stages",value=str(len(self.parent_view.stage)))
        embed.add_field(name="Bricks",value=f"{int(brick_ratio)} % ({len(brick_list)} out of 50 cards)",inline=False)
        embed.add_field(name="1000 Counters",value=f"{int(counter1k_ratio)} % ({len(counter1k_list)} out of 50 cards)",inline=False)
        embed.add_field(name="2000 Counters",value=f"{int(counter2k_ratio)} % ({len(counter2k_list)} out of 50 cards)",inline=False)
        embed.add_field(name="Event Counters",value=f"{int(event_ratio)} % ({len(event_list)} out of 50 cards)",inline=False)
        embed.add_field(name="Total Counters",value=f"{int(counter_ratio)} % ({len(counter_list)} out of 50 cards)",inline=False)
        embed.add_field(name="Triggers",value=f"{int(trigger_ratio)} % ({len(trigger_list)} out of 50 cards)",inline=False)
        embed.set_footer(text="Credits: https://github.com/imjakeym8",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTvgBPvdDUKd0ffWXnQKSuyyYNGy1Sxa-DAmA&s")

        await interaction.edit_original_response(embed=embed,view=self.parent_view)

    async def savestats(self):
        # Calculate statistics without interacting with the Discord API
        brick_list = [each["counter"] for each in self.sum if each["counter"] < 1000]
        counter_list = [each["counter"] for each in self.sum if each["counter"] >= 1000]
        counter1k_list = [each["counter"] for each in self.sum if each["counter"] == 1000 and each["type"] == "character"]
        counter2k_list = [each["counter"] for each in self.sum if each["counter"] == 2000 and each["type"] == "character"]
        event_list = [each["counter"] for each in self.sum if each["counter"] >= 2000 and each["type"] == "event"]
        trigger_list = [each["trigger"] for each in self.sum if each["trigger"] is True]

        # Calculate ratios
        brick_ratio = len(brick_list) / 50 * 100 if brick_list else 0
        counter_ratio = len(counter_list) / 50 * 100 if counter_list else 0
        counter1k_ratio = len(counter1k_list) / 50 * 100 if counter1k_list else 0
        counter2k_ratio = len(counter2k_list) / 50 * 100 if counter2k_list else 0
        event_ratio = len(event_list) / 50 * 100 if event_list else 0      
        trigger_ratio = len(trigger_list) / 50 * 100 if trigger_list else 0

        # Store ratios in a list of dictionaries
        self.ratios = [
            {"category": "Bricks", "ratio": brick_ratio, "count": len(brick_list)},
            {"category": "1000 Counters", "ratio": counter1k_ratio, "count": len(counter1k_list)},
            {"category": "2000 Counters", "ratio": counter2k_ratio, "count": len(counter2k_list)},
            {"category": "Event Counters", "ratio": event_ratio, "count": len(event_list)},
            {"category": "Total Counters", "ratio": counter_ratio, "count": len(counter_list)},
            {"category": "Triggers", "ratio": trigger_ratio, "count": len(trigger_list)},
        ]

    async def save_callback(self, interaction:discord.Interaction):
        await interaction.response.defer()
        
        if self.ratios is None:
            await self.savestats()

        from pymongo import MongoClient
        client = MongoClient(local_uri)
        db = client.mulligan
        coll = db.decks

        try:
            int_uid = str(interaction.user.id)
            ans = coll.find_one({"uid": int_uid},{"_id": 0})
            deck_data = {
                "uid": int_uid,
                "deck": self.sum,
                "stats": self.ratios
            }
            if ans is None:
                coll.insert_one(deck_data)
                # print("Added.")
                await interaction.followup.send("Deck saved successfully!", ephemeral=True)
            else:
                coll.update_one({"uid": int_uid}, {"$set": deck_data})
                await interaction.followup.send("Deck updated successfully!", ephemeral=True)
        
        except Exception as e:
            print(f"An error occured: {e}")

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

@bot.command()
async def mulligan(ctx):
    pass

bot.run(token)