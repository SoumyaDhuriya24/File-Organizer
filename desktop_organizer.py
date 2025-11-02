import os
import shutil
from pathlib import Path
from datetime import datetime


class DesktopOrganizer:
    def __init__(self, desktop_path=None):
        if desktop_path is None:
            self.desktop_path = Path.home() / "Desktop"
        else:
            self.desktop_path = Path(desktop_path)

        # Define organization categories
        self.categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.java', '.cpp', '.c', '.js', '.html', '.css', '.php', '.json', '.xml'],
            'Executables': ['.exe', '.msi', '.app', '.deb', '.rpm'],
            'Others': []
        }

    def get_category(self, file_ext):
        """Determine the category based on file extension"""
        file_ext = file_ext.lower()
        for category, extensions in self.categories.items():
            if file_ext in extensions:
                return category
        return 'Others'

    def organize_by_extension(self):
        """Organize files by their extensions into folders"""
        moved_files = []

        try:
            # Get all files in desktop (not folders)
            files = [f for f in self.desktop_path.iterdir() if f.is_file()]

            for file in files:
                file_ext = file.suffix
                category = self.get_category(file_ext)

                # Create category folder if it doesn't exist
                category_path = self.desktop_path / category
                category_path.mkdir(exist_ok=True)

                # Move file to category folder
                destination = category_path / file.name

                # Handle duplicate names
                counter = 1
                original_dest = destination
                while destination.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    destination = category_path / f"{stem}_{counter}{suffix}"
                    counter += 1

                shutil.move(str(file), str(destination))
                moved_files.append({
                    'file': file.name,
                    'from': str(self.desktop_path),
                    'to': str(destination),
                    'category': category,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            return True, moved_files

        except Exception as e:
            return False, str(e)

    def organize_by_name(self, prefix_length=1):
        """Organize files alphabetically by first letter(s) of filename"""
        moved_files = []

        try:
            files = [f for f in self.desktop_path.iterdir() if f.is_file()]

            for file in files:
                prefix = file.stem[:prefix_length].upper()
                if not prefix.isalnum():
                    prefix = "Special"

                prefix_path = self.desktop_path / f"Name_{prefix}"
                prefix_path.mkdir(exist_ok=True)

                destination = prefix_path / file.name
                counter = 1
                original_dest = destination
                while destination.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    destination = prefix_path / f"{stem}_{counter}{suffix}"
                    counter += 1

                shutil.move(str(file), str(destination))
                moved_files.append({
                    'file': file.name,
                    'from': str(self.desktop_path),
                    'to': str(destination),
                    'category': f"Name_{prefix}",
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            return True, moved_files

        except Exception as e:
            return False, str(e)

    def organize_by_date(self):
        """Organize files by their modification date"""
        moved_files = []

        try:
            files = [f for f in self.desktop_path.iterdir() if f.is_file()]

            for file in files:
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                date_folder = mod_time.strftime('%Y-%m')

                date_path = self.desktop_path / f"Date_{date_folder}"
                date_path.mkdir(exist_ok=True)

                destination = date_path / file.name
                counter = 1
                original_dest = destination
                while destination.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    destination = date_path / f"{stem}_{counter}{suffix}"
                    counter += 1

                shutil.move(str(file), str(destination))
                moved_files.append({
                    'file': file.name,
                    'from': str(self.desktop_path),
                    'to': str(destination),
                    'category': f"Date_{date_folder}",
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            return True, moved_files

        except Exception as e:
            return False, str(e)