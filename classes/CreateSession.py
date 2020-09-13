from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import SendMessageRequest, GetBotCallbackAnswerRequest
from datetime import datetime
import random, re, asyncio, json, logging, configparser
import urllib.request


# read config.ini
config = configparser.ConfigParser()
config.read('config.ini')


class CreateBot(TelegramClient):
    def __init__(self, **kwargs):
        super().__init__(api_id=config['TelegramApi']['api_id'],
                         api_hash=config['TelegramApi']['api_hash'],
                         connection_retries=config['TelegramApi']['connection_retries'],
                         **kwargs)

    def start(self, **kwargs):
        super().start(bot_token=config['Bot']['token'],
                    **kwargs)


class CreateClient(TelegramClient):
    total_arena = 0
    total_swamp = 0
    total_valley = 0

    async def __call__(self, request, **kwargs):
        print(request)
        # if sending a message to ChatWars
        if (isinstance(request, SendMessageRequest) or isinstance(request, GetBotCallbackAnswerRequest)) and hasattr(
                request.peer, 'user_id') and request.peer.user_id == config['SharedResources']['chatwars_channel_id']:
            if self.is_bot_active():
                await asyncio.sleep(random.randint(1, 5))
                return await super().__call__(request, **kwargs)
        else:
            return await super().__call__(request, **kwargs)

    def __init__(self, **kwargs):
        super().__init__(api_id=config['TelegramApi']['api_id'],
                         api_hash=config['TelegramApi']['api_hash'],
                         connection_retries=config['TelegramApi']['connection_retries'],
                         **kwargs)

        self.refresh_quest_return_data()

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

    def refresh_quest_return_data(self):
        json_text = urllib.request.urlopen(config['SharedResources']['quest_return_url']).read().decode('utf-8')
        self.quest_return_json = json.loads(json_text)