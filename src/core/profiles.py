import os
import copy
from typing import Dict, List

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
    backup = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self.go_dirty()
        self._parent = parent

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, profile):
        self.go_dirty()
        self._profile = profile

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.go_dirty()
        self._name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.go_dirty()
        self._value = value

    @property
    def is_active(self):
        return self._profile.active

    def go_dirty(self):
        self.dirty = True
        # Make a shallow copy - original references are needed
        self.backup = copy.copy(self)

    def go_clean(self):
        self.dirty = False
        self.backup = None


class Profile:
    _name = ""
    _active = False

    config_entries: Dict[str, ProfileConfigEntry] = None
    """
    Config entries defined for this profile only
    """

    profiled_configuration = None

    dirty = False
    backup = None

    def __init__(self, name):
        self.name = name
        self.config_entries = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.go_dirty()
        self._name = name

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self.go_dirty()
        self._active = active

    def add_entry(self, name, value):
        if name in self.config_entries:
            raise Exception("Config entry {} already exists in profile {}".format(name, self.name))
        entry = ProfileConfigEntry()
        entry.name = name
        entry.value = value
        entry.profile = self
        self.config_entries[name] = entry
        self.profiled_configuration.reorder()

    def delete_entry(self, name):
        if name not in self.config_entries:
            raise Exception("config entry {} doesn't exist in profile {}".format(name, self.name))
        del self.config_entries[name]
        self.profiled_configuration.reorder()

    def delete(self):
        self.profiled_configuration.delete_profile(self)

    def increase_priority(self):
        self.profiled_configuration.change_profile_priority(self, True)

    def decrease_priority(self):
        self.profiled_configuration.chagne_profile_priority(self, False)

    def go_dirty(self):
        self.dirty = True
        self.backup = copy.copy(self)

    def go_clean(self):
        self.dirty = False
        self.backup = None

    def __str__(self):
        return "Profile(name={}, active={})".format(self.name, self.active)


class ProfiledConfiguration:
    _profiles: Dict[str, Profile] = None
    _config: Dict[str, ProfileConfigEntry] = None
    _profiles_order: ProfilesOrder = None

    config_dir: str = None
    profiles_dirty: bool = False
    order_dirty: bool = False
    deleted_profiles: List[str] = None

    def __init__(self, config_dir):
        self._profiles = {}
        self._config = {}
        self.config_dir = config_dir
        # Could just compare profile directory contents, but who has time to write such algorithms...
        self.deleted_profiles = []

    def profiles(self):
        return self._profiles

    def ordered_profiles(self):
        ret = []
        for e in self._profiles_order.entries:
            ret.append(self._profiles[e.name])
        return ret

    def config(self):
        return self._config

    def create_profile(self, name, active):
        Log.i("Creating profie {} (active={}".format(name, active))
        if name in self._profiles:
            Log.e("Profile {} already exists".format(name))
            raise Exception("Profile {} already exists".format(name))
        p = Profile(name)
        p.active = active
        p.profiled_configuration = self
        self._profiles[name] = p

        order_entry = ProfileEntry(name, active)
        self._profiles_order.entries.append(order_entry)
        self.profiles_dirty = True
        self.order_dirty = True
        self.reorder()

    def delete_profile(self, profile: Profile):
        Log.i("Deleting profile {}".format(profile))
        if profile.name not in self._profiles:
            Log.e("Profile {} wasn't found in configuration. That's weird".format(profile.name))
            raise Exception("Profile {} wasn't found in configuration. That's weird".format(profile.name))
        if profile is not self._profiles[profile.name]:
            Log.e("Inconsistency detected: objects of profile {} don't match".format(profile.name))
            raise Exception("Inconsistency detected: objects of profile {} don't match".format(profile.name))
        del self._profiles[profile.name]
        self.deleted_profiles.append(profile.name)
        self.profiles_dirty = True

        _del = None
        for e in self._profiles_order.entries:
            if e.name == profile.name:
                _del = e
                break

        if _del is not None:
            self._profiles_order.entries.remove(_del)
            self.order_dirty = True
        else:
            Log.w("Profile order entry wasn't found for deleted profile {}".format(profile.name))

        self.reorder()

    def change_profile_priority(self, profile: Profile, increase: bool):
        Log.i("{} priority of {}".format("Increasing" if increase else "Decreasing", profile))
        found = None
        entries = self._profiles_order.entries

        for o in entries:
            if o.name == profile.name:
                found = o
                break
        if found is None:
            Log.e("Profile {} wasn't found in order list".format(profile))
            raise Exception("Profile {} wasn't found in order list".format(profile))

        current = entries.index(found)
        new = current + (1 if increase else -1)
        if 0 < new < len(self._profiles_order.entries):
            Log.d("Indices of profile {}: current={} next={}".format(profile.name, current, new))
            entries[current], entries[new] = entries[new], entries[current]
            self.order_dirty = True
        else:
            Log.i("Profile {} priority is at {} and cannot be {} further"
                  .format(profile.name, current, "increased" if increase else "decreased"))

        self.reorder()

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
                entry.go_clean()
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
            profile_was_dirty = profile.dirty
            for prop in profile.config_entries.values():
                prop_was_dirty = prop.dirty
                if prop.name in hierarchy:
                    old = hierarchy[prop.name]
                    prop.parent = old
                else:
                    prop.parent = None
                if prop.dirty and not prop_was_dirty:
                    prop.go_clean()
                hierarchy[prop.name] = prop

            # Dirty flag will cause profile (and config entry) to be flushed to disk and we don't want that,
            # especially as a result of rebuild action, that isn't really changing anything
            if profile.dirty and not profile_was_dirty:
                profile.go_clean()

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


# noinspection PyProtectedMember
class ProfileConfigWriter:

    # todo: transactions - rollback changes if exception occurs

    @staticmethod
    def write(configuration: ProfiledConfiguration):
        Log.d("Saving profiled configuration")

        for profile in configuration.profiles().values():
            profile_file = os.path.normpath(configuration.config_dir + "/" + profile.name)
            is_new = not os.path.isfile(profile_file)

            if is_new or any([entry.dirty for entry in profile.config_entries.values()]):
                Log.d("Detected dirty property in profile {}, writing the file".format(profile.name))
                parser = Parser(profile_file)
                parser.write({entry.name: entry.value for entry in profile.config_entries.values()})
                for entry in profile.config_entries.values():
                    entry.dirty = False
                    entry.backup = None

            if not profile.dirty:
                continue

            ordered_entry = ProfileConfigWriter._get_ordered_profile_entry(configuration, profile.name)
            if profile.backup is not None and profile.backup.name != profile.name:
                old_file = os.path.normpath(configuration.config_dir + "/" + profile.backup.name)
                ordered_entry.name = profile.name
                configuration.order_dirty = True
                Log.d("Renaming profile: {} -> {}".format(profile.backup.name, profile.name))
                os.rename(old_file, profile_file)

            if profile.backup is None or profile.backup.active is not profile.active:
                ordered_entry.active = profile.active
                configuration.order_dirty = True

            profile.dirty = False
            profile.backup = None

        if configuration.order_dirty:
            Log.d("Updating profiles order file")
            configuration._profiles_order.save()

        for deleted in configuration.deleted_profiles:
            Log.d("Deleting file of deleted profile {}".format(deleted))
            os.remove(os.path.normpath(configuration.config_dir + "/" + deleted))

        configuration.profiles_dirty = False
        configuration.order_dirty = False
        configuration.deleted_profiles.clear()

    @staticmethod
    def _get_ordered_profile_entry(configuration: ProfiledConfiguration, profile_name):
        for e in configuration._profiles_order.entries:
            if e.name == profile_name:
                return e
