
class Player(object):
    def __init__(self, player_id, region_id):
        self.player_id = player_id
        self.region_id = region_id
        self.inventory = []

    def tick(self):
        for item in inventory:
            item.tick()
