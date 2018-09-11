import random

from .area import Area, AreaId


class Region(object):
    def __init__(self, region_id):
        self.region_id = region_id
        self.areas = [Area(AreaId(self.region_id, n)) for n in range(50)]
        self.params = [Cls(region_id) for Cls in all_region_params]

    def tick(self):
        for param in self.params:
            param.tick()
        for area in self.areas:
            area.tick()


all_region_params = []


def region_param(cls):
    all_region_params.append(cls)


class RegionParam(object):
    def __init__(self, region_id):
        self.region_id = region_id
        self.value = self.generate_default()

    def tick(self):
        pass  # override for erosion/weather/...


@region_param
class Height(RegionParam):
    @staticmethod
    def generate_default():
        return 1 / (.001 + random.random()) + 99.999

    def tick(self):
        raise NotImplementedError
