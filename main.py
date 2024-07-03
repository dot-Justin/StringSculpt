from dotenv import load_dotenv
import os
import time
import queue
import requests
import pyperclip
import pyautogui
import collections
from system_hotkey import SystemHotkey, SystemRegisterError
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
LLM_TEMPERATURE = 0.7

# Patch system_hotkey to use collections.abc.Iterable for compatibility with Python 3.10+
if not hasattr(collections, 'Iterable'):
    import collections.abc
    collections.Iterable = collections.abc.Iterable

# Queue for inter-thread communication
ui_queue = queue.Queue()

def get_selected_text(retries=3):
    initial_clipboard_content = pyperclip.paste()  # Get the initial clipboard content
    time.sleep(0.5)  # Add delay to ensure the text is copied
    pyautogui.hotkey('ctrl', 'c')
    for _ in range(retries):
        selected_text = pyperclip.paste()
        if selected_text and selected_text != initial_clipboard_content:
            return selected_text
        # time.sleep(0.5)  # Wait a bit before retrying
    return None

def replace_selected_text(text):
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')

def format_text(selected_text, instructions):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # If no text selected, different prompt for regular generations.
    if not selected_text:
        print("No text selected, defaulting to regular generation")
        data = {
            'model': 'llama3-8b-8192',
            'messages': [
                {
                    "role": "user",
                    "content": f"{instructions}"
                }
            ],
            'temperature': LLM_TEMPERATURE
        }
    # Else, format mode
    else:
        data = {
            'model': 'llama3-8b-8192',
            'messages': [
                {
                    "role": "user",
                    "content": f"Format the following text based on these instructions. KEEP THE MESSAGE GENERALLY THE SAME UNLESS THE USER SPECIFIES OTHERWISE. Do not output \"Here is the formatted text\" or anything similar, pretend you are the user by sending their message, but edited. If no relevant instructions are provided, output the text exactly as it came to you. Shortcodes: fix (fix grammar and spelling, etc), caps|capitalize (fix capitalization only, not grammar or spelling) spelling|spell (fix spelling only) summarize|sum (Summarize the selected text. Keep important details, but don't use extra words that do the same job as one short word.): {instructions}\n\nText:\n{selected_text}"
                }
            ],
            'temperature': LLM_TEMPERATURE
        }
    try:
        response = requests.post(BASE_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        formatted_text = response_data['choices'][0]['message']['content'].strip()
        return formatted_text
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        print(f"Response: {response.text}")
        return None

class CustomDialog(ctk.CTkToplevel):
    def __init__(self, master, selected_text, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("250x285")
        self.resizable(False, False)
        self.title("StringSculpt")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        self.lift()
        self.focus_force()

        self.logo = Image.open("assets/banner.png")
        self.update_idletasks()

        # Get the dimensions of the window, then do some math to correctly size the banner
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        aspect_ratio = self.logo.width / self.logo.height
        max_width = window_width * 0.9
        max_height = window_height * 0.9
        if max_width / aspect_ratio <= max_height:
            desired_size = (int(max_width), int(max_width / aspect_ratio))
        else:
            desired_size = (int(max_height * aspect_ratio), int(max_height))

        self.logo = self.logo.resize(desired_size, Image.LANCZOS)
        self.logo_ctk = ctk.CTkImage(self.logo, size=desired_size)

        self.logo_label = ctk.CTkLabel(self, image=self.logo_ctk, text="")
        self.logo_label.pack(pady=10)

        self.spacer = ctk.CTkLabel(self, text="", height=20)
        self.spacer.pack()

        custom_font = ctk.CTkFont(family="Consolas", size=15, weight="normal")

        # Change text based on if text is selected or not
        if not selected_text:
            self.label = ctk.CTkLabel(
                self, 
                text="What do you want me to generate today?", 
                text_color="#f6f3ff", 
                font=custom_font,
                wraplength=240  # Adjust the wrap length as needed
            )
            self.label.pack(pady=5)
        else:
            self.label = ctk.CTkLabel(
                self, 
                text="How do you want me to sculpt this?", 
                text_color="#f6f3ff", 
                font=custom_font,
                wraplength=240  # Adjust the wrap length as needed
            )
            self.label.pack(pady=5)

        # Text entry
        text_entry_font = ctk.CTkFont(family="Consolas", size=15, weight="normal")
        self.entry_frame = ctk.CTkFrame(self, fg_color="#242424")
        self.entry_frame.pack(pady=5, fill="x", expand=True)

        self.entry = ctk.CTkEntry(
            self.entry_frame,
            text_color="#6bcad7",
            fg_color="#242424",
            font=text_entry_font,
            height=40,
            border_width=1,
            border_color="#48a8cc"
        )
        self.entry.pack(side='left', fill='x', padx=(10, 10), pady=(0, 0), expand=True)

        # "Go" button
        button_font = ctk.CTkFont(family="Consolas", size=15, weight="normal")

        self.button = ctk.CTkButton(
            self.entry_frame,
            text="Go",
            command=self.on_submit,
            text_color="#ffffff",
            width=40,
            height=40,  # Adjust height to ensure vertical centering
            font=button_font,
            anchor="center",  # Center-align the text
            fg_color="#242424",  # Match button background color with entry field
            hover_color="#48a8cc",  # Set hover color
            border_width=1,
            border_color="#48a8cc"
        )
        self.button.pack(side='right', padx=(0, 10), pady=(0, 0))

        self.update()

        # Center window on the screen, near the bottom.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = screen_height - window_height - 200  # Adjust as needed
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.after(100, self.set_focus)

        self.entry.bind("<Escape>", lambda event: self.destroy())
        self.entry.bind("<Return>", self.on_submit)

        self.result = None

    def set_focus(self):
        self.entry.focus_set()

    def on_submit(self, event=None):
        self.result = self.entry.get()
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.result



def show_custom_dialog(selected_text):
    dialog = CustomDialog(root, selected_text)
    return dialog.get_input()

def process_ui_queue():
    try:
        while True:
            task = ui_queue.get_nowait()
            task()
            ui_queue.task_done()
    except queue.Empty:
        pass
    root.after(100, process_ui_queue)

def on_activate(event):
    print("Hotkey activated!")
    selected_text = get_selected_text()

    def handle_ui():
        instructions = show_custom_dialog(selected_text)
        if not instructions:
            print("No instructions provided")
            return

        formatted_text = format_text(selected_text, instructions)
        if formatted_text:
            replace_selected_text(formatted_text)
            print("Text replaced")
        else:
            print("Failed to format text")

    ui_queue.put(handle_ui)

# Create the main application window
root = ctk.CTk()
root.withdraw()

try:
    hk = SystemHotkey()
    hk.register(('control', 'shift', 'f'), callback=on_activate)
    print("Hotkey registered successfully!")
except SystemRegisterError as e:
    print(f"Failed to register hotkey: {e}")

print("Script is running and waiting for hotkey...")

# Start the UI queue processing
root.after(100, process_ui_queue)

# Keep the script running to listen for the hotkey
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Script terminated by user")
