from netmon_proc.metrics import *

METRICS_MAP: dict = {"received": RxBytes}
METRICS_GROUPS: dict = {"transferred": (RxBytes)}


class MetricsFactory:
    @staticmethod
    def from_name(name: str) -> Metric:
        if name not in METRICS_MAP:
            raise KeyError
        return METRICS_MAP[name]()

    @staticmethod
    def from_grp(name: str) -> Metric:
        if name not in METRICS_GROUPS:
            raise KeyError
        composite: Metric = CompositeMetric(name)
        for component in METRICS_GROUPS[name]:
            composite.add(component)
        return composite

    @staticmethod
    def from_list(metrics: list[Metrics]) -> Metric:
        composite: Metric = CompositeMetric("Collected")
        for m in metrics:
            if m in METRICS_MAP:
                composite.add(MetricsFactory.from_name(m))
            elif m in METRICS_GROUPS:
                composite.add(MetricsFactory.from_grp(m))
        return composite
