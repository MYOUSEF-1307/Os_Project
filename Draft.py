import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import os
import subprocess
import schedule
import threading
import time
import paramiko

class DirectorySelectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Directory Selector")
        self.geometry("650x340")
        self.font = ctk.CTkFont(family="Arial Black", size=14, weight="bold")
        self.font_2 = ctk.CTkFont(family="Arial Black", size=22, weight="bold")
       

        self.create_widgets()

    def create_widgets(self):

        

        self.directory_label1 = ctk.CTkLabel(self, text="LOCAL SYNCING", font=self.font_2)
        self.directory_label1.grid(row=0, column=1, padx=0, pady=9, sticky="we")

        self.directory_label1 = ctk.CTkLabel(self, text="REMOTE SYNCING", font=self.font_2)
        self.directory_label1.grid(row=10, column=1, padx=0, pady=9, sticky="we")

        self.directory_label1 = ctk.CTkLabel(self, text="ROOT DIRECTORY", font=self.font)
        self.directory_label1.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.directory_label2 = ctk.CTkLabel(self, text="TARGET DIRECTORY", font=self.font)
        self.directory_label2.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.directory_entry1 = ctk.CTkEntry(self, width=300, font=self.font)
        self.directory_entry1.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        self.directory_entry2 = ctk.CTkEntry(self, width=300, font=self.font)
        self.directory_entry2.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        self.select_button1 = ctk.CTkButton(self, text="SELECT", command=lambda: self.select_directory(self.directory_entry1), font=self.font)
        self.select_button1.grid(row=1, column=2, padx=5, pady=5, sticky="e")

        self.select_button2 = ctk.CTkButton(self, text="SELECT", command=lambda: self.select_directory(self.directory_entry2), font=self.font)
        self.select_button2.grid(row=2, column=2, padx=5, pady=5, sticky="e")

        self.open_window_button = ctk.CTkButton(self, text="GUEST VM", command=lambda: self.open_window(), font=self.font)
        self.open_window_button.grid(row=12, column=1,padx=5, pady=5, sticky="we")

        self.sync_button = ctk.CTkButton(self, text="SYNC", command=lambda: self.sync_directories(), font=self.font, fg_color="green")
        self.sync_button.grid(row=6, column=1, padx=5, pady=5, sticky="we")

        self.desync_button = ctk.CTkButton(self, text="DE-SYNC", command=lambda: self.desync_directories(), font=self.font,fg_color="red")
        self.desync_button.grid(row=7, column=1, padx=5, pady=5, sticky="we")

        self.ssh_button = ctk.CTkButton(self, text="SYNC", command=lambda: self.sync_directory_ip(), font=self.font,fg_color="green")
        self.ssh_button.grid(row=20, column=1, padx=5, pady=5, sticky="we")

        self.sync_mode = tk.StringVar(value="bi-directional")
        self.one_way_radio = tk.Radiobutton(self, text="One-way Sync", variable=self.sync_mode, value="one-way", bg="#f0f0f0")
        self.one_way_radio.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.bi_directional_radio = tk.Radiobutton(self, text="Bi-directional Sync", variable=self.sync_mode, value="bi-directional", bg="#f0f0f0")
        self.bi_directional_radio.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Schedule automatic syncing every hour
        # Start a separate thread for scheduling
        self.schedule_thread = threading.Thread(target=self.run_schedule)
        self.schedule_thread.daemon = True
        self.schedule_thread.start()

    def open_window(self):
        new_window = ctk.CTkToplevel(self)
        self.hostname = ""  # Set your remote server IP here
        self.username = ""  # Set your SSH username here
        self.password = ""  # Set your SSH password here

        self.ip_label = ctk.CTkLabel(new_window, text="IP", font=self.font)
        self.ip_label.grid(row=0, column=0, padx=5, pady=5)

        self.ip_entry = ctk.CTkEntry(new_window, font=self.font)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        self.user_label = ctk.CTkLabel(new_window, text="Username", font=self.font)
        self.user_label.grid(row=1, column=0, padx=5, pady=5)

        self.user_entry = ctk.CTkEntry(new_window, font=self.font)
        self.user_entry.grid(row=1, column=1, padx=5, pady=5)

        self.pass_label = ctk.CTkLabel(new_window, text="Password", font=self.font)
        self.pass_label.grid(row=2, column=0, padx=5, pady=5)

        self.pass_entry = ctk.CTkEntry(new_window, show="*", font=self.font)
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5)

        self.connect_button = ctk.CTkButton(new_window, text="Connect", command=self.generate_dropdown, font=self.font,fg_color="green")
        self.connect_button.grid(row=3, column=1,padx=5, pady=5)

        self.selected_directory = ctk.StringVar(new_window)
        self.selected_directory.set("Select Directory")

        self.dropdown = ctk.CTkOptionMenu(new_window, variable=self.selected_directory, values=["Select Directory"], font=self.font)
        self.dropdown.grid(row=4, column=1,  padx=5, pady=5)

    def generate_dropdown(self):
        self.hostname = self.ip_entry.get()
        self.username = self.user_entry.get()
        self.password = self.pass_entry.get()

        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.hostname, username=self.username, password=self.password)
            stdin, stdout, stderr = self.ssh.exec_command("cd Desktop && ls -d */")
            directories = stdout.read().decode().splitlines()

            self.selected_directory.set("Select Directory")
            self.dropdown.configure(values=directories)

            for directory in directories:
                command = lambda dir=directory: self.set_and_print_selected_directory(dir)
                self.dropdown.set(command)

        except Exception as e:
            ctk.CTkMessageBox.showerror("Error", f"Failed to connect: {e}")

    def set_and_print_selected_directory(self, directory):
        self.selected_directory.set(directory)
        self.selected_directory_str = "Desktop/" + self.selected_directory.get()
        self.selected_directory_str = self.username + "@" + self.hostname + ":" + "~" + "/" + self.selected_directory_str

        self.directory_entry1.delete(0, "end")
        self.directory_entry1.insert(0, self.selected_directory_str)
        self.directory_entry1.configure(state="disabled")

    def __del__(self):
        if hasattr(self, 'ssh'):
            self.ssh.close()

    def toggle_entry(self):
        if self.checkbox_var.get():
            self.ip_field.configure(state="normal")
            self.pass_field.configure(state="normal")
            self.user_field.configure(state="normal")
        else:
            self.ip_field.delete(0, "end")
            self.ip_field.configure(state="disabled")

            self.pass_field.delete(0, "end")
            self.pass_field.configure(state="disabled")

            self.user_field.delete(0, "end")
            self.user_field.configure(state="disabled")

    def sync_directory_ip(self):
        dest = self.directory_entry2.get()
        print("-------------" + dest)
        r_c = "rsync" + '-zaP ' + self.selected_directory_str + " " + dest
        print(r_c)
        sync_mode = self.sync_mode.get()
        print(f"Sync mode selected: {sync_mode}")

        if sync_mode == "one-way":
            rsync_command = ["rsync", "-zaP", self.selected_directory_str, dest]
        else:
            rsync_command = ["rsync", "-zaP", self.selected_directory_str, dest]
            rsync_command_reverse = ["rsync", "-zaP", dest, self.selected_directory_str]

        try:
            subprocess.run(rsync_command, check=True)
            if sync_mode == "bi-directional":
                subprocess.run(rsync_command_reverse, check=True)
            print("Directories synced successfully.")
        except subprocess.CalledProcessError as e:
            print("Error syncing directories:", e)

    def select_directory(self, entry):
        chosen_directory = filedialog.askdirectory()
        if chosen_directory:
            entry.delete(0, ctk.END)
            entry.insert(0, chosen_directory)

    def sync_directories(self):
        source_dir = self.directory_entry1.get()
        target_dir = self.directory_entry2.get()
        sync_mode = self.sync_mode.get()


        if self.directory_exists(source_dir) and self.directory_exists(target_dir):
            dir1 = source_dir + "/"
            dir2 = target_dir + "/"
            self.cronjob(dir1, dir2)
            self.show_alert("Directories synced successfully")
        else:
            self.show_error_message("There is a missing directory")

    def desync_directories(self):
        source_dir = self.directory_entry1.get()
        target_dir = self.directory_entry2.get()
        if self.directory_exists(source_dir) and self.directory_exists(target_dir):
            dir1 = source_dir + "/"
            job = "/usr/bin/python3" + " " + dir1 + ".py"
            self.delete_cron_job_if_exists(job)
            self.show_alert("Directories de-synced successfully")
        else:
            self.show_error_message("There is a missing directory")

    def show_error_message(self, message):
        ctk.CTkMessageBox.showerror("Error", message)

    def show_alert(self, message):
        ctk.CTkMessageBox.showinfo("Information", message)

    def directory_exists(self, directory_path):
        return os.path.isdir(directory_path)

    def run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def cronjob(self, source_directory, destination_directory):
        home_directory = os.path.expanduser('~')
        sync_script_path = os.path.join(home_directory, f"{source_directory}.py")

        sync_script_content = f"""\
import subprocess
def sync_directories():
    source = '{source_directory}'
    destination = '{destination_directory}'
    try:
        subprocess.run(['rsync', '-avz', source, destination], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['rsync', '-avz', destination, source], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {{e.stderr.decode('utf-8')}}")

sync_directories()
        """

        with open(sync_script_path, 'w') as f:
            f.write(sync_script_content)

        os.chmod(sync_script_path, 0o755)

        def setup_cron_job(script_path, python_path='/usr/bin/python3'):
            result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cron_jobs = result.stdout.decode('utf-8') if result.returncode == 0 else ''

            cron_job = f"* * * * * {python_path} {script_path}\n"

            if cron_job not in cron_jobs:
                cron_jobs += cron_job
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate(input=cron_jobs.encode('utf-8'))
                print("Cron job added.")
            else:
                print("Cron job already exists.")

        setup_cron_job(sync_script_path)

    def delete_cron_job_if_exists(self, job_identifier):
        try:
            result = subprocess.run(f"(crontab -l | grep '{job_identifier}')", shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                subprocess.run(f"(crontab -l | grep -v '{job_identifier}' | crontab -)", shell=True, check=True)
                print(f"Cron job '{job_identifier}' deleted successfully.")
            else:
                print(f"Cron job '{job_identifier}' not found.")
        except subprocess.CalledProcessError as e:
            print(f"Error deleting cron job: {e}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    app = DirectorySelectorApp()
    app.mainloop()
