import os
from typing import Dict

from .config import Configuration
from .log import Log
from .parser import Parser
from .profiles_order import ProfilesOrder, ProfileEntry


class ProfileConfigEntry:
    _parent = None
    """
    Previous ProfileConfigEntry this one overrides
    """
    _profile = None
    _name = ""
    _value = ""

    dirty = False

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        self.dirty = True

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, profile):
        self._profile = profile
        self.dirty = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.dirty = True

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.dirty = True

    @property
    def is_active(self):
        return self._profile.active


class Profile:
    _name = ""
    _active = False

    config_entries: Dict[str, ProfileConfigEntry] = None
    """
    Config entries defined for this profile only
    """

    profiled_configuration = None
    dirty = False

    def __init__(self, name):
        self.name = name
        self.config_entries = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.dirty = True

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active
        self.dirty = True

    def add_entry(self, name, value):
        if name in self.config_entries:
            raise Exception("Config entry {} already exists in profile {}".format(name, self.name))
        entry = ProfileConfigEntry()
        entry.name = name
        entry.value = value
        entry.profile = self
        entry.dirty = True
        self.config_entries[name] = entry
        self.profiled_configuration.reorder()

    def delete_entry(self, name):
        if name not in self.config_entries:
            raise Exception("config entry {} doesn't exist in profile {}".format(name, self.name))
        del self.config_entries[name]
        self.profiled_configuration.reorder()


class ProfiledConfiguration:
    _profiles: Dict[str, Profile] = None
    _config: Dict[str, ProfileConfigEntry] = None
    _profiles_order: ProfilesOrder = None

    config_dir: str = None

    def __init__(self, config_dir):
        self._profiles = {}
        self._config = {}
        self.config_dir = config_dir

    def profiles(self):
        return self._profiles

    def config(self):
        return self._config

    def reload(self):
        Log.i("Reloading profiled configuration")
        self._profiles_order.reload()
        updated = ProfileConfigLoader.load(self._profiles_order)

        self._profiles = updated._profiles
        self._config = updated._config

    def reorder(self):
        ProfileConfigLoader.rebuild_hierarchy(self)

    def save(self):
        ProfileConfigWriter.write(self)


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
        configuration = ProfiledConfiguration(self.profiles_dir)
        configuration._profiles_order = self.profiles_order

        # Load all profiles from from the directory
        raw_profiles = {}
        for p_name, profile_properties in mapping.items():
            profile = Profile(p_name)
            profile.profiled_configuration = configuration
            for k, v in profile_properties.items():
                entry = ProfileConfigEntry()
                entry.profile = profile
                entry.name = k
                entry.value = v
                profile.config_entries[k] = entry
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
        self.rebuild_hierarchy(configuration)
        return configuration

    @staticmethod
    def rebuild_hierarchy(configuration):
        hierarchy = {}
        for profile in configuration.profiles().values():
            profile.dirty = False
            for prop in profile.config_entries.values():
                prop.dirty = False
                if prop.name in hierarchy:
                    old = hierarchy[prop.name]
                    prop.parent = old
                else:
                    prop.parent = None
                hierarchy[prop.name] = prop

        configuration._config = hierarchy

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


class ProfileConfigWriter:

    @staticmethod
    def write(configuration: ProfiledConfiguration):
        Log.d("Saving profiled configuration")
        for profile in configuration.profiles().values():
            if any([entry.dirty for entry in profile.config_entries.values()]):
                Log.d("Detected dirty property in profile {}, writing the file".format(profile.name))
                parser = Parser(os.path.normpath(configuration.config_dir + "/" + profile.name))
                parser.write({entry.name: entry.value for entry in profile.config_entries.values()})
                for entry in profile.config_entries.values():
                    entry.dirty = False

            # todo: handle profile name change
