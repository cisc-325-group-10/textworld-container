
import textworld
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import json
import random
import time
import threading
import os
import sys

env = None


class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        print(message.message)
        command = message.message['command']
        if(command == "begin"):
            game_state = env.reset()
            done = False
            message = game_state.feedback.split("$$$$$$$")[-1]
        else:
            game_state, _, done = env.step(command)
            message = game_state.feedback.replace('\n', ' ').replace('\r', '')
        time.sleep(1)
        pubnub.publish().channel(os.getenv("CHANNEL") + "B").message({"feedback": message}).sync()
        if(done):
            print("Played {} steps, scoring {} points.".format(
                game_state.nb_moves, game_state.score))


def setup():
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = 'sub-c-6ba13e32-38a0-11e9-b5cf-1e59042875b2'
    pnconfig.publish_key = 'pub-c-6592a63e-134f-4327-9ed7-b2f36a38b8b2'
    pubnub = PubNub(pnconfig)
    options = textworld.GameOptions()
    seed = random.randint(1, 65635)
    print("SEED: " + str(seed))
    options.seeds = seed
    options.nb_objects = 10
    options.quest_length = 5
    options.nb_rooms = 5
    game_file, _ = textworld.make(options)  # Generate a random game.
    global env
    env = textworld.start(game_file)  # Load the game.
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(os.getenv("CHANNEL") + "A").execute()


workThread = threading.Thread(target=setup)
workThread.setDaemon(True)
workThread.start()

time.sleep(60*60)  # timeout after an hour
sys.exit()
