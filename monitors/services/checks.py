# monitors/services/checks.py - Updated to use request_method

import time
import requests
from icmplib import ping


def check_http_monitor(monitor):
    """
    Check an HTTP monitor and return the result
    """
    start_time = time.time()
    try:
        # Select the appropriate method from the requests library based on monitor.request_method
        method = getattr(requests, monitor.request_method.lower())

        # For methods that don't typically include a body, use head() for HEAD method
        # and send empty data for other methods
        if monitor.request_method == "HEAD":
            response = requests.head(
                monitor.url, timeout=monitor.timeout_seconds, allow_redirects=True
            )
        elif monitor.request_method in ["POST", "PUT", "PATCH"]:
            # For methods that typically have a body, send an empty JSON body
            # This could be expanded to allow custom request bodies in the future
            response = method(
                monitor.url,
                timeout=monitor.timeout_seconds,
                allow_redirects=True,
                json={},  # Empty JSON body
            )
        else:
            # GET, DELETE, OPTIONS
            response = method(
                monitor.url, timeout=monitor.timeout_seconds, allow_redirects=True
            )

        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000

        # Check if status code matches expected status code (if set)
        expected_status = monitor.expected_status_code or 200
        is_up = response.status_code == expected_status

        return {
            "is_up": is_up,
            "response_time": response_time_ms,
            "status_code": response.status_code,
            "error_message": (
                None
                if is_up
                else f"Expected status code {expected_status}, got {response.status_code}"
            ),
        }
    except requests.RequestException as e:
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        return {
            "is_up": False,
            "response_time": response_time_ms,
            "status_code": None,
            "error_message": str(e),
        }


def check_ping_monitor(monitor):
    """
    Check a ping monitor and return the result
    """
    try:
        host = monitor.url
        ping_result = ping(host, count=4, interval=0.2, timeout=monitor.timeout_seconds)

        is_up = ping_result.is_alive
        response_time_ms = ping_result.avg_rtt if is_up else None

        return {
            "is_up": is_up,
            "response_time": response_time_ms,
            "status_code": None,
            "error_message": (
                None if is_up else "Host is not responding to ICMP echo requests"
            ),
        }
    except Exception as e:
        return {
            "is_up": False,
            "response_time": None,
            "status_code": None,
            "error_message": str(e),
        }


def check_monitor(monitor):
    """
    Check a monitor based on its type and return the result
    """
    if monitor.monitor_type == "http":
        return check_http_monitor(monitor)
    elif monitor.monitor_type == "ping":
        return check_ping_monitor(monitor)
    else:
        return {
            "is_up": False,
            "response_time": None,
            "status_code": None,
            "error_message": f"Unknown monitor type: {monitor.monitor_type}",
        }
