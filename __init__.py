
import ctypes
import threading
import sys
import signal
import time
import asyncio

import jupyter_client

from subprocess import Popen, PIPE

from binaryninja.plugin import BackgroundTask, BackgroundTaskThread
from binaryninja import *

from ipykernel.kernelapp import IPKernelApp
from IPython import get_ipython

from .binjamagic import load_ipython_extension

# this is the heavy monkey-patching that actually works
# i.e. you can start the kernel fine and connect to it e.g. via
# ipython console --existing
signal.signal = lambda *args, **kw: None


class KernelWrapper(BackgroundTaskThread):
    def __init__(self):
        BackgroundTaskThread.__init__(self, "", can_cancel=False)
        self.connection_file = None

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        app = IPKernelApp.instance()
        app.initialize()
        ip = get_ipython()
        load_ipython_extension(ip)
        self.connection_file = app.connection_file
        app.start()

    def spawn_qt(self, bv):
        argv = []
        cf = jupyter_client.find_connection_file(self.connection_file)
        cmd = ';'.join([
            "from IPython.qt.console import qtconsoleapp",
            "qtconsoleapp.main()"
        ])
        kwargs = {}
        kwargs['start_new_session'] = True
        Popen(
            ['python', '-c', cmd, '--existing', cf] + argv,
            stdout=PIPE, stderr=PIPE, close_fds=(
                sys.platform != 'win32'),
            **kwargs
        )


def setup_plugin():
    kw = KernelWrapper()
    kw.start()
    PluginCommand.register("Binja IPython: Start QT Shell",
                           "Binja IPython", kw.spawn_qt)


setup_plugin()
