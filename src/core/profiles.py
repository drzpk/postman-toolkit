import os

from .parser import Parser


class ProfileConfigEntry:
    parent = None
    """
    Previous ProfileConfigEntry this one overrides
    """
    profile = None
    name = ""
    value = ""


class Profile:
    name = ""

    config_entries: ProfileConfigEntry = []
    """
    Config entries for current profile (profile overriding applies)
    """

    def __init__(self, name):
        self.name = name


class ProfiledConfiguration:
    profiles: [Profile] = []
    """
    List of active profiles
    """

    config_entries: [ProfileConfigEntry] = []
    """
    Current configuration as objects
    """

    config = {}
    """
    Current configuration as dictionary
    """


class ProfileConfigLoader:
    profiles_dir = ""
    active_profiles = []

    def __init__(self, profiles_dir, active_profiles):
        if not os.path.isdir(profiles_dir):
            raise FileNotFoundError("profiles directory doesn't exist")

        self.profiles_dir = profiles_dir
        self.active_profiles = active_profiles

    def load(self) -> ProfiledConfiguration:
        dir_list = [self.profiles_dir]
        # (profile: properties dit)
        mapping = {}

        while len(dir_list) > 0:
            _dir = dir_list.pop(0)
            result = self._load_dir(_dir)

            for d in result["dirs"]:
                dir_list.append(d)

            for p, v in result["profiles"].items():
                # Config values from profiles defines in subdirectories will override existing values
                if p not in mapping:
                    mapping[p] = {}
                mapping[p].update(v)

        return self._deflate_config(mapping)

    def _deflate_config(self, mapping) -> ProfiledConfiguration:
        configuration = ProfiledConfiguration()
        active_config_entries = {}

        for p_name in self.active_profiles:
            profile = Profile(p_name)

            if p_name in mapping:
                for k, v in mapping[p_name].items():
                    entry = ProfileConfigEntry()
                    entry.profile = profile
                    entry.name = k
                    entry.value = v

                    if k in active_config_entries:
                        entry.parent = active_config_entries[k]
                    active_config_entries[k] = entry

                configuration.profiles.append(profile)

        # Append active config entries to profiled configuration
        configuration.config_entries = [v for v in active_config_entries.values()]
        configuration.config = {k: v.value for k, v in active_config_entries.items()}

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
