"""Start all carrier simulators programmatically."""

import asyncio

import uvicorn


async def start_simulators():
    configs = [
        uvicorn.Config("sayata.simulators.carrier_a_sim:app", host="0.0.0.0", port=8001, log_level="warning"),
        uvicorn.Config("sayata.simulators.carrier_b_sim:app", host="0.0.0.0", port=8002, log_level="warning"),
        uvicorn.Config("sayata.simulators.carrier_c_sim:app", host="0.0.0.0", port=8003, log_level="warning"),
        uvicorn.Config("sayata.simulators.carrier_d_sim:app", host="0.0.0.0", port=8004, log_level="warning"),
    ]
    servers = [uvicorn.Server(config) for config in configs]
    await asyncio.gather(*(server.serve() for server in servers))


if __name__ == "__main__":
    asyncio.run(start_simulators())
