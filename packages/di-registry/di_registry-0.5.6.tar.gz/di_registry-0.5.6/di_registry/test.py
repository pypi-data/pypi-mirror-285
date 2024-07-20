from typing import Any, Dict, Optional
import json
import functools
import responses


def mock_http_configuration(host: str, name: str, default_configuration: Optional[Dict[str, Any]] = None):
    config = {} if default_configuration is None else default_configuration
    url = f'http://{host}/{name}'

    def get_config(request):
        return 200, {}, json.dumps(config)

    def put_config(request):
        nonlocal config
        config = json.loads(request.body)
        return get_config(request)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            responses.add_callback(responses.GET, url, content_type='application/json', callback=get_config)
            responses.add_callback(responses.PUT, url, content_type='application/json', callback=put_config)

            return func(*args, **kwargs)

        return responses.activate(wrapper)

    return decorator
