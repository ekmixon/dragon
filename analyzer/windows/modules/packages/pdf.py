# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os

from lib.common.abstracts import Package
from lib.api.process import Process
from lib.common.exceptions import CuckooPackageError

class PDF(Package):
    """PDF analysis package."""

    def get_path(self):
        paths = [
            os.path.join(os.getenv("ProgramFiles"), "Adobe", "Reader 8.0", "Reader", "AcroRd32.exe"),
            os.path.join(os.getenv("ProgramFiles"), "Adobe", "Reader 9.0", "Reader", "AcroRd32.exe"),
            os.path.join(os.getenv("ProgramFiles"), "Adobe", "Reader 10.0", "Reader", "AcroRd32.exe"),
            os.path.join(os.getenv("ProgramFiles"), "Adobe", "Reader 11.0", "Reader", "AcroRd32.exe")
        ]

        return next((path for path in paths if os.path.exists(path)), None)

    def start(self, path):
        reader = self.get_path()
        if not reader:
            raise CuckooPackageError("Unable to find any Adobe Reader executable available")

        free = self.options.get("free", False)
        suspended = not free
        p = Process()
        if not p.execute(path=reader, args="\"%s\"" % path, suspended=suspended):
            raise CuckooPackageError("Unable to execute initial Adobe Reader process, analysis aborted")

        if free or not suspended:
            return None
        p.inject()
        p.resume()
        return p.pid

    def check(self):
        return True

    def finish(self):
        return True
