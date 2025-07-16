import unittest
import os
import tempfile
import shutil
from commun import get, init_new_player

# Je ne veux pas de unittest, surement proposé par ChatGPT
class TestScenario1(unittest.TestCase):

    # Tout ceci ne sert à rien
    # --------SNIP-------
    # --------SNIP-------
    
    def test_scenario(self):
        try:
            player_id, key, station_id = init_new_player(self.test_username)
            initial_status = get(f"/player/{player_id}", key=key)
            initial_money = initial_status["money"]
            print(f"Argent de départ: {initial_money}")
            
            trader = get(f"/station/{station_id}/crew/hire/trader", key=key)["id"]
            self.assertIn(str(trader), get(f"/station/{station_id}", key=key)["idle_crew"])
            
            get(f"/station/{station_id}/crew/assign/{trader}/trading", key=key)
            self.assertEqual(get(f"/station/{station_id}", key=key)["trader"], trader)
            
            available_ship = get(f"/station/{station_id}/shipyard/list", key=key)["ships"]
            cheapest_ship = sorted(available_ship, key=lambda ship: ship["price"])[0]
            get(f"/station/{station_id}/shipyard/buy/{cheapest_ship['id']}", key=key)
            
            data = get(f"/player/{player_id}", key=key)
            ships = data["ships"]
            self.assertTrue(ships)

            current_money = data["money"]
            self.assertLess(current_money, initial_money)
            initial_money = current_money
            

            pilot = get(f"/station/{station_id}/crew/hire/pilot", key=key)["id"]
            self.assertIn(str(pilot), get(f"/station/{station_id}", key=key)["idle_crew"])

            get(f"/station/{station_id}/crew/assign/{pilot}/{ships[0]['id']}/pilot", key=key)
            self.assertEqual(get(f"/ship/{ships[0]['id']}", key=key)["pilot"], pilot)
            
            modtype = list(get(f"/station/{station_id}/shop/modules", key=key).keys())[0]
            mod_id = get(f"/station/{station_id}/shop/modules/{ships[0]['id']}/buy/{modtype}", key=key)["id"]

            data = get(f"/player/{player_id}", key=key)
            current_money = data["money"]

            self.assertLess(current_money, initial_money)
            initial_money = current_money
            
            op = get(f"/station/{station_id}/crew/hire/operator", key=key)["id"]
            get(f"/station/{station_id}/crew/assign/{op}/{ships[0]['id']}/{mod_id}", key=key)

            module_info = get(f"/ship/{ships[0]['id']}", key=key)["modules"][str(mod_id)]
            self.assertEqual(module_info["operator"], op)
        
        except Exception as e:
            self.fail(f"Erreur inattendue: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
