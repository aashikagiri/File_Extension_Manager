import tkinter as tk
from tkinter import filedialog, simpledialog, scrolledtext, messagebox
from tkinter.ttk import Separator, Style
import sqlite3
from fleep import get
import os


# Constants
FONT = ("Mononoki Nerd Font", 12)
DB_NAME = "log.db"

def get_file_extension_with_fleep(file_path):
    with open(file_path, 'rb') as file:  # Added colon here
        info = get(file.read(128))
        return info.extension[0] if info.extension else "Unknown"

def create_database():  
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS file_log 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT, renamed_name TEXT)''')
    connection.commit()
    connection.close()

def log_rename(original_name, renamed_name):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO file_log (original_name, renamed_name) VALUES (?, ?)", (original_name, renamed_name))
    connection.commit()
    connection.close()

def browse_file():
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("All Files", "*.*")])
    entry_path.delete(0, tk.END)
    entry_path.insert(0, file_path)
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Click 'Reveal' to show file extension.")
    result_text.config(state=tk.DISABLED)

def reveal_file_extension():
    file_path = entry_path.get().strip()
    if not file_path:
        show_message("Error", "Invalid file path.")
        return
    extension = get_file_extension_with_fleep(file_path)
    update_result(f"The detected file extension is: {extension}")

def rename_file():
    file_path = entry_path.get().strip()
    if not file_path:
        show_message("Error", "Invalid file path.")
        return
    selected_name = ask_for_new_name()
    if selected_name:
        original_name = os.path.basename(file_path)
        new_file_path = os.path.join(os.path.dirname(file_path), selected_name)
        os.rename(file_path, new_file_path)
        update_result(f"File renamed to: {new_file_path}")
        log_rename(original_name, selected_name)
    else:
        show_message("Info", "File not renamed.")

def undo_rename():
    file_path = entry_path.get().strip()
    if not file_path:
        show_message("Error", "Invalid file path.")
        return
    original_name = os.path.basename(file_path)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT original_name FROM file_log WHERE renamed_name=?", (original_name,))
    original_name_result = cursor.fetchone()
    connection.close()
    if original_name_result:
        original_name = original_name_result[0]
        new_file_path = os.path.join(os.path.dirname(file_path), original_name)
        os.rename(file_path, new_file_path)
        update_result(f"Undo: File reverted to original path: {new_file_path}")
    else:
        show_message("Info", "No renaming operation to undo.")

def ask_for_new_name():
    return simpledialog.askstring("Enter New Name", "Enter the desired file name (with extension):", initialvalue=os.path.basename(entry_path.get()))

def read_log():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM file_log")
    changes = cursor.fetchall()
    connection.close()
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    if not changes:
        result_text.insert(tk.END, "No changes in the log.")
    else:
        result_text.insert(tk.END, "Changes in the log:\n")
        for change in changes:
            result_text.insert(tk.END, f"{change[1]} -> {change[2]}\n")
    result_text.config(state=tk.DISABLED)

def show_message(title, message):
    messagebox.showinfo(title, message)

def update_result(message):
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, message)
    result_text.config(state=tk.DISABLED)

def configure_style():
    style = Style()
    style.configure('TButton', font=FONT)
    style.configure('TLabel', font=FONT)

# Initialize Database
create_database()

# GUI Setup
root = tk.Tk()
root.title("Advanced File Extension Manager")
configure_style()

# GUI Elements
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

label_path = tk.Label(frame_top, text="File Path:")
label_path.pack(side=tk.LEFT, padx=5)

entry_path = tk.Entry(frame_top, width=50)
entry_path.pack(side=tk.LEFT, padx=5)

browse_button = tk.Button(frame_top, text="Browse", command=browse_file)
browse_button.pack(side=tk.LEFT, padx=5)

Separator(root, orient='horizontal').pack(fill='x', pady=5)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

reveal_button = tk.Button(frame_buttons, text="Reveal", command=reveal_file_extension)
reveal_button.grid(row=0, column=0, padx=10)

rename_button = tk.Button(frame_buttons, text="Rename", command=rename_file)
rename_button.grid(row=0, column=1, padx=10)

undo_button = tk.Button(frame_buttons, text="Undo", command=undo_rename)
undo_button.grid(row=0, column=2, padx=10)

read_log_button = tk.Button(frame_buttons, text="Read Log", command=read_log)
read_log_button.grid(row=0, column=3, padx=10)

frame_result = tk.Frame(root)
frame_result.pack(pady=10)


result_text = scrolledtext.ScrolledText(frame_result, wrap=tk.WORD, width=70, height=10, state=tk.DISABLED)
result_text.pack()

root.mainloop()