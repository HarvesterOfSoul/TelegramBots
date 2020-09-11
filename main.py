from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from datetime import datetime
import random, re, asyncio, logging
import json, urllib.request
import config, regex

# logging.basicConfig(level=logging.DEBUG)


class CreateClient(TelegramClient):
    total_arena = 0
    total_swamp = 0
    total_valley = 0

    async def __call__(self, request, **kwargs):
        # print(request)
        if (isinstance(request, SendMessageRequest) or isinstance(request, GetBotCallbackAnswerRequest)) and hasattr(
                request.peer, 'user_id') and request.peer.user_id == ChatWars_Channel.id:
            if client.is_bot_active():
                await asyncio.sleep(random.randint(1, 5))
                return await super().__call__(request, **kwargs)
        else:
            return await super().__call__(request, **kwargs)

    def __init__(self, **kwargs):
        super().__init__(api_id=config.api_id,
                         api_hash=config.api_hash,
                         connection_retries=config.connection_retries,
                         **kwargs)

        self.bot_active: bool = False
        self.current_activity = None  # Valley / Swamp / Arena
        self.activity_counter = None
        self.start_event = None
        self.arena_test_closed = None
        self.use_found_energy = False
        self.exhaust_energy = False
        self.exhaust_activity_reply_quests = False
        self.results = 0
        self.quest_return_json = None

    def reset_status(self):
        self.set_bot_active(False)
        self.current_activity = None
        self.activity_counter = None
        self.start_event = None
        self.arena_test_closed = None
        self.use_found_energy = False
        self.exhaust_energy = False
        self.exhaust_activity_reply_quests = False
        self.results = 0

    def is_bot_active(self) -> bool:
        return self.bot_active

    def set_bot_active(self, bool_: bool):
        self.bot_active = bool_


sync.syncify(CreateClient)

# user config
client = CreateClient(session=config.Session_File).start()
Control_Channel = client.get_entity(config.Control_Channel_URL)
ChatWars_Channel = client.get_entity('@chtwrsbot')




def print_unhandled_error():
    print("{}   {} {} {}".format(datetime.now(), client.is_bot_active(), client.current_activity, client.activity_counter))


def refresh_quest_return_data():
    json_text = urllib.request.urlopen(config.quest_return_url).read().decode('utf-8')
    client.quest_return_json = json.loads(json_text)


@client.on(events.NewMessage(chats=ChatWars_Channel, incoming=True))
async def cw_logic(event):
    if client.is_bot_active():
        # Valley
        if client.current_activity == "Valley":
            # inside quest command
            if re.search(regex.quests, event.raw_text):
                print_unhandled_error()
                if client.activity_counter > 0:
                    print("{}   sending valley command".format(datetime.now()))
                    await event.click(text="⛰️Valley")
                else:
                    print("ERROR: Unhandled exception")
                    await client.start_event.reply("ERROR: Unhandled exception")
                    await client.start_event.reply(
                        "Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(client.is_bot_active(),
                                                                                            client.current_activity,
                                                                                            client.activity_counter))
                    await client.send_message(ChatWars_Channel, "⬅Back")
                    client.reset_status()

            # # # Valley Handlers # # #

            # Return from Valley
            responses = client.quest_return_json["Valley"]["Successful"] + client.quest_return_json["Valley"]["Unsuccessful"]
            for x in responses:
                if x in event.raw_text:
                    client.results += 1
                    client.exhaust_activity_reply_quests = False
                    client.activity_counter -= 1
                    print_unhandled_error()
                    if client.activity_counter > 0:
                        sleep_time = random.randint(5, 300)
                        print("{} sleeping {}".format(datetime.now(), sleep_time))
                        await asyncio.sleep(sleep_time)
                        if client.is_bot_active() and client.current_activity == "Valley":
                            print("{} Sending quests command".format(datetime.now()))
                            if random.randint(1, 3) == 1:
                                await client.send_message(ChatWars_Channel, "🏅Me")
                                await asyncio.sleep(random.randint(3, 5))
                            await client.send_message(ChatWars_Channel, "🗺Quests")
                    elif client.activity_counter == 0:
                        if client.exhaust_energy:
                            client.exhaust_activity_reply_quests = True
                            await client.send_message(ChatWars_Channel, "🏅Me")
                        else:
                            print("{} valley done".format(datetime.now()))
                            await client.start_event.reply("Done\nQuests Completed: {}".format(client.results))
                            client.reset_status()


            # not enough stamina
            if re.search(regex.error_not_enough_stamina, event.raw_text):
                await client.start_event.reply("ERROR: Not enough Stamina\nQuests Completed: {}".format(client.results))
                client.reset_status()

            # if we saved / found an energy while questing
            if client.use_found_energy and re.search(r"\+1🔋", event.raw_text):
                client.activity_counter += 1

            # if warehouse is full
            if re.search("your warehouse is full and you lost your loot", event.raw_text):
                await client.start_event.reply("WARNING: Warehouse full")

        # Swamp
        elif client.current_activity == "Swamp":
            # inside quest command
            if re.search(regex.quests, event.raw_text):
                print_unhandled_error()
                if client.activity_counter > 0:
                    print("{}   sending swamp command".format(datetime.now()))
                    await event.click(text="🍄Swamp")
                else:
                    print("ERROR: Unhandled exception")
                    await client.start_event.reply("ERROR: Unhandled exception")
                    await client.start_event.reply(
                        "Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(client.is_bot_active(),
                                                                                            client.current_activity,
                                                                                            client.activity_counter))
                    await client.send_message(ChatWars_Channel, "⬅Back")
                    client.reset_status()

            # # # Swamp Handlers # # #

            # Return from Swamp
            responses = client.quest_return_json["Swamp"]["Successful"] + client.quest_return_json["Swamp"]["Unsuccessful"]
            for x in responses:
                if x in event.raw_text:
                    client.results += 1
                    client.exhaust_activity_reply_quests = False
                    client.activity_counter -= 1
                    print_unhandled_error()
                    if client.activity_counter > 0:
                        sleep_time = random.randint(5, 300)
                        print("{} sleeping {}".format(datetime.now(), sleep_time))
                        await asyncio.sleep(sleep_time)
                        if client.is_bot_active() and client.current_activity == "Swamp":
                            print("{} Sending quests command".format(datetime.now()))
                            if random.randint(1, 3) == 1:
                                await client.send_message(ChatWars_Channel, "🏅Me")
                                await asyncio.sleep(random.randint(3, 5))
                            await client.send_message(ChatWars_Channel, "🗺Quests")
                    elif client.activity_counter == 0:
                        if client.exhaust_energy:
                            client.exhaust_activity_reply_quests = True
                            await client.send_message(ChatWars_Channel, "🏅Me")
                        else:
                            print("{} swamp done".format(datetime.now()))
                            await client.start_event.reply("Done\nQuests Completed: {}".format(client.results))
                            client.reset_status()


            # not enough stamina
            if re.search(regex.error_not_enough_stamina, event.raw_text):
                await client.start_event.reply("ERROR: Not enough Stamina\nQuests Completed: {}".format(client.results))
                client.reset_status()

            # if we saved / found an energy while questing
            if client.use_found_energy and re.search(r"\+1🔋", event.raw_text):
                client.activity_counter += 1

            # if warehouse is full
            if re.search("your warehouse is full and you lost your loot", event.raw_text):
                await client.start_event.reply("WARNING: Warehouse full")

        # Arena
        elif client.current_activity == "Arena":
            # inside quest command
            if re.search(regex.quests, event.raw_text):
                # if arena is open
                if re.search(regex.quests_arena_open, event.raw_text):
                    # if unknown count remaining
                    if client.activity_counter is None:
                        # Let's find out how many
                        await event.click(text="📯Arena")
                    elif client.activity_counter >= 0:
                        # We have some more arena to do
                        await event.click(text="📯Arena")
                    else:
                        print("ERROR: Unhandled exception")
                        await client.start_event.reply("ERROR: Unhandled exception")
                        await client.start_event.reply(
                            "Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(client.is_bot_active(),
                                                                                                client.current_activity,
                                                                                                client.activity_counter))
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        client.reset_status()
                # if arena is closed:
                if re.search(regex.quests_arena_locked, event.raw_text):
                    # arena is closed for one of three reasons:
                    # 1. war less < 2 hours
                    # 1.1. arena ia already completed
                    # 2. arena closed while we were working on it
                    # else: unhandled
                    # if unknown count remaining
                    if client.activity_counter is None:
                        # Either war in < 2 hours OR arena is already completed
                        client.arena_test_closed = True
                        # send arena button to find out
                        await event.click(text="📯Arena")
                    elif client.activity_counter > 0:
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        await client.send_message(ChatWars_Channel, "/g_def")
                        await client.start_event.reply(
                            "ERROR: Arena closed before finishing.  Completed: {}/5".format(client.activity_counter))
                        client.reset_status()
                    else:
                        print("ERROR: Unhandled exception")
                        await client.start_event.reply("ERROR: Unhandled exception")
                        await client.start_event.reply(
                            "Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(client.is_bot_active(),
                                                                                                client.current_activity,
                                                                                                client.activity_counter))
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        client.reset_status()
            # inside arena command
            if re.search(regex.arena_capture_remaining_fights, event.raw_text):
                client.activity_counter = int(re.findall(regex.arena_capture_remaining_fights, event.raw_text, re.MULTILINE)[0])
                # If arena is closed & unknown counter: we're finding out why
                if client.arena_test_closed:
                    if client.activity_counter < 5:
                        await client.start_event.reply("ERROR: Arena is closed due to upcoming war.")
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        client.reset_status()
                    elif client.activity_counter == 5:
                        await client.start_event.reply("ERROR: Arena already completed.")
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        client.reset_status()
                else:
                    # if we have more to do
                    if client.activity_counter < 5:
                        await client.send_message(ChatWars_Channel, "▶️Fast fight")
                    # error handling
                    elif client.activity_counter == 5:
                        print("ERROR: Unhandled exception")
                        await client.start_event.reply("ERROR: Unhandled exception")
                        await client.start_event.reply(
                            "Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(client.is_bot_active(),
                                                                                                client.current_activity,
                                                                                                client.activity_counter))
                        await client.send_message(ChatWars_Channel, "⬅Back")
                        client.reset_status()
            # arena finished
            if re.search(regex.arena_response, event.raw_text):
                client.activity_counter += 1
                if client.activity_counter == 5:
                    await client.send_message(ChatWars_Channel, "/g_def")
                    await client.start_event.reply("Done")
                    client.reset_status()
                elif client.activity_counter < 5:
                    await asyncio.sleep(random.randint(3, 15))
                    await client.send_message(ChatWars_Channel, "🗺Quests")

            # # # Arena Handlers # # #

            # Opponent not found
            if event.raw_text == "You didn’t find an opponent. Return later.":
                await client.send_message(ChatWars_Channel, "🗺Quests")

            # Not enough money
            if event.raw_text == "Not enough gold to pay the entrance fee.":
                await client.start_event.reply("ERROR: Insufficient funds")
                client.reset_status()

            # war in < 2 hours
            if re.search(regex.arena_too_dark, event.raw_text):
                await client.start_event.reply("ERROR: War in < 2 hours")
                client.reset_status()

        # # # Global Handlers # # #

        # Too busy response
        if re.search(regex.error_too_busy, event.raw_text):
            await client.start_event.reply("ERROR: Too busy\nQuests Completed: {}".format(client.results))
            client.reset_status()

        # Battle is < 5 minutes away
        if event.raw_text == "Battle is coming. You have no time for games.":
            await client.start_event.reply("ERROR: War starting soon\nQuests Completed: {}".format(client.results))
            client.reset_status()

        # War is ongoing
        if event.raw_text == regex.war_finished:
            await client.start_event.reply("ERROR: War is ongoing\nQuests Completed: {}".format(client.results))
            client.reset_status()

        # Not enough HP
        if event.raw_text == "You should heal up a bit first.":
            await asyncio.sleep(600)
            await client.send_message(ChatWars_Channel, "🗺Quests")

        # Level up
        # if hasattr(event.message.media.document.thumb, "bytes") and regex.level_up_bytes in event.message.media.document.thumb.bytes:
        #    await client.start_event.reply("Level up!")

        # Update stamina
        if client.exhaust_energy and re.search(regex.status_update_capture_stamina, event.raw_text):
            client.activity_counter = int(re.findall(regex.status_update_capture_stamina, event.raw_text)[0])
            if client.activity_counter > 0 and client.exhaust_activity_reply_quests:
                await client.send_message(ChatWars_Channel, "🗺Quests")
            elif client.activity_counter == 0:
                await client.start_event.reply("Done\nQuests Completed: {}".format(client.results))
                await client.send_message(ChatWars_Channel, "/g_def")
                client.reset_status()


@client.on(events.NewMessage(chats=Control_Channel, outgoing=True, forwards=False))
async def control_chat(event):
    # valley given number of times
    if re.search(r"^/[v|V]alley (\d{1,2})\+?$", event.raw_text):
        user_input = int(re.findall(r"^/[v|V]alley (\d{1,2})\+?$", event.raw_text)[0])
        if user_input > 0:
            if client.is_bot_active():
                await event.reply("ERROR: Bot already active")
            elif not client.is_bot_active():
                client.reset_status()
                refresh_quest_return_data()
                client.set_bot_active(True)
                client.current_activity = "Valley"
                client.activity_counter = user_input
                client.start_event = event
                if re.search(r"^/[v|V]alley (\d{1,2})\+$", event.raw_text):
                    client.use_found_energy = True
                await client.start_event.reply("Starting")
                await client.send_message(ChatWars_Channel, "🗺Quests")
    # valley until exhausted
    if re.search(r"^/[v|V]alley$", event.raw_text):
        if client.is_bot_active():
            await event.reply("ERROR: Bot already active")
        elif not client.is_bot_active():
            client.reset_status()
            refresh_quest_return_data()
            client.set_bot_active(True)
            client.current_activity = "Valley"
            # client.activity_counter = 1
            client.exhaust_energy = True
            client.exhaust_activity_reply_quests = True
            client.start_event = event
            client.use_found_energy = True
            await client.start_event.reply("Starting")
            await client.send_message(ChatWars_Channel, "🏅Me")
    # swamp given number of times
    elif re.search(r"^/[s|S]wamp (\d{1,2})\+?$", event.raw_text):
        user_input = int(re.findall(r"^/[s|S]wamp (\d{1,2})\+?$", event.raw_text)[0])
        if user_input > 0:
            if client.is_bot_active():
                await event.reply("ERROR: Bot already active")
            elif not client.is_bot_active():
                client.reset_status()
                refresh_quest_return_data()
                client.set_bot_active(True)
                client.current_activity = "Swamp"
                client.activity_counter = user_input
                client.start_event = event
                if re.search(r"^/[s|S]wamp (\d{1,2})\+$", event.raw_text):
                    client.use_found_energy = True
                await client.start_event.reply("Starting")
                await client.send_message(ChatWars_Channel, "🗺Quests")
    # swamp until exhausted
    if re.search(r"^/[s|S]wamp$", event.raw_text):
        if client.is_bot_active():
            await event.reply("ERROR: Bot already active")
        elif not client.is_bot_active():
            client.reset_status()
            refresh_quest_return_data()
            client.set_bot_active(True)
            client.current_activity = "Swamp"
            # client.activity_counter = 1
            client.exhaust_energy = True
            client.exhaust_activity_reply_quests = True
            client.start_event = event
            client.use_found_energy = True
            await client.start_event.reply("Starting")
            await client.send_message(ChatWars_Channel, "🏅Me")
    # Arena until exhausted
    elif re.search("^/[a|A]rena$", event.raw_text):
        if client.is_bot_active():
            await event.reply("ERROR: Bot already active")
        elif not client.is_bot_active():
            client.reset_status()
            refresh_quest_return_data()
            client.set_bot_active(True)
            client.current_activity = "Arena"
            client.start_event = event
            await client.start_event.reply("Starting")
            await client.send_message(ChatWars_Channel, "🗺Quests")
    elif re.search("^/([s|S]top)|^/[r|R]estart$", event.raw_text):
        await event.reply("Done\nQuests Completed: {}".format(client.results))
        client.reset_status()
    elif re.search("^/[p|P]ing$", event.raw_text):
        await event.reply("Pong")
    elif re.search("^/[s|S]tatus$", event.raw_text):
        await event.reply(
            "Bot active: {}\nCurrent activity: {}\nActivity counter: {}".format(client.is_bot_active(), client.current_activity,
                                                                                client.activity_counter))
    elif re.search("^/[d|D]ebug$", event.raw_text):
        await event.reply(
            "Bot active: {}\nCurrent activity: {}\nActivity counter: {}\nstart_event: {}\narena_test_closed: {}\nuse_found_energy: {}\nexhaust_energy: {}\nexhaust_activity_reply_quests: {}".format(
                client.is_bot_active(), client.current_activity, client.activity_counter, client.start_event, client.arena_test_closed, client.use_found_energy,
                client.exhaust_energy, client.exhaust_activity_reply_quests))
    elif re.search("^/[h|H]elp$", event.raw_text):
        await event.reply(regex.help_message)


# @client.on(events.NewMessage(incoming=True))
# async def two(event):
#     print(event.stringify())

# run_forever
print("started")
refresh_quest_return_data()
asyncio.get_event_loop().run_forever()
