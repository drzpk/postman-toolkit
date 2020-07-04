from typing import List, Dict, Optional

from .base.entity import Entity
from .property import Property


class Profile(Entity):
    _id: int
    _name: str
    _priority: int
    _enabled: bool
    _environment_id: int

    properties: List[Property]

    def __init__(self):
        super().__init__()
        self.properties = []

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
    def priority(self):
        """
        Returns priority of this profile. Smaller value means greater priority.
        """
        return self._priority

    @priority.setter
    def priority(self, priority):
        self._priority = priority
        self.mark_dirty()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self.mark_dirty()

    @property
    def environment_id(self):
        return self._environment_id

    @environment_id.setter
    def environment_id(self, environment_id):
        self._environment_id = environment_id
        self.mark_dirty()

    def get_property(self, property_id) -> Optional[Property]:
        matched = list(filter(lambda p: p.id == property_id, self.properties))
        if len(matched) == 1:
            return matched[0]
        else:
            return None

    def find_property(self, property_name) -> Optional[Property]:
        matched = list(filter(lambda p: p.name == property_name, self.properties))
        if len(matched) > 1:
            raise Exception("Inconsistency detected: there is more properties with name {}".format(property_name))
        elif len(matched) == 1:
            return matched[0]
        else:
            return None

    def create_property(self, name, value) -> Property:
        existing = self.find_property(name)
        if existing is not None:
            raise Exception("Cannot create property {}: another property with the same name already exists".format(name))

        prop = Property.create(name, self.id)
        prop.value = value
        self.properties.append(prop)
        return prop

    def delete_property(self, property_id) -> bool:
        existing = self.get_property(property_id)
        if existing is None:
            return False

        existing.mark_deleted()
        self.properties.remove(existing)
        return True

    def serialize(self) -> Dict:
        d = {
            "name": self.name,
            "priority": self.priority,
            "enabled": 1 if self.enabled else 0,
            "environment_id": self.environment_id
        }

        if self._id > 0:
            d["id"] = self._id

        return d

    def deserialize(self, data: Dict):
        self._id = int(data["id"])
        self._name = data["name"]
        self._priority = data["priority"]
        self._enabled = data["enabled"] == 1
        self._environment_id = data["environment_id"]

    @staticmethod
    def create(name, priority, environment_id):
        profile = Profile()
        profile._id = -1
        profile.name = name
        profile.priority = priority
        profile.enabled = True
        profile.environment_id = environment_id
        profile.mark_new()
        return profile
