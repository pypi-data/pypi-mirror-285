import datetime

from ..my_utils import MyUtils

utils = MyUtils()


class Streams(dict):
    """TBI

    Args:
        dict (_type_): _description_
    """

    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
