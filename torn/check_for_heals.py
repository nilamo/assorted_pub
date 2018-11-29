# this is YOUR api key, which you can find/create here:
# https://www.torn.com/preferences.php#tab=api
# DO NOT share your key with anyone
API_KEY = ""

# ignore users in hosp that only have a few minutes left (they can just wait)
MINIMUM_MINUTES_IN_HOSP = 30

# if someone's in hosp overseas, should we still open them up?
# unless you actually go there, you can't help them, so...
INCLUDE_USERS_OVERSEAS = False

# stop running once someone needing help is found
# if false, it'll continue running forever,
# until you manually kill it from the command line via ctrl-c
STOP_AT_FIRST_FOUND = False

# to avoid getting your ip blocked, the torn api doesn't want you making more than 100 requests per minute
# if you're bold, feel free to make requests more frequently
SECONDS_PER_MINUTE = 60
REQUESTS_PER_MINUTE = 100
TIME_PER_REQUEST = SECONDS_PER_MINUTE / REQUESTS_PER_MINUTE

class Faction(int): pass
class User(int): pass
ThingsToTrack = [
    # TheReformation, check them before any user
    Faction(21687),
    Faction(15151), # Lifeline (can't heal if we're all out lol)
    
    # these users are next in priority to Reformation
    User(1873683), # Kapten_Klitoris
    User(20228), # ornery
    User(307651), # Atari
    User(1874922), # JussiJernkuuk
    User(2016267), # Kylar
    User(2006415), # Obsession
    User(135825), # Jimmy007
    User(1160609), # Tipsy
    User(2038695), # EXPLOITED
    User(2006124), # tinytown
    User(1366534), # Dilz
    User(666860), # Ikazuchiryu
    User(9944), # zme1004
    User(927610), # UGK_GEE
    User(1563002), # __Franky__
    User(2154292), # Calla
    User(2163874), # Herpes
#][
    Faction(36891), # Flatline
    Faction(11376), # Buttgrass
    Faction(9201), # axiom
    Faction(9953), # The Drunk Tank
    Faction(31312), # Tornado
    Faction(10174), # The Quidnunks HQ
    Faction(11356), # UGK
    Faction(12863), # Noobs
]

# that's it for the config.
# You shouldn't need to go any further in this file


# external modules
import requests


# bulit into python
from datetime import datetime
import sys
import time
import webbrowser

class TornAPI:
    def __init__(self, key):
        self.key = key
        self.last_request = None

    def get(self, uri):
        if self.last_request:
            since_last_request = time.time() - self.last_request
            time_to_sleep = TIME_PER_REQUEST - since_last_request
            time.sleep(time_to_sleep)

        uri = uri.format(self.key)
        content = requests.get(uri)
        self.last_request = time.time()
        return content.json()

API = TornAPI(API_KEY)

def lookup_users(user_ids):
    for user_id in user_ids:
        data = API.get(f"https://api.torn.com/user/{user_id}?selections=profile&key={{0}}")
        yield data

def lookup_faction(faction_id):
    data = API.get(f"https://api.torn.com/faction/{faction_id}?selections=basic&key={{0}}")
    uri = f"https://www.torn.com/factions.php?step=profile&ID={faction_id}"
    print(f"\nSearching through faction: {data['name']} - {uri}")
    members = data["members"]

    yield from lookup_users(members.keys())

def main():
    for obj in ThingsToTrack:
        func = lookup_faction
        if isinstance(obj, User):
            func = lookup_users
            obj = [obj]

        for user in func(obj):
            # status is a two element array.
            # The first element will normally be "Okay", and the second is almost always blank
            # For in hosp, the first will be "In hospital for N mins",
            # and the second will be the reason why
            # ie: "Burned in an arson attempt"

            states = user["states"]
            timestamp = states["hospital_timestamp"]
            if not timestamp:
                # not in hosp
                print(".", end="")
            else:
                out_of_hosp = datetime.fromtimestamp(timestamp)
                time_until_out = (out_of_hosp - datetime.now()).seconds
                # convert to minutes
                time_until_out = time_until_out / 60
                if time_until_out <= MINIMUM_MINUTES_IN_HOSP:
                    # currently in hosp, but only for a few more minutes
                    print("#", end="")
                else:
                    if "In hospital" not in user["status"][0]:
                        # in hosp, needs help, but is overseas
                        print("@", end="")
                        if INCLUDE_USERS_OVERSEAS:
                            webbrowser.open(f"https://www.torn.com/profiles.php?XID={user['player_id']}")
                    else:
                        # in hosp, needs help
                        print("!", end="")
                        webbrowser.open(f"https://www.torn.com/profiles.php?XID={user['player_id']}")
                    if STOP_AT_FIRST_FOUND:
                        return True
            sys.stdout.flush()

        if isinstance(obj, Faction): 
            print()
    return False

if __name__ == "__main__":
    try:
        running = True
        while running:
            user_found = main()
            if STOP_AT_FIRST_FOUND and user_found:
                running = False
    except KeyboardInterrupt:
        # swallow up ctrl-c for early termination
        print()
        