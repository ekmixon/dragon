# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os

from lib.common.abstracts import Package
from lib.api.process import Process
from lib.common.exceptions import CuckooPackageError

class IE(Package):
    """Internet Explorer analysis package."""

    def start(self, url):
        free = self.options.get("free", False)
        suspended = not free
        p = Process()
        if not p.execute(path=os.path.join(os.getenv("ProgramFiles"), "Internet Explorer", "iexplore.exe"), args="\"%s\"" % url, suspended=suspended):
            raise CuckooPackageError("Unable to execute initial Internet Explorer process, analysis aborted")

        if free or not suspended:
            return None
        p.inject()
        p.resume()
        return p.pid

    def check(self):
        return True

    def finish(self):
        return True
