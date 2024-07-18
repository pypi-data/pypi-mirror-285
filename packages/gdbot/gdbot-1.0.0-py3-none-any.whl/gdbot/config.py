class Config:
    def __init__(self, **kwargs):
        self.config = kwargs

    def get(self, key: str, default=None):
        return self.config.get(key, default)