from configparser import ConfigParser


class Config:
    def __init__(self, config="config.ini"):
        self.config = ConfigParser()
        self.config.read(config)
