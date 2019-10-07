from ..core.globals import Globals


class WebFacade:

    # todo: optionally return overridden values
    @staticmethod
    def get_config(name):
        if name not in Globals.profiled_configuration.config_dict:
            return None

        e = Globals.profiled_configuration.config_dict[name]
        return {
            "name": e.name,
            "value": e.value
        }
