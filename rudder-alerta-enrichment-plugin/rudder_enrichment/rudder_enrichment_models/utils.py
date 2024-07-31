import urllib.parse as urlparse
from urllib.parse import urlencode

def add_query_params_to_url(url, parameters):
    if not isinstance(parameters, dict):
        parameters = dict()
    implicit_params = {"utm_source": "notisvc", "utm_medium": "email"}
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({**implicit_params, **parameters})
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)