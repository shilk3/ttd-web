"""Write the site's service worker with a content fingerprint for every file.

The worker only downloads files whose fingerprint changed since the copy the
phone already holds, so a small update stays small.

Usage: python3 write_sw.py SITE_DIR TEMPLATE OPENTTD_VERSION
"""
import hashlib
import json
import os
import sys

# Files the app needs offline; './' is the start page and is the same file as index.html.
FILES = ['index.html', 'openttd.js', 'openttd.wasm', 'openttd.data',
         'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png']


def fingerprint(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def main():
    site, template, openttd_version = sys.argv[1], sys.argv[2], sys.argv[3]
    files = {name: fingerprint(os.path.join(site, name)) for name in FILES}
    files['./'] = files['index.html']
    # The version only changes when some file changes, so a rebuild with no real
    # change gives a byte-identical sw.js and phones see no update.
    combined = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:8]
    with open(template) as f:
        sw = f.read()
    for placeholder, value in (('@@VERSION@@', f'{openttd_version}-{combined}'),
                               ('/*@@FILES@@*/ {}', json.dumps(files, indent=2, sort_keys=True))):
        assert sw.count(placeholder) == 1, placeholder
        sw = sw.replace(placeholder, value)
    with open(os.path.join(site, 'sw.js'), 'w') as f:
        f.write(sw)
    print(f'sw.js version {openttd_version}-{combined}')


if __name__ == '__main__':
    main()
