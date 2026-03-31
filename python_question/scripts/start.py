"""Start servers — carrier simulators and/or candidate server.

Usage:
    uv run python scripts/start.py                  # start everything
    uv run python scripts/start.py server            # just the candidate server
    uv run python scripts/start.py carrier_a         # just Carrier A
    uv run python scripts/start.py carrier_a carrier_b server  # specific combination
    uv run python scripts/start.py --port 9000 server          # custom port

Each carrier gets a fixed offset from the base port:
    server    = BASE_PORT     (default 8000)
    carrier_a = BASE_PORT + 1
    carrier_b = BASE_PORT + 2
    carrier_c = BASE_PORT + 3
    carrier_d = BASE_PORT + 4

Set BASE_PORT env var to change the range (default 8000).
"""

import asyncio
import importlib
import os
import sys

import uvicorn


def _simulator_package():
    """Use installed wheel (delivery) or source package (development)."""
    try:
        importlib.import_module("sayata_simulators")
        return "sayata_simulators"
    except ImportError:
        return "sayata.simulators"


SERVICES = {
    "server": {"module": "sayata.server:app", "offset": 0, "label": "Candidate server"},
    "carrier_a": {"offset": 1, "label": "Carrier A"},
    "carrier_b": {"offset": 2, "label": "Carrier B"},
    "carrier_c": {"offset": 3, "label": "Carrier C"},
    "carrier_d": {"offset": 4, "label": "Carrier D"},
}


async def main():
    base = int(os.environ.get("BASE_PORT", "8000"))
    sim = _simulator_package()

    # Fill in simulator module paths
    for name in ["carrier_a", "carrier_b", "carrier_c", "carrier_d"]:
        SERVICES[name]["module"] = f"{sim}.{name}_sim:app"

    # Parse arguments: filter to requested services
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    requested = args if args else list(SERVICES.keys())

    unknown = [r for r in requested if r not in SERVICES]
    if unknown:
        print(f"Unknown services: {', '.join(unknown)}")
        print(f"Available: {', '.join(SERVICES.keys())}")
        sys.exit(1)

    configs = []
    for name in requested:
        svc = SERVICES[name]
        port = base + svc["offset"]
        log_level = "info" if name == "server" else "warning"
        configs.append((name, uvicorn.Config(svc["module"], host="0.0.0.0", port=port, log_level=log_level)))

    servers = [(name, uvicorn.Server(config)) for name, config in configs]

    print("Starting Sayata Quoting Platform...")
    print()
    for name, _ in configs:
        svc = SERVICES[name]
        port = base + svc["offset"]
        print(f"  {svc['label']:20s} http://localhost:{port}")
    print()

    await asyncio.gather(*(server.serve() for _, server in servers))


if __name__ == "__main__":
    asyncio.run(main())
