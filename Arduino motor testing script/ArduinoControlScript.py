# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:24:34 2024

@author: Tony
"""
import subprocess
import sys
import re
import struct
import time
from typing import List

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as ex:
        print(ex)
        print('Press enter to exit ...')
        input()
        sys.exit(255)

try:
    import serial
except ImportError as e:
    install('pySerial')

class Rugg:
    def __init__(self, portname: str):
        # To prevent from rebooting the board, set RTS and DTR control to False before
        # opening the port. To do so, don't give the portname to serial.Serial ctor (
        # it would then immediately open the port with DTR = True).
        self._ser = serial.Serial(baudrate=115200)
        self._ser.port = portname
        self._ser.rts = False
        self._ser.dtr = False
        self._ser.open()

        # NOTE: Possible Ruggeduino Mega reboot and freeze.
        # When the serial port is opened first time after the Ruggeduino Mega board is
        # connected to a Windows PC, the board will reboot (this is an Arduino feature
        # for making it easier to upload the sketch). More precisely, when DTR pin drops
        # from HIGH to LOW, the board resets itself.
        # 
        # When it happens, we need to wait for about 2 seconds before the board becomes 
        # responsive again. If we send serial command without waiting for it, board takes
        # even longer to become responsive again and you will see all (or most) commands
        # being ignored.
        # 
        # As of now, we don't implement any action against this here. If desired, we could
        # monitor the DTR pin toggle (as done in Gemini::OctEngine::SerialPort) but it 
        # may be nontrivial to do soe with pySerial.

        # Ignore any bytes already in the read buffer.
        # Serial.read_all immediately after opening the port is unreliable so use
        # Serial.read(n) instead.
        self._ser.timeout = 0
        time.sleep(0.1)
        buffer = self._ser.read(10)

        while len(buffer) > 0:
            print(f"Ignoring initial bytes: ({self._to_hexstr(buffer)})")
            buffer = self._ser.read(10)

        self._ser.timeout = 0.2

        self.xyz_state_dict = {
            0x00: 'PoweredOff',
            0x01: 'Stopped',
            0x02: 'Homing',
            0x03: 'CancelingHoming',
            0x04: 'Moving',
            0x0f: 'Error'
        }
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._ser.close()

    def _to_hexstr(self, buf: bytes):
        return " ".join(f"{b:02x}" for b in buf)

    def write_read(self, cmd: bytes):
        # print(bytes([len(cmd)]) + cmd)
        self._ser.write(bytes([len(cmd)]) + cmd)
        payload_size = self._ser.read(1)
        if len(payload_size) != 1:
            print(f'Error: payload_size={payload_size}')
            return
        
        res = self._ser.read(payload_size[0])
        if (len(res) >= 2):
            print(res)
        else:
            print(f'Error: res={res}')
        
        response_str = res.decode('latin1')
        response_dict = {}
        prev_pos = -1
        prev_key = ''
        for m in re.finditer('\[[a-zA-Z0-9]+\]', response_str):
            if prev_key:
                response_dict[prev_key] = response_str[slice(prev_pos, m.start())].strip()
            prev_pos = m.end()
            prev_key = m.group()[1:-1]
        if prev_key:
            response_dict[prev_key] = response_str[prev_pos:].strip()
        
        return response_dict
                
    def query_name_and_version(self):
        print('query_name_and_version')
        self.write_read(b'\x01')
        self.write_read(b'\x04')
    
    def query_status(self):
        print('query_status')
        response = self.write_read(b'\x10')
        state_value = int(response['HomeAndState'])
        homed = state_value >> 4
        xyz_state_str = self.xyz_state_dict[state_value & 0x0f]
        #print(f'Homed: {homed:03b}, State: {xyz_state_str}')
        return (homed, xyz_state_str)
    
    def configure_directions(self, dir_as_positive: List[bool]):
        print('configure_directions')
        dir_as_positive_flags = 0x00
        for i in range(3):
            dir_as_positive_flags |= dir_as_positive[i] << i
        self.write_read(b'\x11' + bytes([dir_as_positive_flags]))
    
    def start_home_async(self, motor: bytes, target_velocity_x: int, target_velocity_y: int, target_velocity_z: int):
        print('home_async_motors')
        cmd = b'\x13' + motor + struct.pack('<H', target_velocity_x) + struct.pack('<H', target_velocity_y) + struct.pack('<H', target_velocity_z)
        #print(self._to_hexstr(cmd))
        self.write_read(cmd)
    
    def cancel_home_async(self):
        print('cancel_home_async')
        self.write_read(b'\x14')
        
    def configure_velocity_profile(self, start_velocity_x: int, start_velocity_y: int, start_velocity_z: int, accel_x: int, accel_y: int, accel_z: int):
        print('configure_velocity_profile')
        cmd = b'\x12' + struct.pack('<H', start_velocity_x) + struct.pack('<H', start_velocity_y) + struct.pack('<H', start_velocity_z) + struct.pack('<I', accel_x) + struct.pack('<I', accel_y) + struct.pack('<I', accel_z)
        self.write_read(cmd)

    def set_limits(self, position_x_0: int, position_x_1: int, 
                         position_y_0: int, position_y_1: int, 
                         position_z_0: int, position_z_1: int):
        print('set_limit')
        cmd = b'\x15' + struct.pack('<h', position_x_0) + struct.pack('<h', position_x_1) + struct.pack('<h', position_y_0) + struct.pack('<h', position_y_1) + struct.pack('<h', position_z_0) + struct.pack('<h', position_z_1)
        self.write_read(cmd)
    
    def query_limits(self):
        print('query_limit')
        self.write_read(b'\x16')
    
    def start_move_async(self, target_velocity_x: int, target_velocity_y: int, target_velocity_z: int):
        print('start_move_async')
        cmd = b'\x17' + struct.pack('<h', target_velocity_x) + struct.pack('<h', target_velocity_y) + struct.pack('<h', target_velocity_z)
        #print(self._to_hexstr(cmd))
        self.write_read(cmd)
        
    def start_moveto_async(self, target_pos_x: int, target_pos_y: int, target_pos_z: int, target_velocity_x: int, target_velocity_y: int, target_velocity_z: int):
        print('start_moveto_async')
        cmd = b'\x18' + struct.pack('<h', target_pos_x) + struct.pack('<h', target_pos_y) + struct.pack('<h', target_pos_z) + struct.pack('<H', target_velocity_x) + struct.pack('<H', target_velocity_y) + struct.pack('<H', target_velocity_z)
        #print(self._to_hexstr(cmd))
        self.write_read(cmd)

    def gpio_query(self):
        print('gpio_query')
        cmd = b'\x50'
        self.write_read(cmd)
    
    def gpio_set(self, mask, bits):
        print('gpio_set')
        cmd = b'\x51' + struct.pack('<I', mask) + struct.pack('<I', bits)
        # cmd = b'\x51' + struct.pack('<B', bits)
        self.write_read(cmd)

########################################################

def exit_prog():
    print("""
Usage: python3 ArduinoControlScript.py [PORTNAME] [TIME BASED] [Duration] [Loops] [Velocity] [Acceleration]

PORTNAME: Serial port of device
TIME BASED: Run loops based on time (Y = time duration, N = loop amount)
Duration: If time based, set duration of test in seconds
Loops: If not time based, set amount of loops (1 loop = single run from one edge to the other)
Velocity: Target Velocity to reach in Steps/s
Acceleration: Acceleration to reach target velocity in Steps/s2

Press enter to exit ...
""")
    input()
    sys.exit(255)

comport = '\\\\.\\CNCA0'

# X Axis, Y Axis, Z Axis
pos_direction = [False, False, True] # Inverted or not inverted
init_velocity = [1000, 1000, 1000] # Steps/s
target_velocity = [5000, 3000, 5000] # Steps/s
acceleration = [100000, 100000, 100000] # Steps/s
lower_boundary = [0, 0, 0] # Steps
upper_boundary = [30000, 30000, 30000] # Steps
target_position = [0, 0, 0] # Steps

run_loop = 0 # run_loop of 0 will run based on time
run_time = 60 # time in seconds
run_type = True

if __name__ == "__main__":
    if len(sys.argv) > 8:
        exit_prog()
    
    if len(sys.argv) >= 8:
        # comport
        comport = sys.argv[1]
        
        # run type
        if sys.argv[2].upper() == 'Y':
            run_type = True
        elif sys.argv[2].upper() == 'N':
            run_type = False
        else:
            exit_prog()
        
        # duration
        if sys.argv[3].isnumeric() is True:
            run_time = int(sys.argv[3])
        else:
            exit_prog()
        
        # loop amount
        if sys.argv[4].isnumeric() is True:
            run_loop = int(sys.argv[4])
        else:
            exit_prog()
        
        # velocity
        if sys.argv[5].isnumeric() is True:
            target_velocity = [int(sys.argv[5]), int(sys.argv[5]), int(sys.argv[5])]
        else:
            exit_prog()
        
        # acceleration
        if sys.argv[6].isnumeric() is True:
            acceleration = [int(sys.argv[6]), int(sys.argv[6]), int(sys.argv[6])]
        else:
            exit_prog()
        
        if sys.argv[7].isnumeric() is True and (0 <= int(sys.argv[7]) <= 2):
            target_position[int(sys.argv[7])] = 30000
        else:
            exit_prog()
            
    else:
        exit_prog()

print('Input Settings:')
print(f'Comport = {comport}')
print(f'Run type = {run_type}')
print(f'Run time = {run_time}')
print(f'Run Loop Amt = {run_loop}')
print(f'Target Velocity = {target_velocity}')
print(f'Target Acceleration = {acceleration}')
print(f'Axis Movement = {target_position}')

print('\nPress enter to continue ...')
input()

try:
    with Rugg(comport) as mega:        
        mega.query_name_and_version()
        
        # Configure motors
        mega.configure_directions(pos_direction)
        
        mega.configure_velocity_profile(init_velocity[0], init_velocity[1], init_velocity[2], 
                                        acceleration[0], acceleration[1], acceleration[2])
        
        mega.set_limits(lower_boundary[0], upper_boundary[0], 
                        lower_boundary[1], upper_boundary[1], 
                        lower_boundary[2], upper_boundary[2])
    
        # Home Motors
        mega.start_home_async(b'\x07', target_velocity[0], target_velocity[1], target_velocity[2])
        
        _,xyz_state_str = mega.query_status()
        print('Homing.')
        while xyz_state_str != 'Stopped':
            time.sleep(0.05)
            _,xyz_state_str = mega.query_status()
            
        # Start looping side to side
        forward = True
        current_loop = 1
        
        print('Test Starting.')
        start_time = time.time()
        while True:
            if not run_type:
                if current_loop > run_loop:
                    break
            else:
                current_time = time.time() - start_time
                print(f'Elapsed time: {current_time}')
                
                if current_time > run_time:
                    break
            
            if forward:
                print('Direction: Positive')
                mega.start_moveto_async(target_position[0], target_position[1], target_position[2], target_velocity[0], target_velocity[1], target_velocity[2])
            else:
                print('Direction: Negative')
                mega.start_moveto_async(0, 0, 0, target_velocity[0], target_velocity[1], target_velocity[2])
            
            # Check status, make sure to reach one end before starting other end
            _,xyz_state_str = mega.query_status()
            time.sleep(0.05)
            
            while xyz_state_str != 'Stopped':
                time.sleep(0.05)
                _,xyz_state_str = mega.query_status()
                
            forward ^= 1    
            
            print(f'Loop {current_loop} finished.')
            
            current_loop += 1
        
        print('Test finished.')
        
        print("Press Enter to continue ...")
        input()
except Exception as ex:
    print(ex)
    print("Press Enter to continue ...")
    input()