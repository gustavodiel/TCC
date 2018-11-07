#!/usr/local/bin/python3

from __future__ import with_statement

import errno
import locale
import optparse
import os
import platform
import shutil
import socket
from io import StringIO
import subprocess
import sys
import tarfile
import tempfile
import unicodedata
import threading
import time
import traceback
from urllib.request import urlopen

try:
    import gpgme
except ImportError:
    gpgme = None

from contextlib import closing, contextmanager
from posixpath import curdir, sep, pardir, join, abspath, commonprefix

enc = locale.getpreferredencoding()

def is_dropbox_running():
    pidfile = os.path.expanduser("~/.dropbox/dropbox.pid")

    try:
        with open(pidfile, "r") as f:
            pid = int(f.read())
        with open("/proc/%d/cmdline" % pid, "r") as f:
            cmdline = f.read().lower()
    except:
        cmdline = ""

    return "dropbox" in cmdline

def console_print(st=u"", f=sys.stdout, linebreak=True):
    global enc
    f.write(st)
    if linebreak: f.write(os.linesep)


def requires_dropbox_running(meth):
    def newmeth(*n, **kw):
        if is_dropbox_running():
            return meth(*n, **kw)
        else:
            console_print(u"Dropbox isn't running!")
    newmeth.func_name = meth.__name__
    newmeth.__doc__ = meth.__doc__
    return newmeth

class CommandTicker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        ticks = ['[.  ]', '[.. ]', '[...]', '[ ..]', '[  .]', '[   ]']
        i = 0
        first = True
        while True:
            self.stop_event.wait(0.25)
            if self.stop_event.isSet(): break
            if i == len(ticks):
                first = False
                i = 0
            if not first:
                sys.stderr.write("\r%s\r" % ticks[i])
                sys.stderr.flush()
            i += 1
        sys.stderr.flush()

class DropboxCommand(object):
    class CouldntConnectError(Exception): pass
    class BadConnectionError(Exception): pass
    class EOFError(Exception): pass
    class CommandError(Exception): pass

    def __init__(self, timeout=5):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.settimeout(timeout)
        try:
            self.s.connect(os.path.expanduser(u'~/.dropbox/command_socket'))
        except:
            raise DropboxCommand.CouldntConnectError()
        self.f = self.s.makefile("rwb", 4096)

    def close(self):
        self.f.close()
        self.s.close()

    def __readline(self):
        try:
            toret = self.f.readline().decode('utf8').rstrip(u"\n")
        except:
            raise DropboxCommand.BadConnectionError()
        if toret == '':
            raise DropboxCommand.EOFError()
        else:
            return toret

    # atttribute doesn't exist, i know what you want
    def send_command(self, name, args):
        self.f.write(name.encode('utf8'))
        self.f.write(u"\n".encode('utf8'))
        self.f.writelines((u"\t".join([k] + (list(v)
                                             if hasattr(v, '__iter__') else
                                             [v])) + u"\n").encode('utf8')
                          for k,v in args.items())
        self.f.write(u"done\n".encode('utf8'))

        self.f.flush()

        # Start a ticker
        ticker_thread = CommandTicker()
        ticker_thread.start()

        # This is the potentially long-running call.
        try:
            ok = self.__readline() == u"ok"
        except KeyboardInterrupt:
            raise DropboxCommand.BadConnectionError("Keyboard interruption detected")
        finally:
            # Tell the ticker to stop.
            ticker_thread.stop()
            ticker_thread.join()

        if ok:
            toret = {}
            for i in range(21):
                if i == 20:
                    raise Exception(u"close this connection!")

                line = self.__readline()
                if line == u"done":
                    break

                argval = line.split(u"\t")
                toret[argval[0]] = argval[1:]

            return toret
        else:
            problems = []
            for i in range(21):
                if i == 20:
                    raise Exception(u"close this connection!")

                line = self.__readline()
                if line == u"done":
                    break

                problems.append(line)

            raise DropboxCommand.CommandError(u"\n".join(problems))

    # this is the hotness, auto marshalling
    def __getattr__(self, name):
        try:
            return super(DropboxCommand, self).__getattr__(name)
        except:
            def __spec_command(**kw):
                return self.send_command(name, kw)
            self.__setattr__(name, __spec_command)
            return __spec_command


@requires_dropbox_running
def status():
    u"""get current status of the dropboxd
dropbox status

Prints out the current status of the Dropbox daemon.
"""

    try:
        with closing(DropboxCommand()) as dc:
            try:
                lines = dc.get_dropbox_status()[u'status']
                if len(lines) == 0:
                    console_print(u'Idle')
                else:
                    for line in lines:
                        console_print(line)
            except KeyError:
                console_print(u"Couldn't get status: daemon isn't responding")
            except DropboxCommand.CommandError:
                console_print(u"Couldn't get status: " + str(e))
            except DropboxCommand.BadConnectionError:
                console_print(u"Dropbox isn't responding!")
            except DropboxCommand.EOFError:
                console_print(u"Dropbox daemon stopped.")
    except DropboxCommand.CouldntConnectError:
        console_print(u"Dropbox isn't running!")


if __name__ == "__main__":
    status()