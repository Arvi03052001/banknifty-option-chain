# Option Chain Snapshot Module

## Overview
The option chain snapshot functionality has been extracted from `web_app.py` into separate modules for better organization and maintainability.

## Files Structure

### New Files Created:
1. **`option_chain_snapshot.py`** - Main snapshot functionality
2. **`option_chain_utils.py`** - Shared utility functions
3. **`run_app.py`** - Application runner script
4. **`test_snapshot.py`** - Test script for snapshot functionality

### Modified Files:
1. **`web_app.py`** - Cleaned up, imports snapshot functionality

## Key Features

### 1. Separated Concerns
- **Web App**: Handles HTTP requests and UI rendering
- **Snapshot Module**: Handles periodic data saving to CSV
- **Utils Module**: Shared functions for data processing

### 2. Fixed Duplicate Snapshot Issue
- **Problem**: Scheduler was running multiple times causing duplicate snapshots
- **Solution**: 
  - Implemented singleton pattern for scheduler to prevent multiple instances
  - Added thread-safe locks to prevent race conditions
  - Added time-based duplicate prevention (prevents multiple snapshots in same minute)
  - Added scheduler job configuration with `max_instances=1` and `coalesce=True`

### 3. Improved Data Integrity
- **Raw Data**: CSV files now store raw numeric values instead of formatted strings
- **Display Data**: Web interface still shows formatted values (K, M notation)

### 4. Robust Duplicate Prevention
- **Multiple Layers**: 
  - Scheduler-level: Prevents multiple scheduler instances
  - Job-level: Prevents multiple job executions
  - Time-based: Prevents snapshots within the same minute
  - Thread-safe: Uses locks to prevent race conditions

## How to Run

### Option 1: Start All Services (Recommended)
```bash
python start_all.py
```
This will start both the web application and snapshot service automatically.

### Option 2: Manual Startup
Start the snapshot service first:
```bash
python snapshot_service.py
```

Then in a separate terminal, start the web application:
```bash
python web_app.py
```

### Option 3: Web App Only (No Snapshots)
```bash
python web_app.py
```

## Services

### Web Application
- **Port**: 5000
- **URL**: http://localhost:5000
- **Purpose**: Serves the web interface for viewing option chain data

### Snapshot Service
- **Purpose**: Takes periodic snapshots of option chain data
- **Frequency**: Every minute
- **Output**: CSV files in `option_chain_snapshots/` directory
- **Independence**: Runs separately from web app to avoid conflicts

## Snapshot Configuration

### Directory
- Snapshots are saved in `option_chain_snapshots/` directory
- Files are named by date: `YYYY-MM-DD.csv`

### Frequency
- Default: Every minute (configurable in `option_chain_snapshot.py`)
- Market hours check is available but currently commented out

### Data Saved
Each snapshot includes:
- Timestamp
- Spot price and futures price
- Strike prices with call/put OI data
- Color intensity classes for visualization
- Highlighted strikes and 500-point markers

## Testing

### Test Single Snapshot
```bash
python test_snapshot.py
```

### Verify No Duplicates
1. Run the application
2. Check console output - should see only one "Taking snapshot" message per minute
3. Check CSV files - timestamps should not duplicate

## Benefits

1. **Better Organization**: Code is now modular and easier to maintain
2. **No Duplicates**: Fixed the duplicate snapshot issue
3. **Data Integrity**: Raw numeric data preserved in CSV files
4. **Concurrent Execution**: Web app and snapshot scheduler run simultaneously
5. **Easy Testing**: Separate test scripts for validation
6. **Graceful Shutdown**: Proper cleanup when application stops

## Configuration Options

### Market Hours (in option_chain_snapshot.py)
```python
# Uncomment to enable market hours check
# if now.weekday() >= 5:  # Weekend check
#     return
# if not (time(9, 15) <= now.time() <= time(15, 30)):  # Trading hours
#     return
```

### Snapshot Frequency
```python
# In start_snapshot_scheduler() function
scheduler.add_job(save_option_chain_snapshot, 'cron', minute='*/1', second=0)
# Change minute='*/1' to desired interval (e.g., minute='*/5' for every 5 minutes)
```

## Troubleshooting

### If snapshots are still duplicating:
1. Check if multiple instances of the application are running
2. Verify only one scheduler is started
3. Check console output for "Scheduler already running" message

### If CSV data looks wrong:
1. Verify raw numeric values are being saved (not formatted strings)
2. Check the `raw_option_chain` processing in `save_option_chain_snapshot()`

### If scheduler doesn't start:
1. Check for import errors in console
2. Verify all required modules are available
3. Check file permissions for snapshot directory