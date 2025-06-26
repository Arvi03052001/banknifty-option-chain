"""
Standalone Option Chain Snapshot Service
This runs independently of the web application to avoid Flask debug mode issues
"""

import os
import csv
import time
from datetime import datetime, time as dt_time
from apscheduler.schedulers.background import BackgroundScheduler
from option_chain_fetcher import run_option_chain, get_spot_price, get_futures_price
from option_chain_utils import find_closest_strike, add_color_classes

# Configuration
SNAPSHOT_DIR = 'option_chain_snapshots'
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# Table columns to save (as per index.html)
COLUMNS = [
    'timestamp', 'spot_price', 'futures_price', 'strike',
    'call_chg_oi', 'call_oi', 'price', 'put_oi', 'put_chg_oi',
    'call_chg_oi_class', 'call_oi_class', 'put_oi_class', 'put_chg_oi_class', 'highlighted', 'every_500'
]

def save_option_chain_snapshot():
    """Save option chain snapshot to CSV"""
    now = datetime.now()
    
    # Only run during market hours (Mon-Fri, 9:15-15:30)
    # Uncomment the lines below to enable market hours check
    if now.weekday() >= 4: #Monday to Friday are 0-4, Saturday and Sunday are 5-6
         return
    if not (dt_time(9, 15) <= now.time() <= dt_time(15, 30)):
         return
    
    print(f"Taking snapshot at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        spot_price = get_spot_price()
        futures_price = get_futures_price()
        option_chain = run_option_chain(return_data=True)
        option_chain = add_color_classes(option_chain)
        closest_strike = find_closest_strike(futures_price, option_chain)

        filename = os.path.join(SNAPSHOT_DIR, f"{now.strftime('%Y-%m-%d')}.csv")
        file_exists = os.path.isfile(filename)
        
        print(f"Saving snapshot to: {filename}")
        print(f"Spot price: {spot_price}, Futures price: {futures_price}")
        print(f"Option chain rows: {len(option_chain) if option_chain else 0}")

        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            if not file_exists:
                writer.writeheader()
            for row in option_chain:
                writer.writerow({
                    'timestamp': now.strftime('%Y-%m-%d %H:%M'),
                    'spot_price': spot_price,
                    'futures_price': futures_price,
                    'strike': row['strike'],
                    'call_chg_oi': row['call']['chg_oi'],
                    'call_oi': row['call']['oi'],
                    'price': row.get('price', ''),
                    'put_oi': row['put']['oi'],
                    'put_chg_oi': row['put']['chg_oi'],
                    'call_chg_oi_class': row['call']['chg_oi_class'],
                    'call_oi_class': row['call']['oi_class'],
                    'put_oi_class': row['put']['oi_class'],
                    'put_chg_oi_class': row['put']['chg_oi_class'],
                    'highlighted': int(row['strike'] == closest_strike),
                    'every_500': int(row['strike'] % 500 == 0)
                })
        
        print(f"Snapshot saved successfully with {len(option_chain)} rows")
        
    except Exception as e:
        print(f"Error saving snapshot: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to run the snapshot service"""
    print("Starting Option Chain Snapshot Service...")
    
    # Scheduler setup
    scheduler = BackgroundScheduler()
    scheduler.add_job(save_option_chain_snapshot, 'cron', minute='*/15', second=0)
    scheduler.start()
    
    print("Snapshot scheduler started - will take snapshots every minute")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down snapshot service...")
        scheduler.shutdown()
        print("Snapshot service stopped")

if __name__ == '__main__':
    main()