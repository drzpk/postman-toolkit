import os
from typing import List, Dict

from .config import Configuration
from .log import Log
from .parser import Parser
from .profiles_order import ProfilesOrder, ProfileEntry


class ProfileConfigEntry:
    parent = None
    """
    Previous ProfileConfigEntry this one overrides
    """
    profile = None
    name = ""
    value = ""

    @property
    def is_active(self):
        return self.profile.active


class Profile:
    name = ""
    active = False

    config_entries: List[ProfileConfigEntry] = None
    """
    Config entries for current profile (profile overriding applies)
    """

    def __init__(self, name):
        self.name = name
        self.config_entries = []


class ProfiledConfiguration:
    _profiles: Dict[str, Profile] = {}
    _config_list: List[ProfileConfigEntry] = []
    _config_dict: Dict[str, ProfileConfigEntry] = {}

    _profiles_order: ProfilesOrder = None

    def profiles(self, active_only=True):
        """
        List of (active) profiles
        """
        if not active_only:
            return self._profiles

        return {k: v for k, v in self._profiles if v.active}

    def config_list(self, active_only=True):
        """
        Current configuration as objects
        """
        if not active_only:
            return self._config_list

        return [c for c in self._config_list if c.is_active()]

    def config_dict(self, active_only=True):
        """
        Current configuration as dictionary
        """
        if not active_only:
            return self._config_dict

        return {k: v for k, v in self._config_dict if v.is_active()}

    def reload(self):
        Log.i("Reloading profiled configuration")
        self._profiles_order.reload()
        updated = ProfileConfigLoader.load(self._profiles_order)

        self._profiles = updated._profiles
        self._config_list = updated._config_list
        self._config_dict = updated._config_dict


class ProfileConfigLoader:
    profiles_dir = ""
    profiles_order: ProfilesOrder = []

    def __init__(self, profiles_dir, profiles_order: ProfilesOrder):
        if not os.path.isdir(profiles_dir):
            raise FileNotFoundError("profiles directory doesn't exist")

        self.profiles_dir = profiles_dir
        self.profiles_order = profiles_order

    @staticmethod
    def load(profiles_order: ProfilesOrder):
        loader = ProfileConfigLoader(Configuration.profiles_dir, profiles_order)

        return loader._load()

    def _load(self) -> ProfiledConfiguration:
        dir_list = [self.profiles_dir]
        # (profile: properties dir)
        mapping = {}

        while len(dir_list) > 0:
            _dir = dir_list.pop(0)
            result = self._load_dir(_dir)

            for d in result["dirs"]:
                dir_list.append(d)

            for p, v in result["profiles"].items():
                # Config values from profiles defined in subdirectories will override existing values
                if p not in mapping:
                    mapping[p] = {}
                mapping[p].update(v)

        return self._inflate_config(mapping)

    # noinspection PyShadowingNames
    def _inflate_config(self, mapping) -> ProfiledConfiguration:
        configuration = ProfiledConfiguration()
        configuration._profiles_order = self.profiles_order

        # Load all profiles from from the directory
        raw_profiles = {}
        for p_name, profile_properties in mapping.items():
            profile = Profile(p_name)
            for k, v in profile_properties.items():
                entry = ProfileConfigEntry()
                entry.profile = profile
                entry.name = k
                entry.value = v
                profile.config_entries.append(entry)
            raw_profiles[p_name] = profile

        profiles_order_dirty = False

        # Determine the order
        ordered_profiles = []
        entries_to_delete = []
        for entry in self.profiles_order.entries:
            if entry.name not in raw_profiles:
                Log.i("Profile file for profile {} wasn't found, deleting profile from list".format(entry.name))
                entries_to_delete.append(entry)
                profiles_order_dirty = True
            else:
                profile = raw_profiles.pop(entry.name)
                profile.active = entry.active
                ordered_profiles.append(profile)

        for to_delete in entries_to_delete:
            self.profiles_order.entries.remove(to_delete)
            Log.d("Deleted profile {} from entry list".format(to_delete.name))

        # Add unlisted profiles to profile list
        for new_profile in raw_profiles.values():
            profiles_order_dirty = True
            new_profile.active = False
            entry = ProfileEntry(new_profile.name, False)
            self.profiles_order.entries = [entry] + self.profiles_order.entries
            Log.d("Added new inactive profile {} to order list".format(new_profile.name))

        if profiles_order_dirty:
            self.profiles_order.save()

        configuration._profiles = {p.name: p for p in ordered_profiles}
        self._rebuild_hierarchy(configuration)
        return configuration

    @staticmethod
    def _rebuild_hierarchy(configuration):
        hierarchy = {}
        for profile in configuration.profiles(False).values():
            for prop in profile.config_entries:
                if prop.name in hierarchy:
                    old = hierarchy[prop.name]
                    prop.parent = old
                    hierarchy[prop.name] = prop
                else:
                    prop.parent = None

        configuration._config_dict = hierarchy
        configuration._config_list = [v for v in hierarchy.values()]

    def _load_dir(self, _dir):
        ret = {
            "dirs": [],
            "profiles": {}
        }
        with os.scandir(_dir) as it:
            for entry in it:
                if entry.name.find(".") == 0 and entry.is_dir():
                    continue

                if entry.is_file():
                    try:
                        parser = Parser(entry.path)
                        data = parser.parse()

                        name = self.get_profile_name(entry.name)
                        ret["profiles"][name] = data
                    except Exception as e:
                        # todo: recover from such errors
                        raise Exception("Error while parsing file " + entry.path) from e
                else:
                    pass
                    # todo: need to rethink this behavior
                    # ret["dirs"].append(entry.path)

        return ret

    @staticmethod
    def get_profile_name(filename: str):
        if filename.find(".") > -1:
            parts = filename.rsplit(".")
            return "".join(parts[0:len(parts) - 1])
        else:
            return filename
