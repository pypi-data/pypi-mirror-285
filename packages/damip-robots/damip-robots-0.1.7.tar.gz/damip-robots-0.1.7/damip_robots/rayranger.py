"""
Created on 02 28 00:58:20 2024

@project: damip
@author : kaiwei.li
@company: Digitopia Robotics Ltd.,Co.
"""

import sys
import os
import time
import json
import serial
import logging

# Set logging level
logging.basicConfig(level=logging.DEBUG, format=':) %(asctime)s %(levelname)s: %(message)s')

class Robot:

    __uart_dev= "/dev/ttyUSB0"
    __baudrate = 115200 #(9600,19200,38400,57600,115200,921600)
    serial_delay = 1 #delay seconds for serial

    name = "RayRanger"

    # servo parameter
    param_servo_identity_h  = 6
    param_servo_identity_r  = 2
    param_servo_identity_l  = 8
    param_servo_ppid_value  = 16
    param_servo_initial_pos = 500
    param_servo_swing_range = 350
    param_servo_swing_speed = 600
    param_servo_swing_accel =  50

    # wheel parameter
    param_wheel_init_speed_l = 100
    param_wheel_init_speed_r = 100
    param_wheel_step_speed_l =  50
    param_wheel_step_speed_r =  50

    __BUS_FULL_VOL = 12.324

    # json messages

    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            Robot._instance = object.__new__(cls)
        return Robot._instance
    
    # serial open
    try:
        __ser = serial.Serial(__uart_dev, int(__baudrate), dsrdtr=None, timeout=2) # timeout
    except Exception as e:
        logging.debug(":) Open serial failed!")

    # Initial
    def __init__(self):
        self.name = "RayRanger"
        self.initial_serial()
        # self.initial_servos()
        self.initial_wheels()
    
    # Hello Robot
    def hello(self):
        return(':) Hello, I am a RayRanger robot, My name is ' + self.name + ".")

    # Initial servo by serial
    def initial_serial(self):
        self.__serial_buffer_clear()
        self.set_serial_echo(1)
        return True

    # Initial servo by serial
    def initial_servos(self):
        # pos
        self.set_head_postion(self.param_servo_initial_pos)
        self.set_rarm_postion(self.param_servo_initial_pos)
        self.set_larm_postion(self.param_servo_initial_pos)
        # pid
        self.set_servo_pid(self.param_servo_identity_h, self.param_servo_ppid_value)
        self.set_servo_pid(self.param_servo_identity_r, self.param_servo_ppid_value)
        self.set_servo_pid(self.param_servo_identity_l, self.param_servo_ppid_value)
        return True
    
    # Initial wheel by serial
    def initial_wheels(self):
        # spd
        self.set_move_speed(0, 0)
        return True
    
    # Open serial
    def serial_open(self):
        try:
            self.__ser.open()
            return True
        except Exception as e:
            logging.debug(":) Open serial failed!")
            return False
    
    # Close serial
    def serial_close(self):
        try:
            self.__ser.close()
            return True
        except Exception as e:
            logging.debug(":) Close serial failed!")
            return False
    
    # Check serial
    def serial_check(self):
        try:
            ser_status = self.__ser.is_open
            logging.debug(":) Check serial opened!")
            return ser_status
        except Exception as e:
            logging.debug(":) Check serial failed!")
        return False

    # serial query
    def serial_query(self, message, flag):
        try:
            # add \n
            cmd_msg = message + "\n"
            # send data
            cmd_len = self.__ser.write(cmd_msg.encode('UTF-8'))
            logging.debug(":) Send: " + str(cmd_msg.replace("\n", "")))
            # delay
            time.sleep(self.serial_delay)
            # receive data
            rcv_msg = self.__ser.readline().decode('UTF-8')
            logging.debug(":) Recv: "+ str(rcv_msg.replace("\n", "")))
            # check mismatch
            if str(cmd_msg) not in str(rcv_msg):
                logging.error("serial receive datas mismatch error!")
                self.__serial_buffer_clear()
                return False
            # read the return data
            if flag:
                # time.sleep(self.serial_delay)
                rcv_msg = self.__ser.readline().decode('UTF-8')
                logging.debug(":) Recv: " + str(rcv_msg.replace("\n", "")))
                return str(rcv_msg)
        except serial.SerialException as e:
            logging.error(f"SerialException: {e}")
            return False
        except serial.SerialTimeoutException as e:
            logging.error(f"SerialTimeoutException: {e}")
            return False
        finally:
            logging.debug(":) Serial query success.")
        return True
    
    # Set head postion by serial
    def set_head_postion(self, pos):
        sid = self.param_servo_identity_h
        spd = self.param_servo_swing_speed
        acc = self.param_servo_swing_accel
        cmd_head_pos = "{\"T\":505,\"id\":" + str(sid) + ",\"pos\":" + str(pos) + ",\"spd\":" + str(spd) + ",\"acc\":" + str(acc) + "}"
        self.serial_query(cmd_head_pos, False)
        return True

    # Shake head by serial
    def head_shake(self, value):
        if value < 0 or value > 1:
            logging.error(":) Head shake value not support, value should be in [0:1].")
            return False
        pos_m = self.param_servo_initial_pos
        pos_a = pos_m - self.param_servo_swing_range * value
        pos_b = pos_m + self.param_servo_swing_range * value
        self.set_head_postion(pos_a)
        self.set_head_postion(pos_b)
        self.set_head_postion(pos_m)
        return True

    # Set right arm postion by serial
    def set_rarm_postion(self, pos):
        sid = self.param_servo_identity_r
        spd = self.param_servo_swing_speed
        acc = self.param_servo_swing_accel
        cmd_arm_pos = "{\"T\":505,\"id\":" + str(sid) + ",\"pos\":" + str(pos) + ",\"spd\":" + str(spd) + ",\"acc\":" + str(acc) + "}"
        self.serial_query(cmd_arm_pos, False)
        return True

    # Shake right arm by serial
    def right_arm_shake(self, value):
        if value < 0 or value > 1:
            logging.error(":) Arm shake value not support, value should be in [0:1].")
            return False
        pos_m = self.param_servo_initial_pos
        pos_a = pos_m - self.param_servo_swing_range * value
        pos_b = pos_m + self.param_servo_swing_range * value
        self.set_rarm_postion(pos_a)
        self.set_rarm_postion(pos_b)
        self.set_rarm_postion(pos_m)
        return True

    # Set left arm postion by serial
    def set_larm_postion(self, pos):
        sid = self.param_servo_identity_l
        spd = self.param_servo_swing_speed
        acc = self.param_servo_swing_accel
        cmd_arm_pos = "{\"T\":505,\"id\":" + str(sid) + ",\"pos\":" + str(pos) + ",\"spd\":" + str(spd) + ",\"acc\":" + str(acc) + "}"
        self.serial_query(cmd_arm_pos, False)
        return True

    # Shake left arm by serial
    def left_arm_shake(self, value):
        if value < 0 or value > 1:
            logging.error(":) Left arm shake value not support, value should be in [0:1].")
            return False
        pos_m = self.param_servo_initial_pos
        pos_a = pos_m - self.param_servo_swing_range * value
        pos_b = pos_m + self.param_servo_swing_range * value
        self.set_larm_postion(pos_a)
        self.set_larm_postion(pos_b)
        self.set_larm_postion(pos_m)
        return True
    
    # Set servo P/PID by serial
    def set_servo_pid(self, id, pid):
        cmd_servo_pid = "{\"T\":503,\"id\":" + str(id) + ",\"p\":" + str(pid) + "}"
        self.serial_query(cmd_servo_pid, False)
        return True

    # Set serial echo mode by serial
    def set_serial_echo(self, mode):
        cmd_serial_echo = "{\"T\":143,\"cmd\":" + str(mode) + "}"
        self.serial_query(cmd_serial_echo, False)
        return True
    
    # Set speed by serial
    def set_move_speed(self, left_value, right_value):
        cmd_mov_speed = "{\"T\":11,\"L\":" + str(left_value) + ",\"R\":" + str(right_value) + "}"
        self.serial_query(cmd_mov_speed, False)
        return True
    
    # Manage move by serial
    def move_manage(self, value):
        if value < 0 or value > 1:
            logging.error(":) Move value not support, value should be in [0:1].")
            return False
        left_speed = self.param_wheel_init_speed_l + self.param_wheel_step_speed_l * value
        right_speed =self.param_wheel_init_speed_r + self.param_wheel_step_speed_r * value
        
        i = 0

        # lowly start
        for i in range(0,10,1): # 9~0 
            self.set_move_speed(int(left_speed * i/10), int(right_speed * i/10))
            time.sleep(self.serial_delay)
        
        # lowly stop
        for i in range(9,-1,-1): # 9~0 
            self.set_move_speed(int(left_speed * i/10), int(right_speed * i/10))
            time.sleep(self.serial_delay)
        
        # self.set_move_speed(0, 0)
        return True
    
    # Clear serial read buffer
    def __serial_buffer_clear(self):
        try:
            received_data = self.__ser.read_all().decode('UTF-8')
            received_data = self.__ser.read_all().decode('UTF-8')
            received_data = self.__ser.read_all().decode('UTF-8')
        except serial.SerialException as e:
            logging.error(f"SerialException: {e}")
            return False
        except serial.SerialTimeoutException as e:
            logging.error(f"SerialTimeoutException: {e}")
            return False
        finally:
            logging.debug(":) Cleared serial read buffer.")
        return True

    # Get base status
    def get_base_status(self):
        cmd_base_status = "{\"T\":130}"
        received_data = self.serial_query(cmd_base_status, True)        
        
        json_data = json.loads(received_data)
        bus_r = json_data['r']
        bus_p = json_data['p']
        bus_y = json_data['y']
        bus_v = json_data['v']

        logging.debug(":) base status:" + str(bus_r) + str(bus_p) + str(bus_y))

        bat_p = str(round((bus_v / self.__BUS_FULL_VOL) * 100, 2))
        logging.debug(":) base battery:" + str(bat_p) + "%")

        return str(bus_r), str(bus_p), str(bus_y), str(bat_p)

    # Get servo info
    def get_servo_status(self, id):
        cmd_servo_status = "{\"T\":506,\"id\":" + str(id) + "}"
        received_data = self.serial_query(cmd_servo_status, True)
        
        if len(received_data) != 0:
            json_data = json.loads(received_data)
            pos = str(json_data['pos'])
            volt = str(json_data['volt'])
            temp = str(json_data['temp'])
        else:
            pos = ""
            volt = ""
            temp = ""
            logging.error(":) Recv length is zero, bypass.")
        return pos, volt, temp

    # Get stance status
    def get_stance_status(self):
        cmd_get_stance = "{\"T\":126}"
        received_data = self.serial_query(cmd_get_stance, True)
        
        if len(received_data) != 0:
            json_data = json.loads(received_data)
            temp = str(json_data['temp'])
            roll = str(json_data['r'])
            pitch = str(json_data['p'])
            yaw = str(json_data['y'])
            acce_X = str(json_data['ax'])
            acce_Y = str(json_data['ay'])
            acce_Z = str(json_data['az'])
            gyro_X = str(json_data['gx'])
            gyro_Y = str(json_data['gy'])
            gyro_Z = str(json_data['gz'])
            magn_X = str(json_data['mx'])
            magn_Y = str(json_data['my'])
            magn_Z = str(json_data['mz'])
        else:
            temp = ""
            roll = ""
            pitch = ""
            yaw = ""
            acce_X = ""
            acce_Y = ""
            acce_Z = ""
            gyro_X = ""
            gyro_Y = ""
            gyro_Z = ""
            magn_X = ""
            magn_Y = ""
            magn_Z = ""
            logging.error(":) Recv length is zero, bypass.")
        logging.debug(":) acceleration info:" + str(acce_X) + "/" + str(acce_Y) + "/" + str(acce_Z))
        logging.debug(":) gyroscope info:" + str(gyro_X) + "/" + str(gyro_Y) + "/" + str(gyro_Z))
        logging.debug(":) magnetic field info:" + str(magn_X) + "/" + str(magn_Y) + "/" + str(magn_Z))
        return temp, roll, pitch, yaw, acce_X, acce_Y, acce_Z, gyro_X, gyro_Y, gyro_Z, magn_X, magn_Y, magn_Z

    # Get website url
    def website_url(self):
        url = 'https://digitopia.com.cn/rayranger/'
        return url

    # Speak english by espeak
    def speak_en(self, voice):
        cmd_data = 'espeak "' + str(voice) + '"'
        logging.debug(":) " + cmd_data)
        os.system(cmd_data)
        return True
