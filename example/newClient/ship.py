import time

from commun import service, gameData
from error import SimeisError

max_lvl = {
    "pilot": 5,
    "ReactorUpgrade": 20,
    "HullUpgrade": 2000,
    "Shield": 5,
}

def new_ship():
    print("[*] Buying a new ship")
    ship_index = len(gameData.ship)
    station_id = gameData.station["id"]
    available = service.get(f"/station/{station_id}/shipyard/list")["ships"]
    cheapest = sorted(available, key=lambda ship: ship["price"])[0]
    ship = service.get(f"/station/{station_id}/shipyard/buy/" + str(cheapest["id"]))["shipId"]
    pilot = service.get(f"/station/{station_id}/crew/hire/pilot")["id"]
    service.get(f"/station/{station_id}/crew/assign/{pilot}/{ship}/pilot")
    modtype = "GasSucker" if (not gameData.solid_planet) or ship % 2 == 1 else "Miner"
    mod_id = service.buy_module(station_id, ship, modtype)["id"]
    op = service.hire_crew(station_id, "operator")["id"]
    service.set_crew(station_id, ship, op, mod_id)
    gameData.ship.append(service.get_ship(ship))
    run(ship_index)
    
def run(ship_id):
    print("[*] Starting the ship operation")
    try:
        while True:
            go_mine(ship_id)
            go_sell(ship_id)
            shopping(ship_id)
    except SimeisError as e:
        print(f"[*] Error occurred: {e}")
        
    
def travel(ship_id, pos):
        costs = service.navigate(gameData.ship[ship_id]["id"], pos)
        print("[*] Traveling to {}, will take {}".format(pos, costs["duration"]))
        time.sleep(costs["duration"])
        
def wait_idle(ship_id, ts = 0.1):
    while service.get_ship(gameData.ship[ship_id]["id"])["state"] != "Idle":
        time.sleep(ts)

def go_mine(ship_id):
        print("[*] Starting the Mining operation")
        mvp = gameData.gaz_planet if (not gameData.solid_planet) or ship_id % 2 == 1 else gameData.solid_planet
        
        wait_idle(ship_id)  # If we are currently occupied, wait

        # If we are not current at the position of the target planet, travel there
        if gameData.ship[ship_id]["position"] != mvp:
            travel(ship_id, mvp)

        wait_idle(ship_id)  # If we are currently occupied, wait

        # Now that we are there, let's start mining
        info = service.start_mining(gameData.ship[ship_id]["id"])
        print("[*] Starting extraction:")
        for res, amnt in info.items():
            print(f"\t- Extraction of {res}: {amnt}/sec")

        sid = gameData.ship[ship_id]["id"]
        data = service.get_player_status(gameData.player)
        ship_ = [d for d in data["ships"] if d["id"] == sid]
        if len(ship_) > 0 : gameData.ship[ship_id] = ship_[0]
        
        # Wait until the cargo is full
        wait_idle(ship_id)
        print("[*] The cargo is full, stopping mining process")
        
def go_sell(ship_id):
    wait_idle(ship_id)  # If we are currently occupied, wait
    ship = gameData.ship[ship_id]
    station = gameData.station
    
    gain_money = 0
    
    # If we aren't at the station, got there
    if ship["position"] != station["position"]:
        travel(ship["id"], station["position"])
    wait_idle(ship_id)  # If we are currently occupied, wait
    # Unload the cargo and sell it directly on the market
    for res, amnt in ship["cargo"]["resources"].items():
        if amnt == 0:
            continue
        _amnt = amnt
        for _ in range(int(amnt) // 1000 + 1):
            amnt_ = min(1000, _amnt)
            if amnt_ == 0:
                break
            print(f"[*] Unloading {amnt_} of {res} from ship {ship_id}")
            unloaded = service.unload(ship["id"], res, unloaded["unloaded"])
            sold = service.sell_resource(station["id"], res, unloaded["unloaded"])
            print(
                "[*] Unloaded and sold {} of {}, for {} credits".format(
                    unloaded["unloaded"], res, sold["added_money"] if sold else 0
                )
            )
            gain_money += sold["added_money"] if sold else 0
            _amnt -= unloaded["unloaded"]
    
    sid = gameData.ship[ship_id]["id"]
    data = service.get_player_status(gameData.player)
    ship_ = [d for d in data["ships"] if d["id"] == sid]
    if len(ship_) > 0 : gameData.ship[ship_id] = ship_[0]
    gameData.cost = data["costs"]
    gain_money -= ship_repair(ship_id)
    gain_money -= ship_refuel(ship_id)
    gameData.money += gain_money

def ship_repair(ship_id):
    req = int(gameData.ship[ship_id]["hull_decay"])
    # No need for any reparation
    if req == 0:
        return
    # In case we don't have enough hull plates in stock
    bought = service.buy_resource(gameData.station["id"], "hullplate", req)
    print(f"[*] Bought {req} of hull plates for", bought["removed_money"])
    repair = service.repair_ship(gameData.station["id"], gameData.ship[ship_id]["id"])
    print("[*] Repaired {} hull plates on the ship".format(repair["added-hull"]))
    return bought["removed_money"]

def ship_refuel(ship_id):
    req = int(gameData.ship[ship_id]["fuel_tank_capacity"] - gameData.ship[ship_id]["fuel_tank"])
    # No need for any refuel
    if req == 0:
        return
    bought = service.buy_resource(gameData.station["id"], "Fuel", req)
    print(f"[*] Bought {req} of fuel for", bought["removed_money"])
    refuel = service.refuel_ship(gameData.station["id"], gameData.ship[ship_id]["id"])
    print("[*] Refilled {} fuel on the ship for {} credits".format(refuel["added-fuel"], bought["removed_money"]))
    return bought["removed_money"]

def shopping(ship_id):
    shop_money = (gameData.money - gameData.cost * 60 * 5) * 0.8
    has_bought = True
    
    while has_bought:
        crew_upgrade_ = service.get_crew_upgrades(gameData.station["id"], gameData.ship[ship_id]["id"])
        for k, v in crew_upgrade_.items():
            if v["price"] < shop_money and (k not in max_lvl.keys() or gameData.ship[ship_id]["crew"][k] < max_lvl[k]):
                print(f"[*] Upgrading {k} for {v['price']} credits")
                service.upgrade_crew(gameData.station["id"], gameData.ship[ship_id]["id"], k)
                gameData.ship[ship_id]["crew"][k] += 1
                shop_money -= v["price"]
                has_bought = True
        
        module_upgrade_ = service.get_module_upgrade(gameData.station["id"], gameData.ship[ship_id]["id"])
        for k, v in module_upgrade_.items():
            if v["price"] < shop_money and (k not in max_lvl.keys() or gameData.ship[ship_id]["modules"][k] < max_lvl[k]):
                print(f"[*] Upgrading {k} for {v['price']} credits")
                service.upgrade_module(gameData.station["id"], gameData.ship[ship_id]["id"], k)
                gameData.ship[ship_id]["modules"][k] += 1
                shop_money -= v["price"]
                has_bought = True
                
        if gameData.upgrades_ship["CargoExpansion"] < shop_money:
                print(f"[*] Upgrading {k} for {v['price']} credits")
                service.upgrade_ship(gameData.station["id"], gameData.ship[ship_id]["id"], "CargoExpansion")
                gameData.ship[ship_id]["modules"]["CargoExpansion"] += 120
                shop_money -= v["price"]
                has_bought = True
                
    gameData.money -= (gameData.money - gameData.cost * 60 * 5) * 0.8 + shop_money