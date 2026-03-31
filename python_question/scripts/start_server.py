"""Start the candidate server.

Usage:
    uv run python scripts/start_server.py              # port 8000
    uv run python scripts/start_server.py --port 9000  # custom port
"""

import argparse

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Start the Sayata candidate server")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    args = parser.parse_args()

    print(f"Starting candidate server on http://localhost:{args.port}")
    uvicorn.run("sayata.server:app", host="0.0.0.0", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
