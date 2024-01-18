from logging import StreamHandler


class CveExploreUpdateStreamHandler(StreamHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
