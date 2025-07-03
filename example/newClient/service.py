import urllib.request
import json
from typing import Optional

from error import SimeisError

class Service:
    URL: str
    
    def __init__(self, url):
        self.URL = url
        
    def get(self, path, **qry):
        if hasattr(self, "key"):
            qry["key"] = self.key

        tail = ""
        if len(qry) > 0:
            tail += "?"
            tail += "&".join(
                ["{}={}".format(k, urllib.parse.quote(v)) for k, v in qry.items()]
            )

        qry = f"{self.URL}{path}{tail}"
        reply = urllib.request.urlopen(qry, timeout=60)

        data = json.loads(reply.read().decode())
        err = data.pop("error")
        if err != "ok":
            raise SimeisError(err)

        return data
        
    def ping(self):
        return self.get("/ping")
    
    def get_player_status(self, player):
        return self.get("/player/" + str(player))
    
    def new_player(self, username):
        player = self.get(f"/player/new/{username}")
        self.key = player["key"]
        return player
    
    def get_sattion(self, station):
        return self.get(f"/station/{station}")
    
    def get_prices(self):
        return self.get("/market/prices")
    
    def get_ship(self, ship):
        return self.get(f"/ship/{ship}")
    
    def scan(self, station):
        return self.get(f"/station/{station}/scan")
    
    def get_resources(self):
        return self.get("/resources")
    
    def list_shipyard(self, station):
        return self.get(f"/station/{station}/shipyard/list")
    
    def buy_ship(self, station, ship):
        return self.get(f"/station/{station}/shipyard/buy/{ship}")
    
    def get_modules(self, station):
        return self.get(f"/station/{station}/shop/modules")
    
    def buy_module(self, station, ship, module):
        return self.get(f"/station/{station}/shop/modules/{ship}/buy/{module}")
    
    def hire_crew(self, station, crew):
        return self.get(f"/station/{station}/crew/hire/{crew}")
    
    def set_crew(self, station, ship, crew, post):
        return self.get(f"/station/{station}/crew/assign/{crew}/{ship}/{post}")
    
    def set_trader(self, station, trader):
        return self.get(f"/station/{station}/crew/assign/{trader}/trading")
    
    def navigate(self, ship, coord):
        return self.get(f"/ship/{ship}/navigate/{coord[0]}/{coord[1]}/{coord[2]}")
    
    def buy_resource(self, station, resource, amount):
        return self.get(f"/market/{station}/buy/{resource}/{amount}")
    
    def repair_ship(self, station, ship):
        return self.get(f"/station/{station}/repair/{ship}")
    
    def refuel_ship(self, station, ship):
        return self.get(f"/station/{station}/refuel/{ship}")
    
    def start_mining(self, ship):
        return self.get(f"/ship/{ship}/extraction/start")
    
    def unload(self, ship, resources, amount):
        return self.get(f"/ship/{ship}/unload/{resources}/{amount}")
                        
    def sell_resource(self, station, resource, amount):
        return self.get(f"/market/{station}/sell/{resource}/{amount}")
    
    #----- get upgrades -----#
    
    def get_ship_upgrades(self, station):
        return self.get(f"/station/{station}/shipyard/upgrade")
    
    def get_crew_upgrades(self, station, ship):
        return self.get(f"/station/{station}/crew/upgrade/ship/{ship}")
    
    def get_station_upgrades(self, station):
        return self.get(f"/station/{station}/shipyard/upgrade")
    
    def get_module_upgrade(self, station, ship):
        return self.get(f"/station/{station}/shop/modules/{ship}/upgrade")
    
    #----- upgrades -----#
    
    def upgrade_station(self, station, amount):
        return self.get(f"/station/{station}/shop/cargo/buy/{amount}")
    
    def upgrade_trader(self, station):
        return self.get(f"/station/{station}/crew/upgrade/trader")
    
    def upgrade_ship(self, station, ship, upgrade):
        return self.get(f"/station/{station}/shipyard/upgrade/{ship}/{upgrade}")
    
    def upgrade_crew(self, station, ship, crew):
        print(f"Upgrading crew {crew} on ship {ship} at station {station}")
        return self.get(f"/station/{station}/crew/upgrade/ship/{ship}/{crew}")
    
    def upgrade_module(self, station, ship, module):
        return self.get(f"/station/{station}/shop/modules/{ship}/upgrade/{module}")
        
    