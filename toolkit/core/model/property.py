from typing import Dict

from .base.entity import Entity


class Property(Entity):
    _id: int
    _name: str
    _value: str
    _type: str
    _enabled: bool
    _profile_id: int

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.mark_dirty()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.mark_dirty()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, _type):
        self._type = _type
        self.mark_dirty()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self.mark_dirty()

    def serialize(self) -> Dict:
        return {
            "id": self._id,
            "name": self.name,
            "value": self.value,
            "type": self.type,
            "enabled": 1 if self.enabled else 0,
            "profile_id": self._profile_id
        }

    def deserialize(self, data: Dict):
        self._id = int(data["id"])
        self._name = data["name"]
        self._value = data["value"]
        self._type = data["type"]
        self._enabled = data["enabled"] == 1
        self._profile_id = data["profile_id"]

    @staticmethod
    def create(name, profile_id):
        prop = Property()
        prop._id = -1
        prop.name = name
        prop.type = "S"
        prop.enabled = True
        prop._profile_id = profile_id
        prop.mark_new()
        return prop
