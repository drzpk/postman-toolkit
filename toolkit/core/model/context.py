from .environment import *


class Context:
    environments: List[Environment]

    def create_environment(self, name) -> Environment:
        existing = self.find_environment(name)
        if existing is not None:
            raise Exception("Environemnt {} already exists".format(name))

        env = Environment.create(name)
        self.environments.append(env)
        return env

    def get_environment(self, _id):
        return next((x for x in self.environments if x.id == _id), None)

    def find_environment(self, name):
        return next((x for x in self.environments if x.name == name), None)
