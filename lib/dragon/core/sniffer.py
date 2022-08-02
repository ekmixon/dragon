# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import stat
import logging
import subprocess

from lib.dragon.common.constants import CUCKOO_GUEST_PORT
from lib.dragon.common.config import Config

log = logging.getLogger(__name__)

class Sniffer:
    """Sniffer Manager.

    This class handles the execution of the external tcpdump instance.
    """

    def __init__(self, tcpdump):
        """@param tcpdump: tcpdump path."""
        self.tcpdump = tcpdump
        self.proc = None

    def start(self, interface="eth0", host="", file_path=""):
        """Start sniffing.
        @param interface: network interface name.
        @param host: guest host IP address.
        @param file_path: tcpdump path.
        @return: operation status.
        """
        if not os.path.exists(self.tcpdump):
            log.error("Tcpdump does not exist at path \"%s\", network capture "
                      "aborted" % self.tcpdump)
            return False

        mode = os.stat(self.tcpdump)[stat.ST_MODE]
        if mode and stat.S_ISUID != 2048:
            log.error("Tcpdump is not accessible from this user, network "
                      "capture aborted")
            return False

        if not interface:
            log.error("Network interface not defined, network capture aborted")
            return False

        pargs = [
            self.tcpdump,
            '-U',
            '-q',
            '-i',
            interface,
            '-n',
            *['-w', file_path],
            *['host', host],
            *[
                'and',
                'not',
                '(',
                'host',
                host,
                'and',
                'port',
                str(CUCKOO_GUEST_PORT),
                ')',
            ],
            *[
                'and',
                'not',
                '(',
                'host',
                str(Config().resultserver.ip),
                'and',
                'port',
                str(Config().resultserver.port),
                ')',
            ],
        ]

        try:
            self.proc = subprocess.Popen(pargs,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        except (OSError, ValueError) as e:
            log.exception("Failed to start sniffer (interface=%s, host=%s, "
                          "dump path=%s)" % (interface, host, file_path))
            return False

        log.info(
            f"Started sniffer (interface={interface}, host={host}, dump path={file_path})"
        )


        return True

    def stop(self):
        """Stop sniffing.
        @return: operation status.
        """
        if self.proc and not self.proc.poll():
            try:
                self.proc.terminate()
            except:
                try:
                    if not self.proc.poll():
                        log.debug("Killing sniffer")
                        self.proc.kill()
                except OSError as e:
                    # Avoid "tying to kill a died process" error.
                    log.debug(f"Error killing sniffer: {e}. Continue")
                except Exception as e:
                    log.exception("Unable to stop the sniffer with pid %d"
                                  % self.proc.pid)
                    return False

        return True
