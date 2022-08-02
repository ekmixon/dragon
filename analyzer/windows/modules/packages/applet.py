# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import string
import random

from lib.common.abstracts import Package
from lib.api.process import Process
from lib.common.exceptions import CuckooPackageError

class Applet(Package):
    """Java Applet analysis package."""

    def get_path(self):
        paths = [
            os.path.join(os.getenv("ProgramFiles"), "Mozilla Firefox", "firefox.exe"),
            os.path.join(os.getenv("ProgramFiles"), "Internet Explorer", "iexplore.exe")
        ]

        return next((path for path in paths if os.path.exists(path)), None)

    def make_html(self, path, class_name):
        html = "<html>" + "<body>"
        html += "<applet archive=\"%s\" code=\"%s\" width=\"1\" height=\"1\">" % (path, class_name)
        html += "</applet>"
        html += "</body>"
        html += "</html>"

        file_name = (
            "".join(random.choice(string.ascii_lowercase) for _ in range(6))
            + ".html"
        )

        file_path = os.path.join(os.getenv("TEMP"), file_name)
        with open(file_path, "w") as file_handle:
            file_handle.write(html)
        return file_path

    def start(self, path):
        browser = self.get_path()
        if not browser:
            raise CuckooPackageError("Unable to find any browser executable available")

        free = self.options.get("free", False)
        class_name = self.options.get("class", None)
        suspended = not free
        html_path = self.make_html(path, class_name)

        p = Process()
        if not p.execute(path=browser, args="\"%s\"" % html_path, suspended=suspended):
            raise CuckooPackageError("Unable to execute initial Internet Exploer process, analysis aborted")

        if free or not suspended:
            return None
        p.inject()
        p.resume()
        return p.pid

    def check(self):
        return True

    def finish(self):
        return True
