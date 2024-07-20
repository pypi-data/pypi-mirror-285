import time
from threading import Thread
from typing import List

import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from yaspin import yaspin
from yaspin.spinners import Spinners

import netmon_proc.utils
from netmon_proc.logger import Logger, LogLevel
from netmon_proc.metrics import Metric, Metrics
from netmon_proc.metricsfactory import METRICS_MAP, MetricsFactory
from netmon_proc.options import Opts
from netmon_proc.sniffer import PacketSniffer
from netmon_proc.socketwatcher import SocketWatcher

LOGGER: Logger = Logger()
OPTS: Opts = Opts()


def output_metrics(collected: Metric):
    console: Console = Console()
    table: Table = Table("Name", "Value")
    metrics: list[Metric] = (
        [collected] if collected.name() in METRICS_MAP else collected.children()
    )

    while len(metrics) > 0:
        try:
            current: Metric = metrics[0]
            if current.name().lower() in METRICS_MAP:
                table.add_row(current.name(), current.human_readable_value())
            metrics.pop(0)
            metrics.extend(current.children())
        except NotImplementedError:
            continue

    console.print(table)


def main(
    processes: Annotated[
        List[str], typer.Argument(help="List of processes to monitor")
    ],
    delay: Annotated[
        float,
        typer.Option(
            "--delay", "-d", min=0, help="Seconds to wait for before monitoring"
        ),
    ] = 0,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose output")
    ] = False,
    bpf_filter: Annotated[
        str, typer.Option("--filter", "-f", help="BPF filter to use")
    ] = "tcp and inbound",
    metrics: Annotated[
        List[Metrics], typer.Option("--metrics", "-m", help="Metrics to collect")
    ] = [Metrics.received],
):
    OPTS.set_verbose(verbose)

    if delay > 0:
        with yaspin(Spinners.dots, text=f"Waiting for {delay} seconds", color="blue"):
            time.sleep(delay)

    pids = netmon_proc.utils.find_pids(processes)
    if len(pids) == 0:
        LOGGER.log(LogLevel.ERROR, "No PID associated with given names")
        raise typer.Exit(1)

    collected_metrics = MetricsFactory.from_list(metrics)
    sniffer = PacketSniffer(bpf_filter, collected_metrics)

    socketwatcher = SocketWatcher(pids)
    socketwatcher_thread = Thread(target=socketwatcher.start)
    socketwatcher_thread.start()

    sniffer.start()

    OPTS.set_running(False)
    output_metrics(collected_metrics)


def run():
    typer.run(main)
