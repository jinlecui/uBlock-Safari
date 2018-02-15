#!/usr/bin/env python3

import base64
import os
import re
import sys

if len(sys.argv) == 1 or not sys.argv[1]:
    raise SystemExit('Build dir missing.')

# resource_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
build_dir = os.path.abspath(sys.argv[1])

# Read list of resource tokens to convert
to_import = set()
with open('./src/web_accessible_resources/to-import.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if len(line) != 0 and line[0] != '#':
            to_import.add(line)

# scan the file until a resource to import is found
def find_next_resource(f):
    for line in f:
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue
        parts = line.partition(' ')
        if parts[0] in to_import:
            return (parts[0], parts[2].strip())
    return ('', '')

def safe_filename_from_token(token, mime):
    name = str(base64.b64encode(bytes(token, 'utf-8'), b'-_'), 'utf-8').strip('=')
    # extract file extension from mime
    match = re.search('^[^/]+/([^\s;]+)', mime)
    if match:
        name += '.' + match.group(1)
    return name

def import_resource(f, token, mime):
    isBinary = mime.endswith(';base64')
    lines = []
    for line in f:
        if line.strip() == '':
            break
        if line.lstrip()[0] == '#':
            continue
        if isBinary:
            line = line.strip()
        lines.append(line)
    filename = safe_filename_from_token(token, mime)
    filepath = os.path.join(build_dir, 'web_accessible_resources', filename)
    filedata = ''.join(lines)
    if isBinary:
        filedata = base64.b64decode(filedata)
    else:
        filedata = bytes(filedata, 'utf-8')
    with open(filepath, 'wb') as fo:
        fo.write(filedata)

# Read content of the resources to convert
# - At this point, it is assumed resources.txt has been imported into the
#   package.
resources_filename = os.path.join(build_dir, 'assets/ublock/resources.txt')
with open(resources_filename, 'r') as f:
    while True:
        token, mime = find_next_resource(f)
        if token == '':
            break
        import_resource(f, token, mime)

