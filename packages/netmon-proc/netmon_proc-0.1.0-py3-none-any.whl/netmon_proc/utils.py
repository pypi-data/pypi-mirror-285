import psutil

from netmon_proc.logger import Logger, LogLevel


def human_readable_format(num_bytes: int) -> tuple[str, str] | None:
    """
    Returns size of bytes in a human-readable format
    """
    for unit in ["B", "Ki", "Mi", "Gi", "Ti", "Pi"]:
        if num_bytes < 1024:
            return (f"{num_bytes:.2f}", unit)
        num_bytes /= 1024
    return None


def find_pids(processes: list[str]) -> set[int]:
    pids: set[int] = set()
    logger: Logger = Logger()

    logger.log(LogLevel.INFO, "Looking for pids of processes", True)
    for p in psutil.process_iter(attrs=["pid", "name"]):
        if p.info["name"] in processes:
            pids.add(p.info["pid"])
            logger.log(
                LogLevel.SUCCESS,
                f"Found process '{p.info['name']}' with pid {p.info['pid']}",
                True,
            )

    return pids


def yaspin_terminator(*_, spinner):
    spinner.ok()
    spinner.stop()
    raise KeyboardInterrupt
