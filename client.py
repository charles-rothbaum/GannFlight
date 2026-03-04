#!/usr/bin/env python3
"""TCP client for sending commands to controller.py."""

import argparse
import socket


def send_command(host: str, port: int, command: str, timeout: float = 10.0) -> str:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(command.encode("utf-8"))
        return sock.recv(4096).decode("utf-8").strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Client for SITL controller")
    parser.add_argument("--host", default="127.0.0.1", help="Controller host/IP")
    parser.add_argument("--port", type=int, default=14500, help="Controller TCP port")

    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start a SITL instance")
    start.add_argument("instance_id", help="Instance identifier")
    start.add_argument("out_port", type=int, help="UDP output port for MAVLink stream")

    stop = sub.add_parser("stop", help="Stop one SITL instance")
    stop.add_argument("instance_id", help="Instance identifier")

    sub.add_parser("list", help="List running instances")
    sub.add_parser("stop-all", help="Stop all running instances")

    raw = sub.add_parser("raw", help="Send a raw command string")
    raw.add_argument("payload", help='Raw payload, example: "start 0 14550"')

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "start":
        payload = f"start {args.instance_id} {args.out_port}"
    elif args.command == "stop":
        payload = f"stop {args.instance_id}"
    elif args.command == "list":
        payload = "list"
    elif args.command == "stop-all":
        payload = "stop-all"
    else:
        payload = args.payload

    print(send_command(args.host, args.port, payload))


if __name__ == "__main__":
    main()
