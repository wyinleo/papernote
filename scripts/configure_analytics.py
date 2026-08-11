#!/usr/bin/env python3
"""Generate the deployment-only GoatCounter endpoint configuration."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SITE_CODE_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-code", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("site/analytics-config.js"),
    )
    args = parser.parse_args()

    site_code = args.site_code.strip().lower()
    if not SITE_CODE_RE.fullmatch(site_code):
        raise SystemExit("GOATCOUNTER_CODE must contain only lowercase letters, digits, and hyphens")

    config = {
        "goatcounterEndpoint": f"https://{site_code}.goatcounter.com/count",
        "allowedHosts": ["wyinleo.github.io"],
    }
    payload = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "/* Generated during deployment; do not commit credentials here. */\n"
        f"window.PAPERNOTE_ANALYTICS = Object.freeze({payload});\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
