#!/usr/bin/env python3
"""Mirror the live Neocities site into the current directory.

Reads the file list from the Neocities API and downloads any file whose
sha1 hash differs from what's on disk. Requires NEOCITIES_API_KEY in the
environment. Does not delete local files that were removed from the site.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

SITENAME = "atomicunwasteland"
API_KEY = os.environ.get("NEOCITIES_API_KEY")

if not API_KEY:
    print("NEOCITIES_API_KEY is not set", file=sys.stderr)
    sys.exit(1)


def local_sha1(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    req = urllib.request.Request(
        "https://neocities.org/api/list",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)

    if data.get("result") != "success":
        print(f"Neocities API error: {data}", file=sys.stderr)
        sys.exit(1)

    changed = []
    for entry in data["files"]:
        if entry.get("is_directory"):
            continue
        path = entry["path"]
        remote_hash = entry.get("sha1_hash")

        if remote_hash and remote_hash == local_sha1(path):
            continue

        url = f"https://{SITENAME}.neocities.org/{urllib.parse.quote(path)}"
        try:
            with urllib.request.urlopen(url) as r:
                body = r.read()
        except urllib.error.HTTPError as e:
            print(f"failed to fetch {path}: {e}", file=sys.stderr)
            continue

        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(path, "wb") as out:
            out.write(body)

        changed.append(path)
        print(f"synced {path}")

    if not changed:
        print("no changes")


if __name__ == "__main__":
    main()
