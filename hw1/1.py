from abc import ABCMeta, abstractmethod
import pickle
import json


class SerializationInterface(metaclass=ABCMeta):
    def __init__(self, data) -> None:
        self.data = data

    @abstractmethod
    def save_to_file(self):
        pass


class SerializationBin(SerializationInterface):
    def save_to_file(self):
        with open("file.bin", "wb") as file:
            pickle.dump(self.data, file)


class SerializationJson(SerializationInterface):
    def save_to_file(self):
        with open("file.json", "w") as file:
            json.dump(self.data, file)
