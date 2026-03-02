# GannFlight  
Genetic Neural Network Control Framework for ArduCopter (Multi-Instance SITL)

## Overview

GannFlight is a research framework for running and coordinating multiple ArduCopter SITL (Software-In-The-Loop) instances to test evolutionary neural network flight controllers.

The system provides:

- Programmatic control of multiple SITL instances
- TCP-based orchestration layer
- Automated instance lifecycle management
- Scalable testing infrastructure for controller evolution

This project was built to experiment with adaptive control strategies in simulated UAV environments.

---

## Architecture


The `simulation_controller.py` script:

- Listens on TCP port 14500
- Starts/stops individual ArduCopter SITL instances
- Manages process groups cleanly
- Supports multi-instance parallel simulation

---

## Features

- Launch multiple ArduCopter instances with isolated instance IDs
- Clean process group termination
- UDP output routing per instance
- Designed for integration with evolutionary training systems

---

## Requirements

- ArduPilot source installed at:
  `/home/robotics/ardupilot`
- Python 3
- Linux (tested on Ubuntu)

---
## Example Output

![image](/images/Figure_3.png)
