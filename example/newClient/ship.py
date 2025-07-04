import time
import traceback

from commun import get_dist, service, gameData, loop

max_lvl = {
    "Pilot": 15,
    "ReactorUpgrade": 100,
    "HullUpgrade": 1000,
    "Shield": 5,
}

upgrade_priority = [
    "ReactorUpgrade", "ReactorUpgrade", "CargoExpansion", "CargoExpansion", "CargoExpansion",
    "CargoExpansion", "CargoExpansion", "CargoExpansion", "CargoExpansion", "CargoExpansion"
]

async def new_ship():
    print("[*] Buying a new ship")
    ship_index = len(gameData.ship)
    gameData.ship.append({"data": {}, "planet": False, "lvl": 0})
    station_id = gameData.station["id"]
    available = service.get(f"/station/{station_id}/shipyard/list")["ships"]
    cheapest = sorted(available, key=lambda ship: ship["price"])[0]
    ship = service.get(f"/station/{station_id}/shipyard/buy/" + str(cheapest["id"]))["shipId"]
    pilot = service.get(f"/station/{station_id}/crew/hire/pilot")["id"]
    service.get(f"/station/{station_id}/crew/assign/{pilot}/{ship}/pilot")
    gameData.ship[ship_index]["data"] = service.get_ship(ship)
    get_most_profitables(ship_index)
    modtype = "Miner" if gameData.ship[ship_index]["planet"] else "GasSucker"
    mod_id = service.buy_module(station_id, ship, modtype)["id"]
    op = service.hire_crew(station_id, "operator")["id"]
    service.set_crew(station_id, ship, op, mod_id)
    gameData.ship[ship_index]["data"] = service.get_ship(ship)
    run(ship_index)
    
def get_most_profitables(ship_id):
        is_resources_solid = {
            "Copper": True,
            "Freon": False,
            "Gold": True,
            "Helium": False,
            "Iron": True,
            "Oxygen": False,
            "Ozone": False,
            "Stone": True,
        }

        if not gameData.solid_planet:
            return gameData.gaz_planet
        if not gameData.gaz_planet:
            return gameData.solid_planet

        gaz_travel_cost = (
            get_dist(gameData.station["position"], gameData.gaz_planet)
            / gameData.ship[ship_id]["data"]["stats"]["speed"]
        )
        solid_travel_cost = (
            get_dist(gameData.station["position"], gameData.solid_planet)
            / gameData.ship[ship_id]["data"]["stats"]["speed"]
        )

        prices = service.get_prices()["prices"]
        resources = [(key, value) for key, value in gameData.resources.items()]
        solid_ressources = [
            prices[x[0]] / x[1]["difficulty"] / x[1]["volume"]
            for x in resources
            if "min-rank" in x[1].keys() and is_resources_solid[x[0]] and x[1]["min-rank"]
        ]
        gaz_ressources = [
            prices[x[0]] / x[1]["difficulty"] / x[1]["volume"]
            for x in resources
            if "min-rank" in x[1].keys() and not is_resources_solid[x[0]] and x[1]["min-rank"]
        ]

        solid_value = (
            eval(" + ".join([str(s) for s in solid_ressources])) / len(solid_ressources)
            - solid_travel_cost
        )
        gaz_value = (
            eval(" + ".join([str(s) for s in gaz_ressources])) / len(gaz_ressources)
            - gaz_travel_cost
        )
        gameData.ship[ship_id]["planet"] = solid_value > gaz_value
    
def run(ship_id):
    print("[*] Starting the ship operation")
    while True:
        try:
            go_mine(ship_id)
            go_sell(ship_id)
            shopping(ship_id)
            print(gameData.ship[ship_id]["data"])
        except KeyboardInterrupt:
            print("\n[*] Exiting the game")
            break
        except Exception as e:
            if "This player lost the game and cannot play anymore" in str(e):
                print("!!! Player lost, exiting the game")
                break
            print(traceback.format_exc())
            print(f"!!! An error occurred: {e}")
        
    
def travel(ship_id, pos):
        costs = service.navigate(gameData.ship[ship_id]["data"]["id"], pos)
        print("[*] Traveling to {}, will take {}".format(pos, costs["duration"]))
        time.sleep(costs["duration"])
        
def wait_idle(ship_id, ts = 0.1):
    state = service.get_ship(gameData.ship[ship_id]["data"]["id"])["state"]
    while state != "Idle":
        state = service.get_ship(gameData.ship[ship_id]["data"]["id"])["state"]
        time.sleep(ts)

def go_mine(ship_id):
        print("[*] Starting the Mining operation")
        mvp = gameData.solid_planet if gameData.ship[ship_id]["planet"] else gameData.gaz_planet
        
        wait_idle(ship_id)  # If we are currently occupied, wait

        # If we are not current at the position of the target planet, travel there
        if gameData.ship[ship_id]["data"]["position"] != mvp:
            travel(ship_id, mvp)

        wait_idle(ship_id)  # If we are currently occupied, wait

        # Now that we are there, let's start mining
        info = service.start_mining(gameData.ship[ship_id]["data"]["id"])
        print("[*] Starting extraction:")
        for res, amnt in info.items():
            print(f"\t- Extraction of {res}: {amnt}/sec")

        sid = gameData.ship[ship_id]["data"]["id"]
        data = service.get_player_status(gameData.player)
        ship_ = [d for d in data["ships"] if d["id"] == sid]
        if len(ship_) > 0 : gameData.ship[ship_id]["data"] = ship_[0]
        
        # Wait until the cargo is full
        wait_idle(ship_id)
        print("[*] The cargo is full, stopping mining process")
        
def go_sell(ship_id):
    wait_idle(ship_id)  # If we are currently occupied, wait
    gameData.ship[ship_id]["data"] = service.get_ship(gameData.ship[ship_id]["data"]["id"])
    ship = gameData.ship[ship_id]["data"]
    station = gameData.station
    
    gain_money = 0
    
    # If we aren't at the station, got there
    if ship["position"] != station["position"]:
        travel(ship_id, station["position"])
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
            unloaded = service.unload(ship["id"], res, amnt_)
            sold = service.sell_resource(station["id"], res, unloaded["unloaded"])
            print(
                "[*] Unloaded and sold {} of {}, for {} credits".format(
                    unloaded["unloaded"], res, sold["added_money"] if sold else 0
                )
            )
            gain_money += sold["added_money"] if sold else 0
            _amnt -= unloaded["unloaded"]
    
    sid = gameData.ship[ship_id]["data"]["id"]
    data = service.get_player_status(gameData.player)
    ship_ = [d for d in data["ships"] if d["id"] == sid]
    if len(ship_) > 0 : gameData.ship[ship_id]["data"] = ship_[0]
    gameData.cost = data["costs"]
    gain_money -= ship_repair(ship_id)
    gain_money -= ship_refuel(ship_id)
    gameData.money += gain_money

def ship_repair(ship_id):
    req = int(gameData.ship[ship_id]["data"]["hull_decay"])
    # No need for any reparation
    if req == 0:
        return
    # In case we don't have enough hull plates in stock
    bought = service.buy_resource(gameData.station["id"], "hullplate", req)
    print(f"[*] Bought {req} of hull plates for", bought["removed_money"])
    repair = service.repair_ship(gameData.station["id"], gameData.ship[ship_id]["data"]["id"])
    print("[*] Repaired {} hull plates on the ship".format(repair["added-hull"]))
    return bought["removed_money"] if bought else 0

def ship_refuel(ship_id):
    req = int(gameData.ship[ship_id]["data"]["fuel_tank_capacity"] - gameData.ship[ship_id]["data"]["fuel_tank"])
    # No need for any refuel
    if req == 0:
        return
    bought = service.buy_resource(gameData.station["id"], "Fuel", req)
    print(f"[*] Bought {req} of fuel for", bought["removed_money"])
    refuel = service.refuel_ship(gameData.station["id"], gameData.ship[ship_id]["data"]["id"])
    print("[*] Refilled {} fuel on the ship for {} credits".format(refuel["added-fuel"], bought["removed_money"]))
    return bought["removed_money"] if bought else 0

def shopping(ship_id):
    shop_money = (gameData.money - gameData.cost * 60 * 5) * 0.9
    gameData.money -= shop_money
    
    print(len(gameData.ship), gameData.max_ship, gameData.ship[ship_id]["lvl"])
    if len(gameData.ship) < gameData.max_ship and gameData.ship[ship_id]["lvl"] > 25:
        gameData.new_ship_money += shop_money * 0.1
        shop_money *= 0.9
        print(f"[*] You have {gameData.new_ship_money} credits for a new ship")
        if gameData.new_ship_money > 100000:
            print("[*] You have enough money to buy a new ship, buying one")
            gameData.new_ship_money -= 100000
            loop.create_task(new_ship())
            return
    
    has_bought = True
    
    while has_bought:
        has_bought = False
        crew_upgrade_ = service.get_crew_upgrades(gameData.station["id"], gameData.ship[ship_id]["data"]["id"])
        for k, v in crew_upgrade_.items():
            if gameData.ship[ship_id]["lvl"] < len(upgrade_priority) and upgrade_priority[gameData.ship[ship_id]["lvl"]] != k: continue
            if v["price"] < shop_money and (k not in max_lvl.keys() or gameData.ship[ship_id]["data"]["crew"][k] < max_lvl[k]):
                print(f"[*] Upgrading {k} for {v['price']} credits")
                service.upgrade_crew(gameData.station["id"], gameData.ship[ship_id]["data"]["id"], k)
                gameData.ship[ship_id]["data"]["crew"][k]["rank"] += 1
                shop_money -= v["price"]
                gameData.ship[ship_id]["lvl"] += 1
                has_bought = True
        
        module_upgrade_ = service.get_module_upgrade(gameData.station["id"], gameData.ship[ship_id]["data"]["id"])
        for k, v in module_upgrade_.items():
            if gameData.ship[ship_id]["lvl"] < len(upgrade_priority) and upgrade_priority[gameData.ship[ship_id]["lvl"]] != k: continue
            if v["price"] < shop_money and (k not in max_lvl.keys() or gameData.ship[ship_id]["data"]["modules"][k] < max_lvl[k]):
                print(f"[*] Upgrading {k} for {v['price']} credits")
                service.upgrade_module(gameData.station["id"], gameData.ship[ship_id]["data"]["id"], k)
                gameData.ship[ship_id]["data"]["modules"][k]["rank"] += 1
                shop_money -= v["price"]
                gameData.ship[ship_id]["lvl"] += 1
                has_bought = True
                
        if (not(gameData.ship[ship_id]["lvl"] < len(upgrade_priority) and upgrade_priority[gameData.ship[ship_id]["lvl"]] != "ReactorUpgrade"))\
            and gameData.upgrades_ship["ReactorUpgrade"] < shop_money and gameData.ship[ship_id]["data"]["reactor_power"] < max_lvl["ReactorUpgrade"]:
                print(f"[*] Upgrading ReactorUpgrade for {v['price']} credits")
                service.upgrade_ship(gameData.station["id"], gameData.ship[ship_id]["data"]["id"], "ReactorUpgrade")
                gameData.ship[ship_id]["data"]["cargo"]["capacity"] += 120
                shop_money -= v["price"]
                gameData.ship[ship_id]["lvl"] += 1
                has_bought = True
                
        if (not(gameData.ship[ship_id]["lvl"] < len(upgrade_priority) and upgrade_priority[gameData.ship[ship_id]["lvl"]] != "CargoExpansion"))\
            and gameData.upgrades_ship["CargoExpansion"] < shop_money:
                print(f"[*] Upgrading CargoExpansion for {v['price']} credits")
                service.upgrade_ship(gameData.station["id"], gameData.ship[ship_id]["data"]["id"], "CargoExpansion")
                gameData.ship[ship_id]["data"]["cargo"]["capacity"] += 120
                shop_money -= v["price"]
                gameData.ship[ship_id]["lvl"] += 1
                has_bought = True
    gameData.money += shop_money