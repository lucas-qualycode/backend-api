from domain.locations.repository import LocationRepository


def embed_locations_on_event_dicts(rows: list[dict], location_repo: LocationRepository) -> list[dict]:
    if not rows:
        return []
    ids = list({r.get("location_id") for r in rows if r.get("location_id")})
    loc_map = location_repo.get_by_ids(ids)
    for r in rows:
        lid = r.get("location_id")
        if not lid:
            r["location"] = None
            continue
        loc = loc_map.get(lid)
        if loc is None or loc.deleted:
            r["location"] = None
        else:
            r["location"] = loc.model_dump(mode="json")
    return rows
