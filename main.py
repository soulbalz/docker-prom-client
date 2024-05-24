from datetime import datetime, timedelta
import os
import requests
from prometheus_client.parser import text_string_to_metric_families

PUSHGATEWAY_METRICS_URL = os.getenv("PUSHGATEWAY_METRICS_URL", "http://prometheus-prometheus-pushgateway:9091/metrics")
PUSH_TIME_METRICS_NAME = os.getenv("PUSH_TIME_METRICS_NAME", "push_time_seconds")
RETENTION_PERIOD_MINUTES = int(os.getenv("RETENTION_PERIOD_MINUTES", "2"))


def is_metrics_stale(timestamp: float, retention_period_minutes: int = RETENTION_PERIOD_MINUTES) -> bool:
    return datetime.fromtimestamp(timestamp) < datetime.now() - timedelta(minutes=retention_period_minutes)


if __name__ == "__main__":
    with requests.session() as session:
        metrics_list_response = session.get(PUSHGATEWAY_METRICS_URL)
        metrics_list_response.raise_for_status()
        for family in text_string_to_metric_families(metrics_list_response.text):
            for sample in family.samples:
                if sample.name.startswith(PUSH_TIME_METRICS_NAME):
                    if is_metrics_stale(sample.value):
                        url = f"{PUSHGATEWAY_METRICS_URL}/job/{sample.labels['job']}"
                        if sample.labels['instance']:
                            url += f"/instance/{sample.labels['instance']}"
                        res = session.delete(url)
                        res.raise_for_status()