import socket
import subprocess
import os
import signal
import time

host = '0.0.0.0'
port = 14500

# A dictionary to keep track of processes
processes = {}

def start_instance_sitl(instance_id, out_port):
    # Define the base path to the ArduPilot's directory
    ardupilot_base_path = "/home/robotics/ardupilot"
    arducopter_path = os.path.join(ardupilot_base_path, "ArduCopter")  # Adjusted to point to the ArduCopter directory
    
    # Define the full path to the ArduPilot's sim_vehicle.py script
    # No need to append "sim_vehicle.py" to cmd as we're specifying it directly in the command
    sim_vehicle_script = os.path.join(ardupilot_base_path, "Tools/autotest/sim_vehicle.py")
    
    # Define the command to run sim_vehicle.py with appropriate flags
    cmd = f"python3 {sim_vehicle_script} -v ArduCopter --instance {instance_id} --out 192.168.1.40:{out_port}"
    
    # Start the process in the ArduCopter directory
    process = subprocess.Popen(cmd, shell=True, cwd=arducopter_path, preexec_fn=os.setsid)
    processes[instance_id] = process
    print(f"Started instance {instance_id} with PID {process.pid}")

def stop_instance_sitl(instance_id):
    print(f"Stopping process {instance_id}")
    if instance_id in processes:
        # Send SIGTERM to all processes in the group
        os.killpg(os.getpgid(processes[instance_id].pid), signal.SIGTERM)
        processes.pop(instance_id)  # Remove the process from the dictionary
        print(f"Instance {instance_id} stopped.")

def handle_command(command):
    parts = command.split()
    try:
        if parts[0] == 'start':
            start_instance_sitl(parts[1], int(parts[2]))
        elif parts[0] == 'stop':
            stop_instance_sitl(parts[1])
        else:
            print("Unknown command")
    except IndexError:
        print("Invalid command format")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    command = data.decode('utf-8').strip()
                    handle_command(command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down. Stopping all instances.")
        for instance_id in list(processes.keys()):
            stop_instance_sitl(instance_id)
