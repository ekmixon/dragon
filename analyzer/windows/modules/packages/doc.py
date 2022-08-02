# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os

from lib.common.abstracts import Package
from lib.api.process import Process
from lib.common.exceptions import CuckooPackageError

class DOC(Package):
    """Word analysis package."""

    def get_path(self):
        paths = [
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "WINWORD.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office11", "WINWORD.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office12", "WINWORD.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office14", "WINWORD.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office15", "WINWORD.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "WORDVIEW.EXE"),
            os.path.join(os.getenv("ProgramFiles"), "Microsoft Office", "Office11", "WORDVIEW.EXE")
        ]

        return next((path for path in paths if os.path.exists(path)), None)

    def start(self, path):
        word = self.get_path()
        if not word:
            raise CuckooPackageError("Unable to find any Microsoft Office Word executable available")

        free = self.options.get("free", False)
        suspended = not free
        p = Process()
        if not p.execute(path=word, args="\"%s\"" % path, suspended=suspended):
            raise CuckooPackageError("Unable to execute initial Microsoft Office Word process, analysis aborted")

        if free or not suspended:
            return None
        p.inject()
        p.resume()
        return p.pid

    def check(self):
        return True

    def finish(self):
        return True
