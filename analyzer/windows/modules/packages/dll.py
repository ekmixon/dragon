# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

from lib.common.abstracts import Package
from lib.api.process import Process
from lib.common.exceptions import CuckooPackageError

class Dll(Package):
    """DLL analysis package."""

    def start(self, path):
        free = self.options.get("free", False)
        function = self.options.get("function", "DllMain")
        arguments = self.options.get("arguments", None)
        suspended = not free
        args = "{0},{1}".format(path, function)
        if arguments:
            args += " {0}".format(arguments)

        p = Process()
        if not p.execute(path="C:\\WINDOWS\\system32\\rundll32.exe", args=args, suspended=suspended):
            raise CuckooPackageError("Unable to execute rundll32, analysis aborted")

        if free or not suspended:
            return None
        p.inject()
        p.resume()
        return p.pid

    def check(self):
        return True

    def finish(self):
        return True
