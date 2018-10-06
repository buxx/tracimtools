# coding: utf-8


class BaseModel(object):
    def __init__(self, **kwargs) -> None:
        for attr_name, attr_value in kwargs.items():
            setattr(self, attr_name, attr_value)
