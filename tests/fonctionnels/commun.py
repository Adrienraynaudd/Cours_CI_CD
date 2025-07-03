import json
import urllib.request


URL = "http://127.0.0.1:9345"

class SimeisError(Exception):
    pass

key = None

def get(path, **qry):
    tail = ""
    if len(qry) > 0:
        tail += "?"
        tail += "&".join([
            "{}={}".format(k, urllib.parse.quote(v)) for k, v in qry.items()
        ])
    qry = f"{URL}{path}{tail}"
    reply = urllib.request.urlopen(qry, timeout=1)
    data = json.loads(reply.read().decode())
    err = data.pop("error")
    if err != "ok":
        raise SimeisError(err)
    return data

def init_new_player(name, is_rich=False):
    if is_rich: name = "test-rich-" + name
    data = get(f"/player/new/{name}")
    player_id, key = data["playerId"], data["key"]
    data = get(f"/player/{player_id}", key=key)
    station_id = list(data["stations"].keys())[0]
    return player_id, key, station_id
    
def init_first_ship(name, is_rich=False):
    player_id, key, station_id = init_new_player(name, is_rich)
    available = get(f"/station/{station_id}/shipyard/list", key=key)["ships"]
    cheapest = sorted(available, key = lambda ship: ship["price"])[0]
    get(f"/station/{station_id}/shipyard/buy/" + str(cheapest["id"]), key=key)
    data = get(f"/player/{player_id}", key=key)
    return player_id, key, station_id, data["ships"][0]["id"]

def init_first_ship_crew(name, is_rich=False):
    player_id, key, station_id, ships_id = init_first_ship(name, is_rich)
    pilot = get(f"/station/{station_id}/crew/hire/pilot", key=key)["id"]
    get(f"/station/{station_id}/crew/assign/{pilot}/{ships_id}/pilot", key=key)
    mod_id = get(f"/station/{station_id}/shop/modules/{ships_id}/buy/Miner", key=key)["id"]
    op = get(f"/station/{station_id}/crew/hire/operator", key=key)["id"]
    get(f"/station/{station_id}/crew/assign/{op}/{ships_id}/{mod_id}", key=key)
    trader = get(f"/station/{station_id}/crew/hire/trader", key=key)["id"]
    get(f"/station/{station_id}/crew/assign/{trader}/trading", key=key)
    return player_id, key, station_id, ships_id