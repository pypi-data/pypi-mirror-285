import signal
import sys

import typer
from scapy.packet import Packet
from scapy.sendrecv import sniff
from yaspin import yaspin
from yaspin.spinners import Spinners

from netmon_proc.logger import Logger, LogLevel
from netmon_proc.metrics import Metric
from netmon_proc.options import Opts
from netmon_proc.socket import Socket
from netmon_proc.utils import yaspin_terminator

YASPIN_SIGMAP: dict = {
    signal.SIGINT: yaspin_terminator,
    signal.SIGTERM: yaspin_terminator,
}


class PacketSniffer:
    def __init__(self, bpf_filter: str, metric: Metric):
        self._bpf_filter: str = bpf_filter
        self._metric: Metric = metric
        self._logger: Logger = Logger()
        self._opts: Opts = Opts()

    def _process_packet(self, packet: Packet):
        sockets = self._opts.open_sockets()
        try:
            packet_connection = Socket(packet.sport, packet.dport)
        except (AttributeError, IndexError):
            pass
        else:
            if packet_connection in sockets:
                self._metric += packet

    def start(self):
        try:
            self._logger.log(LogLevel.INFO, "Started sniffing packets", True)
            spinner = yaspin(
                Spinners.dots,
                sigmap=YASPIN_SIGMAP,
                text="Monitoring traffic",
                color="blue",
            )
            self._logger.set_yaspin(spinner)
            spinner.start()
            sniff(
                store=False,
                prn=self._process_packet,
                filter=self._bpf_filter,
            )
            self._logger.set_yaspin(None)
        except PermissionError as exc:
            self._opts.set_running(False)
            self._logger.set_yaspin(None)
            spinner.stop()
            self._logger.log(
                LogLevel.ERROR, "Insufficient permissions. Root privileges required."
            )
            raise typer.Exit(1) from exc
