from flask import request
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNTER = Counter(
    'alerta_http_requests_total', 'App Request Count',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY_HISTOGRAM = Histogram('request_latency_seconds', 'Request latency',
    ['method', 'endpoint']
)

ALERT_COUNTER = Counter('alerta_alerts', 'Alerta Requests', 
    ['alert_name', 'alert_mode', 'resource_type', 'resource_id', 'is_duplicate', 'is_correlated']
)

def start_timer():
    request.start_time = time.time()

def stop_timer(response):
    resp_time = time.time() - request.start_time
    REQUEST_LATENCY_HISTOGRAM.labels(request.method, request.path).observe(resp_time)
    return response

def record_request_data(response):
    REQUEST_COUNTER.labels(request.method, request.path,
            response.status_code).inc()
    return response

def setup_metrics(app):
    app.before_request(start_timer)
    # The order here matters since we want stop_timer
    # to be executed first
    app.after_request(record_request_data)
    app.after_request(stop_timer)
