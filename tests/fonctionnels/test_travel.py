
import unittest

from commun import get, init_first_ship_crew


class TestUpgrade(unittest.TestCase):
    def test_travel(self):
        player_id, key, station_id, ships_id = init_first_ship_crew("test_travel", True)
        
        pla = get(f"/station/{station_id}/scan", key=key)["planets"][0]["position"]
    
        costs = get(f"/ship/{ships_id}/navigate/{pla[0]}/{pla[1]}/{pla[2]}",  key=key)["duration"]

        # è_é
        status = get(f"/player/{player_id}",  key=key)["ships"][0]["state"]
        
        start = get(f"/player/{player_id}", key=key)["ships"][0]["position"]
        
        get("/tick")
        current = get(f"/player/{player_id}", key=key)["ships"][0]["position"]
        self.assertEqual(list(status.keys())[0], "InFlight")
        self.assertNotEqual(current, pla)
        self.assertNotEqual(current, start)
        
        get(f"/tick/{int(costs * 50) - 1}")
        current = get(f"/player/{player_id}", key=key)["ships"][0]["position"]
        status = get(f"/player/{player_id}",  key=key)["ships"][0]["state"]
        self.assertEqual(list(status.keys())[0], "InFlight")
        self.assertNotEqual(current, pla)
        self.assertNotEqual(current, start)
        
        
        get(f"/tick")
        status = get(f"/player/{player_id}",  key=key)["ships"][0]["state"]        
        current = get(f"/player/{player_id}", key=key)["ships"][0]["position"]
        self.assertEqual(current, pla)
        self.assertEqual(status, "Idle")


        
