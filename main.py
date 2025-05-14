#######
# version: 20250220
#######

from machine import Pin, PWM
from L298N_motor import L298N
import time
import machine

# UART0 with TX on Pin 0 and RX on Pin 1
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(16), rx=machine.Pin(17))

ENA = PWM(Pin(0))        
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))

stick_deadzone = 31000
trigger_deadzone = 31000

left_motor = L298N(ENA, IN1, IN2) 
right_motor = L298N(ENB, IN4, IN3)


def translate(value, from_min, from_max, to_min, to_max):
    if value is None:
        return None
    mod_value = value
    from_range = from_max - from_min
    to_range = to_max - to_min
    scaled_value = float(mod_value - from_min) / float(from_range)
    final_value = to_min + (scaled_value * to_range)
    
    return int(-final_value)


while True:
    if uart.any():
        try:
            log_line = uart.readline().decode('utf-8').rstrip()
            data = eval(log_line)
            
            lsx = data.get('axisLX')
            rt = data.get('rightTrigger')
            lt = data.get('leftTrigger')
            
            fwd_drive_speed = abs(translate(rt, 0, 1024, 30000, 65535))
            rev_drive_speed = abs(translate(lt, 0, 1024, 30000, 65535))
            turn_speed = translate(lsx, -512, 512, -65534, 65534)
            
            if fwd_drive_speed is None:
                pass
                
            else:
                if (rev_drive_speed > trigger_deadzone):
                    
                    if turn_speed > 0:
   
                        left_motor.setSpeed(abs(rev_drive_speed - turn_speed))
                        right_motor.setSpeed(rev_drive_speed)
                        
                    else:
                        left_motor.setSpeed(rev_drive_speed)
                        right_motor.setSpeed(abs(rev_drive_speed - abs(turn_speed)))
                        
                    left_motor.backward()
                    right_motor.backward()
                    
                elif (fwd_drive_speed > trigger_deadzone):
                    
                    if turn_speed > 0:
   
                        left_motor.setSpeed(abs(fwd_drive_speed - turn_speed))
                        right_motor.setSpeed(fwd_drive_speed)
                        
                    else:
                        left_motor.setSpeed(fwd_drive_speed)
                        right_motor.setSpeed(abs(fwd_drive_speed - abs(turn_speed)))
                        
                    left_motor.forward()
                    right_motor.forward()
                    
                else:
                    left_motor.setSpeed(0)
                    right_motor.setSpeed(0)
                    left_motor.forward()
                    right_motor.forward()

        except (ValueError, SyntaxError):
            # print("Error: Invalid JSON data received")
            pass
    time.sleep(0.01)
