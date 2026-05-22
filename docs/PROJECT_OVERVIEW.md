# Project Overview: Why This Framework Matters

## What This Project Is

A **dual-mode data generation pipeline** for thermal control systems:

- **Software-in-Loop (SIL)** – Pure MATLAB/Simulink simulation. Fast, repeatable, no hardware required. Ideal for initial ML model training.

- **Hardware-in-Loop (HIL)** – Real sensor data is generated in Simulink, streamed to an RP2040 microcontroller, processed with a deterministic RTOS scheduler (1ms/10ms tasks), and returned to MATLAB. The hardware adds realistic timing jitter, USB latency, and on-chip mean calculation – exactly what a flight computer would experience.

## Why Two Modes?

| Aspect | SIL | HIL |
|--------|-----|-----|
| Speed | Very fast (software only) | Slower (real-time USB + MCU) |
| Realism | Idealised timing | Includes hardware latencies |
| Mean calculation | Done in Simulink | Done on RP2040 (offloads host) |
| Use case | Early ML prototyping | Final validation before deployment |

## Aerospace Relevance

- **DO-254 / ECSS-E-ST-40C** mandates HIL testing for certifiable avionics.
- Predictive health monitoring (PHM) for batteries & power inverters requires realistic failure data – our autopilot injects exponential runaway, cyclic transients, and ripple.
- On-silicon preprocessing (means, timestamps) mimics how flight computers reduce telemetry bandwidth.

## What This Project Does NOT Do

- ❌ Train any machine learning models
- ❌ Include real physical sensors (all data is simulated in Simulink)
- ❌ Provide a complete PHM system

## What It DOES Do

- ✅ Generate labeled thermal datasets (16 channels, with and without hardware timing) and save as Excel/CSV
- ✅ Demonstrate a working RTOS scheduler on an RP2040 (1ms/10ms tasks)
- ✅ Show how to bridge Simulink ↔ microcontroller ↔ MATLAB workspace
- ✅ Provide a foundation for someone else to train ML models for failure prediction

## Who Should Use This

- Students learning HIL and RTOS concepts
- Researchers needing realistic thermal telemetry for ML experiments
- Engineers prototyping avionics thermal control validation

## Next Steps (For You, The User)

1. Run the SIL model to generate a pure‑software dataset (Excel/CSV).
2. Run the HIL model (with RP2040) to generate a hardware‑in‑the‑loop dataset (Excel/CSV).
3. Compare both datasets – notice the timing differences.
4. Train your own ML model (Random Forest, CNN, GPR) on either dataset to predict thermal runaway.

## License

MIT – free for academic and commercial use with attribution.
