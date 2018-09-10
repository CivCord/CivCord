import random

from .area import Area, AreaId


class Region(object):
    def __init__(self, region_id):
        self.region_id = region_id
        self.areas = [Area(AreaId(self.region_id, n)) for n in range(50)]
        self.params = [Cls(region_id) for Cls in all_region_params]

    def tick(self, n=1):
        for area in self.areas.values():
            area.tick(n=n)


all_region_params = []


def region_param(cls):
    all_region_params.append(cls)


class RegionParam(object):
    def __init__(self, region_id):
        self.region_id = region_id
        self.value = self.generate_default()

    def tick(self, n=1):
        raise NotImplementedError


@region_param
class Height(RegionParam):
    @staticmethod
    def generate_default():
        return random.random() * (256 - 64) + 64

    def tick(self, n=1):
        raise NotImplementedError
