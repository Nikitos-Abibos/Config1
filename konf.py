import tkinter as tk
from tkinter import scrolledtext
import tarfile
from datetime import date
import argparse
import os

class ShellEmulator:
    def __init__(self, master, hostname, tar_path):
        self.master = master
        self.master.title("Shell Emulator")
        self.master.geometry("600x400")

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')

        self.command_entry = tk.Entry(master)
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.pack(fill='x')

        self.current_dir = ""
        self.tar_file = None
        self.hostname = hostname
        self.load_tar_file(tar_path)

    def load_tar_file(self, tar_path):
        try:
            self.tar_file = tarfile.open(tar_path, 'r')
            self.text_area.insert(tk.END, "Virtual file system loaded from TAR.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error loading TAR file: {str(e)}\n")

    def close_tar_file(self):
        if self.tar_file:
            self.tar_file.close()
            self.tar_file = None

    def execute_command(self, event):
        command = self.command_entry.get()
        self.command_entry.delete(0, tk.END)
        self.text_area.insert(tk.END, f"{self.hostname}:~\\{self.current_dir}$ {command}\n")
        output = self.process_command(command)
        if output:
            self.text_area.insert(tk.END, output)

    def process_command(self, command):
        if command == "ls":
            return self.list_contents()
        elif command.startswith("cd"):
            return self.change_directory(command)
        elif command == "date":
            return self.show_date()
        elif command.startswith("uniq"):
            return self.remove_duplicates_from_file(command)
        elif command == "exit":
            self.master.quit()
        else:
            return f"command not found: {command}\n"

    def list_contents(self):
        contents = [member.name[len(self.current_dir):].split("/")[0] for member in self.tar_file.getmembers()
                    if member.name.startswith(self.current_dir) and member.name != self.current_dir]
        return '\n'.join(sorted(set(contents))) + '\n'

    def change_directory(self, command):
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return "Usage: cd <directory>\n"

        target_dir = parts[1]
        if target_dir == "..":
            self.current_dir = "/".join(self.current_dir.strip('/').split('/')[:-1])
            if self.current_dir:
                self.current_dir += "/"
        else:
            target_path = self.current_dir + target_dir + "/"
            if any(member.name.startswith(target_path) for member in self.tar_file.getmembers()):
                self.current_dir = target_path
            else:
                return "cd: no such directory\n"

    def show_date(self):
        today = date.today()
        return f'Current Date: {today.isoformat()}\n'

    def remove_duplicates_from_file(self, command):
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return 'Usage: uniq "filename.txt"\n'

        file_name = parts[1].strip('"')
        text_file_path = self.current_dir + file_name

        if not any(member.name == text_file_path for member in self.tar_file.getmembers()):
            return f'File not found: {file_name}\n'

        try:
            with self.tar_file.extractfile(text_file_path) as file:
                lines = file.readlines()

            unique_lines = list(dict.fromkeys(line.decode('utf-8').strip() for line in lines))
            unique_lines.sort()

            return 'Unique lines:\n' + '\n'.join(unique_lines) + '\n'
        
        except Exception as e:
            return f'Error reading file: {str(e)}\n'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Shell Emulator with TAR file support.')
    parser.add_argument('--hostname', type=str, required=True, help='Name of the computer to display in prompt')
    parser.add_argument('--tar_path', type=str, required=True, help='Path to the TAR archive for the virtual file system')
    parser.add_argument('--start_script', type=str, help='Path to the startup script (not implemented)')

    args = parser.parse_args()

    if not os.path.isfile(args.tar_path):
        print(f"Error: TAR file '{args.tar_path}' does not exist.")
        exit(1)

    root = tk.Tk()
    app = ShellEmulator(root, args.hostname, args.tar_path)
    root.mainloop()




