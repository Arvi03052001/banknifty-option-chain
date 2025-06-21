# futures_config.py
"""
Configuration module for managing BANKNIFTY futures symbols.
This module automatically calculates current and next month futures symbols
based on the current date and expiry schedule.
"""

from datetime import datetime, date
from calendar import monthrange

class FuturesConfig:
    """
    Class to manage BANKNIFTY futures symbols and expiry dates.
    """
    
    # Month abbreviations for futures symbols
    MONTH_ABBREV = {
        1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN',
        7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'
    }
    
    def __init__(self):
        self.current_date = date.today()
    
    def get_last_thursday_of_month(self, year, month):
        """
        Get the last Thursday of a given month and year.
        BANKNIFTY futures expire on the last Thursday of each month.
        """
        # Get the last day of the month
        last_day = monthrange(year, month)[1]
        
        # Find the last Thursday
        for day in range(last_day, 0, -1):
            if date(year, month, day).weekday() == 3:  # Thursday is 3
                return date(year, month, day)
        
        # This should never happen, but just in case
        return None
    
    def get_current_expiry_month_year(self):
        """
        Get the current expiry month and year based on today's date.
        If today is past the current month's expiry, move to next month.
        """
        current_year = self.current_date.year
        current_month = self.current_date.month
        
        # Get current month's expiry date
        current_expiry = self.get_last_thursday_of_month(current_year, current_month)
        
        # If today is past current month's expiry, move to next month
        if self.current_date > current_expiry:
            if current_month == 12:
                return current_year + 1, 1
            else:
                return current_year, current_month + 1
        else:
            return current_year, current_month
    
    def get_next_expiry_month_year(self):
        """
        Get the next expiry month and year after the current expiry.
        """
        current_year, current_month = self.get_current_expiry_month_year()
        
        if current_month == 12:
            return current_year + 1, 1
        else:
            return current_year, current_month + 1
    
    def format_futures_symbol(self, year, month):
        """
        Format the futures symbol for a given year and month.
        Format: NSE:BANKNIFTY{YY}{MMM}FUT
        Example: NSE:BANKNIFTY25JUNFUT
        """
        year_suffix = str(year)[-2:]  # Get last 2 digits of year
        month_abbrev = self.MONTH_ABBREV[month]
        return f"NSE:BANKNIFTY{year_suffix}{month_abbrev}FUT"
    
    def get_current_futures_symbol(self):
        """
        Get the current month futures symbol.
        """
        year, month = self.get_current_expiry_month_year()
        return self.format_futures_symbol(year, month)
    
    def get_next_futures_symbol(self):
        """
        Get the next month futures symbol.
        """
        year, month = self.get_next_expiry_month_year()
        return self.format_futures_symbol(year, month)
    
    def get_expiry_date(self, year, month):
        """
        Get the expiry date for a given year and month.
        """
        return self.get_last_thursday_of_month(year, month)
    
    def get_current_expiry_date(self):
        """
        Get the current month's expiry date.
        """
        year, month = self.get_current_expiry_month_year()
        return self.get_expiry_date(year, month)
    
    def get_next_expiry_date(self):
        """
        Get the next month's expiry date.
        """
        year, month = self.get_next_expiry_month_year()
        return self.get_expiry_date(year, month)
    
    def get_futures_info(self):
        """
        Get comprehensive futures information.
        Returns a dictionary with current and next month futures details.
        """
        current_year, current_month = self.get_current_expiry_month_year()
        next_year, next_month = self.get_next_expiry_month_year()
        
        return {
            'current': {
                'symbol': self.get_current_futures_symbol(),
                'year': current_year,
                'month': current_month,
                'month_name': self.MONTH_ABBREV[current_month],
                'expiry_date': self.get_current_expiry_date()
            },
            'next': {
                'symbol': self.get_next_futures_symbol(),
                'year': next_year,
                'month': next_month,
                'month_name': self.MONTH_ABBREV[next_month],
                'expiry_date': self.get_next_expiry_date()
            },
            'updated_on': self.current_date
        }
    
    def print_futures_info(self):
        """
        Print futures information in a readable format.
        """
        info = self.get_futures_info()
        
        print("=" * 60)
        print("BANKNIFTY FUTURES CONFIGURATION")
        print("=" * 60)
        print(f"Configuration Date: {info['updated_on']}")
        print()
        print("CURRENT MONTH:")
        print(f"  Symbol: {info['current']['symbol']}")
        print(f"  Expiry: {info['current']['expiry_date']} ({info['current']['month_name']} {info['current']['year']})")
        print()
        print("NEXT MONTH:")
        print(f"  Symbol: {info['next']['symbol']}")
        print(f"  Expiry: {info['next']['expiry_date']} ({info['next']['month_name']} {info['next']['year']})")
        print("=" * 60)


# Global instance for easy access
futures_config = FuturesConfig()

# Convenience functions for backward compatibility
def get_current_futures_symbol():
    """Get the current month futures symbol."""
    return futures_config.get_current_futures_symbol()

def get_next_futures_symbol():
    """Get the next month futures symbol."""
    return futures_config.get_next_futures_symbol()

def get_futures_symbols():
    """Get both current and next month futures symbols."""
    return {
        'current': get_current_futures_symbol(),
        'next': get_next_futures_symbol()
    }

def get_futures_info():
    """Get comprehensive futures information."""
    return futures_config.get_futures_info()


# Test the configuration when run directly
if __name__ == "__main__":
    config = FuturesConfig()
    config.print_futures_info()
    
    print("\nTesting symbol generation:")
    print(f"Current Futures: {get_current_futures_symbol()}")
    print(f"Next Futures: {get_next_futures_symbol()}")