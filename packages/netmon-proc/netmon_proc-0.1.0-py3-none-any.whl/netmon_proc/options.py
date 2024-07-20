from netmon_proc.singleton import SingletonMeta
from netmon_proc.socket import Socket


class Opts(metaclass=SingletonMeta):
    def __init__(self):
        self._verbose = False
        self._running = True
        self._open_sockets: set[Socket] = set()

    def set_verbose(self, verbose: bool):
        self._verbose = verbose

    def verbose(self):
        return self._verbose

    def running(self):
        return self._running

    def set_running(self, running: bool):
        self._running = running

    def open_sockets(self):
        return self._open_sockets

    def set_open_sockets(self, open_sockets: set[Socket]):
        self._open_sockets = open_sockets
