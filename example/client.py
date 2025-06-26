PORT = 8080
URL = f"http://127.0.0.1:{PORT}"

import os
import sys
import math
import time
import json
import string
import urllib.request


class SimeisError(Exception):
    pass


# Théorème de Pythagore pour récupérer la distance entre 2 points dans l'espace 3D
def get_dist(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))

# Check if types are present in the list
def check_has(alld, key, *req):
    alltypes = [c[key] for c in alld.values()]
    return all([k in alltypes for k in req])

class Game:
    def __init__(self, username):
        # Init connection & setup player
        assert self.get("/ping")["ping"] == "pong"
        print("[*] Connection to server OK")
        self.setup_player(username)

        # Useful for our game loops
        self.pid = self.player["playerId"]  # ID of our player
        self.sid = None  # ID of our ship
        self.sta = None  # ID of our station

    def get(self, path, **qry):
        if hasattr(self, "player"):
            qry["key"] = self.player["key"]

        tail = ""
        if len(qry) > 0:
            tail += "?"
            tail += "&".join(
                ["{}={}".format(k, urllib.parse.quote(v)) for k, v in qry.items()]
            )

        qry = f"{URL}{path}{tail}"
        reply = urllib.request.urlopen(qry, timeout=60)

        data = json.loads(reply.read().decode())
        err = data.pop("error")
        if err != "ok":
            raise SimeisError(err)

        return data

    def disp_status(self):
        status = game.get("/player/" + str(game.pid))
        print(
            "[*] Current status: {} credits, costs: {}, time left before lost: {} secs".format(
                round(status["money"], 2),
                round(status["costs"], 2),
                int(status["money"] / status["costs"]),
            )
        )
        return (
            round(status["money"], 2),
            round(status["costs"], 2),
            int(status["money"] / status["costs"]),
        )

    # If we have a file containing the player ID and key, use it
    # If not, let's create a new player
    # If the player has lost, print an error message
    def setup_player(self, username, force_register=False):
        # Sanitize the username, remove any symbols
        username = "".join(
            [c for c in username if c in string.ascii_letters + string.digits]
        ).lower()

        # If we don't have any existing account
        if force_register or not os.path.isfile(f"./{username}.json"):
            player = self.get(f"/player/new/{username}")
            with open(f"./{username}.json", "w") as f:
                json.dump(player, f, indent=2)
            print(f"[*] Created player {username}")
            self.player = player

        # If an account already exists
        else:
            with open(f"./{username}.json", "r") as f:
                self.player = json.load(f)
            print(f"[*] Loaded data for player {username}")

        # Try to get the profile
        try:
            player = self.get("/player/{}".format(self.player["playerId"]))

        # If we fail, that must be that the player doesn't exist on the server
        except SimeisError:
            # And so we retry but forcing to register a new account
            return self.setup_player(username, force_register=True)

        # If the player already failed, we must reset the server
        # Or recreate an account with a new nickname
        if player["money"] <= 0.0:
            print(
                "!!! Player already lost, please restart the server to reset the game"
            )
            sys.exit(0)

    def get_resources(self):
        # Get the resources available in the station
        res = self.get("/resources")
        print("[*] Resources available in station {}:".format(res))

    def get_most_profitables(self, sid):
        station = self.get(f"/station/{self.sta}")
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
        ship = self.get(f"/ship/{sid}")
        # print(ship)
        planets = self.get(f"/station/{self.sta}/scan")["planets"]
        # print(planets)
        solid_planets = [pla for pla in planets if pla["solid"]]
        if len(solid_planets) != 0:
            solid_planets = sorted(
                solid_planets,
                key=lambda pla: get_dist(station["position"], pla["position"]),
            )[0]

        gaz_planets = [pla for pla in planets if not pla["solid"]]
        if len(gaz_planets) != 0:
            gaz_planets = sorted(
                gaz_planets,
                key=lambda pla: get_dist(station["position"], pla["position"]),
            )[0]

        if len(solid_planets) == 0:
            return gaz_planets
        if len(gaz_planets) == 0:
            return solid_planets

        gaz_travel_cost = (
            get_dist(station["position"], gaz_planets["position"])
            / ship["stats"]["speed"]
        )
        solid_travel_cost = (
            get_dist(station["position"], solid_planets["position"])
            / ship["stats"]["speed"]
        )

        resources = self.get("/resources")
        # print(resources)
        prices = self.get("/market/prices")["prices"]
        # print(prices)
        # print(ship)
        miner_lvl = 0
        gas_lvl = 0
        for m in ship["modules"].values():
            if m["modtype"] == "Miner":
                miner_lvl = m["rank"]
            if m["modtype"] == "GasSucker":
                gas_lvl = m["rank"]
        # print(resources)
        resources = [(key, value) for key, value in resources.items()]
        solid_ressources = [
            prices[x[0]] / x[1]["difficulty"] / x[1]["volume"]
            for x in resources
            if "min-rank" in x[1].keys() and is_resources_solid[x[0]] and x[1]["min-rank"] <= miner_lvl
        ]
        gaz_ressources = [
            prices[x[0]] / x[1]["difficulty"] / x[1]["volume"]
            for x in resources
            if "min-rank" in x[1].keys() and not is_resources_solid[x[0]] and x[1]["min-rank"] <= gas_lvl
        ]

        solid_value = (
            eval(" + ".join([str(s) for s in solid_ressources])) / len(solid_ressources)
            - solid_travel_cost
        )
        gaz_value = (
            eval(" + ".join([str(s) for s in gaz_ressources])) / len(gaz_ressources)
            - gaz_travel_cost
        )
        mvp = [gaz_planets, solid_planets][solid_value > gaz_value]
        # print(mvp)
        return mvp

    def buy_first_ship(self, sta):
        # Get all the ships available for purchasing in the station
        available = self.get(f"/station/{sta}/shipyard/list")["ships"]
        # Get the cheapest option
        cheapest = sorted(available, key=lambda ship: ship["price"])[0]
        print("[*] Purchasing the first ship for {} credits".format(cheapest["price"]))
        # Buy it
        self.get(f"/station/{sta}/shipyard/buy/" + str(cheapest["id"]))

    def buy_first_mining_module(self, modtype, sta, sid):
        # Buy the mining module
        all = self.get(f"/station/{sta}/shop/modules")
        mod_id = self.get(f"/station/{sta}/shop/modules/{sid}/buy/{modtype}")["id"]

        # Check if we have the crew assigned on this module
        # If not, hire an operator, and assign it to the mining module of our ship
        ship = self.get(f"/ship/{sid}")
        if not check_has(ship["crew"], "member_type", "Operator"):
            op = self.get(f"/station/{sta}/crew/hire/operator")["id"]
            self.get(f"/station/{sta}/crew/assign/{op}/{sid}/{mod_id}")

    def hire_first_pilot(self, sta, ship):
        # Hire a pilot, and assign it to our ship
        pilot = self.get(f"/station/{sta}/crew/hire/pilot")["id"]
        self.get(f"/station/{sta}/crew/assign/{pilot}/{ship}/pilot")

    def hire_first_trader(self, sta):
        # Hire a trader, assign it on our station
        trader = self.get(f"/station/{sta}/crew/hire/trader")["id"]
        self.get(f"/station/{sta}/crew/assign/{trader}/trading")

    def travel(self, sid, pos):
        costs = self.get(f"/ship/{sid}/navigate/{pos[0]}/{pos[1]}/{pos[2]}")
        print("[*] Traveling to {}, will take {}".format(pos, costs["duration"]))
        time.sleep(costs["duration"])

    def wait_idle(self, sid, ts=0.1):
        ship = self.get(f"/ship/{sid}")
        while ship["state"] != "Idle":
            time.sleep(ts)
            ship = self.get(f"/ship/{sid}")

    # Repair the ship:     Buy the plates, then ask for reparation
    def ship_repair(self, sid):
        ship = self.get(f"/ship/{sid}")
        req = int(ship["hull_decay"])

        # No need for any reparation
        if req == 0:
            return

        # In case we don't have enough hull plates in stock
        station = self.get(f"/station/{self.sta}")["cargo"]
        if "HullPlate" not in station["resources"]:
            station["resources"]["HullPlate"] = 0
        if station["resources"]["HullPlate"] < req:
            need = req - station["resources"]["HullPlate"]
            bought = self.get(f"/market/{self.sta}/buy/hullplate/{need}")
            print(f"[*] Bought {need} of hull plates for", bought["removed_money"])
            station = self.get(f"/station/{self.sta}")["cargo"]

        if station["resources"]["HullPlate"] > 0:
            # Use the plates in stock to repair the ship
            repair = self.get(f"/station/{self.sta}/repair/{self.sid}")
            print(
                "[*] Repaired {} hull plates on the ship".format(repair["added-hull"])
            )

    # Refuel the ship:    Buy the fuel, then ask for a refill
    def ship_refuel(self, sid):
        ship = self.get(f"/ship/{sid}")
        req = int(ship["fuel_tank_capacity"] - ship["fuel_tank"])

        # No need for any refuel
        if req == 0:
            return

        # In case we don't have enough fuel in stock
        station = self.get(f"/station/{self.sta}")["cargo"]
        if "Fuel" not in station["resources"]:
            station["resources"]["Fuel"] = 0
        if station["resources"]["Fuel"] < req:
            need = req - station["resources"]["Fuel"]
            bought = self.get(f"/market/{self.sta}/buy/Fuel/{need}")
            print(f"[*] Bought {need} of fuel for", bought["removed_money"])
            station = self.get(f"/station/{self.sta}")["cargo"]

        if station["resources"]["Fuel"] > 0:
            # Use the fuel in stock to refill the ship
            refuel = self.get(f"/station/{self.sta}/refuel/{self.sid}")
            print(
                "[*] Refilled {} fuel on the ship for {} credits".format(
                    refuel["added-fuel"],
                    bought["removed_money"],
                )
            )

    # Initializes the game:
    #     - Ensure our player exists
    #     - Ensure our station has a Trader hired
    #     - Ensure we own a ship
    #     - Setup the ship
    #         - Hire a pilot & assign it to our ship
    #         - Buy a mining module to be able to farm
    #         - Hire an operator & assign it on the mining module of our ship
    def init_game(self):
        # Ensure we own a ship, buy one if we don't
        status = self.get(f"/player/{self.pid}")
        self.sta = list(status["stations"].keys())[0]
        station = self.get(f"/station/{self.sta}")

        if not check_has(station["crew"], "member_type", "Trader"):
            self.hire_first_trader(self.sta)
            print("[*] Hired a trader, assigned it on station", self.sta)

        if len(status["ships"]) == 0:
            self.buy_first_ship(self.sta)
            status = self.get(f"/player/{self.pid}")  # Update our status
        ship = status["ships"][0]
        self.sid = ship["id"]

        # Ensure our ship has a crew, hire one if we don't
        if not check_has(ship["crew"], "member_type", "Pilot"):
            self.hire_first_pilot(self.sta, self.sid)
            print("[*] Hired a pilot, assigned it on ship", self.sid)

        print("[*] Game initialisation finished successfully")

    # - Find the nearest planet we can mine
    # - Go there
    # - Fill our cargo with resources
    # - Once the cargo is full, we stop mining, and this function returns
    def go_mine(self):
        print("[*] Starting the Mining operation")
        mvp = game.get_most_profitables(self.sid)

        # If the planet is solid, we need a Miner to mine it
        # If it's gaseous, we need a GasSucker to mine it
        if mvp["solid"]:
            modtype = "Miner"
        else:
            modtype = "GasSucker"

        # Ensure the ship has a corresponding module, buy one if we don't
        ship = self.get(f"/ship/{self.sid}")
        print("[*] Ship info:", ship)
        if not check_has(ship["modules"], "modtype", modtype):
            self.buy_first_mining_module(modtype, self.sta, self.sid)
        print("[*] Targeting planet at", mvp["position"])

        self.wait_idle(self.sid)  # If we are currently occupied, wait

        # If we are not current at the position of the target planet, travel there
        if ship["position"] != mvp["position"]:
            self.travel(ship["id"], mvp["position"])

        self.wait_idle(self.sid)  # If we are currently occupied, wait

        # Now that we are there, let's start mining
        info = self.get(f"/ship/{self.sid}/extraction/start")
        print("[*] Starting extraction:")
        for res, amnt in info.items():
            print(f"\t- Extraction of {res}: {amnt}/sec")

        # Wait until the cargo is full
        self.wait_idle(
            self.sid
        )  # The ship will have the state "Idle" once the cargo is full
        print("[*] The cargo is full, stopping mining process")

    # - Go back to the station
    # - Unload all the cargo
    # - Sell it on the market
    # - Refuel & repair the ship
    def go_sell(self):
        self.wait_idle(self.sid)  # If we are currently occupied, wait
        ship = self.get(f"/ship/{self.sid}")
        station = self.get(f"/station/{self.sta}")
        # print(station)
        # resources = self.get("/resources")
        # prices = self.get("/market/prices")["prices"]

        # If we aren't at the station, got there
        if ship["position"] != station["position"]:
            self.travel(ship["id"], station["position"])

        self.wait_idle(self.sid)  # If we are currently occupied, wait

        # Unload the cargo and sell it directly on the market
        for res, amnt in ship["cargo"]["resources"].items():
            if amnt == 0.0:
                continue
            unloaded = self.get(f"/ship/{self.sid}/unload/{res}/{amnt}")
            # sold = None
            # if prices[res] - resources[res]["base-price"] > 0 or station["cargo"]['usage'] / station["cargo"]['capacity'] > 0.8:
            sold = self.get(f"/market/{self.sta}/sell/{res}/{amnt}")
            print(
                "[*] Unloaded and sold {} of {}, for {} credits".format(
                    unloaded["unloaded"], res, sold["added_money"] if sold else 0
                )
            )

        self.ship_repair(self.sid)
        self.ship_refuel(self.sid)

        self.shopping()

    def shopping(self):
        player = self.get(f"/player/{self.pid}")
        money = player["money"]
        conso = player["costs"]
        upgrade = []

        shipyard_upgrade = self.get(f"/station/{self.sta}/shipyard/upgrade")
        for k, v in shipyard_upgrade.items():
            upgrade.append(
                (f"/station/{self.sta}/shipyard/upgrade/{self.sid}/{k}", v["price"], 100)
            )

        station_upgrade = self.get(f"/station/{self.sta}/upgrades")
        upgrade.append(
            (
                f" /station/{self.sta}/crew/upgrade/trader",
                station_upgrade["trader-upgrade"],
                1,
            )
        )

        crew_upgrade = self.get(f"/station/{self.sta}/crew/upgrade/ship/{self.sid}")
        for k, v in crew_upgrade.items():
            upgrade.append(
                (f"/station/{self.sta}/crew/upgrade/ship/{self.sid}/{k}", v["price"], 1.1)
            )

        module_upgrade = self.get(
            f" /station/{self.sta}/shop/modules/{self.sid}/upgrade"
        )
        for k, v in module_upgrade.items():
            upgrade.append(
                (
                    f"/station/{self.sta}/shop/modules/{self.sid}/upgrade/{k}",
                    v["price"],
                    1.05,
                )
            )

        upgrade = sorted(upgrade, key=lambda x: x[1] * x[2])
        for u in upgrade:
            if money - 5*60*conso >= u[1] * u[2]:
                print(f"[*] Buying {u[0]} for {u[1]} credits")
                self.get(u[0])
                money -= u[1]


if __name__ == "__main__":
    name = sys.argv[1]
    game = Game(name)
    game.init_game()

    while True:
        try:
            game.disp_status()
            game.go_mine()

            game.disp_status()
            game.go_sell()
        except:
            pass
