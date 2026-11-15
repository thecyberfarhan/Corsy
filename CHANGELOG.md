#### 1.1.0 (fork)
- Fixed findings overwriting each other when scanned in parallel (shared template record)
- Fixed `-i`/`-u` being ignored when stdin is not a TTY (CI, cron, subprocesses)
- Fixed failed requests looking like clean hosts: only a refused connection printed anything; added `--timeout`
- Fixed the checks database path, which broke when Corsy is imported rather than run as a script
- Added `--proxy`, `--fail-on-finding`, `-V/--version`
- Accept bare hostnames and skip blank/comment lines in input files
- Added a pytest suite and GitHub Actions CI

#### 0.2-beta
- Major bug fixes
- Unicode support
- Added `unescaped regex` test

#### 0.1-beta
initial release (with breaking bugs)
