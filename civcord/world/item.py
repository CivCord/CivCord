import random


class Item(object):
    def __init__(self):
        for Cls in all_item_params:
            setattr(self, Cls.display_name, Cls())

    def __str__(self):
        return ', '.join(str(getattr(self, Cls.display_name)) for Cls in all_item_params)

    def tick(self):
        for Cls in all_item_params:
            getattr(self, Cls.display_name).tick()


all_item_params = []


def item_param(cls):
    all_item_params.append(cls)
    if not getattr(cls, 'display_name', None):
        setattr(cls, 'display_name', cls.__name__)


class ItemParam(object):
    def __init__(self):
        self.value = self.generate_default()

    def __str__(self):
        return '{0.display_name}={0.value:.3f}'.format(self)

    def tick(self):
        pass  # override for decay/maturation/...


@item_param
class Weight(ItemParam):
    @staticmethod
    def generate_default():
        return 1 / (.001 + random.random()) - .001


@item_param
class Sharpness(ItemParam):
    @staticmethod
    def generate_default():
        return random.random()


@item_param
class Strength(ItemParam):
    @staticmethod
    def generate_default():
        return random.random()


@item_param
class Flexibility(ItemParam):
    @staticmethod
    def generate_default():
        return random.random()
