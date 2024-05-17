import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import schedule
import threading
import time
import paramiko


class DirectorySelectorApp(tk.Tk):
    def __init__(self):

        super().__init__()
        self.title("Directory Selector")
        self.configure(bg="#f0f0f0")  
        self.geometry("600x300")  # Set width and height of the window
        self.create_widgets()

    def create_widgets(self):

        self.directory_label1 = tk.Label(self, text="Root Directory:", bg="#f0f0f0")  
        self.directory_label1.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.directory_label2 = tk.Label(self, text="Target Directory:", bg="#f0f0f0") 
        self.directory_label2.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.directory_entry1 = tk.Entry(self, width=50)
        self.directory_entry1.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        self.directory_entry2 = tk.Entry(self, width=50)
        self.directory_entry2.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        self.select_button1 = tk.Button(self, text="Select Directory", command=lambda:self.select_directory(self.directory_entry1), bg="#000000", fg="white")  
        self.select_button1.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.select_button2 = tk.Button(self, text="Select Directory", command=lambda:self.select_directory(self.directory_entry2), bg="#000000", fg="white")  
        self.select_button2.grid(row=1, column=2, padx=5, pady=5, sticky="e")

        #sync mode Selection
        self.sync_mode = tk.StringVar(value="bi-directional")
        self.one_way_radio = tk.Radiobutton(self, text="One-way Sync", variable=self.sync_mode, value="one-way", bg="#f0f0f0")
        self.one_way_radio.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.bi_directional_radio = tk.Radiobutton(self, text="Bi-directional Sync", variable=self.sync_mode, value="bi-directional", bg="#f0f0f0")
        self.bi_directional_radio.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        #SSH PART DELIMETED 

        ####

        """self.ip_label= tk.Label(self, text="IP", bg="#f0f0f0")  
        self.ip_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ip_field=tk.Entry(self, width=50)

        self.ip_field.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        self.ip_field.config(state="disabled")

        self.checkbox_var = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(self, text="SSH", variable=self.checkbox_var, command=self.toggle_entry)
        self.checkbox.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        self.pass_label= tk.Label(self, text="password (optional)", bg="#f0f0f0")  
        self.pass_label.grid(row=3, column=0, padx=4, pady=5, sticky="w")
        self.pass_field=tk.Entry(self, width=50)

        self.pass_field.grid(row=3, column=1, padx=5, pady=5, sticky="we")
        self.pass_field.config(state="disabled")

        self.user_label= tk.Label(self, text="username", bg="#f0f0f0")  
        self.user_label.grid(row=4, column=0, padx=4, pady=5, sticky="w")

        self.user_field=tk.Entry(self, width=50)
        self.user_field.grid(row=4, column=1, padx=5, pady=5, sticky="we")
        self.user_field.config(state="disabled")"""
        ####
        self.open_window_button = tk.Button(self, text="Open Window", command=lambda: self.open_window())
        self.open_window_button.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="we")
        self.sync_button = tk.Button(self, text="Sync", command= lambda:self.sync_directories(), bg="#0000FF", fg="white")  
        self.sync_button.grid(row=6, column=1, padx=5, pady=5, sticky="we")
        self.desync_button = tk.Button(self, text="De-sync", command=lambda:self.desync_directories(), bg="#FF0000", fg="white")  
        self.desync_button.grid(row=6, column=0, padx=5, pady=5, sticky="we")
        self.ssh_button=tk.Button(self, text="SSH sync", command=lambda:self.sync_directory_ip(), bg="#FF0000", fg="white")  
        self.ssh_button.grid(row=9, column=1, padx=10, pady=5, sticky="we")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2,weight=1)

        # Schedule automatic syncing every hour
        # Start a separate thread for scheduling
        self.schedule_thread = threading.Thread(target=self.run_schedule)
        self.schedule_thread.daemon = True
        self.schedule_thread.start()
    
    def open_window(self):

            new_window = tk.Toplevel(self)
            self.hostname = ""  # Set your remote server IP here
            self.username = ""  # Set your SSH username here
            self.password = ""  # Set your SSH password here
            # IP Field
            self.ip_label = tk.Label(new_window, text="IP")
            self.ip_label.grid(row=0, column=0, padx=5, pady=5)

            self.ip_entry = tk.Entry(new_window)
            self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
            # Username Field
            self.user_label = tk.Label(new_window, text="Username")
            self.user_label.grid(row=1, column=0, padx=5, pady=5)

            self.user_entry = tk.Entry(new_window)
            self.user_entry.grid(row=1, column=1, padx=5, pady=5)
            # Password Field
            self.pass_label = tk.Label(new_window, text="Password")
            self.pass_label.grid(row=2, column=0, padx=5, pady=5)

            self.pass_entry = tk.Entry(new_window, show="*")
            self.pass_entry.grid(row=2, column=1, padx=5, pady=5)
            # Button to Connect and Generate Dropdown
            self.connect_button = tk.Button(new_window, text="Connect", command=self.generate_dropdown)
            self.connect_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
            # Dropdown Menu
            self.selected_directory = tk.StringVar(new_window)
            self.selected_directory.set("Select Directory")

            self.dropdown = tk.OptionMenu(new_window, self.selected_directory, "Select Directory")
            self.dropdown.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def generate_dropdown(self):

    # Get IP, username, and password from entries
        self.hostname = self.ip_entry.get()

        self.username = self.user_entry.get()

        self.password = self.pass_entry.get()

        try:
            # Establish SSH Connection
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.hostname, username=self.username, password=self.password)
            # Retrieve Directory Information
            stdin, stdout, stderr = self.ssh.exec_command("cd Desktop && ls -d */")  # Assuming you want to list directories on Desktop
            directories = stdout.read().decode().splitlines()
            # Update Dropdown Menu with Directory Name
            self.selected_directory.set("Select Directory")
            self.dropdown['menu'].delete(0, 'end')

            for directory in directories:
                # Define a lambda function to set selected directory directly into a variable
                command = lambda dir=directory: self.set_and_print_selected_directory(dir)
                self.dropdown['menu'].add_command(label=directory, command=command)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to connect: {e}")

    def set_and_print_selected_directory(self, directory):
        # Set the selected directory directly into the variable
        self.selected_directory.set(directory)
        # Print the selected directory
        self.selected_directory_str = "Desktop/" + self.selected_directory.get()
        self.selected_directory_str= self.username +"@"+ self.hostname +":"+"~"+"/"+ self.selected_directory_str

        self.directory_entry1.delete(0,"end")
        self.directory_entry1.insert(0,self.selected_directory_str)
        self.directory_entry1.config(state="disabled")

    def __del__(self):
        if hasattr(self, 'ssh'):
            self.ssh.close()

    def toggle_entry(self):

        if self.checkbox_var.get():
            self.ip_field.config(state="normal")
            self.pass_field.config(state="normal")
            self.user_field.config(state="normal")
        else:
            self.ip_field.delete(0, "end")
            self.ip_field.config(state="disabled")

            self.pass_field.delete(0, "end")
            self.pass_field.config(state="disabled")

            self.user_field.delete(0, "end")
            self.user_field.config(state="disabled")



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
            entry.delete(0, tk.END) 
            entry.insert(0, chosen_directory) 

    def sync_directories(self):
        source_dir = self.directory_entry1.get()
        target_dir = self.directory_entry2.get()
        sync_mode = self.sync_mode.get()
        
        if self.directory_exists(source_dir) and self.directory_exists(target_dir):
            dir1 = source_dir + "/"
            dir2 = target_dir + "/"
            self.cronjob(dir1,dir2,sync_mode)
            self.show_alert("Directories synced successfully")
        else:
            self.show_error_message("There is a missing directory")

    def desync_directories(self):
        source_dir = self.directory_entry1.get()
        target_dir = self.directory_entry2.get()
        if self.directory_exists(source_dir) and self.directory_exists(target_dir):
            dir1 = source_dir + "/"
            job= "/usr/bin/python3" + " " + dir1 +".py"
            self.delete_cron_job_if_exists(job)
            self.show_alert("Directories de-synced successfully")
        else:
            self.show_error_message("There is a missing directory")
    def show_error_message(self, message):
        messagebox.showerror("Error", message)

    def show_alert(self, message):
        messagebox.showinfo("Alert", message)

    def directory_exists(self, path):
        return os.path.exists(path) and os.path.isdir(path)
    
    def run_rsync(self, source, destination):
        rsync_command = ["rsync", "-avz"] + source + [destination]
        try:
            subprocess.run(rsync_command, check=True)
            print("Directories synced successfully.")
        except subprocess.CalledProcessError as e:
            print("Error syncing directories:", e)
    def run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
    def cronjob(self,source,destination,sync_mode):
        source_directory = source
        destination_directory = destination

        # Define the path for the sync script in the user's home directory
        home_directory = os.path.expanduser('~')
        sync_script_path = os.path.join(home_directory, f"{source_directory}.py")

        # Content of the sync script
        if sync_mode == "one_way":
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
        else:  # bi-directional
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
        
        # Write the sync script to a file
        with open(sync_script_path, 'w') as f:
            f.write(sync_script_content)

        # Make the sync script executable
        os.chmod(sync_script_path, 0o755)

        # Function to set up the cron job
        def setup_cron_job(script_path, python_path='/usr/bin/python3'):
            # Get the current user's crontab
            result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cron_jobs = result.stdout.decode('utf-8') if result.returncode == 0 else ''
            
            # Define the new cron job
            cron_job = f"* * * * * {python_path} {script_path}\n"
            
            # Add the new cron job if it doesn't already exist
            if cron_job not in cron_jobs:
                cron_jobs += cron_job
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate(input=cron_jobs.encode('utf-8'))
                print("Cron job added.")
            else:
                print("Cron job already exists.")

        # Set up the cron job to run the sync script every minute
        setup_cron_job(sync_script_path)
    
    def delete_cron_job_if_exists(self,job_identifier):
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
