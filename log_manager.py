import os
import json
from datetime import datetime
from pathlib import Path


class LogManager:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.log_file = self.log_dir / f"organization_log_{self.current_date}.json"

    def create_log_entry(self, organization_type, moved_files, success=True, error_message=None):
        """Create a log entry for an organization operation"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'organization_type': organization_type,
            'success': success,
            'files_moved': len(moved_files) if isinstance(moved_files, list) else 0,
            'details': moved_files if success else [],
            'error': error_message if not success else None
        }

        return log_entry

    def save_log(self, log_entry):
        """Save log entry to daily log file"""
        logs = []

        # Load existing logs if file exists
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []

        # Append new log entry
        logs.append(log_entry)

        # Save updated logs
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)

        return True

    def get_daily_log(self, date=None):
        """Retrieve log for a specific date"""
        if date is None:
            date = self.current_date

        log_file = self.log_dir / f"organization_log_{date}.json"

        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def get_all_logs(self):
        """Retrieve all available logs"""
        all_logs = {}

        for log_file in sorted(self.log_dir.glob("organization_log_*.json"), reverse=True):
            date = log_file.stem.replace("organization_log_", "")
            try:
                with open(log_file, 'r') as f:
                    all_logs[date] = json.load(f)
            except:
                continue

        return all_logs

    def get_summary(self, date=None):
        """Get a summary of organization for a specific date"""
        logs = self.get_daily_log(date)

        total_operations = len(logs)
        successful_operations = sum(1 for log in logs if log.get('success'))
        total_files_moved = sum(log.get('files_moved', 0) for log in logs)

        return {
            'date': date or self.current_date,
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': total_operations - successful_operations,
            'total_files_moved': total_files_moved
        }

    def export_log_txt(self, date=None):
        """Export log as readable text format"""
        logs = self.get_daily_log(date)
        date_str = date or self.current_date

        txt_file = self.log_dir / f"organization_log_{date_str}.txt"

        with open(txt_file, 'w') as f:
            f.write(f"Desktop Organization Log - {date_str}\n")
            f.write("=" * 60 + "\n\n")

            for i, log in enumerate(logs, 1):
                f.write(f"Operation #{i}\n")
                f.write(f"Time: {log.get('timestamp')}\n")
                f.write(f"Type: {log.get('organization_type')}\n")
                f.write(f"Status: {'Success' if log.get('success') else 'Failed'}\n")
                f.write(f"Files Moved: {log.get('files_moved', 0)}\n")

                if not log.get('success') and log.get('error'):
                    f.write(f"Error: {log.get('error')}\n")

                if log.get('details'):
                    f.write("\nFiles:\n")
                    for detail in log.get('details', []):
                        f.write(f"  - {detail.get('file')} -> {detail.get('category')}\n")

                f.write("\n" + "-" * 60 + "\n\n")

        return str(txt_file)