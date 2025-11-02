import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
from pathlib import Path

# --- Import other modules ---
# These files should be in the same directory as main_app.py
try:
    from date_checker import DateChecker
    from desktop_organizer import DesktopOrganizer
    from log_manager import LogManager
except ImportError:
    messagebox.showerror("Import Error",
                         "Could not find required modules (date_checker.py, desktop_organizer.py, log_manager.py). Please ensure they are in the same folder.")
    exit()


# ----------------------------


class DesktopOrganizerGUI:
    """
    A modern, ChatGPT-style GUI for the Desktop Organizer application.
    """

    # --- Color Palette ---
    COLOR_BG_MAIN = "#343541"
    COLOR_BG_SIDEBAR = "#202123"
    COLOR_BG_TEXT = "#444654"
    COLOR_TEXT = "#ECECF1"
    COLOR_TEXT_MUTED = "#C5C5D2"
    COLOR_ACCENT = "#4FC3F7"
    COLOR_BUTTON = "#3E3F4B"
    COLOR_BUTTON_HOVER = "#4A4B58"
    COLOR_SUCCESS = "#81C784"
    COLOR_ERROR = "#E57373"

    # --- Fonts ---
    FONT_FAMILY = "Segoe UI"
    FONT_NORMAL = (FONT_FAMILY, 10)
    FONT_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_TITLE = (FONT_FAMILY, 18, "bold")
    FONT_HEADER = (FONT_FAMILY, 12, "bold")

    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Organizer")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.configure(bg=self.COLOR_BG_MAIN)

        # Initialize modules
        try:
            self.date_checker = DateChecker()
            self.organizer = DesktopOrganizer()
            self.log_manager = LogManager()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize helper modules: {e}")
            self.root.destroy()
            return

        self.setup_ui()
        self.load_today_log()
        # Check date after UI is built
        self.root.after(100, self.check_date_on_start)

    def setup_ui(self):
        """Setup the user interface."""

        # --- Configure Root Grid ---
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        # --- Sidebar ---
        sidebar_frame = tk.Frame(self.root, bg=self.COLOR_BG_SIDEBAR, width=260)
        sidebar_frame.grid(row=0, column=0, sticky="nsw")
        sidebar_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Sidebar Title
        title_label = tk.Label(
            sidebar_frame,
            text="Desktop Organizer",
            font=self.FONT_TITLE,
            bg=self.COLOR_BG_SIDEBAR,
            fg=self.COLOR_TEXT,
            anchor="w"
        )
        title_label.pack(pady=(20, 25), padx=20, fill="x")

        # --- Sidebar Buttons ---
        button_frame = tk.Frame(sidebar_frame, bg=self.COLOR_BG_SIDEBAR)
        button_frame.pack(fill="x", expand=True, padx=15)

        self.create_sidebar_button(
            button_frame,
            text="Quick Organize (Extension)",
            command=self.quick_organize
        ).pack(fill="x", pady=4)

        self.create_sidebar_button(
            button_frame,
            text="Organize by Name (A-Z)",
            command=self.organize_by_name
        ).pack(fill="x", pady=4)

        self.create_sidebar_button(
            button_frame,
            text="Organize by Date (YYYY-MM)",
            command=self.organize_by_date
        ).pack(fill="x", pady=4)

        # --- Sidebar Footer ---
        footer_frame = tk.Frame(sidebar_frame, bg=self.COLOR_BG_SIDEBAR)
        footer_frame.pack(side="bottom", fill="x", padx=15, pady=20)

        self.create_sidebar_button(
            footer_frame,
            text="View Summary",
            command=self.show_summary
        ).pack(fill="x", pady=4)

        self.create_sidebar_button(
            footer_frame,
            text="Export Log to .txt",
            command=self.export_log
        ).pack(fill="x", pady=4)

        # --- Main Content Area ---
        main_frame = tk.Frame(self.root, bg=self.COLOR_BG_MAIN, padx=20, pady=20)
        main_frame.grid(row=0, column=1, sticky="nsew")
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # --- Status Header ---
        status_frame = tk.Frame(main_frame, bg=self.COLOR_BG_MAIN)
        status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=self.FONT_BOLD,
            bg=self.COLOR_BG_MAIN,
            fg=self.COLOR_TEXT
        )
        self.status_label.pack(side="left")

        self.last_run_label = tk.Label(
            status_frame,
            text=f"Last Run: {self.date_checker.load_last_run_date() or 'Never'}",
            font=self.FONT_NORMAL,
            bg=self.COLOR_BG_MAIN,
            fg=self.COLOR_TEXT_MUTED
        )
        self.last_run_label.pack(side="right")

        # --- Log Title & Refresh ---
        log_header_frame = tk.Frame(main_frame, bg=self.COLOR_BG_MAIN)
        log_header_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        log_title = tk.Label(
            log_header_frame,
            text="Activity Log",
            font=self.FONT_HEADER,
            bg=self.COLOR_BG_MAIN,
            fg=self.COLOR_TEXT
        )
        log_title.pack(side="left")

        self.create_header_button(
            log_header_frame,
            text="Refresh",
            command=self.load_today_log
        ).pack(side="right")

        # --- Log Viewer ---
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=self.FONT_NORMAL,
            bg=self.COLOR_BG_TEXT,
            fg=self.COLOR_TEXT,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            insertbackground=self.COLOR_TEXT  # Cursor color
        )
        self.log_text.grid(row=2, column=0, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)  # Read-only

        # --- Configure Log Tags for Styling ---
        self.log_text.tag_configure("header", font=self.FONT_HEADER, foreground=self.COLOR_ACCENT, spacing1=10,
                                    spacing3=5)
        self.log_text.tag_configure("meta", font=self.FONT_NORMAL, foreground=self.COLOR_TEXT_MUTED)
        self.log_text.tag_configure("success_head", font=self.FONT_BOLD, foreground=self.COLOR_SUCCESS)
        self.log_text.tag_configure("error_head", font=self.FONT_BOLD, foreground=self.COLOR_ERROR)
        self.log_text.tag_configure("error_msg", font=self.FONT_NORMAL, foreground=self.COLOR_ERROR)
        self.log_text.tag_configure("divider", foreground=self.COLOR_BG_TEXT,
                                    overstrike=True)  # Hidden text for spacing
        self.log_text.tag_configure("empty", font=self.FONT_NORMAL, foreground=self.COLOR_TEXT_MUTED, justify="center")

    # --- UI Helper Methods ---

    def create_sidebar_button(self, parent, text, command):
        """Creates a styled button for the sidebar."""
        btn = tk.Button(
            parent,
            text=f"  {text}",  # Add padding
            command=command,
            font=self.FONT_BOLD,
            bg=self.COLOR_BUTTON,
            fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BUTTON_HOVER,
            activeforeground=self.COLOR_TEXT,
            relief="flat",
            borderwidth=0,
            pady=10,
            anchor="w"
        )
        btn.bind("<Enter>", lambda e: e.widget.config(bg=self.COLOR_BUTTON_HOVER))
        btn.bind("<Leave>", lambda e: e.widget.config(bg=self.COLOR_BUTTON))
        return btn

    def create_header_button(self, parent, text, command):
        """Creates a small, styled button for the header area."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.FONT_NORMAL,
            bg=self.COLOR_BUTTON,
            fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BUTTON_HOVER,
            activeforeground=self.COLOR_TEXT,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=4
        )
        btn.bind("<Enter>", lambda e: e.widget.config(bg=self.COLOR_BUTTON_HOVER))
        btn.bind("<Leave>", lambda e: e.widget.config(bg=self.COLOR_BUTTON))
        return btn

    # --- Core Logic Methods ---

    def check_date_on_start(self):
        """Check if date has changed on application start"""
        try:
            changed, _ = self.date_checker.has_date_changed()
            if changed:
                response = messagebox.askyesno("Date Changed",
                                               "A new day has started. Would you like to run a Quick Organize on your desktop?")
                if response:
                    self.quick_organize()
        except Exception as e:
            self.status_label.config(text=f"Date check failed: {e}", fg=self.COLOR_ERROR)

    def _run_organization(self, org_function, org_type_name):
        """Helper function to run any organization task."""
        self.status_label.config(text=f"Organizing by {org_type_name}...", fg=self.COLOR_TEXT)
        self.root.update()

        try:
            success, result = org_function()

            if success:
                log_entry = self.log_manager.create_log_entry(
                    org_type_name,
                    result,
                    success=True
                )
                self.log_manager.save_log(log_entry)

                # Only update run date on Quick Organize
                if org_type_name == "Quick Organize (Extension)":
                    self.date_checker.update_date()
                    self.last_run_label.config(text=f"Last Run: {datetime.now().strftime('%Y-%m-%d')}")

                self.status_label.config(text=f"Success! Organized {len(result)} files.", fg=self.COLOR_SUCCESS)
                messagebox.showinfo("Success", f"Successfully organized {len(result)} files!")

            else:
                # 'result' is an error message on failure
                raise Exception(result)

        except Exception as e:
            log_entry = self.log_manager.create_log_entry(
                org_type_name,
                [],
                success=False,
                error_message=str(e)
            )
            self.log_manager.save_log(log_entry)
            self.status_label.config(text="Organization failed!", fg=self.COLOR_ERROR)
            messagebox.showerror("Error", f"Organization failed: {e}")

        finally:
            self.load_today_log()

    def quick_organize(self):
        """Quick organize by extension"""
        self._run_organization(self.organizer.organize_by_extension, "Quick Organize (Extension)")

    def organize_by_name(self):
        """Organize files by name"""
        self._run_organization(self.organizer.organize_by_name, "Organize by Name (A-Z)")

    def organize_by_date(self):
        """Organize files by date"""
        self._run_organization(self.organizer.organize_by_date, "Organize by Date (YYYY-MM)")

    # --- Log and Summary Methods ---

    def load_today_log(self):
        """Load and display today's log"""
        self.log_text.config(state=tk.NORMAL)  # Enable writing
        self.log_text.delete(1.0, tk.END)

        try:
            logs = self.log_manager.get_daily_log()
        except Exception as e:
            self.log_text.insert(tk.END, f"Failed to load logs: {e}\n", "error_msg")
            self.log_text.config(state=tk.DISABLED)  # Disable writing
            return

        if not logs:
            self.log_text.insert(tk.END, "\n\n\nNo organization activities today.\n", "empty")
            self.log_text.config(state=tk.DISABLED)
            return

        self.log_text.insert(tk.END, f"Activity Log - {datetime.now().strftime('%Y-%m-%d')}\n")

        for i, log in enumerate(reversed(logs), 1):  # Show newest first
            self.log_text.insert(tk.END, "-\n", "divider")  # Visual divider

            self.log_text.insert(tk.END, f"Operation #{len(logs) - i + 1}: {log.get('organization_type')}\n", "header")
            self.log_text.insert(tk.END, f"Time: {log.get('timestamp')}\n", "meta")

            if log.get('success'):
                self.log_text.insert(tk.END, "Status: ✓ Success\n", "success_head")
                self.log_text.insert(tk.END, f"Files Moved: {log.get('files_moved', 0)}\n", "meta")

                # Optionally list moved files (can be long)
                # files = log.get('moved_files_list', [])
                # if files:
                #     self.log_text.insert(tk.END, "Files:\n", "meta")
                #     for f in files[:5]: # Show first 5
                #         self.log_text.insert(tk.END, f"  - {f}\n", "meta")
                #     if len(files) > 5:
                #         self.log_text.insert(tk.END, f"  ...and {len(files) - 5} more.\n", "meta")
            else:
                self.log_text.insert(tk.END, "Status: ✗ Failed\n", "error_head")
                if log.get('error'):
                    self.log_text.insert(tk.END, f"Error: {log.get('error')}\n", "error_msg")

            self.log_text.insert(tk.END, "\n")

        self.log_text.config(state=tk.DISABLED)  # Read-only
        self.log_text.yview_moveto(0.0)  # Scroll to top

    def export_log(self):
        """Export today's log to text file"""
        try:
            file_path = self.log_manager.export_log_txt()
            messagebox.showinfo("Success", f"Log exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export log: {str(e)}")

    def show_summary(self):
        """Show summary of today's activities"""
        try:
            summary = self.log_manager.get_summary()

            summary_text = f"""
Daily Summary - {summary['date']}

Total Operations: {summary['total_operations']}
Successful: {summary['successful_operations']}
Failed: {summary['failed_operations']}

Total Files Moved: {summary['total_files_moved']}
            """
            messagebox.showinfo("Daily Summary", summary_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get summary: {e}")


def main():
    try:
        root = tk.Tk()
        app = DesktopOrganizerGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Unhandled Exception",
                             f"A critical error occurred: {e}\n\nThe application will now close.")


if __name__ == "__main__":
    main()
