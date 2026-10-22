# Project: Microtonal_Workbench_Mint
# Compile Date: 2026-03-01

import math
import subprocess
import tempfile
import os
import struct
import tkinter as tk
from tkinter import ttk

# --- Microtonal Theory & Scale Engine ---
SCALE_MAP = {
    "Chromatic (Full 12)": list(range(12)),
    "Major (Ionian)": [0, 2, 4, 5, 7, 9, 11],
    "Natural Minor": [0, 2, 3, 5, 7, 8, 10],
    "Pentatonic Major": [0, 2, 4, 7, 9],
    "Whole Tone": [0, 2, 4, 6, 8, 10],
    "Pelog (Gamelan approx)": [0, 1, 5, 7, 10],
    "Slendro (Gamelan approx)": [0, 2, 5, 7, 9],
    "Hirajoshi (Japanese)": [0, 2, 3, 7, 8],
    "Raga Bhairav": [0, 1, 4, 5, 7, 8, 11]
}

TEMP_MAP = {
    "Equal Temperament (12-TET)": [0]*12,
    "Just Intonation (Ptolemaic)": [0, -29, 4, -6, -14, -2, -20, 2, -12, 16, -18, -10],
    "Pythagorean Tuning": [0, 4, 8, -8, 12, -4, 16, 2, 6, 10, -12, 14],
    "Quarter-Comma Meantone": [0, -24, -7, 10, -6, -27, -3, 14, -13, 4, -20, -10],
    "Werckmeister III": [0, -6, 2, -4, 4, -2, 6, -2, 2, 4, -4, 2]
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
BLACK_KEYS = {1, 3, 6, 8, 10}

def play_linux_tone(freq_hz, duration_ms=90):
    """Low-latency audio trigger with anti-clipping envelope (fade in/out)."""
    try:
        sample_rate = 8000
        num_samples = int(sample_rate * (duration_ms / 1000.0))
        fade_samples = int(sample_rate * 0.005) # 5ms smooth envelope ramp
        
        wav_data = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            raw_val = math.sin(2 * math.pi * freq_hz * t)
            
            # Apply anti-click envelope multiplier (fade in / fade out)
            envelope = 1.0
            if i < fade_samples:
                envelope = i / float(fade_samples)
            elif i > num_samples - fade_samples:
                envelope = (num_samples - i) / float(fade_samples)
                
            val = int(30000 * raw_val * envelope)
            wav_data.extend(struct.pack('<h', val))
            
        def background_play():
            try:
                fd, path = tempfile.mkstemp(suffix='.raw')
                os.write(fd, wav_data)
                os.close(fd)
                subprocess.run(['aplay', '-q', '-r', str(sample_rate), '-f', 'S16_LE', '-c', '1', path],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.remove(path)
            except Exception:
                pass
                
        import threading
        threading.Thread(target=background_play, daemon=True).start()
    except Exception:
        pass

class SevenOctaveMintWorkbench:
    def __init__(self, root):
        self.root = root
        self.root.title("Microtonal & Scale 7-Octave Audio-Visual Workbench")
        self.root.geometry("1950x1300")
        self.root.minsize(1500, 1000)

        # Style configuration with large fonts
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", font=("Arial", 14))
        self.style.configure("TButton", font=("Arial", 14, "bold"), padding=10)
        self.style.configure("TLabel", font=("Arial", 14))
        self.style.configure("Labelframe.Label", font=("Arial", 15, "bold"))
        self.style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        self.style.configure("Treeview", font=("Arial", 13), rowheight=32)

        # Top Control Panel
        ctrl_frame = ttk.LabelFrame(root, text=" Tuning, Scale & Transposition Controls ", padding=15)
        ctrl_frame.pack(fill="x", padx=20, pady=15)

        # Root Key / Transposition Selector
        ttk.Label(ctrl_frame, text="Root Key:").grid(row=0, column=0, sticky="w", padx=5)
        self.root_var = tk.StringVar(value="C")
        self.root_combo = ttk.Combobox(ctrl_frame, textvariable=self.root_var, values=NOTE_NAMES, state="readonly", width=8, font=("Arial", 14))
        self.root_combo.grid(row=0, column=1, padx=5, pady=10)
        self.root_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())

        # Scale Selection
        ttk.Label(ctrl_frame, text="Scale / Mode:").grid(row=0, column=2, sticky="w", padx=15)
        self.scale_var = tk.StringVar(value="Major (Ionian)")
        self.scale_combo = ttk.Combobox(ctrl_frame, textvariable=self.scale_var, values=list(SCALE_MAP.keys()), state="readonly", width=24, font=("Arial", 14))
        self.scale_combo.grid(row=0, column=3, padx=5, pady=10)
        self.scale_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())

        # Temperament Selection
        ttk.Label(ctrl_frame, text="Temperament:").grid(row=0, column=4, sticky="w", padx=15)
        self.temp_var = tk.StringVar(value="Equal Temperament (12-TET)")
        self.temp_combo = ttk.Combobox(ctrl_frame, textvariable=self.temp_var, values=list(TEMP_MAP.keys()), state="readonly", width=28, font=("Arial", 14))
        self.temp_combo.grid(row=0, column=5, padx=5, pady=10)
        self.temp_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())

        # Reference Pitch (A4)
        ttk.Label(ctrl_frame, text="Ref A4:").grid(row=0, column=6, sticky="w", padx=15)
        self.ref_var = tk.StringVar(value="440 Hz")
        self.ref_combo = ttk.Combobox(ctrl_frame, textvariable=self.ref_var, values=["415 Hz", "432 Hz", "440 Hz", "442 Hz", "528 Hz"], state="readonly", width=10, font=("Arial", 14))
        self.ref_combo.grid(row=0, column=7, padx=5, pady=10)
        self.ref_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())

        # 7-Octave Virtual Keyboard Canvas
        kb_frame = ttk.LabelFrame(root, text=" 7-Octave Keyboard Inspector (Active Scale Notes Playable / Non-Scale Notes Muted & Greyed) ", padding=15)
        kb_frame.pack(fill="x", padx=20, pady=10)

        self.kb_canvas = tk.Canvas(kb_frame, height=240, bg="#1a1a1a", highlightthickness=0)
        self.kb_canvas.pack(fill="x", expand=True)
        self.kb_canvas.bind("<Button-1>", self.on_keyboard_click)

        # Microtonal Glissando / Mouse Probe Area
        gliss_frame = ttk.LabelFrame(root, text=" Continuous Microtonal Spectrum Audio Probe (Drag Mouse Across Pad) ", padding=15)
        gliss_frame.pack(fill="x", padx=20, pady=15)

        self.gliss_canvas = tk.Canvas(gliss_frame, height=100, bg="#0f0f1a", highlightthickness=0)
        self.gliss_canvas.pack(fill="x", expand=True)
        self.gliss_canvas.bind("<B1-Motion>", self.on_gliss_drag)
        self.gliss_canvas.bind("<Button-1>", self.on_gliss_drag)

        self.readout_label = ttk.Label(gliss_frame, text="Click active keys or drag across pad to inspect exact tuning frequencies...", font=("Consolas", 15, "bold"))
        self.readout_label.pack(pady=8)

        # Data Inspection Table
        data_frame = ttk.LabelFrame(root, text=" Mathematical Note Breakdown (7-Octave Span) ", padding=15)
        data_frame.pack(fill="both", expand=True, padx=20, pady=15)

        cols = ("Note", "MIDI", "Frequency (Hz)", "Cents Shift", "Status")
        self.tree = ttk.Treeview(data_frame, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=240, anchor="center")
        
        tree_scroll = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.key_rects = {}
        self.key_items = {}
        
        self.kb_canvas.bind("<Configure>", lambda e: self.refresh_ui())
        self.refresh_ui()

    def get_reference_pitch(self):
        return float(self.ref_var.get().split(" ")[0])

    def get_root_offset(self):
        root_str = self.root_var.get()
        return NOTE_NAMES.index(root_str)

    def calculate_note_freq(self, note_idx_7oct):
        root_offset = self.get_root_offset()
        absolute_semitone = note_idx_7oct + root_offset
        
        semitone_in_octave = absolute_semitone % 12
        ref_f = self.get_reference_pitch()
        midi_note = 24 + absolute_semitone
        
        cents_shift = TEMP_MAP[self.temp_var.get()][semitone_in_octave]
        
        base_et = ref_f * (2 ** ((midi_note - 69) / 12.0))
        actual_freq = base_et * (2 ** (cents_shift / 1200.0))
        return actual_freq, cents_shift, midi_note, absolute_semitone

    def refresh_ui(self):
        self.draw_keyboard()
        self.draw_gliss_pad()
        self.update_table()

    def draw_keyboard(self):
        self.kb_canvas.delete("all")
        self.key_rects.clear()
        self.key_items.clear()

        scale_intervals = SCALE_MAP[self.scale_var.get()]
        root_offset = self.get_root_offset()
        
        self.kb_canvas.update_idletasks()
        canvas_width = self.kb_canvas.winfo_width()
        if canvas_width < 300:
            canvas_width = 1850

        white_keys_list = []
        for i in range(84):
            abs_sem = i + root_offset
            if (abs_sem % 12) not in BLACK_KEYS:
                white_keys_list.append(i)

        num_white_keys = len(white_keys_list)
        available_width = canvas_width - 30
        white_key_width = max(16.0, available_width / float(num_white_keys))
        key_height = 210

        x_pos = 15.0
        for key_idx in white_keys_list:
            _, _, midi_note, abs_sem = self.calculate_note_freq(key_idx)
            semitone_mod = abs_sem % 12
            
            rel_semitone = (semitone_mod - root_offset) % 12
            is_active = rel_semitone in scale_intervals
            
            color = "#ffffff" if is_active else "#444444"
            rect = self.kb_canvas.create_rectangle(x_pos, 15, x_pos + white_key_width, 15 + key_height, fill=color, outline="#000000", width=1.0)
            
            octave_num = midi_note // 12 - 1
            note_label = f"{NOTE_NAMES[semitone_mod]}{octave_num}"
            text_color = "#000000" if is_active else "#999999"
            
            txt = self.kb_canvas.create_text(x_pos + white_key_width/2.0, 175, text=note_label, fill=text_color, font=("Arial", 7, "bold"))
            
            self.key_rects[rect] = key_idx
            self.key_rects[txt] = key_idx
            self.key_items[key_idx] = (rect, txt)
            x_pos += white_key_width

        x_pos = 15.0
        current_w_x = 15.0
        for i in range(84):
            _, _, midi_note, abs_sem = self.calculate_note_freq(i)
            sem = abs_sem % 12
            
            if sem not in BLACK_KEYS:
                current_w_x += white_key_width
            else:
                rel_semitone = (sem - root_offset) % 12
                is_active = rel_semitone in scale_intervals
                
                color = "#111111" if is_active else "#2c2c2c"
                bx = current_w_x - (white_key_width * 0.35)
                
                rect = self.kb_canvas.create_rectangle(bx, 15, bx + (white_key_width * 0.7), 15 + (key_height * 0.58), fill=color, outline="#777777" if not is_active else "#00ffff", width=1.0)
                
                octave_num = midi_note // 12 - 1
                note_label = f"{NOTE_NAMES[sem]}{octave_num}"
                text_color = "#ffffff" if is_active else "#666666"
                txt = self.kb_canvas.create_text(bx + (white_key_width * 0.35), 65, text=note_label, fill=text_color, font=("Arial", 6, "bold"))
                
                self.key_rects[rect] = i
                self.key_rects[txt] = i
                self.key_items[i] = (rect, txt)

    def draw_gliss_pad(self):
        self.gliss_canvas.delete("all")
        w = self.gliss_canvas.winfo_width() or 1800
        self.gliss_canvas.create_line(20, 50, w - 20, 50, fill="#00adb5", width=4)
        self.gliss_canvas.create_text(w/2, 22, text="◄ DRAG MOUSE ACROSS SPECTRUM TO HEAR SOUND & PROBE FREQUENCIES ►", fill="#eeeeee", font=("Arial", 13, "bold"))

    def update_table(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        scale_intervals = SCALE_MAP[self.scale_var.get()]
        root_offset = self.get_root_offset()

        for i in range(84):
            freq, cents, midi_note, abs_sem = self.calculate_note_freq(i)
            sem = abs_sem % 12
            rel_semitone = (sem - root_offset) % 12
            is_in_scale = rel_semitone in scale_intervals
            
            status = "ACTIVE" if is_in_scale else "GREYED OUT (Non-Scale)"
            cent_str = f"{cents:+} Cents" if cents != 0 else "0 (Pure/Standard)"
            octave_num = midi_note // 12 - 1
            note_full = f"{NOTE_NAMES[sem]}{octave_num}"
            
            self.tree.insert("", "end", values=(note_full, midi_note, f"{freq:.2f} Hz", cent_str, status))

    def flash_key(self, key_idx):
        if key_idx in self.key_items:
            rect_id, _ = self.key_items[key_idx]
            self.kb_canvas.itemconfig(rect_id, fill="#00ffff")
            self.root.after(180, lambda: self.reset_key_color(key_idx))

    def reset_key_color(self, key_idx):
        if key_idx in self.key_items:
            rect_id, _ = self.key_items[key_idx]
            scale_intervals = SCALE_MAP[self.scale_var.get()]
            root_offset = self.get_root_offset()
            _, _, _, abs_sem = self.calculate_note_freq(key_idx)
            sem = abs_sem % 12
            
            if sem in BLACK_KEYS:
                orig_color = "#111111"
            else:
                orig_color = "#ffffff"
                
            self.kb_canvas.itemconfig(rect_id, fill=orig_color)

    def on_keyboard_click(self, event):
        item = self.kb_canvas.find_withtag("current")
        if item and item[0] in self.key_rects:
            key_idx = self.key_rects[item[0]]
            freq, cents, midi_note, abs_sem = self.calculate_note_freq(key_idx)
            sem = abs_sem % 12
            octave_num = midi_note // 12 - 1
            note_full = f"{NOTE_NAMES[sem]}{octave_num}"
            
            scale_intervals = SCALE_MAP[self.scale_var.get()]
            root_offset = self.get_root_offset()
            rel_semitone = (sem - root_offset) % 12
            is_active = rel_semitone in scale_intervals
            
            if not is_active:
                self.readout_label.config(text=f"Note {note_full} is muted (Greyed Out / Outside Active Scale)")
                return
            
            self.readout_label.config(text=f"Playing Scale Note: {note_full} | Freq: {freq:.2f} Hz | Shift: {cents:+} Cents")
            self.flash_key(key_idx)
            play_linux_tone(freq, duration_ms=220)

    def on_gliss_drag(self, event):
        w = self.gliss_canvas.winfo_width() or 1800
        norm_x = max(0.0, min(1.0, event.x / float(w)))
        
        root_offset = self.get_root_offset()
        base_midi = 24 + root_offset + (norm_x * 84.0)
        ref_f = self.get_reference_pitch()
        freq = ref_f * (2 ** ((base_midi - 69) / 12.0))
        
        self.gliss_canvas.delete("cursor")
        self.gliss_canvas.create_line(event.x, 15, event.x, 85, fill="#ff2e63", width=4, tags="cursor")
        
        self.readout_label.config(text=f"Probe Audio: {freq:.2f} Hz | Continuous MIDI: {base_midi:.2f}")
        play_linux_tone(freq, duration_ms=45)

if __name__ == "__main__":
    print("Project: Microtonal_Workbench_Mint")
    print("Compile Date: 2026-03-01")
    root = tk.Tk()
    app = SevenOctaveMintWorkbench(root)
    root.mainloop()
