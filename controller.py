#!/usr/bin/env python3
"""Controller process for managing ArduCopter SITL instances over TCP."""

import argparse
import os
import shlex
import signal
import socket
import subprocess
from dataclasses import dataclass


@dataclass
class ManagedProcess:
    instance_id: str
    process: subprocess.Popen
    out_port: int


class SitlController:
    def __init__(self, ardupilot_path: str, out_host: str) -> None:
        self.ardupilot_path = ardupilot_path
        self.arducopter_path = os.path.join(ardupilot_path, "ArduCopter")
        self.sim_vehicle_script = os.path.join(ardupilot_path, "Tools/autotest/sim_vehicle.py")
        self.out_host = out_host
        self.processes: dict[str, ManagedProcess] = {}

    def start_instance(self, instance_id: str, out_port: int) -> str:
        if instance_id in self.processes:
            return f"ERR instance {instance_id} already running"

        cmd = [
            "python3",
            self.sim_vehicle_script,
            "-v",
            "ArduCopter",
            "--instance",
            str(instance_id),
            "--out",
            f"{self.out_host}:{out_port}",
        ]

        process = subprocess.Popen(
            cmd,
            cwd=self.arducopter_path,
            preexec_fn=os.setsid,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.processes[instance_id] = ManagedProcess(instance_id, process, out_port)
        return f"OK started {instance_id} pid={process.pid} out={self.out_host}:{out_port} cmd={shlex.join(cmd)}"

    def stop_instance(self, instance_id: str) -> str:
        managed = self.processes.get(instance_id)
        if not managed:
            return f"ERR instance {instance_id} not running"

        os.killpg(os.getpgid(managed.process.pid), signal.SIGTERM)
        self.processes.pop(instance_id, None)
        return f"OK stopped {instance_id}"

    def list_instances(self) -> str:
        if not self.processes:
            return "OK no instances running"
        summary = ", ".join(
            f"{instance_id}:pid={managed.process.pid},out={self.out_host}:{managed.out_port}"
            for instance_id, managed in sorted(self.processes.items())
        )
        return f"OK {summary}"

    def stop_all(self) -> str:
        ids = list(self.processes.keys())
        for instance_id in ids:
            self.stop_instance(instance_id)
        return f"OK stopped_all count={len(ids)}"

    def handle_command(self, command: str) -> str:
        parts = command.split()
        if not parts:
            return "ERR empty command"

        action = parts[0].lower()
        try:
            if action == "start":
                return self.start_instance(parts[1], int(parts[2]))
            if action == "stop":
                return self.stop_instance(parts[1])
            if action == "list":
                return self.list_instances()
            if action in {"stop-all", "stop_all"}:
                return self.stop_all()
            return f"ERR unknown command: {action}"
        except (IndexError, ValueError):
            return "ERR invalid command format"



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SITL instance controller server")
    parser.add_argument("--host", default="0.0.0.0", help="TCP host for controller listener")
    parser.add_argument("--port", type=int, default=14500, help="TCP port for controller listener")
    parser.add_argument(
        "--ardupilot-path",
        default="/home/robotics/ardupilot",
        help="Path to local ArduPilot checkout",
    )
    parser.add_argument(
        "--out-host",
        default="127.0.0.1",
        help="Destination host used in --out for each SITL instance",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    controller = SitlController(args.ardupilot_path, args.out_host)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.host, args.port))
        server.listen()
        print(f"Listening on {args.host}:{args.port}")

        try:
            while True:
                conn, addr = server.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue
                    command = data.decode("utf-8").strip()
                    response = controller.handle_command(command)
                    conn.sendall((response + "\n").encode("utf-8"))
                    print(f"{addr[0]}:{addr[1]} -> {command} -> {response}")
        except KeyboardInterrupt:
            print("Shutting down. Stopping all instances.")
            controller.stop_all()


if __name__ == "__main__":
    main()
