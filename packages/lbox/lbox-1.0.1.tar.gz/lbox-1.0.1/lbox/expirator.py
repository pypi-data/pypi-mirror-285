import argparse
import sys
import time
import os
import re
import threading
import logging
from configparser import ConfigParser

from .common import to_seconds, expiration_pattern, logging_setup

log = logging.getLogger(__file__)

def read_config(cpobject):
    sections = {}

    for secname in cpobject.sections():
        match = re.search(expiration_pattern, secname, re.IGNORECASE)
        if match:
            secs = to_seconds(int(match.group(1)), match.group(2))
            for var, directory in cpobject[secname].items():
                dirlst = directory.split()  # perhaps more than one per line...
                if secs in sections:
                    sections[secs] += dirlst
                else:
                    sections[secs] = dirlst
    return sections


class PeriodicTask(threading.Timer):

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                break
            self.function(*self.args, **self.kwargs)


class ExpireTask:

    def __init__(self, cp, interval=30.0, logger=None):
        self.log = logger if logger else log
        self.sections = read_config(cp)
        if "options" in cp:
            self.interval = cp["options"].getfloat("interval", 30.0)
        else:
            self.interval = 30.0
        self.task = PeriodicTask(self.interval, self.expire_all)

    def go(self):
        self.task.start()

    def expire_directory(self, dirname, secs):
        with os.scandir(dirname) as it:
            for entry in it:
                if not entry.name.startswith(".") and entry.is_file():
                    self.expire_entry(entry, secs)

    def expire_entry(self, entry, secs):
        stat = entry.stat()
        now = time.time()
        if (now - stat.st_mtime) > secs:
            self.log.info("Removing '%s'", entry.path)
            os.remove(entry.path)

    def expire_all(self):
        for secs in self.sections.keys():
            for directory in self.sections[secs]:
                self.expire_directory(directory, secs)

