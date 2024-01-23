from logging.handlers import RotatingFileHandler


class CveExploreUpdateRfhHandler(RotatingFileHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
