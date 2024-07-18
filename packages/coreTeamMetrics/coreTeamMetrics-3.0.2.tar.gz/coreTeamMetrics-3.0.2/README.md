# MetricsCollector

MetricsCollector is a Python module that allows you to collect and expose metrics of python applications using prometheus.

## Features

- This provides metrics like garbage collections,cpu,memory,fds,thread count.
- Exposes metrics via an HTTP server for Prometheus to scrape.

## Installation

You can install MetricsCollector using pip:

```shell
pip install metricscollector
```

## How to use

    from coreTeamMetrics import MetricsCollector
    
    server_port = server_port 
    metrics_collector = MetricsCollector(server_port)
    metrics_collector.start()