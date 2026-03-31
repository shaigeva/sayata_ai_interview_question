"""Start a carrier simulator.

Usage:
    uv run python scripts/start_carrier.py carrier_a              # default port 8001
    uv run python scripts/start_carrier.py carrier_b --port 9002  # custom port

Available carriers: carrier_a, carrier_b, carrier_c, carrier_d
Default ports: carrier_a=8001, carrier_b=8002, carrier_c=8003, carrier_d=8004
"""

import argparse
import importlib

import uvicorn

CARRIER_DEFAULTS = {
    "carrier_a": 8001,
    "carrier_b": 8002,
    "carrier_c": 8003,
    "carrier_d": 8004,
}


def _simulator_package():
    """Use installed wheel (delivery) or source package (development)."""
    try:
        importlib.import_module("sayata_simulators")
        return "sayata_simulators"
    except ImportError:
        return "sayata.simulators"


def main():
    parser = argparse.ArgumentParser(description="Start a carrier simulator")
    parser.add_argument("carrier", choices=list(CARRIER_DEFAULTS.keys()),
                        help="Which carrier to start")
    parser.add_argument("--port", type=int, default=None,
                        help="Port to listen on (default depends on carrier)")
    args = parser.parse_args()

    port = args.port if args.port is not None else CARRIER_DEFAULTS[args.carrier]
    sim = _simulator_package()
    module = f"{sim}.{args.carrier}_sim:app"

    print(f"Starting {args.carrier} on http://localhost:{port}")
    uvicorn.run(module, host="0.0.0.0", port=port, log_level="warning")


if __name__ == "__main__":
    main()
