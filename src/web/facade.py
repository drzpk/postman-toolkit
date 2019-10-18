from ..core.log import Log
from ..core.profiles import ProfiledConfiguration


class WebFacade:
    config: ProfiledConfiguration = None

    def __init__(self, profiled_configuration):
        self.config = profiled_configuration

    # todo: optionally return overridden values
    def get_config(self, name):
        if name not in self.config.config_dict:
            return None

        e = self.config.config_dict()[name]
        return {
            "name": e.name,
            "value": e.value
        }

    def list_config(self, active_only, profile_name=None):
        _list = []

        if profile_name is None:
            for e in self.config.config_list(active_only):
                _list.append({
                    "name": e.name,
                    "value": e.value,
                    "profile": e.profile.name
                })
        else:
            profiles = self.config.profiles(False)
            if profile_name not in profiles:
                return None
            for v in profiles[profile_name].config_entries:
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
        for p in self.config.profiles(active_only).values():
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
