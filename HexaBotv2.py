"""
Bot for making money on Telegram game @HeXamonbot

Author: TheRealNoob - https://github.com/therealnoob
Version 1.0 - 9/23/2018

Required packages: #Lists officially tested versions
Telethon v1.3
"""

from users import *
from telethon import TelegramClient, events, sync
from telethon.tl.functions.updates import GetStateRequest
from telethon.tl.functions.users import GetUsersRequest
from telethon.tl.functions.messages import CheckChatInviteRequest
from datetime import datetime, timedelta
import time, re, asyncio, functools, logging

# user config (from users.py file)
one = mike
two = danny

# logging
log_filename = datetime.now().strftime("%Y.%m.%d-%H.%M.%S") + ".log"
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
print("logging to: {}".format(log_filename))

timestamp = []
for x in range(0, 20):  # some variance in timestamps
    timestamp.append(datetime.now() + timedelta(seconds=x*2) - timedelta(minutes=1))  # seconds=x*2
last_request = None
last_message = None

# Hexa limits us to 20 interactions per minute as an anti-cheat measure.
# This creates a counter and timestamp of every message we send it
class CreateClient(TelegramClient):
    async def __call__(self, request, **kw):
        # print(request)
        if not isinstance(request, (GetStateRequest, GetUsersRequest, CheckChatInviteRequest)):
            global timestamp
            min_timestamp = min(timestamp)
            while True:
                if datetime.now() >= min_timestamp + timedelta(minutes=1):
                    timestamp[timestamp.index(min_timestamp)] = datetime.now() + timedelta(seconds=10)
                    break
                else:
                    await asyncio.sleep(0.05)
        return await super().__call__(request, **kw)


# setup
sync.syncify(CreateClient)
one_client = CreateClient(session=one.session_name, api_id=one.api_id, api_hash=one.api_hash).start()
two_client = CreateClient(session=two.session_name, api_id=two.api_id, api_hash=two.api_hash).start()

one.display_name = one_client.get_me().first_name
two.display_name = two_client.get_me().first_name
BattlingGroup = one_client.get_entity(one.battle_group)
winner = one.display_name


# calculates damage effectiveness (from the perspective of the attacker)
def find_best_move(message, display_name):
    enemy_type = re.findall(r"(?:[Ww]ild|[Oo]pponent's).+\[(\w+)(?:, (\w+))?\]", message, re.MULTILINE)
    move_list = re.findall(r"(.+) \[(\w+)\].+\nPower: (\d+), Accuracy: (\d+)", message, re.MULTILINE)
    if (winner == one.display_name and display_name == one.display_name)\
            or (winner == two.display_name and display_name == two.display_name):       # supposed to win
        best_move = [-1, ("Default button", "Normal", 0, 0)]
        print("1st check.  supposed to win")
    else:                                                                               # not supposed to win
        best_move = [5, ("Default button", "Normal", 0, 0)]
        print("1st check.  not supposed to win")

    for move in move_list:
        efficiency = efficiency_lookup(attack_type=move[1], enemy_type=enemy_type[0])
        if (winner == one.display_name and display_name == one.display_name) \
                or (winner == two.display_name and display_name == two.display_name):   # supposed to win
            print("2nd check.  supposed to win")
            if efficiency > best_move[0]:
                best_move = (efficiency, move)
            elif efficiency == best_move[0]:
                if int(move[2]) + int(move[3]) > int(best_move[1][2]) + int(best_move[1][3]):
                    best_move = (efficiency, move)
        else:                                                                           # not supposed to win
            print("2nd check.  not supposed to win")
            if efficiency < best_move[0]:
                best_move = (efficiency, move)
            elif efficiency == best_move[0]:
                if int(move[2]) + int(move[3]) < int(best_move[1][2]) + int(best_move[1][3]):
                    best_move = (efficiency, move)

    return best_move


# part of find_best_move()
def efficiency_lookup(attack_type, enemy_type):
    if len(enemy_type) == 1:
        return type_dict[attack_type].get(enemy_type[0], 1)
    if len(enemy_type) == 2:
        return type_dict[attack_type].get(enemy_type[0], 1) * type_dict[attack_type].get(enemy_type[1], 1)


# When we run over 20 messages per minute Hexa sends "too many messages"
# When that message is detected push timestamps +30s, sleep 30, and resend last message
async def overflow():
    global timestamp
    min_timestamp = min(timestamp)
    for stamp in timestamp:
        if stamp >= min_timestamp + timedelta(seconds=30):
            timestamp[timestamp.index(stamp)] = datetime.now() + timedelta(seconds=30)

    await asyncio.sleep(30)
    await last_request()


# Compares latest message in group with the latest message from x seconds ago
# If the same message is detected send a new "Battle Request" message
async def run_check():
    global last_message
    if last_message == (await one_client.get_messages(BattlingGroup))[0]:
        print("Stuck at {}".format(datetime.now()))
        await one_client.send_message(BattlingGroup, "Battle Request")
    last_message = (await one_client.get_messages(BattlingGroup))[0]


# part of run_check() function
async def periodic(delay):
    while True:
        await run_check()
        await asyncio.sleep(delay)


@one_client.on(events.NewMessage(chats=BattlingGroup))
async def one_new_message(event):
    global last_request
    message = event.message.message
    if message == '/Challenge':
        last_request = functools.partial(event.reply, '/Accept')
        await event.reply('/Accept')
    elif "Current turn: {}".format(one.display_name) in message:
        best_move = find_best_move(message=message, display_name=one.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])
    elif message == "Too many messages are being sent/edited here":
        await overflow()


@one_client.on(events.MessageEdited(chats=BattlingGroup))
async def one_message_edited(event):
    global last_request
    message = event.message.message
    if "Current turn: {}".format(one.display_name) in message and "Choose your next pokemon." in message:
        for button in [item for sublist in event.message.buttons for item in sublist]:
            if button.text == " " or button.text == "View pokemon":
                continue
            last_request = functools.partial(button.click)
            await button.click()
    elif "Current turn: {}".format(one.display_name) in message:
        best_move = find_best_move(message=message, display_name=one.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])
    elif "has defeated" in message:
        last_request = functools.partial(one_client.send_message, BattlingGroup, 'Battle Request')
        await one_client.send_message(BattlingGroup, 'Battle Request')
    elif "Player forfeits" in message:
        print("{} forfeit detected.".format(datetime.now()))
        last_request = functools.partial(one_client.send_message, BattlingGroup, 'Battle Request')
        await one_client.send_message(BattlingGroup, 'Battle Request')


@two_client.on(events.NewMessage(chats=BattlingGroup))
async def two_new_message(event):
    global last_request
    message = event.message.message
    if message == 'Battle Request':
        last_request = functools.partial(event.reply, '/Challenge')
        await event.reply('/Challenge')
    elif "Current turn: {}".format(two.display_name) in message:
        best_move = find_best_move(message=message, display_name=two.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])


@two_client.on(events.MessageEdited(chats=BattlingGroup))
async def event_two(event):
    global last_request
    message = event.message.message
    if "Current turn: {}".format(two.display_name) in message and "Choose your next pokemon." in message:
        for button in [item for sublist in event.message.buttons for item in sublist]:
            if button.text == " " or button.text == "View pokemon":
                continue
            last_request = functools.partial(button.click)
            await button.click()
    elif "Current turn: {}".format(two.display_name) in message:
        best_move = find_best_move(message=message, display_name=two.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])


# At this point both clients are already running, they just need a "Battle Request" to start
# Sends "Battle Request" and the asyncio locks us in a loop running the run_check()
# which serves the dual function of keeping our clients going, as the program will end without it
# if we wanted to remove hunt check, the line would be 'asyncio.get_event_loop().run_forever()'
print("Start: {}".format(datetime.now()))
one_client.send_message(BattlingGroup, 'Battle Request')
asyncio.get_event_loop().run_until_complete(periodic(600))
