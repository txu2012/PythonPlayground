import subprocess
import sys
import os
import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
from threading import Thread
import time
from datetime import date
from datetime import datetime

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as ex:
        print(ex)
        print('Press enter to exit ...')
        input()
        sys.exit(255)

try:
    from PIL import ImageGrab
except ImportError as e:
    install('pillow')
    
    from PIL import ImageGrab


class ScreenShotGui():
    def __init__(self):
        self._root_window = tk.Tk()
        self._root_window.title("Screenshot Runner")
        self._width = 400
        self._height = 130
        
        self._btn_directory = None
        self._txt_directory = None
        self._selected_directory = ""
        
        self._btn_start = None
        self._btn_stop = None
        self._status = tk.StringVar()
        self._status.set("Stopped") 
        
        # Intervals in seconds
        #self._interval = 10
        self._interval = tk.IntVar()
        self._interval.set(10)
        self._quality = 80
        
    def __enter__(self):
        return self
        
    def __exit__(self):
        self._root_window.destroy()
        
    def start(self):
        self.create_gui()
        self._root_window.protocol("WM_DELETE_WINDOW", self.__exit__)  
        self._root_window.geometry(f"{self._width}x{self._height}")
        self._root_window.resizable(False, False)
        self._root_window.mainloop()
        
    def create_gui(self):
        self._btn_directory = tk.Button(self._root_window, text="Directory", width=10, command=self.directory_select)
        self._btn_directory.grid(row=0, column=0, padx=(5,5))
        
        xscrollbar = Scrollbar(self._root_window, orient=tk.HORIZONTAL)
        xscrollbar.grid(row=1, column=1, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=2)
        self._txt_directory = tk.Text(self._root_window, width=30, height=1, wrap=tk.NONE, xscrollcommand=xscrollbar.set)
        self._txt_directory.grid(row=0, column=1, padx=(3,2), columnspan=2)
        self._txt_directory.config(state='disabled')
        xscrollbar.config(command=self._txt_directory.xview)
        
        tk.Label(self._root_window, text="Stopped", textvariable=self._status, width=15).grid(row=2, column=0)
        tk.Label(self._root_window, text="Intervals (s)", width=15, height=2, anchor="e").grid(row=2, column=1)
        self._nud_interval = tk.Spinbox(self._root_window, 
                                        from_=1, 
                                        to=86400, 
                                        increment=1,
                                        width=8, 
                                        textvariable=self._interval)
        self._nud_interval.grid(row=2, column=2, sticky="w")# make min/max updateable
        
        self._btn_start = tk.Button(self._root_window, text="Start", width=10, command=self.start_screenshots)
        self._btn_start.grid(row=3, column=0, padx=(5,5), pady=(10,0))
        self._btn_stop = tk.Button(self._root_window, text="Stop", width=10, command=self.stop_screenshots)
        self._btn_stop.grid(row=3, column=1, pady=(10,0))
        
    """
    GUI Functions
    """
    def start_screenshots(self):
        self._take_screenshots = True
        self._screenshot_thread = Thread(target=self.screenshots_thread)
        self._screenshot_thread.start()
        self._status.set("Running") 
    
    def stop_screenshots(self):
        self._take_screenshots = False
        self._screenshot_thread.join()
        self._status.set("Stopped") 
        
    def directory_select(self):
        self._selected_directory = filedialog.askdirectory()
        self._txt_directory.config(state='normal')
        self._txt_directory.delete(1.0, tk.END)
        self._txt_directory.insert(tk.END, f'{self._selected_directory}')
        self._txt_directory.config(state='disabled') 
        
    def screenshots_thread(self):
        while self._take_screenshots:
            today = date.today()
            now = datetime.now()
            fileName = self._selected_directory + os.path.sep + 'scr-' + today.strftime("%Y%m%d") + '-' + now.strftime("%H%M%S") + '.jpg'
            screenshot = ImageGrab.grab()
            screenshot.save(fileName)
        
            time.sleep(self._interval.get())
                

class ScreenshotInterval():
    """Wrapper class for setting the main window"""

    def __init__(self):        
        gui = ScreenShotGui()
        gui.start()

if __name__ == "__main__":
    app = ScreenshotInterval()