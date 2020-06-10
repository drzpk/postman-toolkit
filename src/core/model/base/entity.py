from abc import *
from typing import *


class PendingEntityBuffer:
    deleted_entities: List = []


class Entity:
    dirty: bool
    new: bool

    def __init__(self):
        self.dirty = False
        self.new = False

    def mark_dirty(self):
        self.dirty = True

    def mark_new(self):
        self.new = True

    def mark_deleted(self):
        PendingEntityBuffer.deleted_entities.append(self)

    @abstractmethod
    def serialize(self) -> Dict:
        pass

    @abstractmethod
    def deserialize(self, data: Dict):
        pass
