import os
import time

from core.requester import requester
from core.utils import host, load_json

# resolve the database relative to this file so Corsy works no matter the current
# directory or how it is imported (previously broke when not run as ./corsy.py)
_HERE = os.path.dirname(os.path.abspath(__file__))
details = load_json(os.path.join(_HERE, os.pardir, 'db', 'details.json'))


def finding(url, key, acao_header, acac_header):
    # copy the template so concurrent scans never mutate the shared db entry
    info = dict(details[key])
    info['acao header'] = acao_header
    info['acac header'] = acac_header
    return {url: info}


def passive_tests(url, headers):
    root = host(url)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header == '*':
        return finding(url, 'wildcard value', acao_header, acac_header)
    if root:
        if host(acao_header) and root != host(acao_header):
            return finding(url, 'third party allowed', acao_header, acac_header)


def active_tests(url, root, scheme, header_dict, delay, timeout=10, proxies=None):
    origin = scheme + '://' + root
    headers = requester(url, scheme, header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header is None:
        return

    origin = scheme + '://' + 'example.com'
    headers = requester(url, scheme, header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header and acao_header == (origin):
        return finding(url, 'origin reflected', acao_header, acac_header)
    time.sleep(delay)

    origin = scheme + '://' + root + '.example.com'
    headers = requester(url, scheme, header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header and acao_header == (origin):
        return finding(url, 'post-domain wildcard', acao_header, acac_header)
    time.sleep(delay)

    origin = scheme + '://d3v' + root
    headers = requester(url, scheme, header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header and acao_header == (origin):
        return finding(url, 'pre-domain wildcard', acao_header, acac_header)
    time.sleep(delay)

    origin = 'null'
    headers = requester(url, '', header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header and acao_header == 'null':
        return finding(url, 'null origin allowed', acao_header, acac_header)
    time.sleep(delay)

    origin = scheme + '://' + root + '_.example.com'
    headers = requester(url, scheme, header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header and acao_header == origin:
        return finding(url, 'unrecognized underscore', acao_header, acac_header)
    time.sleep(delay)

    origin = scheme + '://' + root + '%60.example.com'
    headers = requester(url, scheme, header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header and '`.example.com' in acao_header:
        return finding(url, 'broken parser', acao_header, acac_header)
    time.sleep(delay)

    if root.count('.') > 1:
        origin = scheme + '://' + root.replace('.', 'x', 1)
        headers = requester(url, scheme, header_dict, origin, timeout, proxies)
        acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
        if acao_header and acao_header == origin:
            return finding(url, 'unescaped regex', acao_header, acac_header)
        time.sleep(delay)

    origin = 'http://' + root
    headers = requester(url, 'http', header_dict, origin, timeout, proxies)
    acao_header, acac_header = headers.get('access-control-allow-origin', None), headers.get('access-control-allow-credentials', None)
    if acao_header and acao_header.startswith('http://'):
        return finding(url, 'http origin allowed', acao_header, acac_header)
    else:
        return passive_tests(url, headers)
