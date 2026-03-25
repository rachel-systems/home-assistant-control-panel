import json
from collections import defaultdict
from pathlib import Path

import requests


class HomeAssistantClientError(Exception):
    pass


class HomeAssistantClient:
    def __init__(self, config):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config.ha_token}",
            "Content-Type": "application/json",
        }

    def get_all_states(self) -> list[dict]:
        url = f"{self.config.ha_url}/api/states"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise HomeAssistantClientError(
                    "Unexpected response from Home Assistant."
                )

            return data

        except requests.RequestException as exc:
            raise HomeAssistantClientError(
                f"Could not connect to Home Assistant: {exc}"
            ) from exc
        except ValueError as exc:
            raise HomeAssistantClientError(
                "Home Assistant returned invalid JSON."
            ) from exc

    def call_service(self, entity_id: str, service: str) -> None:
        if "." not in entity_id:
            raise HomeAssistantClientError("Invalid entity_id.")

        domain = entity_id.split(".", 1)[0]
        url = f"{self.config.ha_url}/api/services/{domain}/{service}"
        payload = {"entity_id": entity_id}

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise HomeAssistantClientError(
                f"Failed to call Home Assistant service: {exc}"
            ) from exc


def load_demo_states(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise HomeAssistantClientError(
            f"Demo data file not found: {file_path}"
        )

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise HomeAssistantClientError(
                "Demo data file must contain a JSON list."
            )

        return data

    except json.JSONDecodeError as exc:
        raise HomeAssistantClientError(
            "Demo data file contains invalid JSON."
        ) from exc


def normalize_entity(entity: dict) -> dict:
    entity_id = entity.get("entity_id", "")
    attributes = entity.get("attributes", {}) or {}
    state = entity.get("state", "unknown")

    domain = entity_id.split(".", 1)[0] if "." in entity_id else "unknown"
    friendly_name = attributes.get("friendly_name", entity_id)

    return {
        "entity_id": entity_id,
        "domain": domain,
        "name": friendly_name,
        "state": state,
        "attributes": attributes,
    }


def filter_entities(
    states: list[dict],
    allowed_domains: list[str],
    search: str = "",
    domain: str = "all",
    available_only: bool = False,
    show_unavailable: bool = False,
) -> list[dict]:
    results = []
    search_lower = search.lower().strip()

    for raw_entity in states:
        entity = normalize_entity(raw_entity)

        if entity["domain"] not in allowed_domains:
            continue

        if domain != "all" and entity["domain"] != domain:
            continue

        if not show_unavailable and entity["state"] == "unavailable":
            continue

        if available_only and entity["state"] in {"unavailable", "unknown"}:
            continue

        haystack = f'{entity["name"]} {entity["entity_id"]}'.lower()
        if search_lower and search_lower not in haystack:
            continue

        results.append(entity)

    results.sort(key=lambda item: (item["domain"], item["name"].lower()))
    return results


def group_entities(states: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)

    for entity in states:
        grouped[entity["domain"]].append(entity)

    return dict(grouped)


def count_entities(grouped_entities: dict[str, list[dict]]) -> int:
    return sum(len(items) for items in grouped_entities.values())


def state_badge_class(state: str) -> str:
    state = (state or "").lower()

    if state == "on":
        return "state-on"
    if state == "off":
        return "state-off"
    if state == "unavailable":
        return "state-unavailable"
    if state == "unknown":
        return "state-unknown"

    return "state-neutral"


def supports_toggle(domain: str) -> bool:
    return domain in {"light", "switch", "fan"}
