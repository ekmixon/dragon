# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

from lib.common.abstracts import Package
from lib.api.process import Process
from lib.common.exceptions import CuckooPackageError

class Exe(Package):
    """EXE analysis package."""

    def start(self, path):
        free = self.options.get("free", False)
        args = self.options.get("arguments", None)
        suspended = not free
        p = Process()
        if not p.execute(path=path, args=args, suspended=suspended):
            raise CuckooPackageError("Unable to execute initial process, analysis aborted")

        if free or not suspended:
            return None
        p.inject()
        p.resume()
        return p.pid

    def check(self):
        return True

    def finish(self):
        return True
