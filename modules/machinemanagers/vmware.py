# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file was originally produced by Mike Tu.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import logging
import subprocess
import os.path
import time

from lib.dragon.common.abstracts import MachineManager
from lib.dragon.common.exceptions import CuckooMachineError

log = logging.getLogger(__name__)

class VMware(MachineManager):
    """Virtualization layer for VMware Workstation using vmrun utility."""

    def _initialize_check(self):
        """Check for configuration file and vmware setup.
        @raise CuckooMachineError: if configuration is missing or wrong.
        """  
        if not self.options.vmware.path:
            raise CuckooMachineError("VMware vmrun path missing, please add it to vmware.conf")
        if not os.path.exists(self.options.vmware.path):
            raise CuckooMachineError(
                f"VMware vmrun not found in specified path {self.options.vmware.path}"
            )

        # Consistency checks.
        for machine in self.machines():
            host, snapshot = self._parse_label(machine.label)
            self._check_vmx(host)
            self._check_snapshot(host, snapshot)
        # Base checks.
        super(VMware, self)._initialize_check()

    def _check_vmx(self, host):
        """Checks a vmx file
        @param host: file path
        @raise CuckooMachineError: if file not found or not ending with .vmx
        """
        if not host.endswith(".vmx"):
            raise CuckooMachineError(
                f"Wrong configuration: vm path not ending with .vmx: {host})"
            )

        if not os.path.exists(self.options.vmware.path):
            raise CuckooMachineError(f"Vm file {host} not found")

    def _check_snapshot(self, host, snapshot):
        """Checks snapshot existance.
        @param host: file path
        @param snapshot: snapshot name
        @raise CuckooMachineError: if snapshot not found
        """
        try:
            output, error = subprocess.Popen([self.options.vmware.path,
                              "listSnapshots",
                              host],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate()
            if output:
                return snapshot in output
            else:
                raise CuckooMachineError(
                    f"Unable to get snapshot list for {host}. No output from `vmrun listSnapshots`"
                )

        except OSError as e:
            raise CuckooMachineError(
                f"Unable to get snapshot list for {host}. Reason: {e}"
            )

    def start(self, label):
        """Start a virtual machine.
        @param label: virtual machine identifier: path to vmx file and current snapshot name.
        @raise CuckooMachineError: if unable to start.
        """
        host, snapshot = self._parse_label(label)

        # Preventive check
        if self._is_running(host):
            raise CuckooMachineError(f"Machine {host} is already running")

        self._revert(host, snapshot)

        time.sleep(3)

        log.debug(f"Starting vm {host}")
        try:
            proc = subprocess.Popen([self.options.vmware.path,
                              "start",
                              host,
                              self.options.vmware.mode],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
            if self.options.vmware.mode.lower() == "gui":
                output, error = proc.communicate()
                if output:
                    raise CuckooMachineError(f"Unable to start machine {host}: {output}")
        except OSError as e:
            raise CuckooMachineError(
                f"Unable to start machine {host} in {self.options.vmware.mode.upper()} mode: {e}"
            )

    def stop(self, label):
        """Stops a virtual machine.
        @param label: virtual machine identifier: path to vmx file and current snapshot name.
        @raise CuckooMachineError: if unable to stop.
        """
        host, snapshot = self._parse_label(label)

        log.debug(f"Stopping vm {host}")
        if self._is_running(host):
            try:
                if subprocess.call([self.options.vmware.path,
                                   "stop",
                                    host,
                                   "hard"], # Machete never wait.
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE):
                    raise CuckooMachineError(f"Error shutting down machine {host}")
            except OSError as e:
                raise CuckooMachineError(f"Error shutting down machine {host}: {e}")
        else:
            log.warning(f"Trying to stop an already stopped machine: {host}")

    def _revert(self, host, snapshot):
        """Revets machine to snapshot.
        @param host: file path
        @param snapshot: snapshot name
        @raise CuckooMachineError: if unable to revert
        """
        log.debug(f"Revert snapshot for vm {host}")
        try:
            if subprocess.call([self.options.vmware.path,
                               "revertToSnapshot",
                               host,
                               snapshot],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE):
                raise CuckooMachineError(
                    f"Unable to revert snapshot for machine {host}: vmrun exited with error"
                )

        except OSError as e:
            raise CuckooMachineError(f"Unable to revert snapshot for machine {host}: {e}")

    def _is_running(self, host):
        """Checks if host is running.
        @param host: file path
        @return: running status
        """
        try:
            output, error = subprocess.Popen([self.options.vmware.path,
                              "list"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate()
            if output:
                return host in output
            else:
                raise CuckooMachineError(
                    f"Unable to check running status for {host}. No output from `vmrun list`"
                )

        except OSError as e:
            raise CuckooMachineError(
                f"Unable to check running status for {host}. Reason: {e}"
            )

    def _parse_label(self, label):
        """Parse configuration file label.
        @param label: configuration option from config file
        @return: tuple of host file path and snapshot name
        """
        opts = label.strip().split(",")
        if len(opts) != 2:
            raise CuckooMachineError("Wrong label syntax for %s in vmware.conf: %s" % label)
        label = opts[0].strip()
        snapshot = opts[1].strip()
        return label, snapshot
