import concurrent.futures

from core.tests import active_tests, details
from core.utils import host, normalize_url, dedupe
from core.requester import requester

HEADERS = {'User-Agent': 'corsy-tests'}


def scan(base, path):
    url = base + path
    return active_tests(url, host(url), 'http', dict(HEADERS), 0, timeout=5)


def test_db_loaded():
    # every misconfiguration template must be present and shaped right
    assert len(details) == 11
    for entry in details.values():
        assert {'class', 'description', 'severity', 'exploitation'} <= set(entry)


def test_detects_origin_reflection(server):
    res = scan(server, '/reflect')
    key = next(iter(res))
    assert res[key]['class'] == 'origin reflected'
    assert res[key]['acac header'] == 'true'


def test_detects_wildcard(server):
    res = scan(server, '/wildcard_cred')
    assert next(iter(res.values()))['class'] == 'wildcard value'


def test_detects_null_origin(server):
    res = scan(server, '/null')
    assert next(iter(res.values()))['class'] == 'null origin allowed'


def test_clean_host_returns_nothing(server):
    assert scan(server, '/nothing') is None


def test_no_cross_result_corruption(server):
    # the regression: two findings of the same class must not share one dict.
    # cred endpoint has ACAC=true, plain endpoint has ACAC=None - run them
    # concurrently and confirm each keeps its own value.
    urls = [server + '/wildcard_cred', server + '/wildcard_plain']
    for _ in range(5):
        merged = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(scan, server, '/' + u.rsplit('/', 1)[1]) for u in urls]
            for f in concurrent.futures.as_completed(futures):
                r = f.result()
                if r:
                    merged.update(r)
        acac = {k.rsplit('/', 1)[1]: v['acac header'] for k, v in merged.items()}
        assert acac['wildcard_cred'] == 'true'
        assert acac['wildcard_plain'] is None


def test_timeout_returns_empty_fast(server):
    import time
    start = time.time()
    out = requester(server + '/hang', 'http', dict(HEADERS), 'http://example.com', timeout=1)
    assert out == {}
    assert time.time() - start < 5


def test_normalize_url():
    assert normalize_url('example.com') == 'https://example.com'
    assert normalize_url('http://x.com') == 'http://x.com'
    assert normalize_url('https://x.com/a') == 'https://x.com/a'
    assert normalize_url('# comment') is None
    assert normalize_url('has space') is None
    assert normalize_url('') is None


def test_dedupe_preserves_order():
    assert dedupe(['a', 'b', 'a', 'c', 'b']) == ['a', 'b', 'c']
