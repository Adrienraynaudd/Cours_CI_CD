import unittest

from commun import get, init_first_ship_crew

class TestUpgrade(unittest.TestCase):
    def get_cost(self, player_id, key):
        return get(f"/player/{player_id}", key=key)["costs"]
    
    # Upgrade trader
    def test_upgrade_trader(self):
        player_id, key, station_id, ships_id = init_first_ship_crew("test-upgrade-crew-trader", True)
        base_cost = self.get_cost(player_id, key)
        base_rate = get(f"/market/{station_id}/fee_rate", key=key)["fee_rate"]
        
        data = get(f"/station/{station_id}", key=key)
        base_trader_lvl = data["crew"][str(data["trader"])]["rank"]
        
        get(f"/station/{station_id}/crew/upgrade/trader", key=key)
    
        data = get(f"/station/{station_id}", key=key)
        self.assertEqual(data["crew"][str(data["trader"])]["rank"], base_trader_lvl + 1)
        self.assertGreater(self.get_cost(player_id, key), base_cost)
        self.assertLess(get(f"/market/{station_id}/fee_rate", key=key)["fee_rate"], base_rate)
        
    def test_upgrade_pilot(self):
        player_id, key, station_id, ships_id = init_first_ship_crew("test-upgrade-pilot", True)
        base_cost = self.get_cost(player_id, key)
        ship_data = get(f"/ship/{ships_id}", key=key)
        base_speed = ship_data["stats"]["speed"]
        pilot_id = ship_data["pilot"]
        base_pilot_lvl = ship_data["crew"][str(ship_data["pilot"])]["rank"]
        
        get(f"/station/{station_id}/crew/upgrade/ship/{ships_id}/{pilot_id}", key=key)
    
        data = get(f"/ship/{ships_id}", key=key)
        self.assertEqual(data["crew"][str(data["pilot"])]["rank"], base_pilot_lvl + 1)
        self.assertGreater(self.get_cost(player_id, key), base_cost)
        self.assertGreater(get(f"/ship/{ships_id}", key=key)["stats"]["speed"], base_speed)
        
    def test_upgrade_operator(self):
        player_id, key, station_id, ships_id = init_first_ship_crew("test-upgrade-crew-op", True)
        base_cost = self.get_cost(player_id, key)
        pla = get(f"/station/{station_id}/scan", key=key)["planets"]
        planet_pos = [p["position"] for p in pla if p["solid"]]
        if len(planet_pos) == 0:
            mod_id = get(f"/station/{station_id}/shop/modules/{ships_id}/buy/GasSucker", key=key)["id"]
            op = get(f"/station/{station_id}/crew/hire/operator", key=key)["id"]
            get(f"/station/{station_id}/crew/assign/{op}/{ships_id}/{mod_id}", key=key)
            ship_data = get(f"/ship/{ships_id}", key=key)
            operator_id = ship_data["modules"][str(mod_id)]["operator"]
            planet_pos = pla[0]["position"]
        else:
            ship_data = get(f"/ship/{ships_id}", key=key)
            operator_id = list(ship_data["modules"].values())[0]["operator"]
            planet_pos = planet_pos[0]
        base_operator_lvl = ship_data["crew"][str(operator_id)]["rank"]
        duration = get(f"/ship/{ships_id}/navigate/{planet_pos[0]}/{planet_pos[1]}/{planet_pos[2]}", key=key)["duration"]
        get(f"/tick/{int((duration + 1) * 50) }")
        base_info = get(f"/ship/{ships_id}/extraction/start", key=key)
        get("/tick")
        get(f"/ship/{ships_id}/extraction/stop", key=key)
        get("/tick")
        station_pos = get(f"/station/{station_id}", key=key)["position"]
        duration = get(f"/ship/{ships_id}/navigate/{station_pos[0]}/{station_pos[1]}/{station_pos[2]}", key=key)["duration"]
        get(f"/tick/{int((duration + 1) * 50) }")
        
        get(f"/station/{station_id}/crew/upgrade/ship/{ships_id}/{operator_id}", key=key)
    
        data = get(f"/ship/{ships_id}", key=key)
        self.assertEqual(data["crew"][str(operator_id)]["rank"], base_operator_lvl + 1)
        self.assertGreater(self.get_cost(player_id, key), base_cost)
        duration = get(f"/ship/{ships_id}/navigate/{planet_pos[0]}/{planet_pos[1]}/{planet_pos[2]}", key=key)["duration"]
        get(f"/tick/{int((duration + 1) * 50) }")
        info = get(f"/ship/{ships_id}/extraction/start", key=key)
        self.assertGreaterEqual(len(list(info.keys())), len(list(base_info.keys())))
        def_key = list(base_info.keys())[0]
        self.assertGreater(info[def_key], base_info[def_key])