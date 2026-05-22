% =========================================================================
% HIGH-SPEED REAL-TIME HIL STREAMER & RAM-BUFFERED LOGGER
% =========================================================================
clear dev; 
clc;

consolePort = "COM3"; 
baudRate = 115200;
output_filename = 'HIL_RealWorld_Nominal_Data.xlsx';

% 1. Check for file access locks before starting the run
if exist(output_filename, 'file') == 2
    try
        delete(output_filename);
        fprintf('🧹 Fresh canvas initialized. Old sheet cleared.\n');
    catch
        error('❌ Error: The file "%s" is open in Excel! Close it before running.', output_filename);
    end
end

% 2. Initialize Virtual Port Connection
fprintf('Opening Virtual Serial Interface on %s...\n', consolePort);
try
    dev = serialport(consolePort, baudRate, "Timeout", 5); 
    configureTerminator(dev, "CR/LF");
    flush(dev); % Clear out any residual boot bytes instantly
    pause(0.5);
    fprintf('🚀 MASTER LOG ENGINE ARMED: Awaiting continuous stream...\n\n');
catch ME
    error('❌ Cannot open port! Run "instrreset" or cycle the USB cable.');
end

% 3. Standard Wide ML Table Definition
varNames = {'Timestamp_IST', 'Subsystem_Location', ...
            'S101', 'S102', 'S103', 'S104', 'S105', 'S106', 'S107', 'S108', ...
            'S201', 'S202', 'S203', 'S204', 'S205', 'S206', 'S207', 'S208', ...
            'Subsystem_Mean'};

current_timestamp = char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss.SSSSSS'));
active_battery_cells = NaN(1, 8);
active_controller_layers = NaN(1, 8);

% Pre-allocate high-speed RAM Master Table
MasterDataStorage = cell(50000, 19); 
total_rows_logged = 0;

% 4. Real-Time Processing Loop (No slow disk writes allowed inside)
try
    while true
        if dev.NumBytesAvailable > 0
            raw_line = char(readline(dev));
            fprintf('%s\n', raw_line); % Monitor data stream on screen
            
            % Parse Header Line
            if contains(raw_line, "REAL-TIME HIL MONITORING DESK")
                tokens = split(raw_line, "| Local Time: ");
                if length(tokens) > 1
                    current_timestamp = strtrim(tokens{end});
                end
                active_battery_cells = NaN(1, 8);
                active_controller_layers = NaN(1, 8);
            end
            
            % Parse Individual Sensors
            if contains(raw_line, "Sensor ID:")
                clean_line = strtrim(raw_line);
                id_tokens = regexp(clean_line, 'Sensor ID:\s*(\d+)', 'tokens');
                temp_tokens = regexp(clean_line, '->\s*([\d\.]+)', 'tokens');
                
                if ~isempty(id_tokens) && ~isempty(temp_tokens)
                    s_id = str2double(id_tokens{1}{1});
                    s_temp = str2double(temp_tokens{1}{1});
                    if s_id >= 101 && s_id <= 108
                        active_battery_cells(s_id - 100) = s_temp;
                    elseif s_id >= 201 && s_id <= 208
                        active_controller_layers(s_id - 200) = s_temp;
                    end
                end
            end
            
            % Cache Battery Row to RAM
            if contains(raw_line, "BATTERY MEAN:")
                extracted_nums = regexp(raw_line, '[\d\.]+', 'match');
                if ~isempty(extracted_nums)
                    mean_val = str2double(extracted_nums{end});
                    total_rows_logged = total_rows_logged + 1;
                    
                    MasterDataStorage{total_rows_logged, 1} = current_timestamp;
                    MasterDataStorage{total_rows_logged, 2} = 'Battery_Pack';
                    MasterDataStorage{total_rows_logged, 19} = mean_val;
                    for i = 1:8
                        MasterDataStorage{total_rows_logged, 2 + i} = active_battery_cells(i);
                        MasterDataStorage{total_rows_logged, 10 + i} = NaN;
                    end
                end
            end
            
            % Cache Controller Row to RAM
            if contains(raw_line, "CONTROLLER MEAN:")
                extracted_nums = regexp(raw_line, '[\d\.]+', 'match');
                if ~isempty(extracted_nums)
                    mean_val = str2double(extracted_nums{end});
                    total_rows_logged = total_rows_logged + 1;
                    
                    MasterDataStorage{total_rows_logged, 1} = current_timestamp;
                    MasterDataStorage{total_rows_logged, 2} = 'Controller';
                    MasterDataStorage{total_rows_logged, 19} = mean_val;
                    for i = 1:8
                        MasterDataStorage{total_rows_logged, 2 + i} = NaN;
                        MasterDataStorage{total_rows_logged, 10 + i} = active_controller_layers(i);
                    end
                end
            end
        end
        % Microsecond yield delay to maximize CPU throughput
        pause(0.0001); 
    end
    
catch ME
    % 5. SAFE COMMIT PHASE: Executes when you stop the script or when it finishes
    fprintf('\n💾 Real-Time Loop closed. Committing RAM data storage to Excel layout...\n');
    clear dev; % Instantly free COM port so Simulink can relax
    
    if total_rows_logged > 0
        % Strip away any unused rows from our pre-allocated cache
        CleanOutputCells = MasterDataStorage(1:total_rows_logged, :);
        
        % Convert our structured RAM array into a finished Table
        FinalDatasetTable = cell2table(CleanOutputCells, 'VariableNames', varNames);
        
        % Single-shot fast export to disk
        writetable(FinalDatasetTable, output_filename, 'Sheet', 'Nominal_HIL_Data');
        fprintf('✅ SUCCESS: Saved %d master rows cleanly to "%s"!\n', total_rows_logged, output_filename);
    else
        fprintf('⚠️ No full data frames were captured. Excel sheet creation bypassed.\n');
    end
end