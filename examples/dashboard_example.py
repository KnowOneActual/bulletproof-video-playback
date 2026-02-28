#!/usr/bin/env python3
"""Example: Run the bvp dashboard with monitor service.

This demonstrates how to start the web dashboard with an active
monitor service.

Usage:
    python examples/dashboard_example.py --config monitor.yaml
"""

import argparse
import logging
from pathlib import Path

import uvicorn

from bulletproof.api.server import create_app, start_service_background
from bulletproof.config.loader import ConfigLoader


def main():
    """Run the dashboard."""
    parser = argparse.ArgumentParser(
        description="Run bvp dashboard",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to monitor configuration file",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        # Load configuration and create monitor service
        logger.info(f"Loading configuration from {args.config}")
        service = ConfigLoader.load_and_create(args.config)

        # Create FastAPI app
        logger.info("Creating dashboard app...")
        app = create_app(monitor_service=service)

        # Start monitor service in background
        logger.info("Starting monitor service...")
        start_service_background(service)

        # Run uvicorn
        logger.info(f"Starting dashboard at http://{args.host}:{args.port}")
        logger.info(f"API documentation: http://{args.host}:{args.port}/docs")
        logger.info(f"WebSocket stream: ws://{args.host}:{args.port}/api/v1/stream")

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower(),
        )

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
