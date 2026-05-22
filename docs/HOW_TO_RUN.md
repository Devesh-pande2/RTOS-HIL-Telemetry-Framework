# How to Run the MIL/HIL Telemetry Pipeline

## Prerequisites

- MATLAB R2020a or later with Simulink
- CircuitPython installed on RP2040 (download from circuitpython.org)
- USB cable

---

## Option A: Software-in-Loop (SIL) – Pure Simulation, No Hardware

1. Open MATLAB and navigate to the `simulink_models/` folder.
2. Double-click `data_generator_SIL.slx` to open the Simulink model.
3. Set simulation time (e.g., 300 seconds) in the Simulink toolbar.
4. Click **Run**.
5. After simulation completes, data is saved as an **Excel/CSV file** in your MATLAB workspace or specified output folder.

---

## Option B: Hardware-in-Loop (HIL) – Real-Time RP2040 Processing

### Step 1: Prepare RP2040
1. Connect RP2040 to PC via USB.
2. Copy `boot.py` and `code.py` from the `RP2040_Firmware/` folder to the `CIRCUITPY` drive.
3. The RP2040 will reboot. Two virtual COM ports will appear:
   - **COM3** (console) – for telemetry and time sync
   - **COM8** (data) – for high-speed sensor stream

### Step 2: Run MATLAB/Simulink
1. Open MATLAB and navigate to `simulink_models/`.
2. **First, run `Hil.m`** in the MATLAB Command Window. This script:
   - Opens the two COM ports
   - Sends a time sync pulse to RP2040
   - Waits for `SYNC_OK` response
3. Open `data_generator_HIL.slx`.
4. Set simulation time (e.g., 300 seconds).
5. Click **Run**.
6. After simulation completes, data is saved as an **Excel/CSV file**.

---

## Output

The generated Excel/CSV file contains:
- 16 columns (sensor addresses 101-108 for battery, 201-208 for inverter)
- Timestamps
- Mean values computed by RP2040 (for HIL mode)

This file is ready for training machine learning models (Random Forest, CNN, GPR, etc.).

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| COM ports not appearing | Check RP2040 is in CircuitPython mode. Re-copy `boot.py` and reset. |
| No data in workspace/Excel | Ensure `Hil.m` is run **before** starting Simulink. |
| Frame loss errors | Reduce Simulink step size or increase USB buffer. |

---

## Video Demo

See `media/demo_video.mp4` for a live walkthrough.
