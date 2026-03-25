import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


def parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_domains(value: str) -> list[str]:
    if not value:
        return [
            "light",
            "switch",
            "sensor",
            "binary_sensor",
            "climate",
            "fan",
            "cover",
            "media_player",
            "lock",
            "vacuum",
            "camera",
        ]
    return [item.strip().lower() for item in value.split(",") if item.strip()]


@dataclass
class Config:
    ha_url: str = os.getenv("HA_URL", "").strip()
    ha_token: str = os.getenv("HA_TOKEN", "").strip()
    debug: bool = parse_bool(os.getenv("DEBUG", "false"))
    host: str = os.getenv("HOST", "127.0.0.1").strip()
    port: int = int(os.getenv("PORT", "5000"))
    demo_mode: bool = parse_bool(os.getenv("DEMO_MODE", "true"))
    demo_data_file: str = os.getenv("DEMO_DATA_FILE", "demo_data.json").strip()
    show_unavailable: bool = parse_bool(os.getenv("SHOW_UNAVAILABLE", "false"))
    default_domains: list[str] = None

    def __post_init__(self):
        self.default_domains = parse_domains(os.getenv("DEFAULT_DOMAINS", ""))

    def validate(self) -> None:
        if self.demo_mode:
            return

        if not self.ha_url:
            raise ValueError("HA_URL is missing. Add it to your .env file.")

        if not self.ha_token:
            raise ValueError("HA_TOKEN is missing. Add it to your .env file.")

        if not (
            self.ha_url.startswith("http://")
            or self.ha_url.startswith("https://")
        ):
            raise ValueError("HA_URL must start with http:// or https://")
