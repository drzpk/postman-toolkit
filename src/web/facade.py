from ..core.log import Log
from ..core.profiles import ProfiledConfiguration


class WebFacade:
    config: ProfiledConfiguration = None

    def __init__(self, profiled_configuration):
        self.config = profiled_configuration

    def get_config(self, name):
        config = self.config.config()
        if name not in config:
            return None

        e = config[name]
        ancestors = []
        p = e.parent
        while p is not None:
            ancestors.append({
                "name": p.name,
                "value": p.value,
                "profile": p.profile.name,
                "active": e.is_active
            })
            p = p.parent

        content = {
            "name": e.name,
            "value": e.value,
            "profile": e.profile.name,
            "active": e.is_active,
            "ancestors": ancestors
        }
        return {
            "content": content
        }

    def update_config(self, profile_name, name, value):
        profiles = self.config.profiles()
        if profile_name not in profiles:
            Log.d("Profile {} wasn't found".format(profile_name))
            return False

        if name not in profiles[profile_name].config_entries:
            Log.d("Config entry {} wasn't found in profile {}".format(name, profile_name))
            return False

        entry = profiles[profile_name].config_entries[name]
        entry.value = value
        self.config.save()
        return True

    def create_config(self, profile_name, name, value):
        profiles = self.config.profiles()
        if profile_name not in profiles:
            Log.d("Profile {} wasn't found".format(profile_name))
            return False

        if name in profiles[profile_name].config_entries:
            Log.d("Config entry {} already exists in profile {}".format(name, profile_name))
            return False

        profiles[profile_name].add_entry(name, value)
        self.config.save()
        return True

    def delete_config(self, profile_name, name):
        profiles = self.config.profiles()
        if profile_name not in profiles:
            Log.d("Profile {} wasn't found".format(profile_name))
            return False

        if name not in profiles[profile_name].config_entries:
            Log.d("Config entry {} wasn't found in profile {}".format(name, profile_name))
            return False

        profiles[profile_name].delete_entry(name)
        self.config.save()
        return True

    def list_config(self, active_only, profile_name=None):
        _list = []

        if profile_name is None:
            for e in self.config.config().values():
                _list.append({
                    "name": e.name,
                    "value": e.value,
                    "profile": e.profile.name
                })
        else:
            profiles = self.config.profiles()
            if profile_name not in profiles:
                return None
            for v in profiles[profile_name].config_entries.values():
                _list.append({
                    "name": v.name,
                    "value": v.value,
                    "profile": v.profile.name
                })

        return {
            "content": _list
        }

    def list_profiles(self, active_only):
        _list = []
        for p in self.config.profiles().values():
            _list.append({
                "name": p.name,
                "active": p.active,
                "properties_count": len(p.config_entries)
            })

        return {
            "content": _list
        }

    def reload_config(self):
        Log.i("Reloading profile configuration")
        self.config.reload()
