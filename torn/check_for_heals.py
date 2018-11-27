# this is YOUR api key, which you can find/create here:
# https://www.torn.com/preferences.php#tab=api
# DO NOT share your key with anyone
API_KEY = ""

# to avoid getting your ip blocked, the torn api doesn't want you making more than 100 requests per minute
# if you're bold, feel free to make requests more frequently
SECONDS_PER_MINUTE = 60
REQUESTS_PER_MINUTE = 100
TIME_PER_REQUEST = SECONDS_PER_MINUTE / REQUESTS_PER_MINUTE

class LookupBase:
    def __init__(self, obj_id):
        self.obj_id = obj_id
class Faction(LookupBase): pass
class User(LookupBase): pass

ThingsToTrack = [
    # TheReformation, check them before any user
    Faction(21687),
    
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
import webbrowser
import time

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
        data = API.get(f"https://api.torn.com/user/{user_id}?selections=basic&key={{0}}")
        yield data

def lookup_faction(faction_id):
    data = API.get(f"https://api.torn.com/faction/{faction_id}?selections=basic&key={{0}}")
    print(f"Searching through members of faction: {data['name']}")
    members = data["members"]

    yield from lookup_users(members.keys())

def main():
    for obj in ThingsToTrack:
        users = lookup_faction(obj.obj_id) if isinstance(obj, Faction) else lookup_users([obj.obj_id])
        for user in users:
            # status is a two element array.
            # The first element will normally be "Okay", and the second is almost always blank
            # For in hosp, the first will be "In hospital for N mins",
            # and the second will be the reason why
            # ie: "Burned in an arson attempt"
            status = user["status"][0]
            print(f"User {user['name']} is currently: {status}.")
            
            if "hospital" in status:
                webbrowser.open(f"https://www.torn.com/profiles.php?XID={user['player_id']}#/")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # swallow up ctrl-c for early termination
        pass