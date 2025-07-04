from commun import service, gameData, get_dist, loop
from ship import new_ship

def set_up(name):
    gameData.player = service.new_player(name)["playerId"]
    data = service.get_player_status(gameData.player)
    gameData.station = service.get_sattion(list(data["stations"].keys())[0])
    station_id = gameData.station["id"]
    trader = service.get(f"/station/{station_id}/crew/hire/trader")["id"]
    service.get(f"/station/{station_id}/crew/assign/{trader}/trading")
    set_planet()
    set_upgrades()
    loop.create_task(new_ship())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

def set_planet():
    planets = service.scan(gameData.station["id"])["planets"]
    solid_planets = [pla for pla in planets if pla["solid"]]
    if len(solid_planets) != 0:
        gameData.solid_planet = sorted(
            solid_planets,
            key=lambda pla: get_dist(gameData.station["position"], pla["position"]),
        )[0]["position"]
    gaz_planets = [pla for pla in planets if not pla["solid"]]
    if len(gaz_planets) != 0:
        gameData.gaz_planet = sorted(
            gaz_planets,
            key=lambda pla: get_dist(gameData.station["position"], pla["position"]),
        )[0]["position"]
        
def set_upgrades():
    upgrades = {}
    
    shipyard_upgrade = service.get_ship_upgrades(gameData.station["id"])
    for k, v in shipyard_upgrade.items():
        upgrades[k] = v["price"]
    
    gameData.upgrades_ship = upgrades