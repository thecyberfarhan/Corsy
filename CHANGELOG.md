#### 1.1.0 (fork)
- Fixed findings corrupting each other under multithreading (shared template dict)
- Fixed `-i`/`-u` being ignored when stdin is not a TTY (CI/cron/subprocess)
- Added request timeouts (`--timeout`); fixed `TooManyRedirects` never being caught
- Fixed database path breaking when Corsy is imported or run as a module
- Added `--proxy` (Burp etc.), `--fail-on-finding` (CI), `-V/--version`
- Accept bare hostnames and skip blank/comment lines in input
- Added a pytest suite and GitHub Actions CI

#### 0.2-beta
- Major bug fixes
- Unicode support
- Added `unescaped regex` test

#### 0.1-beta
initial release (with breaking bugs)
