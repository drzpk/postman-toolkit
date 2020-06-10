from ..core.toolkit import PostmanToolkit
from ..core.model.context import Context
from ..core.model.environment import Environment

# TODO: environment support in frontend
ENVIRONMENT_NAME = "default"


def interceptor(function):
    def _wrapper(*args, **kwargs):
        ret = function(*args, **kwargs)
        args[0].toolkit.persist_changes()
        return ret
    return _wrapper


class WebFacade:
    context: Context
    toolkit: PostmanToolkit

    def __init__(self, toolkit: PostmanToolkit):
        self.context = toolkit.context
        self.toolkit = toolkit

    @interceptor
    def get_property_details(self, property_name):
        env = self._find_env(ENVIRONMENT_NAME)
        chain = env.get_property_chain(property_name, enabled_only=False)
        if len(chain) == 0:
            raise Exception("Property {} wasn't found".format(property_name))

        first = chain[0]
        content = {
            "name": first[1].name,
            "value": first[1].value,
            "profile": first[0].name,
            "active": first[0].enabled and first[1].enabled
        }

        ancestors = []
        for i in range(1, len(chain)):
            ancestor = chain[i]
            ancestors.append({
                "name": ancestor[1].name,
                "value": ancestor[1].value,
                "profile": ancestor[0].name,
                "active": ancestor[0].enabled and ancestor[1].enabled
            })

        content["ancestors"] = ancestors
        return {
            "content": content
        }

    @interceptor
    def set_property_value(self, profile_name, property_name, value):
        env = self._find_env(ENVIRONMENT_NAME)

        profile = env.find_profile(profile_name)
        if profile is None:
            raise Exception("Profile {} wasn't found".format(profile_name))

        prop = profile.find_property(property_name)
        if prop is None:
            raise Exception("Profile {} doesn't have property {}".format(profile_name, property_name))

        prop.value = str(value)

    @interceptor
    def create_property(self, profile_name, property_name, value):
        env = self._find_env(ENVIRONMENT_NAME)
        profile = env.find_profile(profile_name)
        if profile is None:
            raise Exception("Profile {} wasn't found".format(profile_name))

        profile.create_property(property_name, value)

    @interceptor
    def delete_property(self, profile_name, property_name):
        env = self._find_env(ENVIRONMENT_NAME)
        profile = env.find_profile(profile_name)
        if profile is None:
            raise Exception("Profile {} wasn't found".format(profile_name))

        profile.delete_property(property_name)

    @interceptor
    def rename_property(self, profile_name, old_property_name, new_property_name):
        env = self._find_env(ENVIRONMENT_NAME)
        profile = env.find_profile(profile_name)
        if profile is None:
            raise Exception("Profile {} wasn't found".format(profile_name))

        prop = profile.find_property(old_property_name)
        if prop is None:
            raise Exception("Property {} wasn't found in profile {}".format(old_property_name, profile_name))

        prop.name = new_property_name

    @interceptor
    def list_properties(self, active_only, profile_name=None):
        env = self._find_env(ENVIRONMENT_NAME)
        names = env.get_property_names(profile_name)

        _list = []
        for name in names:
            (profile, prop) = env.get_first_property(name, active_only)
            _list.append({
                "name": prop.name,
                "value": prop.value,
                "profile": profile.name
            })

        return {
            "content": _list
        }

    @interceptor
    def create_profile(self, profile_name, active):
        env = self._find_env(ENVIRONMENT_NAME)
        env.create_profile(profile_name, active)

    def list_profiles(self, active_only):
        env = self._find_env(ENVIRONMENT_NAME)
        profiles = env.get_prioritized_profiles()
        if active_only:
            profiles = filter(lambda x: x.enabled, profiles)

        _list = []
        for p in profiles:
            _list.append({
                "name": p.name,
                "active": p.enabled,
                "properties_count": len(p.properties)
            })

        return {
            "content": _list
        }

    @interceptor
    def set_profile_enabled_state(self, profile_name, new_state):
        env = self._find_env(ENVIRONMENT_NAME)
        profile = env.find_profile(profile_name)
        if profile is None:
            raise Exception("Profile {} wasn't found".format(profile_name))
        profile.enabled = bool(new_state)

    @interceptor
    def change_profile_priority(self, profile_name, increase):
        env = self._find_env(ENVIRONMENT_NAME)
        if increase:
            return env.increase_profile_priority(profile_name)
        else:
            return env.decrease_profile_priority(profile_name)

    @interceptor
    def delete_profile(self, profile_name):
        env = self._find_env(ENVIRONMENT_NAME)
        env.delete_profile(profile_name)

    def _find_env(self, name) -> Environment:
        env = self.context.find_environment(ENVIRONMENT_NAME)
        if env is None:
            raise Exception("Environment {} wasn't found".format(ENVIRONMENT_NAME))
        return env


class FacadeException(Exception):
    message = None

    def __init__(self, message):
        super().__init__(message)
