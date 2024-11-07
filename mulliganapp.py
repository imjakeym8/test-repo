import discord
from discord import app_commands
from discord.ext import commands
import os
from discord.utils import MISSING
from dotenv import load_dotenv
import mulligan as mg

load_dotenv()
intents = discord.Intents.all()
token = os.getenv('DC_JOLLIEB_TOKEN')
local_uri = os.getenv('MONGODB_LOCAL_URI')
bot = commands.Bot(command_prefix="/", intents=intents)

cardtype = mg.Card()

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
        await interaction.response.defer(ephemeral=True)
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
        await interaction.response.defer(ephemeral=True)
        brick_list = [ each["counter"] for each in self.sum if each["counter"] < 1000 ]
        counter_list = [ each["counter"] for each in self.sum if each["counter"] >= 1000 ]
        counter1k_list = [ each["counter"] for each in self.sum if each["counter"] == 1000 and each["type"] == "character" ]
        counter2k_list = [ each["counter"] for each in self.sum if each["counter"] == 2000 and each["type"] == "character" ]
        event_list = [ each["counter"] for each in self.sum if each["counter"] >= 2000 and each["type"] == "event"]
        trigger_list = [ each["trigger"] for each in self.sum if each["trigger"] is True]

        character_count = len(self.parent_view.character)
        event_count = len(self.parent_view.event)
        stage_count = len(self.parent_view.stage)
        character_ratio = character_count / 50 * 100 if self.parent_view.character != [] else 0
        event_ratio = event_count / 50 * 100 if self.parent_view.event != [] else 0
        stage_ratio = stage_count / 50 * 100 if self.parent_view.stage != [] else 0
        brick_ratio = len(brick_list) / 50 * 100 if brick_list != [] else 0
        counter_ratio = len(counter_list) / 50 * 100 if counter_list != [] else 0
        counter1k_ratio = len(counter1k_list) / 50 * 100 if counter1k_list != [] else 0
        counter2k_ratio = len(counter2k_list) / 50 * 100 if counter2k_list != [] else 0
        counterevent_ratio = len(event_list) / 50 * 100 if event_list != [] else 0      
        trigger_ratio = len(trigger_list) / 50 * 100 if trigger_list != [] else 0
        
        self.ratios = [
            {"type": "character", "ratio": character_ratio ,"count": character_count},
            {"type": "event", "ratio": event_ratio,"count": event_count},
            {"type": "stage", "ratio": stage_ratio,"count": stage_count},
            {"category": "Bricks", "ratio": brick_ratio, "count": len(brick_list)},
            {"category": "1000 Counters", "ratio": counter1k_ratio, "count": len(counter1k_list)},
            {"category": "2000 Counters", "ratio": counter2k_ratio, "count": len(counter2k_list)},
            {"category": "Event Counters", "ratio": counterevent_ratio, "count": len(event_list)},
            {"category": "Total Counters", "ratio": counter_ratio, "count": len(counter_list)},
            {"category": "Triggers", "ratio": trigger_ratio, "count": len(trigger_list)},
        ]

        embed = EmbedGuide(description="Here are your deck's stats.\n\nPress `Save` to register your deck.")
        embed.add_field(name="Characters",value=f"{character_count}")
        embed.add_field(name="Events",value=f"{event_count}")
        embed.add_field(name="Stages",value=f"{stage_count}")
        embed.add_field(name="Bricks",value=f"{int(brick_ratio)} % ({len(brick_list)} out of 50 cards)",inline=False)
        embed.add_field(name="1000 Counters",value=f"{int(counter1k_ratio)} % ({len(counter1k_list)} out of 50 cards)",inline=False)
        embed.add_field(name="2000 Counters",value=f"{int(counter2k_ratio)} % ({len(counter2k_list)} out of 50 cards)",inline=False)
        embed.add_field(name="Event Counters",value=f"{int(counterevent_ratio)} % ({len(event_list)} out of 50 cards)",inline=False)
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
        character_count = len(self.parent_view.character)
        event_count = len(self.parent_view.event)
        stage_count = len(self.parent_view.stage)
        character_ratio = character_count / 50 * 100 if self.parent_view.character != [] else 0
        event_ratio = event_count / 50 * 100 if self.parent_view.event != [] else 0
        stage_ratio = stage_count / 50 * 100 if self.parent_view.stage != [] else 0
        brick_ratio = len(brick_list) / 50 * 100 if brick_list else 0
        counter_ratio = len(counter_list) / 50 * 100 if counter_list else 0
        counter1k_ratio = len(counter1k_list) / 50 * 100 if counter1k_list else 0
        counter2k_ratio = len(counter2k_list) / 50 * 100 if counter2k_list else 0
        counterevent_ratio = len(event_list) / 50 * 100 if event_list else 0      
        trigger_ratio = len(trigger_list) / 50 * 100 if trigger_list else 0

        # Store ratios in a list of dictionaries
        self.ratios = [
            {"type": "character", "ratio": character_ratio ,"count": character_count},
            {"type": "event", "ratio": event_ratio,"count": event_count},
            {"type": "stage", "ratio": stage_ratio,"count": stage_count},
            {"category": "Bricks", "ratio": brick_ratio, "count": len(brick_list)},
            {"category": "1000 Counters", "ratio": counter1k_ratio, "count": len(counter1k_list)},
            {"category": "2000 Counters", "ratio": counter2k_ratio, "count": len(counter2k_list)},
            {"category": "Event Counters", "ratio": counterevent_ratio, "count": len(event_list)},
            {"category": "Total Counters", "ratio": counter_ratio, "count": len(counter_list)},
            {"category": "Triggers", "ratio": trigger_ratio, "count": len(trigger_list)},
        ]

    async def save_callback(self, interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
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
        await interaction.response.defer(ephemeral=True)
        trigger = TriggerButton()
        trigger.add_item(MyButton(label="Has Trigger", callback=self.cmodal_callback))
        trigger.add_item(MyButton(label="No Trigger", callback=self.cntmodal_callback))
        trigger.add_item(MyButton(label="Back", callback=self.back_callback))
        await interaction.edit_original_response(view=trigger)
    
    async def etrigger_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        trigger = TriggerButton()
        trigger.add_item(MyButton(label="Has Trigger", callback=self.emodal_callback))
        trigger.add_item(MyButton(label="No Trigger", callback=self.entmodal_callback))
        trigger.add_item(MyButton(label="Back", callback=self.back_callback))
        await interaction.edit_original_response(view=trigger)   

    async def strigger_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        trigger = TriggerButton()
        trigger.add_item(MyButton(label="Has Trigger", callback=self.smodal_callback))
        trigger.add_item(MyButton(label="No Trigger", callback=self.sntmodal_callback))
        trigger.add_item(MyButton(label="Back", callback=self.back_callback))
        await interaction.edit_original_response(view=trigger)
    
    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
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

@bot.tree.command(name="mulligan", description="Test your deck real-time for mulligans, triggers, and draw odds.")
async def mulligan(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    from pymongo import MongoClient
    client = MongoClient(local_uri)
    db = client.mulligan
    coll = db.decks

    doc = coll.find_one({"uid":str(interaction.user.id)},{"_id":0})
    deck = doc["deck"]
    deckstats = doc["stats"]
    my_deck = mg.Deck(cards=deck, stats=deckstats) # for using Deck functions

    class LifeCount(discord.ui.Modal):
        def __init__(self, title="Please input how many cards to add to life."):
            super().__init__(title=title)
            self.add_item(discord.ui.TextInput(style=discord.TextStyle.short, label="Life"))

        async def on_submit(self, interaction: discord.Interaction):
            try:
                life = int(self.children[0].value)

                my_deck.draw_five(option=True)
                my_deck.add_life(life) # maybe assign the value?

                view = SimView()
                await interaction.response.edit_message(embed=view.embed,view=view)
            except ValueError:
                await interaction.response.send_message(f"Please input a number.", ephemeral=True)

    class SimView(discord.ui.View):
        def __init__(self, timeout=180):
            super().__init__(timeout=timeout)
            self.embed = discord.Embed(title="It's your turn. Select a few options below.", description=self.check_hand())
            self.select = discord.ui.Select(placeholder="Play from your hand here..",options=[])

            self.add_item(MyButton(label="Draw", style=discord.ButtonStyle.blurple, callback=self.draw))
            self.add_item(MyButton(label="Play", style=discord.ButtonStyle.success, callback=self.play))

        def check_hand(self):
            hand = "**Hand:**\n"
            for each_card in my_deck.hand:
                type_card = each_card['type']
                counter_num = f" - {each_card['counter']}" if each_card['counter'] != 0 else ""
                trigger = "Has Trigger" if each_card['trigger'] is True else "No Trigger"
                hand = hand + f"{type_card.capitalize()} - {trigger}{counter_num}\n"
            return hand

        async def update_options(self):
            select_options = []
            count = 0
            for each_card in my_deck.hand:
                count += 1
                type_card = each_card['type']
                counter_num = f" - {each_card['counter']}" if each_card['counter'] != 0 else ""
                trigger = "Has Trigger" if each_card['trigger'] is True else "No Trigger"
                select_options.append(discord.SelectOption(
                    label=f"{type_card.capitalize()} - {trigger}{counter_num}",
                    value=str(count)))
            
            self.select.options = select_options

        async def draw(self, interaction:discord.Interaction):
            my_deck.draw()
            self.embed.description = self.check_hand()
            await self.update_options()
            if self.select in self.children:
                self.remove_item(self.select)
            await interaction.response.edit_message(embed=self.embed, view=self)

        async def play(self, interaction:discord.Interaction):
            self.embed.description = self.check_hand()
            await self.update_options()
            
            if self.select in self.children:
                self.remove_item(self.select)
            self.add_item(self.select)

            await interaction.response.edit_message(embed=self.embed, view=self) 
#    
#        @discord.ui.button(label=, style=)
#        async def (self, interaction:discord.Interaction, button:discord.ui.Button):
#    
#        @discord.ui.button(label=, style=)
#        async def (self, interaction:discord.Interaction, button:discord.ui.Button):
#    
#        @discord.ui.button(label=, style=)
#        async def (self, interaction:discord.Interaction, button:discord.ui.Button):

    class StartView(discord.ui.View):
        def __init__(self, timeout=300):
            super().__init__(timeout=timeout)
            self.embed = None
        
        def mulligan_five(self):
            my_deck.shuffle()
            hand = my_deck.draw_five()
            f_desc = "**Hand:**\n"
            for dict in hand:
                type_card = dict['type']
                counter_num = None if dict['counter'] == 0 else f" - {dict['counter']}"
                trigger = "Has Trigger" if dict['trigger'] is True else "No Trigger"
                f_desc = f_desc + f"{type_card.capitalize()} - {trigger}{counter_num}\n" if counter_num else f_desc + f"{type_card.capitalize()} - {trigger}\n"
            return f_desc

        @discord.ui.button(label="Start",style=discord.ButtonStyle.green)
        async def start(self, interaction: discord.Interaction, button:discord.ui.Button):
            self.embed = discord.Embed(title="Here's your hand. You can press `Keep` or `Mulligan` below.",description=self.mulligan_five())

            mulligan_view = discord.ui.View()
            mulligan_view.add_item(MyButton(label="Keep",callback=self.keep_callback))
            mulligan_view.add_item(MyButton(label="Mulligan",callback=self.mulligan_callback))
            await interaction.response.edit_message(embed=self.embed, view=mulligan_view)

        async def keep_callback(self, interaction:discord.Interaction):
            await interaction.response.send_modal(LifeCount())

        async def mulligan_callback(self, interaction:discord.Interaction):
            self.embed.description = self.mulligan_five()
            await interaction.response.edit_message(embed=self.embed)
            
    
    view = StartView()
    embed = EmbedGuide(description=f"Hi, `{interaction.user.display_name}`.\n\nHere are your deck's initial stats. Press `Start` to begin the simulator.")
    embed.add_field(name="Characters",value=f"{deckstats[0]['count']} cards. ({int(deckstats[0]['ratio'])} %)")
    embed.add_field(name="Events",value=f"{deckstats[1]['count']} cards. ({int(deckstats[1]['ratio'])} %)")
    embed.add_field(name="Stages",value=f"{deckstats[2]['count']} cards. ({int(deckstats[2]['ratio'])} %)")
    embed.add_field(name="Bricks",value=f"{deckstats[3]['count']} cards. ({int(deckstats[3]['ratio'])} %)")
    embed.add_field(name="Triggers",value=f"{deckstats[8]['count']} cards. ({int(deckstats[8]['ratio'])} %)")
    embed.add_field(name="1000 Counters",value=f"{deckstats[4]['count']} cards. ({int(deckstats[4]['ratio'])} %)")
    embed.add_field(name="2000 Counters",value=f"{deckstats[4]['count']} cards. ({int(deckstats[4]['ratio'])} %)")
    embed.add_field(name="Event Counters",value=f"{deckstats[5]['count']} cards. ({int(deckstats[5]['ratio'])} %)")
    embed.add_field(name="Total Counters",value=f"{deckstats[5]['count']} cards. ({int(deckstats[5]['ratio'])} %)")
    embed.set_footer(text="Credits: https://github.com/imjakeym8",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTvgBPvdDUKd0ffWXnQKSuyyYNGy1Sxa-DAmA&s")
    await interaction.edit_original_response(embed=embed,view=view)

bot.run(token)