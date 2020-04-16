from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from datetime import datetime
import random, re, asyncio, logging

# logging.basicConfig(level=logging.DEBUG)

# == V2 ==
# TODO evaluate buttons
# TODO improve /stop functionality
# TODO improved logging
#   TODO more "ERROR: Unhandled Exception"

# TODO Config file
#   TODO Configurable ERROR action (such as /g_def)
#   TODO Allow other(s) to send control messages on behalf of self
#   TODO


# == V3 ==
# TODO A bot that you send control commands to
# TODO Additionally the bot stores your config in a db
# TODO This config controls multiple delay timings,
# TODO logging, error_action, etc...

# global variables
bot_active = False
current_activity = None  # Valley / Swamp / Arena
activity_counter = None
start_event = None
arena_test_closed = None
use_found_energy = False
exhaust_energy = False
exhaust_activity_reply_quests = False
results = 0

# user config
Control_Channel_URL = 'https://t.me/joinchat/Fa7...'
Session_File = 'Username'


# Method override on the Telegram client : Force a 1-5 sec delay on all outgoing messages to Chat Wars
class CreateClient(TelegramClient):
    async def __call__(self, request, **kw):
        # print(request)
        if (isinstance(request, SendMessageRequest) or isinstance(request, GetBotCallbackAnswerRequest)) and hasattr(request.peer, 'user_id') and request.peer.user_id == ChatWars_Channel.id:
            if bot_active:
                await asyncio.sleep(random.randint(1, 5))
                return await super().__call__(request, **kw)
        else:
            return await super().__call__(request, **kw)
        
    def __init__(self, **kwargs):
        super().__init__(api_id=123456,
                         api_hash='qwertyuiopasdfghjkl123456789',
                         connection_retries=1000,
                         **kwargs)


sync.syncify(CreateClient)

# user config
client = CreateClient(session=Session_File).start()
Control_Channel = client.get_entity(Control_Channel_URL)
ChatWars_Channel = client.get_entity('@chtwrsbot')

# regex strings
reg_quests = r"""🌲Forest \d{1,2}min
Many things can happen in the forest.

🍄Swamp \d{1,2}min
Who knows what is lurking in mud.

🏔Mountain Valley \d{1,2}min
Watch out for landslides.

🗡Foray 🔋🔋
Foray is a dangerous activity. Someone can notice you and may beat you up. But if you go unnoticed, you will acquire a lot of loot.

📯Arena [🔒]{0,1}
Arena isn't a place for the weak. Here you fight against other players and if you stand victorious, you acquire precious experience."""
reg_quests_arena_open = r"""🌲Forest 5min
Many things can happen in the forest.

🍄Swamp 6min
Who knows what is lurking in mud.

🏔Mountain Valley 6min
Watch out for landslides.

🗡Foray 🔋🔋
Foray is a dangerous activity. Someone can notice you and may beat you up. But if you go unnoticed, you will acquire a lot of loot.

📯Arena 
Arena isn't a place for the weak. Here you fight against other players and if you stand victorious, you acquire precious experience."""
reg_quests_arena_locked = r"""🌲Forest \d{1,2}min
Many things can happen in the forest.

🍄Swamp \d{1,2}min
Who knows what is lurking in mud.

🏔Mountain Valley \d{1,2}min
Watch out for landslides.

🗡Foray 🔋🔋
Foray is a dangerous activity. Someone can notice you and may beat you up. But if you go unnoticed, you will acquire a lot of loot.

📯Arena 🔒
Arena isn't a place for the weak. Here you fight against other players and if you stand victorious, you acquire precious experience."""
reg_arena_capture_remaining_fights = """📯Welcome to Arena!
Dirty air is soaked with the thick smell of blood\. No one ends up here by an accident: you can't leave once you begin your battle\. I hope, your sword is sharp and your shield is steady\.

Your rank: \d+
Your fights: (\d)\/5

Combat Ranking: \/top5
Fastest-growing: \/top6

Entrance fee: 5💰"""
reg_arena_response = """-{0,1}\d{0,4}❤️.+
VS
-{0,1}\d{0,4}❤️.+

.+! \d{0,4}(?:\([-+]{0,1}\d{1,4}\)){0,1}

.+! \d{0,4}(?:\([-+]{0,1}\d{1,4}\)){0,1}

.+ stands victorious over .+
You received: \d{0,4} exp.
Leaderboard of fighters are updated: .top5 & .top6.*"""
reg_error_not_enough_stamina = """Not enough stamina. Come back after you take a rest.

To get more stamina, invite friends to the game via invite link. Press /promo to get it."""
reg_valley_capture_time = """Mountains can be a dangerous place. You decided to investigate, what's going on. You'll be back in (\d{1,2}) minutes."""
reg_swamp_capture_time = """An adventure is calling. But you went to a swamp. You'll be back in (\d{1,2}) minutes."""
reg_error_too_busy = """You are too busy with a different adventure. Try a bit later."""
reg_arena_too_dark = """It’s hard to see your opponent in the dark. Wait until the morning."""
reg_war_finished = """The wind is howling in the meadows, castles are unusually quiet. Warriors are mending their wounds and repairing armor after a tiresome battle. All the establishments and castle gates are closed for the next couple of minutes. Await the battle report at @chtwrsReports"""
level_up_bytes = b'RIFF\xe6\x14\x00\x00WEBPVP8X\n\x00\x00\x00\x10\x00\x00\x00\x7f\x00\x00\x7f\x00\x00ALPH\xb5\x05\x00'
help_message = """Welcome to control chat.
Here are the following commands:

/arena - Go arena until 5/5

/{valley | swamp} {#,#}+
Quest X number of times
Additionally, adding a "+" after the number appends an additional quest action when saving energy

/{valley | swamp}
Quest until out of energy

/status - current status of your control bot

/stop - stops the control bot from sending commands at cw bot

/ping - confirm the bot is running

/help - help message

Bugs:
Stopping and starting again without a few minutes in between will cause it to run twice, causing itself to error"""
reg_status_update_capture_stamina = """Atk: \d+ 🛡Def: \d+\\n🔥Exp: \d+\/\d+\\n❤️Hp: \d+\/\d+\\n🔋Stamina: (\d+)\/\d+"""


def reset_status():
    global bot_active, current_activity, activity_counter, start_event, arena_test_closed, use_found_energy, exhaust_energy, exhaust_activity_reply_quests, results
    bot_active = False
    current_activity = None
    activity_counter = None
    start_event = None
    arena_test_closed = None
    use_found_energy = False
    exhaust_energy = False
    exhaust_activity_reply_quests = False
    results = 0


def print_unhandled_error():
    print("{}   {} {} {}".format(datetime.now(), bot_active, current_activity, activity_counter))


@client.on(events.NewMessage(chats=ChatWars_Channel, incoming=True))
async def one(event):
    global bot_active, current_activity, activity_counter, start_event, arena_test_closed, use_found_energy, exhaust_activity_reply_quests, results

    if bot_active:
        # Valley
        if current_activity == "Valley":
            # inside quest command
            if re.search(reg_quests, event.raw_text):
                print_unhandled_error()
                if activity_counter > 0:
                    print("{}   sending valley command".format(datetime.now()))
                    await event.click(text="⛰️Valley")
                else:
                    print("ERROR: Unhandled exception")
                    await start_event.reply("ERROR: Unhandled exception")
                    await start_event.reply("Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(bot_active, current_activity, activity_counter))
                    await client.send_message(ChatWars_Channel, "⬅Back")
                    reset_status()

            # # # Valley Handlers # # #

            # Left for Valley
            if re.search(reg_valley_capture_time, event.raw_text):
                results += 1
                exhaust_activity_reply_quests = False
                quest_return_time = int(re.findall(reg_valley_capture_time, event.raw_text, re.MULTILINE)[0]) * 60 + 10
                activity_counter -= 1
                print_unhandled_error()
                await asyncio.sleep(quest_return_time)
                if activity_counter > 0:
                    sleep_time = random.randint(0, 300)
                    print("{} sleeping {}".format(datetime.now(), sleep_time))
                    await asyncio.sleep(sleep_time)
                    if bot_active and current_activity == "Valley":
                        print("{} Sending quests command".format(datetime.now(), activity_counter))
                        if random.randint(1, 3) == 1:
                            await client.send_message(ChatWars_Channel, "🏅Me")
                        await client.send_message(ChatWars_Channel, "🗺Quests")
                elif activity_counter == 0:
                    if exhaust_energy:
                        exhaust_activity_reply_quests = True
                        await client.send_message(ChatWars_Channel, "🏅Me")
                    else:
                        print("{} valley done".format(datetime.now(), quest_return_time))
                        await start_event.reply("Done\nQuests Completed: {}".format(results))
                        reset_status()

            # not enough stamina
            if re.search(reg_error_not_enough_stamina, event.raw_text):
                await start_event.reply("ERROR: Not enough Stamina\nQuests Completed: {}".format(results))
                reset_status()

            # if we saved / found an energy while questing
            if use_found_energy and re.search(r"\+1🔋", event.raw_text):
                activity_counter += 1

            # if warehouse is full
            if re.search("your warehouse is full and you lost your loot", event.raw_text):
                await start_event.reply("WARNING: Warehouse full")

        # Swamp
        elif current_activity == "Swamp":
            # inside quest command
            if re.search(reg_quests, event.raw_text):
                print_unhandled_error()
                if activity_counter > 0:
                    print("{}   sending swamp command".format(datetime.now()))
                    await event.click(text="🍄Swamp")
                else:
                    print("ERROR: Unhandled exception")
                    await start_event.reply("ERROR: Unhandled exception")
                    await start_event.reply("Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(bot_active, current_activity, activity_counter))
                    await client.send_message(ChatWars_Channel, "⬅Back")
                    reset_status()

            # # # Swamp Handlers # # #

            # Left for swamp
            if re.search(reg_swamp_capture_time, event.raw_text):
                results += 1
                exhaust_activity_reply_quests = False
                quest_return_time = int(re.findall(reg_swamp_capture_time, event.raw_text, re.MULTILINE)[0]) * 60 + 10
                activity_counter -= 1
                print_unhandled_error()
                await asyncio.sleep(quest_return_time)
                if activity_counter > 0:
                    sleep_time = random.randint(0, 300)
                    print("{} sleeping {}".format(datetime.now(), sleep_time))
                    await asyncio.sleep(sleep_time)
                    if bot_active and current_activity == "Swamp":
                        print("{} Sending quests command".format(datetime.now()))
                        if random.randint(1, 3) == 1:
                            await client.send_message(ChatWars_Channel, "🏅Me")
                        await client.send_message(ChatWars_Channel, "🗺Quests")
                elif activity_counter == 0:
                    if exhaust_energy:
                        exhaust_activity_reply_quests = True
                        await client.send_message(ChatWars_Channel, "🏅Me")
                    else:
                        print("{} swamp done".format(datetime.now(), quest_return_time))
                        await start_event.reply("Done\nQuests Completed: {}".format(results))
                        reset_status()

            # not enough stamina
            if re.search(reg_error_not_enough_stamina, event.raw_text):
                await start_event.reply("ERROR: Not enough Stamina\nQuests Completed: {}".format(results))
                reset_status()

            # if we saved / found an energy while questing
            if use_found_energy and re.search(r"\+1🔋", event.raw_text):
                activity_counter += 1

            # if warehouse is full
            if re.search("your warehouse is full and you lost your loot", event.raw_text):
                await start_event.reply("WARNING: Warehouse full")

        # Arena
        elif current_activity == "Arena":
            # inside quest command
            if re.search(reg_quests, event.raw_text):
                # if arena is open
                if re.search(reg_quests_arena_open, event.raw_text):
                    # if unknown count remaining
                    if activity_counter is None:
                        # Let's find out how many
                        await event.click(text="📯Arena")
                    elif activity_counter >= 0:
                        # We have some more arena to do
                        await event.click(text="📯Arena")
                    else:
                        print("ERROR: Unhandled exception")
                        await start_event.reply("ERROR: Unhandled exception")
                        await start_event.reply("Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(bot_active, current_activity, activity_counter))
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        reset_status()
                # if arena is closed:
                if re.search(reg_quests_arena_locked, event.raw_text):
                    # arena is closed for one of three reasons:
                        # 1. war less < 2 hours
                        # 1.1. arena ia already completed
                        # 2. arena closed while we were working on it
                        # else: unhandled
                    # if unknown count remaining
                    if activity_counter is None:
                        # Either war in < 2 hours OR arena is already completed
                        arena_test_closed = True
                        # send arena button to find out
                        await event.click(text="📯Arena")
                    elif activity_counter > 0:
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        await client.send_message(ChatWars_Channel, "/g_def")
                        await start_event.reply("ERROR: Arena closed before finishing.  Completed: {}/5".format(activity_counter))
                        reset_status()
                    else:
                        print("ERROR: Unhandled exception")
                        await start_event.reply("ERROR: Unhandled exception")
                        await start_event.reply("Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(bot_active, current_activity, activity_counter))
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        reset_status()
            # inside arena command
            if re.search(reg_arena_capture_remaining_fights, event.raw_text):
                activity_counter = int(re.findall(reg_arena_capture_remaining_fights, event.raw_text, re.MULTILINE)[0])
                # If arena is closed & unknown counter: we're finding out why
                if arena_test_closed:
                    if activity_counter < 5:
                        await start_event.reply("ERROR: Arena is closed due to upcoming war.")
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        reset_status()
                    elif activity_counter == 5:
                        await start_event.reply("ERROR: Arena already completed.")
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        reset_status()
                else:
                    # if we have more to do
                    if activity_counter < 5:
                        await client.send_message(ChatWars_Channel, "▶️Fast fight")
                    # error handling
                    elif activity_counter == 5:
                        print("ERROR: Unhandled exception")
                        await start_event.reply("ERROR: Unhandled exception")
                        await start_event.reply("Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(bot_active, current_activity, activity_counter))
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        reset_status()
            # arena finished
            if re.search(reg_arena_response, event.raw_text):
                activity_counter += 1
                if activity_counter == 5:
                    await client.send_message(ChatWars_Channel, "/g_def")
                    await start_event.reply("Done")
                    reset_status()
                elif activity_counter < 5:
                    await asyncio.sleep(random.randint(3, 15))
                    await client.send_message(ChatWars_Channel, "🗺Quests")

            # # # Arena Handlers # # #

            # Opponent not found
            if event.raw_text == "You didn’t find an opponent. Return later.":
                await client.send_message(ChatWars_Channel, "🗺Quests")

            # Not enough money
            if event.raw_text == "Not enough gold to pay the entrance fee.":
                await start_event.reply("ERROR: Insufficient funds")
                reset_status()

            # war in < 2 hours
            if re.search(reg_arena_too_dark, event.raw_text):
                await start_event.reply("ERROR: War in < 2 hours")
                reset_status()

        # # # Global Handlers # # #

        # Too busy response
        if re.search(reg_error_too_busy, event.raw_text):
            await start_event.reply("ERROR: Too busy\nQuests Completed: {}".format(results))
            reset_status()

        # Battle is < 5 minutes away
        if event.raw_text == "Battle is coming. You have no time for games.":
            await start_event.reply("ERROR: War starting soon\nQuests Completed: {}".format(results))
            reset_status()

        # War is ongoing
        if event.raw_text == reg_war_finished:
            await start_event.reply("ERROR: War is ongoing\nQuests Completed: {}".format(results))
            reset_status()

        # Not enough HP
        if event.raw_text == "You should heal up a bit first.":
            await asyncio.sleep(600)
            await client.send_message(ChatWars_Channel, "🗺Quests")

        # Level up
        # if hasattr(event.message.media.document.thumb, "bytes") and level_up_bytes in event.message.media.document.thumb.bytes:
        #    await start_event.reply("Level up!")

        # Update stamina
        if exhaust_energy and re.search(reg_status_update_capture_stamina, event.raw_text):
            activity_counter = int(re.findall(reg_status_update_capture_stamina, event.raw_text)[0])
            if activity_counter > 0 and exhaust_activity_reply_quests:
                await client.send_message(ChatWars_Channel, "🗺Quests")
            elif activity_counter == 0:
                await start_event.reply("Done\nQuests Completed: {}".format(results))
                await client.send_message(ChatWars_Channel, "/g_def")
                reset_status()


@client.on(events.NewMessage(chats=Control_Channel, outgoing=True, forwards=False))
async def one(event):
    global bot_active, current_activity, activity_counter, start_event, arena_test_closed, use_found_energy, exhaust_energy, exhaust_activity_reply_quests
    # valley given number of times
    if re.search(r"^/[v|V]alley (\d{1,2})\+?$", event.raw_text):
        user_input = int(re.findall(r"^/[v|V]alley (\d{1,2})\+?$", event.raw_text)[0])
        if user_input > 0:
            if bot_active:
                await event.reply("ERROR: Bot already active")
            elif not bot_active:
                reset_status()
                bot_active = True
                current_activity = "Valley"
                activity_counter = user_input
                start_event = event
                if re.search(r"^/[v|V]alley (\d{1,2})\+$", event.raw_text):
                    use_found_energy = True
                await start_event.reply("Starting")
                await client.send_message(ChatWars_Channel, "🗺Quests")
    # valley until exhausted
    if re.search(r"^/[v|V]alley$", event.raw_text):
        if bot_active:
            await event.reply("ERROR: Bot already active")
        elif not bot_active:
            reset_status()
            bot_active = True
            current_activity = "Valley"
            # activity_counter = 1
            exhaust_energy = True
            exhaust_activity_reply_quests = True
            start_event = event
            use_found_energy = True
            await start_event.reply("Starting")
            await client.send_message(ChatWars_Channel, "🏅Me")
    # swamp given number of times
    elif re.search(r"^/[s|S]wamp (\d{1,2})\+?$", event.raw_text):
        user_input = int(re.findall(r"^/[s|S]wamp (\d{1,2})\+?$", event.raw_text)[0])
        if user_input > 0:
            if bot_active:
                await event.reply("ERROR: Bot already active")
            elif not bot_active:
                reset_status()
                bot_active = True
                current_activity = "Swamp"
                activity_counter = user_input
                start_event = event
                if re.search(r"^/[s|S]wamp (\d{1,2})\+$", event.raw_text):
                    use_found_energy = True
                await start_event.reply("Starting")
                await client.send_message(ChatWars_Channel, "🗺Quests")
    # swamp until exhausted
    if re.search(r"^/[s|S]wamp$", event.raw_text):
        if bot_active:
            await event.reply("ERROR: Bot already active")
        elif not bot_active:
            reset_status()
            bot_active = True
            current_activity = "Swamp"
            # activity_counter = 1
            exhaust_energy = True
            exhaust_activity_reply_quests = True
            start_event = event
            use_found_energy = True
            await start_event.reply("Starting")
            await client.send_message(ChatWars_Channel, "🏅Me")
    # Arena until exhausted
    elif re.search("^/[a|A]rena$", event.raw_text):
        if bot_active:
            await event.reply("ERROR: Bot already active")
        elif not bot_active:
            reset_status()
            bot_active = True
            current_activity = "Arena"
            start_event = event
            await start_event.reply("Starting")
            await client.send_message(ChatWars_Channel, "🗺Quests")
    elif re.search("^/([s|S]top)|^/[r|R]estart$", event.raw_text):
        await event.reply("Done\nQuests Completed: {}".format(results))
        reset_status()
    elif re.search("^/[p|P]ing$", event.raw_text):
        await event.reply("Pong")
    elif re.search("^/[s|S]tatus$", event.raw_text):
        await event.reply("Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(bot_active, current_activity, activity_counter))
    elif re.search("^/[d|D]ebug$", event.raw_text):
        await event.reply("Bot active: {}\nCurrent activity: {}\nActivity counter: {}\nstart_event: {}\narena_test_closed: {}\nuse_found_energy: {}\nexhaust_energy: {}\nexhaust_activity_reply_quests: {}".format(bot_active, current_activity, activity_counter, start_event, arena_test_closed, use_found_energy, exhaust_energy, exhaust_activity_reply_quests))
    elif re.search("^/[h|H]elp$", event.raw_text):
        await event.reply(help_message)


# @client.on(events.NewMessage(incoming=True))
# async def two(event):
#     print(event.stringify())

# run_forever
print("started")
asyncio.get_event_loop().run_forever()
