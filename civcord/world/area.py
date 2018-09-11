import random
from collections import namedtuple

AreaId = namedtuple('AreaId', 'region_id area_nr')


class Area(object):
    def __init__(self, area_id):
        self.area_id = area_id
        self.params = [Cls(area_id) for Cls in all_area_params]

    def tick(self):
        for param in self.params:
            param.tick()

all_area_params = []


def area_param(cls):
    all_area_params.append(cls)


class AreaParam(object):
    def __init__(self, area_id):
        self.area_id = area_id
        self.value = self.generate_default()

    def tick(self):
        pass  # override for erosion/weather/...


@area_param
class SoilFertility(AreaParam):
    @staticmethod
    def generate_default():
        return random.random()

    def tick(self):
        raise NotImplementedError
