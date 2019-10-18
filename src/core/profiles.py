import os
from typing import List, Dict

from .config import Configuration
from .log import Log
from .parser import Parser
from .profiles_order import ProfilesOrder


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

    config_entries: List[ProfileConfigEntry] = []
    """
    Config entries for current profile (profile overriding applies)
    """

    def __init__(self, name, active):
        self.name = name
        self.active = active


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

        # TODO: generate warnings about files from /profiles directory that aren't listed on profile list
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

        return self._deflate_config(mapping)

    # noinspection PyShadowingNames
    def _deflate_config(self, mapping) -> ProfiledConfiguration:
        configuration = ProfiledConfiguration()
        configuration._profiles_order = self.profiles_order

        profiles = {}
        config_entries = {}

        for a_profile in self.profiles_order.entries:
            profile = Profile(a_profile.name, a_profile.active)

            if a_profile.name in mapping:
                for k, v in mapping[a_profile.name].items():
                    entry = ProfileConfigEntry()
                    entry.profile = profile
                    entry.name = k
                    entry.value = v

                    if k in config_entries:
                        entry.parent = config_entries[k]
                    config_entries[k] = entry
                    profile.config_entries.append(entry)

            profiles[a_profile.name] = profile

        # Append active config entries to profiled configuration
        configuration._profiles = profiles
        configuration._config_list = [v for v in config_entries.values()]
        configuration._config_dict = config_entries

        return configuration

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
                        raise Exception("Error while parsing file " + entry.path) from e
                else:
                    ret["dirs"].append(entry.path)

        return ret

    @staticmethod
    def get_profile_name(filename: str):
        if filename.find(".") > -1:
            parts = filename.rsplit(".")
            return "".join(parts[0:len(parts) - 1])
        else:
            return filename
