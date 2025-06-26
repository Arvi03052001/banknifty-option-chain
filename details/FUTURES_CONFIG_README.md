# BANKNIFTY Futures Configuration System

## Overview

This application now includes an automatic futures symbol management system that eliminates the need to manually update BANKNIFTY futures symbols every month. The system automatically calculates the current and next month futures symbols based on the current date and BANKNIFTY expiry schedule.

## Key Features

### 🔄 Automatic Symbol Generation
- **Current Month**: Automatically detects the active futures contract
- **Next Month**: Calculates the upcoming futures contract
- **Smart Expiry Logic**: Uses last Thursday of each month as expiry date
- **Auto-Update**: Configuration updates automatically when current month expires

### 📊 Application Integration
The futures configuration is integrated throughout the application:

1. **Option Chain Page** (`/`)
   - Uses current month futures for price display
   - Shows both current and next month symbols in header
   - Strike highlighting based on current futures price

2. **Trade Page** (`/trade`)
   - VWAP calculations use current month futures
   - Option symbols automatically use correct expiry

3. **Futures Details** (`/futures-details`)
   - Shows current month futures candle data
   - Automatically updates symbol

4. **Configuration Page** (`/futures-config`)
   - View current configuration status
   - Monitor upcoming expiry dates
   - System status and usage information

## File Structure

```
BankNifty/
├── futures_config.py          # Main configuration module
├── web_app.py                 # Updated to use futures config
├── option_chain_fetcher.py    # Updated to use futures config
└── templates/
    ├── index.html             # Updated with futures info display
    └── futures_config.html    # Configuration management page
```

## Usage

### Viewing Current Configuration

1. **Via Web Interface**: Visit `/futures-config` in your browser
2. **Via Command Line**: Run `python futures_config.py`

### Example Output

```
BANKNIFTY FUTURES CONFIGURATION
Current Month: NSE:BANKNIFTY25JUNFUT (Exp: 2025-06-26)
Next Month: NSE:BANKNIFTY25JULFUT (Exp: 2025-07-31)
```

## Technical Details

### Symbol Format
- **Pattern**: `NSE:BANKNIFTY{YY}{MMM}FUT`
- **Example**: `NSE:BANKNIFTY25JUNFUT`
- **Components**:
  - `NSE:` - Exchange prefix
  - `BANKNIFTY` - Instrument name
  - `25` - Year (last 2 digits)
  - `JUN` - Month abbreviation
  - `FUT` - Futures suffix

### Expiry Logic
- BANKNIFTY futures expire on the **last Thursday** of each month
- If current date is past the current month's expiry, system automatically moves to next month
- Handles year transitions (December → January)

### Month Abbreviations
```
JAN, FEB, MAR, APR, MAY, JUN,
JUL, AUG, SEP, OCT, NOV, DEC
```

## Code Integration

### Using in Python Code

```python
from futures_config import get_current_futures_symbol, get_next_futures_symbol, get_futures_info

# Get current month futures symbol
current_symbol = get_current_futures_symbol()
# Returns: "NSE:BANKNIFTY25JUNFUT"

# Get next month futures symbol
next_symbol = get_next_futures_symbol()
# Returns: "NSE:BANKNIFTY25JULFUT"

# Get comprehensive information
info = get_futures_info()
# Returns detailed dictionary with expiry dates, symbols, etc.
```

### Updated Functions

The following functions have been updated to use the new configuration:

1. `get_futures_price()` in `option_chain_fetcher.py`
2. `get_current_month_futures_symbol()` in `web_app.py`
3. All routes that use futures symbols

## Benefits

### ✅ Before (Manual)
- Had to manually update `NSE:BANKNIFTY25JUNFUT` every month
- Risk of forgetting to update symbols
- Hardcoded values throughout the application
- Manual tracking of expiry dates

### ✅ After (Automatic)
- Symbols update automatically based on current date
- No manual intervention required
- Centralized configuration management
- Built-in expiry date calculation
- Visual configuration management interface

## Monitoring

### Configuration Page Features
- **Current Status**: Shows active futures contract
- **Upcoming Contract**: Displays next month's contract
- **Expiry Dates**: Clear visibility of expiry schedules
- **System Status**: Confirms automatic updates are working
- **Usage Information**: Shows where symbols are used in the application

### Verification
You can verify the configuration is working by:
1. Checking the main option chain page header
2. Visiting the `/futures-config` page
3. Running `python futures_config.py` from command line

## Troubleshooting

### If Symbols Appear Incorrect
1. Check current date and time
2. Verify expiry date calculations
3. Check if it's near month-end transition
4. Visit `/futures-config` page for detailed status

### Manual Override (if needed)
If you need to manually specify a symbol temporarily, you can modify the `futures_config.py` file, but this is not recommended as it defeats the purpose of automatic management.

## Future Enhancements

The system is designed to be extensible for:
- Other instruments (NIFTY, FINNIFTY, etc.)
- Different expiry patterns
- Holiday adjustments
- Multiple contract months
- Historical symbol lookups

---

**Note**: This system assumes standard BANKNIFTY expiry patterns (last Thursday of each month). If NSE changes the expiry pattern, the `get_last_thursday_of_month()` function in `futures_config.py` would need to be updated accordingly.