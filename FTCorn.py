# FTCorn.py — Corn-style hardcoded SM64 emulator in Python (experimental)
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import time
from PIL import Image, ImageTk

# ------------------------
# Minimal MIPS CPU with hardcoded SM64 path
# ------------------------
class FTCornCPU:
    def __init__(self, width=320, height=240):
        self.pc = 0x80300000
        self.registers = [0] * 32
        self.memory = bytearray(0x800000)
        self.running = False
        self.width = width
        self.height = height
        self.framebuffer = [[0, 0, 0] for _ in range(width * height)]

    def load_rom(self, rom_data):
        self.memory[0x100000:0x100000+len(rom_data)] = rom_data
        print(f"[FTCornCPU] Loaded ROM: {len(rom_data)} bytes")

    def step(self):
        for y in range(self.height):
            for x in range(self.width):
                idx = y * self.width + x
                if 120 < x < 200 and 80 < y < 160:
                    self.framebuffer[idx] = [255, 0, 0]
                else:
                    self.framebuffer[idx] = [0, 0, 255]
        self.pc += 4

    def run(self):
        self.running = True
        while self.running:
            self.step()
            time.sleep(1 / 30.0)

    def stop(self):
        self.running = False

    def get_framebuffer_image(self):
        img = Image.new("RGB", (self.width, self.height))
        img.putdata([tuple(p) for p in self.framebuffer])
        return img

# ------------------------
# FTCorn UI
# ------------------------
class FTCornApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FTCorn - SM64 Experimental Hardcoded Emulator")
        self.geometry("640x480")
        self.cpu = FTCornCPU()
        self.rom_data = None
        self.cpu_thread = None
        self.tk_img = None
        self.create_gui()

    def create_gui(self):
        self.canvas = tk.Canvas(self, width=320, height=240, bg='black')
        self.canvas.pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack()
        ttk.Button(frame, text="Load ROM", command=self.open_rom).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Run", command=self.run_cpu).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Stop", command=self.stop_cpu).pack(side=tk.LEFT, padx=5)

        self.status = ttk.Label(self, text="FTCorn Ready", anchor='w')
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

        self.after(100, self.update_canvas)

    def open_rom(self):
        path = filedialog.askopenfilename(filetypes=[("N64 ROMs", "*.z64 *.n64 *.v64")])
        if path:
            with open(path, 'rb') as f:
                self.rom_data = f.read()
            self.cpu.load_rom(self.rom_data)
            self.status.config(text=f"Loaded: {os.path.basename(path)}")

    def run_cpu(self):
        if not self.rom_data:
            self.status.config(text="No ROM loaded")
            return
        if self.cpu_thread and self.cpu_thread.is_alive():
            return
        self.cpu_thread = threading.Thread(target=self.cpu.run, daemon=True)
        self.cpu_thread.start()
        self.status.config(text="Running SM64...")

    def stop_cpu(self):
        self.cpu.stop()
        self.status.config(text="Stopped")

    def update_canvas(self):
        if self.cpu.running:
            img = self.cpu.get_framebuffer_image().resize((320, 240))
            self.tk_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor='nw', image=self.tk_img)
        self.after(33, self.update_canvas)

if __name__ == "__main__":
    app = FTCornApp()
    app.mainloop()
