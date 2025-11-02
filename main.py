"""
Desktop Organizer - Main Scheduler
This script runs in the background and automatically organizes desktop when date changes
"""

import time
import schedule
from date_checker import DateChecker
from desktop_organizer import DesktopOrganizer
from log_manager import LogManager


class DesktopOrganizerScheduler:
    def __init__(self):
        self.date_checker = DateChecker()
        self.organizer = DesktopOrganizer()
        self.log_manager = LogManager()

    def auto_organize(self):
        """Automatically organize desktop if date has changed"""
        changed, current_date = self.date_checker.has_date_changed()

        if changed:
            print(f"Date changed to {current_date}. Starting organization...")

            # Organize by extension
            success, result = self.organizer.organize_by_extension()

            # Log the operation
            if success:
                log_entry = self.log_manager.create_log_entry(
                    "Auto Organize (Scheduled)",
                    result,
                    success=True
                )
                print(f"Successfully organized {len(result)} files")
            else:
                log_entry = self.log_manager.create_log_entry(
                    "Auto Organize (Scheduled)",
                    [],
                    success=False,
                    error_message=result
                )
                print(f"Organization failed: {result}")

            self.log_manager.save_log(log_entry)

            # Update last run date
            self.date_checker.update_date()
        else:
            print(f"No date change detected. Last run: {current_date}")

    def run(self):
        """Run the scheduler"""
        print("Desktop Organizer Scheduler Started")
        print("Checking for date changes every hour...")

        # Schedule the check to run every hour
        schedule.every(1).hours.do(self.auto_organize)

        # Also check immediately on startup
        self.auto_organize()

        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == "__main__":
    scheduler = DesktopOrganizerScheduler()
    scheduler.run()