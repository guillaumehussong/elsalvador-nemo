from salvador_personas.geo.export import build_map_export


def main() -> None:
    manifest = build_map_export()
    print(f"OK — {manifest['row_count']} points, {manifest['bundle_bytes']} bytes, default={manifest['default_scope']}")
