import json

class Model:
    def __new__(cls, **kwargs):
        instance = super(Model, cls).__new__(cls)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

    def _to_dict(self):
        # Include the class name in the dictionary for identification
        data = self.__dict__.copy()
        data['__model_type__'] = self.__class__.__name__
        return data

    def _from_dict(self, data):
        # Populate self with the information from data
        for key, value in data.items():
            setattr(self, key, value)

        return self

    @classmethod
    def _deserialize(cls, data):
        return cls._from_dict(data)