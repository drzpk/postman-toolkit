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

        e = self.config.config_dict[name]
        return {
            "name": e.name,
            "value": e.value
        }

    def list_config(self):
        _list = []
        for e in self.config.config_list:
            _list.append({
                "name": e.name,
                "value": e.value,
                "profile": e.profile.name
            })

        return {
            "content": _list
        }

    def reload_config(self):
        Log.i("Reloading profile configuration")
        self.config.reload()
