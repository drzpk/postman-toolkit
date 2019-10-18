import os
from typing import List

from .log import Log


# todo: profile name validation


class ProfileEntry:
    name = ""
    active = False

    def __init__(self, name, active):
        self.name = name
        self.active = active


class ProfilesOrder:
    file = None
    entries: List[ProfileEntry] = None
    """
    The last entry is the most important (overrides previous ones)
    """

    def __init__(self, file: str):
        self.file = file
        self.reload()

    def reload(self):
        if not os.path.isfile(self.file):
            Log.i("Profiles order doesn't exist, creating an example one")
            self.entries = [
                ProfileEntry("active_1", True),
                ProfileEntry("active_2", True),
                ProfileEntry("inactive_profile", False)
            ]
            self.save()

        else:
            with open(self.file, "r") as h:
                content = h.read()
                return self._parse(content)

    def save(self):
        payload = FILE_HEADER + "\n"
        for e in self.entries:
            payload += "{}{}\n".format("" if e.active else "!", e.name)

        with open(self.file, "w") as h:
            h.write(payload)

    def _parse(self, content):
        entries = []
        for l in content.split("\n"):
            p = l.strip()
            if p.startswith("#") or len(p) == 0:
                continue

            active = not p.startswith("!")
            p_name = p[0 if active else 1:]
            if p_name.find("!") > -1:
                raise SyntaxError("Exclamation mark is not allowed in the profile name")

            entries.append(ProfileEntry(p_name, active))

        self.entries = entries


FILE_HEADER = """# This file contains list of known profiles. Editing it manually is not recommended
# because it may be overwritten by the browser app.
# Below is the list of known profiles. Those starting by the '!' char are recognized as inactive.
# The list should be read from top to bottom - every next profile overrides its predecessors.
"""
