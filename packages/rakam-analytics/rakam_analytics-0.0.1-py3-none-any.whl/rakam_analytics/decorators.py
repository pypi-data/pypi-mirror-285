import requests
import json
from functools import wraps
from rest_framework.response import Response
from rest_framework.request import Request


def register_endpoint_event(event_type: str, company: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Build the Data
            event_data = {
                "endpoint": request.path,
                "type": event_type,
                "content": json.loads(request.body.decode('utf-8')),
                "company": company
            }

            # Extract headers from the incoming request
            headers = {k: v for k, v in request.headers.items()}

            # Rakam Analytics API event url
            url = "http://rakam-analytics-server-lb-890345667.eu-west-3.elb.amazonaws.com/api/application/event/create/"

            # Call Rakam Analytics Endpoint
            try:
                response = requests.post(url=url, json=event_data, headers=headers, timeout=10)

                if response.status_code != 201:
                    return Response("External service is down", status=503)
            except requests.exceptions.RequestException as request_exception:
                return Response(str(request_exception), status=503)

            # Call the original view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
