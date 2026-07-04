#!/usr/bin/env python3
"""Build map binary data from personas + geoBoundaries."""
import json
import sys

from salvador_personas.geo.export import build_map_export


def main() -> None:
    try:
        manifest = build_map_export()
    except Exception as exc:
        print(f"ERREUR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({k: manifest[k] for k in ("row_count", "bundle_bytes", "default_scope")}, indent=2))


if __name__ == "__main__":
    main()
