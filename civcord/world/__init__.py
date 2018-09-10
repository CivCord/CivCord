import random

from .region import Region
from .player import Player
from .item import Item


def create_new():
    return World()


class World(object):
    def __init__(self):
        self.regions = {
            2: Region(2),
        }
        self.players = {}

    def get_or_create_player(self, player_id):
        if player_id not in self.players:
            region_id = random.choice(list(self.regions.keys()))
            new_player = Player(player_id, region_id)
            self.players[player_id] = new_player
            new_player.inventory.append(Item())
            new_player.inventory.append(Item())
            new_player.inventory.append(Item())
            print('Created player', new_player)
        return self.players[player_id]

    def tick(self, n=1):
        for region in self.regions.values():
            region.tick(n=n)
