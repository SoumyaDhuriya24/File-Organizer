import os
import json
from datetime import datetime
from pathlib import Path


class DateChecker:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config_dir = Path(config_path).parent
        self.config_dir.mkdir(exist_ok=True)

    def load_last_run_date(self):
        """Load the last run date from config file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('last_run_date')
            except:
                return None
        return None

    def save_last_run_date(self, date_str):
        """Save the current date to config file"""
        config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            except:
                pass

        config['last_run_date'] = date_str

        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)

    def has_date_changed(self):
        """Check if the date has changed since last run"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        last_date = self.load_last_run_date()

        if last_date is None or last_date != current_date:
            return True, current_date
        return False, current_date

    def update_date(self):
        """Update the last run date to today"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        self.save_last_run_date(current_date)