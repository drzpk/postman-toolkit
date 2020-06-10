from typing import List, Dict, Tuple

from .base.entity import Entity
from .profile import Profile
from .property import Property


START_PROFILE_PRIORITY = 1


class Environment(Entity):
    _id: int
    _name: str

    profiles: List[Profile]

    def __init__(self):
        super().__init__()
        self.profiles = []

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

    def create_profile(self, profile_name, is_enabled=True) -> Profile:
        existing = self.find_profile(profile_name)
        if existing is not None:
            raise Exception("Profile with name {} already exists".format(profile_name))

        priority_list = [p.priority for p in self.profiles]
        priority_list.append(START_PROFILE_PRIORITY)  # First priority if there are no profiles yet

        lowest_existing_priority = max(priority_list)
        profile = Profile.create(profile_name, lowest_existing_priority + 1, self.id)
        profile.enabled = is_enabled
        return profile

    def find_profile(self, profile_name):
        for profile in self.profiles:
            if profile.name == profile_name:
                return profile
        return None

    def increase_profile_priority(self, profile_name) -> bool:
        return self._change_profile_priority(profile_name, -1)

    def decrease_profile_priority(self, profile_name) -> bool:
        return self._change_profile_priority(profile_name, 1)

    def get_prioritized_profiles(self) -> List[Profile]:
        """
        Returns list of profiles sorted by their priority, ascending (profile with highest priority is the first
        element on the list)
        """
        return sorted(self.profiles, key=lambda p: p.priority)

    def delete_profile(self, profile_name):
        profiles = self.get_prioritized_profiles()
        profile_pos = self._get_required_profile_index(profiles, profile_name)
        profile_to_delete = profiles[profile_pos]

        self.profiles.remove(profile_to_delete)
        profiles.remove(profile_to_delete)
        profile_to_delete.mark_deleted()

        for i in range(0, len(profiles)):
            profiles[i].priority = i + START_PROFILE_PRIORITY

    def get_property_chain(self, property_name, enabled_only=True) -> List[Tuple[Profile, Property]]:
        """
        Returns list of pairs (profile, property) for given property name.
        List order is from highest to lowest priority
        :param property_name: proparty name
        :param enabled_only: whether to return only lsit of active profiles AND active properties
        :return: property list ordered form highest to lowest priority
        """
        chain = []
        ordered_profiles = sorted(self.profiles, key=lambda p: p.priority)
        for profile in ordered_profiles:
            if not profile.enabled and enabled_only:
                continue
            prop = profile.find_property(property_name)
            if prop is None or not prop.enabled:
                continue
            chain.append((profile, prop))
        return chain

    def get_first_property(self, property_name, enabled_only=True) -> (Profile, Property):
        """
        Returns property with highest priority
        :param property_name: property name
        :param enabled_only: whether to look only for active properties in active profiles
        :return: property with highest priority
        """
        chain = self.get_property_chain(property_name, enabled_only)
        if len(chain) > 0:
            return chain[0]
        else:
            return None

    def get_property_names(self, profile_name=None) -> List[str]:
        if profile_name is not None:
            profile = self.find_profile(profile_name)
            if profile is None:
                raise Exception("Profile {} wasn't found".format(profile_name))
            profiles = [profile]
        else:
            profiles = self.profiles

        _list = []
        for p in profiles:
            _list.extend([x.name for x in p.properties])
        return list(set(_list))

    def serialize(self) -> Dict:
        return {
            "id": self._id,
            "name": self.name
        }

    def deserialize(self, data: Dict):
        self._id = int(data["id"])
        self._name = data["name"]

    def _change_profile_priority(self, profile_name, direction) -> bool:
        profiles = self.get_prioritized_profiles()
        profile_pos = self._get_required_profile_index(profiles, profile_name)

        new_pos = profile_pos + direction
        if new_pos < 0 or new_pos >= len(profiles):
            return False

        tmp = profiles[profile_pos].priority
        profiles[profile_pos].priority = profiles[new_pos]
        profiles[new_pos] = tmp
        return True

    @staticmethod
    def _get_required_profile_index(profiles, name):
        profile_pos = -1
        for i in range(len(profiles)):
            if profiles[i].name == name:
                profile_pos = i
                break

        if profile_pos == -1:
            raise Exception("Profile {} wasn't found".format(name))

        return profile_pos

    @staticmethod
    def create(name):
        environment = Environment()
        environment._id = -1
        environment.name = name
        environment.mark_new()
        return environment
