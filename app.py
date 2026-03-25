from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

from config import Config
from ha_client import (
    HomeAssistantClient,
    HomeAssistantClientError,
    load_demo_states,
    group_entities,
    filter_entities,
    count_entities,
)

app = Flask(__name__)

config = Config()
client = HomeAssistantClient(config)


def utc_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "").strip()
    domain = request.args.get("domain", "all").strip().lower()
    available_only = request.args.get("available_only", "false").lower() == "true"

    try:
        if config.demo_mode:
            states = load_demo_states(config.demo_data_file)
            connection_status = "Demo Mode"
            connection_error = None
        else:
            config.validate()
            states = client.get_all_states()
            connection_status = "Connected"
            connection_error = None

        filtered_states = filter_entities(
            states=states,
            allowed_domains=config.default_domains,
            search=search,
            domain=domain,
            available_only=available_only,
            show_unavailable=config.show_unavailable,
        )

        grouped_entities = group_entities(filtered_states)
        total_entities = count_entities(grouped_entities)
        domains_present = sorted(grouped_entities.keys())

        return render_template(
            "index.html",
            grouped_entities=grouped_entities,
            total_entities=total_entities,
            domains_present=domains_present,
            connection_status=connection_status,
            connection_error=connection_error,
            last_updated=utc_timestamp(),
            search=search,
            selected_domain=domain,
            available_only=available_only,
            demo_mode=config.demo_mode,
        )

    except HomeAssistantClientError as exc:
        return render_template(
            "index.html",
            grouped_entities={},
            total_entities=0,
            domains_present=[],
            connection_status="Error",
            connection_error=str(exc),
            last_updated=utc_timestamp(),
            search=search,
            selected_domain=domain,
            available_only=available_only,
            demo_mode=config.demo_mode,
        )
    except ValueError as exc:
        return render_template(
            "index.html",
            grouped_entities={},
            total_entities=0,
            domains_present=[],
            connection_status="Configuration Error",
            connection_error=str(exc),
            last_updated=utc_timestamp(),
            search=search,
            selected_domain=domain,
            available_only=available_only,
            demo_mode=config.demo_mode,
        )


@app.route("/service", methods=["POST"])
def call_service():
    if config.demo_mode:
        return redirect(
            url_for(
                "index",
                search=request.form.get("search", ""),
                domain=request.form.get("domain", "all"),
                available_only=request.form.get("available_only", "false"),
            )
        )

    entity_id = request.form.get("entity_id", "").strip()
    service = request.form.get("service", "").strip().lower()
    search = request.form.get("search", "").strip()
    domain = request.form.get("domain", "all").strip().lower()
    available_only = request.form.get("available_only", "false").lower()

    if not entity_id or not service:
        return redirect(
            url_for(
                "index",
                search=search,
                domain=domain,
                available_only=available_only,
            )
        )

    try:
        config.validate()
        client.call_service(entity_id=entity_id, service=service)
    except (HomeAssistantClientError, ValueError):
        pass

    return redirect(
        url_for(
            "index",
            search=search,
            domain=domain,
            available_only=available_only,
        )
    )


if __name__ == "__main__":
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug,
    )
