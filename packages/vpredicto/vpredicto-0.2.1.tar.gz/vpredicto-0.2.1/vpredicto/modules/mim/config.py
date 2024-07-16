'''
The Config class is used to store the configuration parameters for the model.
'''
class Config:
    def __init__(self, config_dict):
        self.__dict__.update(config_dict)