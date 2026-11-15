# Corsy

> A CORS misconfiguration scanner: sends crafted Origin headers and reports the ones the server trusts.

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Fork](https://img.shields.io/badge/-fork-B4232C?style=flat-square)
![CI](https://github.com/thecyberfarhan/Corsy/actions/workflows/tests.yml/badge.svg)

## At a glance

| | |
| --- | --- |
| **Kind** | Fork |
| **Status** | Active |
| **Language** | Python |
| **Requires** | Python 3.10+ |
| **License** | GPL-3.0 |
| **Upstream** | s0md3v/Corsy |
| **Scope** | Authorized testing only |

## Why

Cross-origin resource sharing is easy to get wrong: a server that echoes back whatever `Origin` it
is sent, or trusts `null`, lets any website read responses meant for logged-in users. Corsy tries
the known ways a CORS allow-list gets bypassed and tells you which one the target falls for. This
fork keeps that, and fixes the parts that gave wrong or missing answers in real use.

## What this shows

- Web and API testing: CORS misconfiguration is a standard part of an API assessment, and this is
  a tool I actually run for it.
- Finding a real concurrency bug by testing under load, not just reading the code: the fix for
  threaded scans corrupting each other's findings was reproduced before it was fixed. See
  [What changed](#what-changed).
- Noticing when a tool's own output can't be trusted (a failed request looked identical to a clean
  host) and fixing the gap instead of only adding features.

## Requirements

- Python 3.10 or newer (CI runs 3.10, 3.12 and 3.13; also run by hand on 3.14)
- `requests` 2.25+ and `urllib3` 1.26+ (see `requirements.txt`)
- `nano`, only if you use `--headers` with no value (it opens an editor; Unix only)
- Tried on: Arch Linux, Kali Linux

## Install

### Arch Linux

```bash
sudo pacman -S --needed python python-pip git
git clone https://github.com/thecyberfarhan/Corsy.git
cd Corsy
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Kali Linux, Parrot OS

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/thecyberfarhan/Corsy.git
cd Corsy
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Check it worked:

```bash
python3 corsy.py --version
```

The virtual environment only needs activating in the shell you use it from. Run `deactivate`, or
open a new terminal, to leave it.

## Usage

### Scan one URL

```bash
python3 corsy.py -u https://example.com/api/me
```

Sends the probes to that URL and prints any misconfiguration found.

### Scan a list of URLs

```bash
python3 corsy.py -i urls.txt -o results.json
```

One URL or bare hostname per line (`example.com` is treated as `https://example.com`). Blank lines
and lines starting with `#` are skipped. `-o` saves the findings as JSON.

### Pipe targets in from another tool

```bash
cat urls.txt | python3 corsy.py
subfinder -d example.com | httprobe | python3 corsy.py -t 10
```

Piped targets are merged with `-u` and `-i`, and duplicates are removed.

### Send traffic through Burp

```bash
python3 corsy.py -u https://example.com --proxy http://127.0.0.1:8080
```

### Authenticated scans

```bash
python3 corsy.py -u https://example.com/api/me --headers "Cookie: SESSION=abc123\nUser-Agent: Mozilla/5.0"
```

Headers are separated by a literal `\n`.

### Gate a CI job

```bash
python3 corsy.py -i staging-urls.txt --fail-on-finding -q
```

Exits `1` if anything is found, `0` if clean, so a pipeline can fail on it.

## Options

| Flag | What it does | Default |
| --- | --- | --- |
| `-u URL` | Target URL | none |
| `-i FILE` | File of URLs or hostnames | none |
| `-o FILE` | Write findings as JSON | off |
| `-t N` | Number of threads | `2` |
| `-d SECONDS` | Delay between requests | `0` |
| `--timeout SECONDS` | Per-request timeout | `10` |
| `--proxy URL` | Route requests through a proxy | off |
| `--headers [HEADERS]` | Extra request headers; no value opens an editor | built-in browser headers |
| `-q` | Hide description, severity and exploitation text | off |
| `--fail-on-finding` | Exit `1` when a misconfiguration is found | off |
| `-V`, `--version` | Print the version | |

## Example output

Against a local test server that reflects every Origin:

```text
 + http://127.0.0.1:8911/reflect
   - Class: origin reflected
   - Description: This host allows any origin to make requests to it.
   - Severity: high
   - Exploitation: Make requests from any domain you control.
   - ACAO Header: http://example.com
   - ACAC Header: true
```

`ACAO` is `Access-Control-Allow-Origin` and `ACAC` is `Access-Control-Allow-Credentials`. A
reflected origin with `ACAC: true` means another site can read authenticated responses.

## What it checks

| Check | Severity | What it means |
| --- | --- | --- |
| `origin reflected` | high | Any Origin is echoed back |
| `pre-domain wildcard` | high | A host that ends with the target's name is accepted |
| `post-domain wildcard` | high | A host that starts with the target's name is accepted |
| `null origin allowed` | high | The `null` Origin is trusted |
| `unescaped regex` | high | The allow-list regex has an unescaped dot |
| `unrecognized underscore` | high | An underscore in the Origin bypasses validation |
| `broken parser` | high | A backtick in the Origin bypasses validation |
| `third party allowed` | medium | A different host is trusted |
| `wildcard value` | low | `*` is returned (browsers won't send credentials with it) |
| `http origin allowed` | low | An unencrypted `http://` Origin is trusted |

## How it works

For each URL, Corsy sends GET requests with a different `Origin` header each time: the site's own
origin first, then a third-party origin, then variations of the site's name (prefixed, suffixed,
with an underscore, a backtick, an altered dot) and `null`. If the response's
`Access-Control-Allow-Origin` echoes back an origin it shouldn't trust, that's a finding. If the
first probe shows the server sends no CORS headers at all, it stops there.

## Comparison

| | Upstream `s0md3v/Corsy` | This fork |
| --- | --- | --- |
| Two findings of the same kind scanned together | Share one record, so their `ACAO`/`ACAC` values overwrite each other | Each finding has its own copy |
| `-i` and `-u` when stdin isn't a terminal (CI, cron, a subprocess) | Ignored; only stdin is read | Merged with piped targets |
| Request timeout | None; one dead host can hang a thread forever | `--timeout`, default 10 s |
| A request that fails | Only a refused connection printed anything; every other failure was silent, so the host looked clean | Every failure is reported |
| Where it finds its checks database | Built from `sys.path[0]`, which breaks when Corsy is imported rather than run as a script | Relative to the package |
| Proxy (Burp) | None | `--proxy` |
| Use in CI | Always exits `0` | `--fail-on-finding` exits `1` on a finding |
| Hostnames without a scheme | Skipped | Treated as `https://` |
| Automated tests | None | 9 tests, run in CI |

Use something else when you need preflight (`OPTIONS`) coverage or session-aware testing: Corsy only sends GET requests.

## What changed

### Fixed: findings overwrote each other when scanned in parallel

Every result of the same kind was built from one shared record loaded from `db/details.json`, and
the scanner wrote the headers into that record. With more than one thread, two endpoints of the
same class ended up reporting identical `ACAO` and `ACAC` values. Reproduced with two wildcard
endpoints, one sending `Access-Control-Allow-Credentials: true` and one not: every run reported
them as the same. A credentialed wildcard could be reported as not credentialed, or the reverse.
Each finding now gets its own copy. A regression test runs both endpoints concurrently five times.

### Fixed: `-i` and `-u` were ignored when stdin wasn't a terminal

When stdin was not a TTY, Corsy read targets from stdin only. In CI, cron or any subprocess,
`-i urls.txt` printed "No valid URLs to test" even with a valid file. It now merges `-u`, `-i` and
piped targets, and removes duplicates.

### Fixed: failed requests looked like clean hosts

The request wrapper printed a message only for a refused connection and returned nothing for any
other failure, including a redirect loop (it compared against a string that never appears in the
error). A host that failed to answer was therefore indistinguishable from a host with no
misconfiguration. Failures are now caught by type and reported. There was also no timeout, so a
host that accepted a connection and never answered blocked its thread indefinitely. `--timeout`
adds one.

### Fixed: the checks database path

It was built from `sys.path[0]`, which is empty when Corsy is imported rather than run as a
script, so importing it failed with `FileNotFoundError: /db/details.json`. The path is now
resolved from the package's own location.

### Added: `--proxy`, `--fail-on-finding`, `--version`, bare hostnames

Proxying through Burp, a non-zero exit for CI, a version flag, and acceptance of `example.com`
style input with `#` comments and blank lines skipped.

### Housekeeping

`core/requester.py` mixed tabs and spaces in one block. It parsed fine, so this isn't a bug fix;
it was just tidied while the file was being rewritten.

## Testing

```bash
pip install pytest
pytest -q
```

Nine tests start a small local HTTP server that models each misconfiguration and assert that the
scanner finds it, that a clean host returns nothing, that two findings never share state, that a
hung host times out, and that input parsing behaves. GitHub Actions runs them on Python 3.10, 3.12
and 3.13. Nothing leaves your machine.

## Limitations

- GET requests only. It does not send preflight `OPTIONS` requests.
- It reports the first misconfiguration it finds on a URL and stops, so a URL with two problems
  shows one.
- `invalid value` appears in the checks database and in upstream's list of tests, but no code
  ever emits it, so Corsy effectively runs 10 checks, not 11.
- It sends no cookies or tokens unless you pass `--headers`, so it tests the anonymous view of an
  endpoint unless you give it a session.
- TLS certificates are not verified, so scans work against lab hosts with self-signed certs.

## Responsible use

Only scan systems you own or have written permission to test. Each scan sends up to nine requests
per URL.

## Credits

Built on [s0md3v/Corsy](https://github.com/s0md3v/Corsy) by Somdev Sangwan and contributors.
Upstream's detection logic and checks database are theirs. The fixes and additions above are in
this fork.

## License

GPL-3.0, the same as upstream. See [LICENSE](LICENSE).
