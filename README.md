
<h1 align="center">
  <br>
  <a href="https://github.com/s0md3v/Corsy"><img src="https://i.ibb.co/K0Z7X99/corsy.png" alt="Corsy"></a>
  <br>
  Corsy
  <br>
</h1>

<h4 align="center">CORS Misconfiguration Scanner</h4>

<p align="center">
  <a href="https://github.com/s0md3v/Corsy/releases">
    <img src="https://img.shields.io/github/release/s0md3v/Corsy.svg">
  </a>
  <a href="https://github.com/s0md3v/Corsy/issues?q=is%3Aissue+is%3Aclosed">
      <img src="https://img.shields.io/github/issues-closed-raw/s0md3v/Corsy.svg">
  </a>
</p>

### Introduction
Corsy is a lightweight program that scans for all known misconfigurations in CORS implementations.

![demo](https://i.ibb.co/Jc1HtmW/corsy.png)

### Requirements
Corsy works with `Python 3` and depends on `requests`.

Install the dependencies from the Corsy directory with `pip3 install -r requirements.txt`

### Usage
Using Corsy is pretty simple

`python3 corsy.py -u https://example.com`

##### Scan URLs from a file
`python3 corsy.py -i /path/urls.txt`

##### Scan URLs from stdin
`cat urls.txt | python3 corsy.py`

##### Number of threads
`python3 corsy.py -u https://example.com -t 20`

##### Delay between requests
`python3 corsy.py -u https://example.com -d 2`

##### Export results to JSON
`python3 corsy.py -i /path/urls.txt -o /path/output.json`

##### Request timeout (seconds)
`python3 corsy.py -u https://example.com --timeout 5`

##### Route through a proxy (e.g. Burp)
`python3 corsy.py -u https://example.com --proxy http://127.0.0.1:8080`

##### Fail the run if anything is found (useful in CI)
`python3 corsy.py -i /path/urls.txt --fail-on-finding`

##### Custom HTTP headers
`python3 corsy.py -u https://example.com --headers "User-Agent: GoogleBot\nCookie: SESSION=Hacked"`

##### Skip printing tips
`-q` can be used to skip printing of `description`, `severity`, `exploitation` fields in the output.

### Tests implemented
- Pre-domain bypass
- Post-domain bypass
- Backtick bypass
- Null origin bypass
- Unescaped dot bypass
- Underscore bypass
- Invalid value
- Wild card value
- Origin reflection test
- Third party allowance test
- HTTP allowance test


---

### Changes in this fork

This fork fixes real correctness and usability bugs and adds a few features, with a
test suite (`pytest`) and CI covering all of it. Diff against
[s0md3v/Corsy](https://github.com/s0md3v/Corsy):

**Bug fixes**
- **Findings no longer corrupt each other under threads.** Every result reused the
  same shared template dict from the database, so concurrent scans overwrote one
  another's `ACAO`/`ACAC` headers (last writer won). A credentialed wildcard could be
  reported as non-credentialed, or vice versa. Each finding now gets its own copy.
- **`-i` and `-u` are no longer ignored in non-interactive shells.** When stdin was
  not a TTY (CI, cron, any subprocess) Corsy read *only* stdin and silently dropped
  the input file and target URL. Targets from `-u`, `-i` and piped stdin are now
  merged and de-duplicated.
- **Requests now time out.** There was no timeout, so a single hung host blocked a
  worker thread forever. Added `--timeout` (default 10s).
- **`TooManyRedirects` is actually caught.** The old handler matched on a string that
  never appears, so the exception escaped; it is now caught by type, alongside
  `Timeout` and `ConnectionError`.
- **Database path no longer depends on the working directory.** It was built from
  `sys.path[0]`, which broke when Corsy was imported or run as a module. It is now
  resolved relative to the package.
- Normalised mixed tabs/spaces that could raise `TabError` on stricter parsers.

**Features**
- `--timeout` — per-request timeout in seconds.
- `--proxy` — route all traffic through a proxy such as Burp Suite.
- `--fail-on-finding` — exit `1` when a misconfiguration is found, for CI gating.
- `-V` / `--version`.
- Bare hostnames in input (`example.com`) are accepted and assumed `https://`, and
  blank/`#` comment lines in input files are skipped.

**Tested**
- `pytest` suite spins up a local target modelling each misconfiguration and asserts
  detection plus the two regressions above; runs on Python 3.9-3.13 in CI.
