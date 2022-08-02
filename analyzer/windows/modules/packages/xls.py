# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os

from lib.common.abstracts import Package
from lib.api.process import Process

class XLS(Package):
    """Excel analysis package."""

    def get_path(self):
        paths = [
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "EXCEL.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office11", "EXCEL.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office12", "EXCEL.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office14", "EXCEL.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office15", "EXCEL.EXE")
        ]

        return next((path for path in paths if os.path.exists(path)), None)

    def start(self, path):
        excel = self.get_path()
        if not excel:
            raise CuckooPackageError("Unable to find any Microsoft Office Excel executable available")

        free = self.options.get("free", False)
        suspended = not free
        p = Process()
        if not p.execute(path=excel, args="\"%s\"" % path, suspended=suspended):
            raise CuckooPackageError("Unable to execute initial Microsoft Office Excel process, analysis aborted")

        if free or not suspended:
            return None
        p.inject()
        p.resume()
        return p.pid

    def check(self):
        return True

    def finish(self):
        return True
