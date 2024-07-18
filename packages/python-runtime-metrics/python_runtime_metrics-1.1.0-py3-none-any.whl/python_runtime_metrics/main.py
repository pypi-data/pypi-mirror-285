import threading
from prometheus_client import start_http_server, Gauge
import time

class MetricsCollector:
    def __init__(self, server_port):
        self.server_port = server_port
        self.g_thread_count = Gauge('thread_count', 'Total number of active threads')

    def collect_metrics(self):
        self.g_thread_count.set(threading.active_count())

    def start(self):
        start_http_server(self.server_port)

if __name__ == '__main__':
  metrics_collector = MetricsCollector()
