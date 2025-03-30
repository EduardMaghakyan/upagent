import time
import requests
import socket


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
    host = monitor.url
    port = 80  # Default to checking HTTP port, you could make this configurable

    start_time = time.time()
    is_up = False
    error_message = None

    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(monitor.timeout_seconds)

        # Attempt to connect
        result = sock.connect_ex((host, port))
        is_up = result == 0

        if not is_up:
            error_message = f"TCP connection failed with error code {result}"

        # Calculate response time
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000 if is_up else None

        sock.close()

    except socket.gaierror:
        error_message = "Host name resolution failed"
    except socket.timeout:
        error_message = "Connection timed out"
    except Exception as e:
        error_message = str(e)

    return {
        "is_up": is_up,
        "response_time": response_time_ms,
        "status_code": None,
        "error_message": error_message,
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
