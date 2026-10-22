# Microtonal & Scale Audio-Visual Workbench

A responsive desktop workbench built with **Python 3** and **Tkinter** designed to study, test, and perform microtonal tuning systems, historical temperaments, and custom scale geometries in real time.

---

## 🎹 Core Features

* **7-Octave Virtual Keyboard (C_1 to C_8):** Spans the full standard acoustic piano range with dynamically scaling white and black keys that fit your window size.
* **Strict Scale Muting:** Select from multiple traditional and exotic scales/modes. Active scale notes are fully playable and highlighted, while non-scale keys are visually greyed out and muted.
* **Historical & Microtonal Temperaments:** Instantly toggle between Equal Temperament (12-TET), Just Intonation (Ptolemaic), Pythagorean Tuning, Quarter-Comma Meantone, and Werckmeister III with precise cent-deviation calculations.
* **Continuous Glissando Audio Probe:** Drag your mouse across the spectrum pad to sweep smoothly through microtonal frequencies and cent shifts.
* **Click-Free Low-Latency Audio:** Leverages Linux `aplay` with background threading and a built-in 5ms anti-clipping envelope (fade in/out) to eliminate speaker pops and provide instant auditory feedback.
* **Mathematical Breakdown Table:** Real-time inspection table detailing exact MIDI note numbers, exact frequencies in Hertz, cent shifts, and active/muted status across all 84 notes.

---

## 🛠️ Requirements & Dependencies

* **Python:** Python 3.x
* **Libraries:** Standard library modules only (`tkinter`, `math`, `subprocess`, `tempfile`, `os`, `struct`, `threading`).
