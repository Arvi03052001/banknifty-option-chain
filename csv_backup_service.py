"""
CSV Backup Service for BankNifty Option Chain
Automatically saves option chain data to GitHub as CSV files
"""

import os
import time
import schedule
import pandas as pd
from datetime import datetime, timedelta
from github_storage import GitHubStorage, save_option_chain_to_github
from option_chain_fetcher import run_option_chain
from timezone_utils import get_ist_now, IST

class CSVBackupService:
    def __init__(self):
        self.github = None
        self.setup_github()
        
    def setup_github(self):
        """Setup GitHub storage"""
        try:
            self.github = GitHubStorage()
            if self.github.token:
                # Set repository (replace with your GitHub username)
                self.github.set_repository("your-username", "banknifty-data")
                print("✓ GitHub storage configured")
            else:
                print("⚠ GitHub token not found - CSV backup disabled")
        except Exception as e:
            print(f"✗ GitHub setup failed: {e}")
    
    def is_market_hours(self):
        """Check if current time is within market hours (9:15 AM - 3:30 PM IST)"""
        now = get_ist_now()
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        is_weekday = now.weekday() < 5
        
        return is_weekday and market_start <= now <= market_end
    
    def save_option_chain_snapshot(self):
        """Save current option chain data as CSV"""
        if not self.is_market_hours():
            print("Outside market hours - skipping CSV backup")
            return
        
        if not self.github or not self.github.token:
            print("GitHub not configured - skipping CSV backup")
            return
        
        try:
            print("Taking option chain snapshot...")
            
            # Get option chain data
            option_chain = run_option_chain(return_data=True)
            
            if not option_chain:
                print("No option chain data available")
                return
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"option_chain_{timestamp}.csv"
            
            # Save to GitHub
            success, message = save_option_chain_to_github(option_chain, filename)
            
            if success:
                print(f"✓ Option chain saved: {message}")
            else:
                print(f"✗ Failed to save option chain: {message}")
                
        except Exception as e:
            print(f"✗ Error saving option chain snapshot: {e}")
    
    def save_daily_summary(self):
        """Save daily summary at market close"""
        if not self.github or not self.github.token:
            return
        
        try:
            print("Creating daily summary...")
            
            # Get final option chain data
            option_chain = run_option_chain(return_data=True)
            
            if not option_chain:
                print("No data for daily summary")
                return
            
            # Create daily summary filename
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"daily_summary_{date_str}.csv"
            
            # Add summary metadata
            df = pd.DataFrame(option_chain)
            df['snapshot_date'] = datetime.now().strftime('%Y-%m-%d')
            df['snapshot_time'] = datetime.now().strftime('%H:%M:%S')
            df['market_session'] = 'close'
            
            # Save to GitHub
            success, message = self.github.upload_dataframe_as_csv(
                df, filename,
                github_path=f"daily_summaries/{filename}",
                commit_message=f"Daily summary - {date_str}"
            )
            
            if success:
                print(f"✓ Daily summary saved: {message}")
            else:
                print(f"✗ Failed to save daily summary: {message}")
                
        except Exception as e:
            print(f"✗ Error saving daily summary: {e}")
    
    def cleanup_old_files(self):
        """Clean up old CSV files (keep last 30 days)"""
        # This would require GitHub API calls to list and delete files
        # For now, we'll just log the cleanup attempt
        print("CSV cleanup scheduled (manual cleanup recommended)")
    
    def start_scheduler(self):
        """Start the backup scheduler"""
        print("Starting CSV backup scheduler...")
        
        # Schedule snapshots every 15 minutes during market hours
        schedule.every(15).minutes.do(self.save_option_chain_snapshot)
        
        # Schedule daily summary at market close (3:35 PM IST)
        schedule.every().day.at("15:35").do(self.save_daily_summary)
        
        # Schedule cleanup weekly
        schedule.every().sunday.at("02:00").do(self.cleanup_old_files)
        
        print("CSV backup scheduler started:")
        print("- Option chain snapshots: Every 15 minutes during market hours")
        print("- Daily summary: 3:35 PM IST")
        print("- Cleanup: Sundays at 2:00 AM")
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function to run CSV backup service"""
    service = CSVBackupService()
    
    # Test GitHub connection
    if service.github and service.github.token:
        print("Testing GitHub connection...")
        success, files = service.github.list_repository_files()
        if success:
            print(f"✓ GitHub connection successful - {len(files)} files in repository")
        else:
            print(f"✗ GitHub connection failed: {files}")
    
    # Start scheduler
    service.start_scheduler()

if __name__ == "__main__":
    main()