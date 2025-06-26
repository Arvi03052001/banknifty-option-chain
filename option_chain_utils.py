"""
Option Chain Utility Functions
Shared functions for option chain processing
"""

def find_closest_strike(futures_price, option_chain):
    """Find the strike price closest to the futures price"""
    if not option_chain:
        return None
    
    closest_strike = None
    min_difference = float('inf')
    
    for option in option_chain:
        strike = option['strike']
        difference = abs(strike - futures_price)
        if difference < min_difference:
            min_difference = difference
            closest_strike = strike
    
    return closest_strike

def calculate_color_intensity(value, max_value, min_value=0):
    """Calculate color intensity class (1-10) based on value relative to max"""
    if max_value == min_value:
        return 1
    
    # Normalize value to 0-1 range
    normalized = (value - min_value) / (max_value - min_value)
    
    # Convert to 1-10 scale
    intensity = max(1, min(10, int(normalized * 10) + 1))
    return intensity

def format_number(value):
    """Format large numbers to K (thousands) and M (millions) format"""
    abs_value = abs(value)
    sign = '-' if value < 0 else ''
    
    if abs_value >= 1_000_000:
        return f"{sign}{abs_value/1_000_000:.2f}M"
    elif abs_value >= 1_000:
        return f"{sign}{abs_value/1_000:.2f}K"
    else:
        return str(value)

def add_color_classes(option_chain):
    """Add color intensity classes to option chain data"""
    if not option_chain:
        return option_chain
    
    # Extract all values for normalization
    call_chg_oi_values = [abs(opt['call']['chg_oi']) for opt in option_chain if opt['call']['chg_oi'] != 0]
    call_oi_values = [opt['call']['oi'] for opt in option_chain if opt['call']['oi'] != 0]
    put_chg_oi_values = [abs(opt['put']['chg_oi']) for opt in option_chain if opt['put']['chg_oi'] != 0]
    put_oi_values = [opt['put']['oi'] for opt in option_chain if opt['put']['oi'] != 0]
    
    # Get max values for normalization
    max_call_chg_oi = max(call_chg_oi_values) if call_chg_oi_values else 1
    max_call_oi = max(call_oi_values) if call_oi_values else 1
    max_put_chg_oi = max(put_chg_oi_values) if put_chg_oi_values else 1
    max_put_oi = max(put_oi_values) if put_oi_values else 1
    
    # Add color classes to each option and format numbers
    for option in option_chain:
        # Call side color classes
        call_chg_oi_intensity = calculate_color_intensity(abs(option['call']['chg_oi']), max_call_chg_oi)
        call_oi_intensity = calculate_color_intensity(option['call']['oi'], max_call_oi)
        
        # Put side color classes
        put_chg_oi_intensity = calculate_color_intensity(abs(option['put']['chg_oi']), max_put_chg_oi)
        put_oi_intensity = calculate_color_intensity(option['put']['oi'], max_put_oi)
        
        # Add classes to the option data
        option['call']['chg_oi_class'] = f'call-chg-oi-{call_chg_oi_intensity}'
        option['call']['oi_class'] = f'call-oi-{call_oi_intensity}'
        option['put']['chg_oi_class'] = f'put-chg-oi-{put_chg_oi_intensity}'
        option['put']['oi_class'] = f'put-oi-{put_oi_intensity}'
        
        # Format the OI and Change in OI values
        option['call']['oi'] = format_number(option['call']['oi'])
        option['call']['chg_oi'] = format_number(option['call']['chg_oi'])
        option['put']['oi'] = format_number(option['put']['oi'])
        option['put']['chg_oi'] = format_number(option['put']['chg_oi'])
    
    return option_chain