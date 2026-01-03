import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import threading
import os
import re

# Globális változó a folyamat vezérléséhez
letoltesi_folyamat = None
letoltesi_mappa = os.getcwd()

def mappa_valasztas():
    global letoltesi_mappa
    uj_mappa = filedialog.askdirectory()
    if uj_mappa:
        letoltesi_mappa = uj_mappa
        mappa_label.config(text=f"Mentés ide: {letoltesi_mappa}")

def beillesztes():
    try:
        url_entry.delete(0, tk.END)
        url_entry.insert(0, root.clipboard_get())
    except:
        pass

def leallitas():
    global letoltesi_folyamat
    if letoltesi_folyamat:
        letoltesi_folyamat.terminate()
        statusz_label.config(text="Státusz: Megszakítva", fg="red")
        letolt_gomb.config(state="normal")
        stop_gomb.config(state="disabled")
        progress_bar['value'] = 0

def letoltes():
    global letoltesi_folyamat
    url = url_entry.get().strip()
    mod = valasztott_mod.get()
    formatum = audio_format.get()

    if not url:
        statusz_label.config(text="Státusz: Kérlek, adj meg egy URL-t!", fg="red")
        return

    letolt_gomb.config(state="disabled")
    stop_gomb.config(state="normal")
    statusz_label.config(text="Státusz: Letöltés indítása...", fg="blue")
    progress_bar['value'] = 0

    def futtas():
        global letoltesi_folyamat
        try:
            cmd = ["yt-dlp", "--newline", "-o", os.path.join(letoltesi_mappa, "%(title)s.%(ext)s")]
            
            if mod == "audio":
                cmd += ["-f", "bestaudio", "--extract-audio", "--audio-format", formatum]
            
            cmd.append(url)

            letoltesi_folyamat = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            for line in letoltesi_folyamat.stdout:
                # Százalék keresése a kimenetben
                match = re.search(r"(\d+\.\d+)%", line)
                if match:
                    szazalek = float(match.group(1))
                    progress_bar['value'] = szazalek
                    statusz_label.config(text=f"Státusz: Letöltés... {szazalek}%", fg="black")
                
                # Fájlnév kiírása az elején
                if "[download] Destination" in line:
                    fajlnev = line.split("Destination: ")[-1].strip()
                    statusz_label.config(text=f"Fájl: {fajlnev[:50]}...")

            letoltesi_folyamat.wait()
            
            if letoltesi_folyamat.returncode == 0:
                statusz_label.config(text="Státusz: ✅ Kész!", fg="green")
            
        except Exception as e:
            statusz_label.config(text=f"Hiba: {str(e)}", fg="red")
        
        letolt_gomb.config(state="normal")
        stop_gomb.config(state="disabled")

    threading.Thread(target=futtas, daemon=True).start()

# GUI
root = tk.Tk()
root.title("YouTube Downloader - YT-dlp")
root.geometry("600x500")
root.resizable(True, True)

# URL Mező
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(fill="both", expand=True)

tk.Label(main_frame, text="YouTube URL:", font=("Arial", 10, "bold")).pack(anchor="w")
url_entry = tk.Entry(main_frame, font=("Arial", 10), width=50)
url_entry.pack(fill="x", pady=5)

tk.Button(main_frame, text="📋 Beillesztés a vágólapról", command=beillesztes).pack(pady=2)

# Beállítások
options_frame = tk.Frame(main_frame, pady=10)
options_frame.pack(fill="x")

valasztott_mod = tk.StringVar(value="video")
ttk.Radiobutton(options_frame, text="Videó", variable=valasztott_mod, value="video").pack(side="left", padx=5)
ttk.Radiobutton(options_frame, text="Audió (FFmpeg telepítés szükséges.)", variable=valasztott_mod, value="audio").pack(side="left", padx=5)

audio_format = tk.StringVar(value="mp3")
formatum_lista = ttk.Combobox(options_frame, textvariable=audio_format, values=["mp3", "wav", "m4a"], width=5, state="readonly")
formatum_lista.pack(side="right")
tk.Label(options_frame, text="Formátum:").pack(side="right", padx=5)

# Mappa és Statusz
mappa_label = tk.Label(main_frame, text=f"Mentés ide: {letoltesi_mappa}", font=("Arial", 8), fg="gray")
mappa_label.pack(pady=5)
tk.Button(main_frame, text="📁 Mappa választása", command=mappa_valasztas).pack()

# Kontroll Gombok
btn_frame = tk.Frame(main_frame, pady=15)
btn_frame.pack(fill="x")

letolt_gomb = tk.Button(btn_frame, text="LETÖLTÉS", command=letoltes, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15)
letolt_gomb.pack(side="left", expand=True)

stop_gomb = tk.Button(btn_frame, text="MEGSZAKÍTÁS", command=leallitas, bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=15, state="disabled")
stop_gomb.pack(side="right", expand=True)

# Haladásjelző
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
progress_bar.pack(fill="x", pady=10)

statusz_label = tk.Label(main_frame, text="Státusz: Készen áll", font=("Arial", 9, "italic"))
statusz_label.pack(fill="x")

root.mainloop()
