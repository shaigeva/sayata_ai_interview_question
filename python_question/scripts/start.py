"""Start all servers — carrier simulators + candidate server.

Set BASE_PORT to change the port range (default 8000).
The candidate server runs on BASE_PORT, carriers on BASE_PORT+1 through +4.
"""

import asyncio
import importlib
import os

import uvicorn


def _simulator_package():
    """Use installed wheel (delivery) or source package (development)."""
    try:
        importlib.import_module("sayata_simulators")
        return "sayata_simulators"
    except ImportError:
        return "sayata.simulators"


async def main():
    base = int(os.environ.get("BASE_PORT", "8000"))
    sim = _simulator_package()
    configs = [
        uvicorn.Config(f"{sim}.carrier_a_sim:app", host="0.0.0.0", port=base + 1, log_level="warning"),
        uvicorn.Config(f"{sim}.carrier_b_sim:app", host="0.0.0.0", port=base + 2, log_level="warning"),
        uvicorn.Config(f"{sim}.carrier_c_sim:app", host="0.0.0.0", port=base + 3, log_level="warning"),
        uvicorn.Config(f"{sim}.carrier_d_sim:app", host="0.0.0.0", port=base + 4, log_level="warning"),
        uvicorn.Config("sayata.server:app", host="0.0.0.0", port=base, log_level="info"),
    ]
    servers = [uvicorn.Server(config) for config in configs]

    print("Starting Sayata Quoting Platform...")
    print()
    print(f"  Candidate server:  http://localhost:{base}")
    print(f"  Carrier A:         http://localhost:{base + 1}")
    print(f"  Carrier B:         http://localhost:{base + 2}")
    print(f"  Carrier C:         http://localhost:{base + 3}")
    print(f"  Carrier D:         http://localhost:{base + 4}")
    print()

    await asyncio.gather(*(server.serve() for server in servers))


if __name__ == "__main__":
    asyncio.run(main())
