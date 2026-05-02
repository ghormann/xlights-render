import json


class GregLightsConfig:
    def __init__(self, path="greglights_config.json"):
        with open(path) as f:
            data = json.load(f)
        self.host = data["host"]
        self.port = data["port"]
        self.username = data["username"]
        self.password = data["password"]
        self.fpp_ips = data["fpp_ips"]
        self.base_names = data["base_names"]
        if len(self.fpp_ips) < 1:
            raise ValueError("greglights_config.json must have at least 1 entry in fpp_ips")
        if len(self.base_names) < 13:
            raise ValueError("greglights_config.json must have at least 13 entries in base_names")
