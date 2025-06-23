import yaml
from easydict import EasyDict

with open("config.yaml", "r", encoding="utf-8") as f:
    config_dict = yaml.safe_load(f)

settings = EasyDict(config_dict)
