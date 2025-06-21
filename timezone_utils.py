"""
Timezone utilities for ensuring IST (Indian Standard Time) across the application
"""

from datetime import datetime, date
import pytz

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current datetime in IST"""
    return datetime.now(IST)

def get_ist_date():
    """Get current date in IST"""
    return get_ist_now().date()

def get_ist_time_string():
    """Get current time as formatted string in IST"""
    return get_ist_now().strftime("%Y-%m-%d %H:%M:%S")

def convert_to_ist(dt):
    """Convert any datetime to IST"""
    if dt.tzinfo is None:
        # If naive datetime, assume UTC
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(IST)

def format_ist_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """Format datetime in IST"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime(format_str)

def get_market_date():
    """Get current market date in IST (useful for market hours logic)"""
    ist_now = get_ist_now()
    # If before 9:15 AM IST, consider it previous trading day
    if ist_now.time() < datetime.strptime('09:15', '%H:%M').time():
        return (ist_now - pytz.timedelta(days=1)).date()
    return ist_now.date()

def is_market_hours():
    """Check if current IST time is within market hours"""
    ist_now = get_ist_now()
    current_time = ist_now.time()
    market_start = datetime.strptime('09:15', '%H:%M').time()
    market_end = datetime.strptime('15:30', '%H:%M').time()
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    is_weekday = ist_now.weekday() < 5
    
    return is_weekday and market_start <= current_time <= market_end