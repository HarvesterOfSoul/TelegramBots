from users import *
from telethon import TelegramClient, events, sync
from telethon.tl.functions.updates import GetStateRequest
from telethon.tl.functions.users import GetUsersRequest
from telethon.tl.functions.messages import CheckChatInviteRequest
from datetime import datetime, timedelta
import time, re, asyncio, functools, logging

# user config
one = mike      # will win every fight
two = danny

# logging
log_filename = datetime.now().strftime("%Y.%m.%d-%H.%M.%S") + ".log"
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
print("logging to: {}".format(log_filename))

timestamp = []
for x in range(0, 20):  # some variance in timestamps
    timestamp.append(datetime.now() + timedelta(seconds=x*2) - timedelta(minutes=1))
last_request = None
last_message = None


class CreateClient(TelegramClient):
    async def __call__(self, request, **kw):
        # print(request)
        if not isinstance(request, (GetStateRequest, GetUsersRequest, CheckChatInviteRequest)):
            global timestamp
            min_timestamp = min(timestamp)
            print("min timestamp: {}").format(min_timestamp)
            while True:
                if datetime.now() >= min_timestamp + timedelta(minutes=1):
                    timestamp[timestamp.index(min_timestamp)] = datetime.now() + timedelta(seconds=10)
                    break
                else:
                    await asyncio.sleep(0.05)
        return await super().__call__(request, **kw)


# setup
sync.syncify(CreateClient)
one_client = CreateClient(one.session_name, one.api_id, one.api_hash, connection_retries=20).start()
two_client = CreateClient(two.session_name, two.api_id, two.api_hash, connection_retries=20).start()
one.display_name = one_client.get_me().first_name
two.display_name = two_client.get_me().first_name
BattlingGroup = one_client.get_entity(one.battle_group)
winner = one.display_name


def efficiency_lookup(attack_type, enemy_type):
    if len(enemy_type) == 1:
        return type_dict[attack_type][enemy_type[0]]
    if len(enemy_type) == 2:
        return type_dict[attack_type][enemy_type[0]] * type_dict[attack_type][enemy_type[1]]


def find_best_move(message, client):
    enemy_type = re.findall(r"(?:[Ww]ild|[Oo]pponent's).+\[(\w+)(?:, (\w+))?\]", message, re.MULTILINE)
    move_list = re.findall(r"(.+) \[(\w+)\].+\nPower: (\d+), Accuracy: (\d+)", message, re.MULTILINE)
    if winner == client:                                                    # supposed to win
        best_move = [-1, ("Default button", "Normal", 0, 0)]
    else:                                                                    # not supposed to win
        best_move = [5, ("Default button", "Normal", 0, 0)]

    for move in move_list:
        # print("testing move: {} type: {}".format(move[0], move[1]))
        efficiency = efficiency_lookup(attack_type=move[1], enemy_type=enemy_type[0])
        if winner == client:                                                # supposed to win
            if efficiency > best_move[0]:
                best_move = (efficiency, move)
            elif efficiency == best_move[0]:
                if int(move[2]) + int(move[3]) > int(best_move[1][2]) + int(best_move[1][3]):
                    best_move = (efficiency, move)
        else:                                                               # not supposed to win
            if efficiency < best_move[0]:
                best_move = (efficiency, move)
            elif efficiency == best_move[0]:
                if int(move[2]) + int(move[3]) < int(best_move[1][2]) + int(best_move[1][3]):
                    best_move = (efficiency, move)

    return best_move


async def overflow():
    global timestamp
    min_timestamp = min(timestamp)
    for stamp in timestamp:
        if stamp <= min_timestamp + timedelta(seconds=30):
            timestamp[timestamp.index(stamp)] = datetime.now() + timedelta(seconds=30)

    print("overflow.  sleeping 30s")
    time.sleep(30)
    await last_request()


@one_client.on(events.NewMessage(chats=BattlingGroup))
async def one_new_message(event):
    global last_request
    message = event.message.message
    if message == '/Challenge':
        last_request = functools.partial(event.reply, '/Accept')
        await event.reply('/Accept')
        # return
    elif "Current turn: {}".format(one.display_name) in message:
        best_move = find_best_move(message, one.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])
        # return
    elif message == "Too many messages are being sent/edited here":
        await overflow()


@one_client.on(events.MessageEdited(chats=BattlingGroup))
async def one_message_edited(event):
    global last_request
    message = event.message.message
    if "Current turn: {}".format(one.display_name) in message and "Choose your next pokemon." in message:
        buttons = re.findall(r"text='([-\w ]*)'", event.stringify(), re.MULTILINE)
        buttons = list(set(buttons))
        buttons.remove('View pokemon')
        for number in buttons:
            if number != " ":
                last_request = functools.partial(event.click, text=number)
                await event.click(text=number)
                return
    elif "Current turn: {}".format(one.display_name) in message:
        best_move = find_best_move(message, one.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])
        # return
    elif "has defeated" in message:
        last_request = functools.partial(one_client.send_message, BattlingGroup, 'Battle Request')
        await one_client.send_message(BattlingGroup, 'Battle Request')
        # return
    elif "Player forfeits" in message:
        print("{} lost fight.".format(datetime.now()))
        last_request = functools.partial(one_client.send_message, BattlingGroup, 'Battle Request')
        await one_client.send_message(BattlingGroup, 'Battle Request')
        # return


@two_client.on(events.NewMessage(chats=BattlingGroup))
async def two_new_message(event):
    global last_request
    message = event.message.message
    if message == 'Battle Request':
        last_request = functools.partial(event.reply, '/Challenge')
        await event.reply('/Challenge')
        # return
    elif "Current turn: {}".format(two.display_name) in message:
        best_move = find_best_move(message, two.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])
        # return


@two_client.on(events.MessageEdited(chats=BattlingGroup))
async def event_two(event):
    global last_request
    message = event.message.message
    if "Current turn: {}".format(two.display_name) in message and "Choose your next pokemon." in message:
        buttons = re.findall(r"text='([-\w ]*)'", event.stringify(), re.MULTILINE)
        buttons = list(set(buttons))
        buttons.remove('View pokemon')
        for number in buttons:
            if number != " ":
                last_request = functools.partial(event.click, text=number)
                await event.click(text=number)
                return
    elif "Current turn: {}".format(two.display_name) in message:
        best_move = find_best_move(message, two.display_name)
        last_request = functools.partial(event.click, text=best_move[1][0])
        await event.click(text=best_move[1][0])
        # return


async def run_check():
    global last_message
    if last_message == (await one_client.get_messages(BattlingGroup))[0]:
        print("Stuck at {}".format(datetime.now()))
        await one_client.send_message(BattlingGroup, "Battle Request")
    last_message = (await one_client.get_messages(BattlingGroup))[0]


async def periodic(delay):
    while True:
        await run_check()
        await asyncio.sleep(delay)


# Start
print("Start: {}".format(datetime.now()))
one_client.send_message(BattlingGroup, 'Battle Request')
asyncio.get_event_loop().run_until_complete(periodic(600))
