# RTOS-HIL-Telemetry-Framework

**Author:** Devesh Harish Pande  
**Domain:** Embedded Systems, HIL Simulation, RTOS, Predictive Maintenance (Data Generation)

---

## Overview

This project provides a **dual-mode data generation pipeline** for aerospace thermal control validation:

- **SIL (Software-in-Loop)** – Pure MATLAB/Simulink simulation. No hardware required. Generates 16-channel thermal data (battery + inverter) with exponential warmup, noise, and autopilot fault injection (runaway, ripple, transients).

- **HIL (Hardware-in-Loop)** – Simulink streams sensor values to an RP2040 microcontroller running a **dual-task RTOS scheduler** (1ms RX / 10ms processing). The RP2040 computes battery & inverter means on‑silicon, adds IST timestamps, and returns processed data to MATLAB workspace. This adds real‑world timing and hardware‑induced latencies.

**Note:** This project does **not** train any machine learning models. It generates clean, labeled datasets (Excel/CSV files) ready for you to train your own PHM (Predictive Health Monitoring) models.

---

## Repository Structure
RTOS-HIL-Telemetry-Framework/
├── simulink_models/
│ ├── data_generator_SIL.slx
│ ├── data_generator_HIL.slx
│ └── Hil.m
├── RP2040_Firmware/
│ ├── boot.py
│ └── code.py
├── docs/
│ ├── HOW_TO_RUN.md
│ └── PROJECT_OVERVIEW.md
├── media/
│ └── demo_video.mp4
├── README.md
├── LICENSE
└── .gitignore

text

---

## Hardware Required (HIL mode only)

- Any RP2040 board (Raspberry Pi Pico, Vichrak Shrike Lite, etc.)
- USB cable (connects to PC – no external sensors)

---

## Quick Start

1. **Clone or download** this repository.
2. **For SIL mode:** Open `data_generator_SIL.slx` in MATLAB/Simulink and run. Data is saved as Excel/CSV.
3. **For HIL mode:**  
   - Copy `boot.py` and `code.py` to the `CIRCUITPY` drive of your RP2040.  
   - Run `Hil.m` in MATLAB.  
   - Open `data_generator_HIL.slx` and run.  
   - Data is saved as Excel/CSV.
4. Use the Excel/CSV file for ML training.

📹 See `media/demo_video.mp4` for a live walkthrough.

---

## License

MIT – see [LICENSE](LICENSE) file.

---

## Author

Devesh Harish Pande 
