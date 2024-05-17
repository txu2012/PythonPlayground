#import vgamepad as vg

#print(f"Setting up VDS4Gamepad")

#WAIT_S = 0.1

#g = vg.VDS4Gamepad()
#g.reset()
#g.update()
# press a button to wake the device up
#g.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
#g.update()
#time.sleep(WAIT_S)
#g.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
## wake axes up
#g.left_joystick_float(x_value_float=0.3, y_value_float=-0.3)
#g.right_joystick_float(x_value_float=-0.3, y_value_float=0.3)
#g.left_trigger_float(value_float=0.3)
#g.right_trigger_float(value_float=0.3)
#g.update()
#time.sleep(WAIT_S)
#g.left_joystick_float(x_value_float=-0.3, y_value_float=0.3)
#g.right_joystick_float(x_value_float=0.3, y_value_float=-0.3)
#g.update()
#time.sleep(WAIT_S)
#g.reset()
#g.update()
#time.sleep(WAIT_S)

#while True:
    #g.left_joystick(x_value_float=0.3, y_value_float=-0.3)
    #g.left_joystick(x_value=0, y_value=127)
    #g.update()
import vgamepad as vg
import time
import threading

class DummyJoystick:
    def __init__(self):
        self._joystick = vg.VDS4Gamepad()
        
        self._event = threading.Event()
        self._js_thread = threading.Thread(target=self.joystick_th, daemon=True, args=(self._event,))
        
    def __enter__(self):
        return self    
        
    def __exit__(self, type, value, tb):
        pass      
        
    def joystick_th(self, event: threading.Event) -> None:
        # Needed to keep joystick device discoverable
        while not event.is_set():
            # To receive Ctrl-C signal reliably, insert a small wait.
            time.sleep(0.001)
            
    def start_joystick(self):
        self._event.clear()        
        self._js_thread.start()
        
        self.reset_joystick_positions()
    
    def stop_joystick(self):
        self._event.set()
        del self._joystick
        
    def move_left_joystick(self, x_pos: int=128, y_pos: int=128):
        # integer between 0 and 255 (128 = neutral position)    
        self._joystick.left_joystick(x_value=x_pos, y_value=y_pos)
        self._joystick.update()
        time.sleep(0.1)
    
    def move_right_joystick(self, x_pos: int=128, y_pos: int=128):
        # integer between 0 and 255 (128 = neutral position)
        self._joystick.right_joystick(x_value=x_pos, y_value=y_pos)
        self._joystick.update()
        time.sleep(0.1)
        
    def reset_joystick_positions(self):
        self._joystick.left_joystick(x_value=128, y_value=128)
        self._joystick.right_joystick(x_value=128, y_value=128)
        self._joystick.update()
        time.sleep(0.1)
        
with DummyJoystick() as js:
    js.start_joystick()
    js.reset_joystick_positions()
    
    while True:
        direction = input("Direction input: [up, down, left, right, forward, back, center, exit]")
        
        if str(direction) == "left":
            js.move_left_joystick(0, 128)
        elif str(direction) == "right":
            js.move_left_joystick(255, 128)
        elif str(direction) == "up":
            js.move_left_joystick(128, 255)
        elif str(direction) == "down":
            js.move_left_joystick(128, 0)
        elif str(direction) == "forward":
            js.move_right_joystick(128, 255)
        elif str(direction) == "back":
            js.move_right_joystick(128, 0)
        elif str(direction) == "center":
            js.reset_joystick_positions()
        elif str(direction) == "exit":
            break
        else:
            pass
    
    js.stop_joystick()