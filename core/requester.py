import urllib3
import requests
from core.colors import bad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def requester(url, scheme, headers, origin, timeout=10, proxies=None):
    # send the probe with the attacker-controlled Origin and hand back the response
    # headers, but only when the server actually echoes a CORS policy
    headers = dict(headers)
    headers['Origin'] = origin
    try:
        response = requests.get(
            url, headers=headers, verify=False, timeout=timeout, proxies=proxies,
        )
    except requests.exceptions.Timeout:
        print('%s %s timed out' % (bad, url))
        return {}
    except requests.exceptions.TooManyRedirects:
        print('%s %s has too many redirects' % (bad, url))
        return {}
    except requests.exceptions.ConnectionError:
        print('%s %s is unreachable' % (bad, url))
        return {}
    except requests.exceptions.RequestException as e:
        print('%s %s failed: %s' % (bad, url, e))
        return {}
    for key in response.headers:
        if key.lower() == 'access-control-allow-origin':
            return response.headers
    return {}
