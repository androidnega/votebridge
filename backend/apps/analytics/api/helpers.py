"""Analytics API response helpers."""

from apps.candidates.models import Candidate


def attach_candidate_image_urls(data: dict, request) -> dict:
    if not data or not request:
        return data

    candidate_uuids = set()

    for position in data.get("positions", []):
        for key in ("candidates",):
            for candidate in position.get(key, []):
                if candidate.get("candidate_uuid"):
                    candidate_uuids.add(candidate["candidate_uuid"])
        for role_key in ("leader", "runner_up", "winner"):
            role = position.get(role_key)
            if role and role.get("candidate_uuid"):
                candidate_uuids.add(role["candidate_uuid"])

    for candidate in data.get("candidates", []):
        if candidate.get("candidate_uuid"):
            candidate_uuids.add(candidate["candidate_uuid"])

    for section_key in ("highlights", "summary"):
        section = data.get(section_key, {})
        if not isinstance(section, dict):
            continue
        for list_key in ("top_trending", "closest_races", "leading_by_position"):
            for item in section.get(list_key, []):
                for role_key in ("leader", "runner_up", "winner"):
                    role = item.get(role_key)
                    if role and role.get("candidate_uuid"):
                        candidate_uuids.add(role["candidate_uuid"])
        for role_key in ("closest_race", "biggest_win_margin", "most_competitive_position"):
            item = section.get(role_key)
            if isinstance(item, dict):
                for nested_key in ("leader", "runner_up", "winner"):
                    role = item.get(nested_key)
                    if role and role.get("candidate_uuid"):
                        candidate_uuids.add(role["candidate_uuid"])

    if not candidate_uuids:
        return data

    image_urls = {
        str(candidate.uuid): request.build_absolute_uri(candidate.image.url)
        for candidate in Candidate.objects.filter(uuid__in=candidate_uuids).exclude(image="")
        if candidate.image
    }

    def enrich(candidate: dict | None) -> dict | None:
        if not candidate:
            return candidate
        image_url = image_urls.get(candidate.get("candidate_uuid"))
        if image_url:
            candidate["image_url"] = image_url
        return candidate

    for position in data.get("positions", []):
        for candidate in position.get("candidates", []):
            enrich(candidate)
        position["leader"] = enrich(position.get("leader"))
        position["runner_up"] = enrich(position.get("runner_up"))
        position["winner"] = enrich(position.get("winner"))

    for candidate in data.get("candidates", []):
        enrich(candidate)
        enrich(candidate.get("top_competitor"))

    highlights = data.get("highlights", {})
    if isinstance(highlights, dict):
        for item in highlights.get("top_trending", []):
            enrich(item)
        for item in highlights.get("closest_races", []):
            enrich(item.get("leader"))
            enrich(item.get("runner_up"))

    summary = data.get("summary", {})
    if isinstance(summary, dict):
        for role_key in ("closest_race", "biggest_win_margin", "most_competitive_position"):
            item = summary.get(role_key)
            if isinstance(item, dict):
                enrich(item.get("leader"))
                enrich(item.get("runner_up"))
                enrich(item.get("winner"))

    standings = data.get("standings")
    if standings:
        for position in standings.get("positions", []):
            for candidate in position.get("candidates", []):
                enrich(candidate)

    return data
