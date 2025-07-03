import math

from service import Service

service = Service("http://127.0.0.1:8080")

class GameData:
    resources = service.get_resources()
    player = None
    station = None
    ship = []
    gaz_planet = []
    solid_planet = []
    upgrades_ship = {}
    money = 0
    cost = 0.0
    max_ship = 20
    new_ship_money = 0
    
gameData = GameData()

def get_dist(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))