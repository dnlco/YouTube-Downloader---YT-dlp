import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import threading
import os
import re

# Global variable to control the process
download_process = None
download_folder = os.getcwd()

def select_folder():
    global download_folder
    new_folder = filedialog.askdirectory()
    if new_folder:
        download_folder = new_folder
        folder_label.config(text=f"Save to: {download_folder}")

def paste_url():
    try:
        url_entry.delete(0, tk.END)
        url_entry.insert(0, root.clipboard_get())
    except:
        pass

def stop_download():
    global download_process
    if download_process:
        download_process.terminate()
        status_label.config(text="Status: Cancelled", fg="red")
        download_btn.config(state="normal")
        stop_btn.config(state="disabled")
        progress_bar['value'] = 0

def start_download():
    global download_process
    url = url_entry.get().strip()
    mode = selected_mode.get()
    fmt = audio_format.get()

    if not url:
        status_label.config(text="Status: Please provide a URL!", fg="red")
        return

    download_btn.config(state="disabled")
    stop_btn.config(state="normal")
    status_label.config(text="Status: Starting download...", fg="blue")
    progress_bar['value'] = 0

    def run():
        global download_process
        try:
            # Note: ensure yt-dlp is in your PATH or the script directory
            cmd = ["yt-dlp", "--newline", "-o", os.path.join(download_folder, "%(title)s.%(ext)s")]
            
            if mode == "audio":
                cmd += ["-f", "bestaudio", "--extract-audio", "--audio-format", fmt]
            
            cmd.append(url)

            # creationflags=subprocess.CREATE_NO_WINDOW hides the terminal on Windows
            download_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            for line in download_process.stdout:
                # Extract percentage (e.g., [download]  25.3% of...)
                match = re.search(r"(\d+\.\d+)%", line)
                if match:
                    percent = float(match.group(1))
                    progress_bar['value'] = percent
                    status_label.config(text=f"Status: Downloading... {percent}%", fg="black")
                
                # Show filename if detected
                if "[download] Destination" in line:
                    filename = line.split("Destination: ")[-1].strip()
                    status_label.config(text=f"File: {filename[:50]}...")

            download_process.wait()
            
            if download_process.returncode == 0:
                status_label.config(text="Status: ✅ Done!", fg="green")
            else:
                if status_label.cget("text") != "Status: Cancelled":
                    status_label.config(text="Status: ❌ Error during download", fg="red")
            
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg="red")
        
        download_btn.config(state="normal")
        stop_btn.config(state="disabled")

    threading.Thread(target=run, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("YouTube Downloader - YT-dlp")
root.geometry("600x500")
root.resizable(True, True)

main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(fill="both", expand=True)

# URL Section
tk.Label(main_frame, text="YouTube URL:", font=("Arial", 10, "bold")).pack(anchor="w")
url_entry = tk.Entry(main_frame, font=("Arial", 10), width=50)
url_entry.pack(fill="x", pady=5)

tk.Button(main_frame, text="📋 Paste from Clipboard", command=paste_url).pack(pady=2)

# Options Section
options_frame = tk.LabelFrame(main_frame, text=" Settings ", padx=10, pady=10)
options_frame.pack(fill="x", pady=10)

selected_mode = tk.StringVar(value="video")
ttk.Radiobutton(options_frame, text="Video", variable=selected_mode, value="video").pack(side="left", padx=10)
ttk.Radiobutton(options_frame, text="Audio Only (FFmpeg installation is required.)", variable=selected_mode, value="audio").pack(side="left", padx=10)

audio_format = tk.StringVar(value="mp3")
format_list = ttk.Combobox(options_frame, textvariable=audio_format, values=["mp3", "wav", "m4a"], width=5, state="readonly")
format_list.pack(side="right")
tk.Label(options_frame, text="Format:").pack(side="right", padx=5)

# Folder Selection
folder_label = tk.Label(main_frame, text=f"Save to: {download_folder}", font=("Arial", 8), fg="gray")
folder_label.pack(pady=5)
tk.Button(main_frame, text="📁 Select Download Folder", command=select_folder).pack()

# Control Buttons
btn_frame = tk.Frame(main_frame, pady=15)
btn_frame.pack(fill="x")

download_btn = tk.Button(btn_frame, text="DOWNLOAD", command=start_download, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15)
download_btn.pack(side="left", expand=True)

stop_btn = tk.Button(btn_frame, text="CANCEL / STOP", command=stop_download, bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=15, state="disabled")
stop_btn.pack(side="right", expand=True)

# Progress and Status
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
progress_bar.pack(fill="x", pady=10)

status_label = tk.Label(main_frame, text="Status: Ready", font=("Arial", 9, "italic"))
status_label.pack(fill="x")

root.mainloop()
