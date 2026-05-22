import time
import usb_cdc
import gc

print("--- Integrated RTOS Telemetry Desk Active ---")

matlab_serial = usb_cdc.console   # For detailed telemetry desk (COM3)
simulink_serial = usb_cdc.data    # For high-speed sensor streams (COM8)

buffer = ""
raw_frame = ""
new_frame_ready = False

# Real-Time Master Epoch Synchronization Anchors
time_synchronized = False
base_seconds = 0
base_nanoseconds = 0
sync_reference_ns = 0

current_time_ns = time.monotonic_ns()
last_rx_tick = current_time_ns
last_processing_tick = current_time_ns

RX_INTERVAL_NS = 1000000          # 1 Millisecond High-Priority Thread
PROCESSING_INTERVAL_NS = 10000000 # 10 Millisecond Processing Thread

def get_real_wall_clock_str():
    if not time_synchronized:
        return "NOT_SYNCED"
    
    # Calculate exactly how many nanoseconds have elapsed since synchronization
    elapsed_ns = time.monotonic_ns() - sync_reference_ns
    total_ns = base_nanoseconds + elapsed_ns
    
    additional_seconds = total_ns // 1000000000
    remaining_ns = total_ns % 1000000000
    microseconds = remaining_ns // 1000
    
    # CRITICAL: Apply +5:30 Indian Standard Time (IST) Offset to the Unix Epoch seconds
    ist_offset_seconds = (5 * 3600) + (30 * 60)
    current_epoch_seconds = base_seconds + additional_seconds + ist_offset_seconds
    
    # Convert adjusted epoch to a local time structure breakdown
    t_struct = time.localtime(current_epoch_seconds)
    
    return f"{t_struct.tm_year:04d}-{t_struct.tm_mon:02d}-{t_struct.tm_mday:02d} {t_struct.tm_hour:02d}:{t_struct.tm_min:02d}:{t_struct.tm_sec:02d}.{microseconds:06d}"

def decode_and_log_hil(frame):
    try:
        tokens = frame.strip().split(',')
        batt_sum, batt_count = 0.0, 0
        ctrl_sum, ctrl_count = 0.0, 0
        
        # Buffers to capture raw lines for individual sensors
        batt_details = ""
        ctrl_details = ""
        
        for token in tokens:
            if not token or ":" not in token:
                continue
            addr_str, val_str = token.split(':')
            address = int(addr_str)
            temperature = float(val_str)
            
            # Subsystem Decoding & Structural Location Mapping
            if 101 <= address <= 108:
                batt_sum += temperature
                batt_count += 1
                cell_idx = address - 100
                batt_details += f"   [Pack Cell {cell_idx:02d} | Sensor ID: {address}] -> {temperature:.2f} C\r\n"
            elif 201 <= address <= 208:
                ctrl_sum += temperature
                ctrl_count += 1
                mosfet_idx = address - 200
                ctrl_details += f"   [MOSFET Layer {mosfet_idx:02d} | Sensor ID: {address}] -> {temperature:.2f} C\r\n"
                
        if batt_count > 0 and ctrl_count > 0:
            b_avg = batt_sum / batt_count
            c_avg = ctrl_sum / ctrl_count
            
            # Pull precise local IST time profile
            wall_time = get_real_wall_clock_str()
            
            # Build unified console presentation report matrix
            report = []
            report.append("\r\n=======================================================================")
            report.append(f"📡 REAL-TIME HIL MONITORING DESK | Local Time: {wall_time}")
            report.append("=======================================================================")
            
            report.append("\r\n🔋 SUBSYSTEM VIRTUAL LOCATION: EV BATTERY PACK CELLS")
            report.append(batt_details.rstrip())
            report.append(f"   >> HARDWARE COMPUTED BATTERY MEAN: {b_avg:.2f} C\r\n")
            
            report.append("⚡ SUBSYSTEM VIRTUAL LOCATION: POWERTRAIN INVERTER CONTROLLER")
            report.append(ctrl_details.rstrip())
            report.append(f"   >> HARDWARE COMPUTED CONTROLLER MEAN: {c_avg:.2f} C")
            report.append("=======================================================================\r\n")
            
            # Send the complete telemetry data package down COM3
            matlab_serial.write("\r\n".join(report).encode())
            
    except Exception:
        pass

# =======================================================================
# CORE SCHEDULER LOOP
# =======================================================================
while True:
    current_time_ns = time.monotonic_ns()
    
    # Listen for MATLAB initial clock synchronization pulse over COM3
    if not time_synchronized:
        if matlab_serial.in_waiting > 0:
            sync_line = matlab_serial.readline().decode().strip()
            if sync_line.startswith("SYNC:"):
                try:
                    _, sec_str, ns_str = sync_line.split(":")
                    base_seconds = int(sec_str)
                    base_nanoseconds = int(ns_str)
                    sync_reference_ns = time.monotonic_ns()
                    time_synchronized = True
                    matlab_serial.write(b"SYNC_OK\r\n")
                except Exception:
                    pass
        continue
    
    # TASK 1: High-Priority Serial Stream Ingestion (Runs every 1ms)
    if (current_time_ns - last_rx_tick) >= RX_INTERVAL_NS:
        last_rx_tick = current_time_ns
        if simulink_serial.in_waiting > 0:
            data = simulink_serial.read(1)
            if data:
                char = data.decode()
                if char == '\n':
                    raw_frame = buffer
                    new_frame_ready = True
                    buffer = ""
                else:
                    buffer += char

    # TASK 2: Medium-Priority Telemetry Compilation (Runs every 10ms)
    if (current_time_ns - last_processing_tick) >= PROCESSING_INTERVAL_NS:
        last_processing_tick = current_time_ns
        if new_frame_ready:
            new_frame_ready = False
            decode_and_log_hil(raw_frame)
        gc.collect()