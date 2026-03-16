"""Start all servers — carrier simulators + candidate server."""

import asyncio
import importlib

import uvicorn


def _simulator_package():
    """Use installed wheel (delivery) or source package (development)."""
    try:
        importlib.import_module("sayata_simulators")
        return "sayata_simulators"
    except ImportError:
        return "sayata.simulators"


async def main():
    sim = _simulator_package()
    configs = [
        uvicorn.Config(f"{sim}.carrier_a_sim:app", host="0.0.0.0", port=8001, log_level="warning"),
        uvicorn.Config(f"{sim}.carrier_b_sim:app", host="0.0.0.0", port=8002, log_level="warning"),
        uvicorn.Config(f"{sim}.carrier_c_sim:app", host="0.0.0.0", port=8003, log_level="warning"),
        uvicorn.Config(f"{sim}.carrier_d_sim:app", host="0.0.0.0", port=8004, log_level="warning"),
        uvicorn.Config("sayata.server:app", host="0.0.0.0", port=8000, log_level="info"),
    ]
    servers = [uvicorn.Server(config) for config in configs]

    print("Starting Sayata Quoting Platform...")
    print()
    print("  Candidate server:  http://localhost:8000")
    print("  Carrier A:         http://localhost:8001")
    print("  Carrier B:         http://localhost:8002")
    print("  Carrier C:         http://localhost:8003")
    print("  Carrier D:         http://localhost:8004")
    print()

    await asyncio.gather(*(server.serve() for server in servers))


if __name__ == "__main__":
    asyncio.run(main())
