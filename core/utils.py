import os
import re
import json
import tempfile
import re

from urllib.parse import urlparse

def host(string):
    if string and '*' not in string:
        return urlparse(string).netloc


def load_json(file):
    with open(file) as f:
        return json.load(f)


def format_result(result):
    new_result = {}
    for each in result:
        if each:
            for i in each:
                new_result[i] = each[i]
    return new_result


def normalize_url(line):
    # accept full URLs as-is and bare hosts (example.com, sub.example.com[:port][/path])
    # by assuming https, so -i wordlists and httprobe output both work
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    if line.startswith(('http://', 'https://')):
        return line
    if ' ' in line or '://' in line:
        return None
    return 'https://' + line


def _read_lines(lines):
    urls = []
    for line in lines:
        url = normalize_url(line)
        if url:
            urls.append(url)
    return urls


def create_url_list(target_url, inp_file):
    urls = []
    if inp_file:
        with open(inp_file, 'r') as file:
            urls.extend(_read_lines(file))
    if target_url:
        target = normalize_url(target_url)
        if target:
            urls.append(target)
    return urls


def create_stdin_list(stdin):
    return _read_lines(stdin)


def dedupe(urls):
    # preserve order, drop duplicates
    return list(dict.fromkeys(urls))

def prompt(default=None):
    editor = 'nano'
    with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
        if default:
            tmpfile.write(default)
            tmpfile.flush()

        child_pid = os.fork()
        is_child = child_pid == 0

        if is_child:
            os.execvp(editor, [editor, tmpfile.name])
        else:
            os.waitpid(child_pid, 0)
            tmpfile.seek(0)
            return tmpfile.read().strip()


def extractHeaders(headers: str):
    sorted_headers = {}
    for header in headers.split('\\n'):
        name, value = header.split(":", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 1 and value[-1] == ',':
            value = value[:-1]
        sorted_headers[name] = value
    return sorted_headers