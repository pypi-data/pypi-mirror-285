###### 实体控制器---API 示例
###### 
###### Date: 2024-7-16
###### Modify : 2024-7-17
####

####
#-*-coding:utf-8 -*-
'''
Mirobot GCode通信协议
'''
import math
from collections.abc import Collection
from contextlib import AbstractContextManager
import logging
import os
from pathlib import Path
import re
import time
from typing import TextIO, BinaryIO
import math
from collections import namedtuple
from enum import Enum
from typing import NamedTuple
import sqlite3

import socket
import modbus_tk.modbus_tcp as modbus_tcp
import modbus_tk.defines as cst
from modbus_tk.modbus_rtu import RtuMaster
from modbus_tk.defines import WRITE_MULTIPLE_REGISTERS,WRITE_SINGLE_COIL,WRITE_MULTIPLE_COILS,WRITE_SINGLE_REGISTER
from modbus_tk.defines import READ_COILS,READ_INPUT_REGISTERS,READ_HOLDING_REGISTERS,READ_DISCRETE_INPUTS
import struct
from serial import Serial

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from .wlkata_mirobot_serial import WlkataMirobotSerial
from .wlkata_mirobot_status import MirobotStatus, MirobotAngles, MirobotCartesians
from .wlkata_mirobot_exceptions import ExitOnExceptionStreamHandler, MirobotError, MirobotAlarm, MirobotReset, MirobotAmbiguousPort, MirobotStatusError, MirobotResetFileError, MirobotVariableCommandError



# 判断操作系统的类型
# nt: 微软NT标准
os_is_nt = os.name == 'nt'
# Linux跟Mac都属于 posix 标准
# posix: 类Unix 操作系统的可移植API
os_is_posix = os.name == 'posix'

robot_logger=logging.getLogger("Motor-Driver")



class master_io():
    def __init__(self,host = None) -> None:
        super().__init__()
        if  host == None:

            self.host = socket.gethostname()
        else :
            self.host = host
        self._master_init()
        
    def _master_init(self):
        self.master = modbus_tcp.TcpMaster(host=self.host)
        self.master.set_timeout(5.0)


    # 获取所有的DI
    def get_All_DI(self,num :int =5):
        try:
            value = -1
            value = self.master.execute(1,cst.READ_HOLDING_REGISTERS,starting_address=73,quantity_of_x=10)
            return value
        except Exception as e:
            print(e) 

    # 获取第几个DI
    def get_DI(self,num :int =5):
        try:
            value = -1
            value = self.master.execute(1,cst.READ_HOLDING_REGISTERS,starting_address=73,quantity_of_x=10)
            return value[num]
        except Exception as e:
            print(e)   

    # 获取状态
    def get_status(self,):
        try:
            value = self.master.execute(1,cst.READ_HOLDING_REGISTERS,0,1)
            return value
        except Exception as e:
            print(e)   


    # 设置DO
    def set_DO(self,num = 0,value=0):
        try:
            value = [num,value,1]
            i = 91
            self.master.execute(1,cst.WRITE_MULTIPLE_REGISTERS,starting_address=i,output_value=value)
        except Exception as e:
            print(e)

    
    def set_motor(self,en=0):
        try:
            match en:
                case 0:
                    value = [0,0]
                case 1:
                    value = [1,0]
                case -1:
                    value = [0,1]
                case _:
                    value = [0,0]
            i = 86
            self.master.execute(1,cst.WRITE_MULTIPLE_REGISTERS,starting_address=i,output_value=value)
        except Exception as e:
            print(e)
    

      
    def get_reg_float(self,num :int =5):
        try:
            num = num 
            motion = self.master.execute(1,cst.READ_HOLDING_REGISTERS,starting_address=101,quantity_of_x=16)
            P =[]
            for i in range(0,16,2):
                P.append(self.int2float(motion[i],motion[i+1]))
            return P[num]
        except Exception as e:
            print(e)   


    def set_reg_float(self,num = 0,value=0):
        try:
            start_add = 101 + num*2
            out = []
            a = self.float_to_int16s(value)
            out.append(a[0])
            out.append(a[1])
     
            self.master.execute(1,cst.WRITE_MULTIPLE_REGISTERS,starting_address=start_add,output_value=out)
        except Exception as e:
            robot_logger.error(e,exc_info=True)


    def get_reg_int(self,):
        try:
            # 得到8个寄存器的值 整形控制寄存器
            motion = self.master.execute(1,cst.READ_HOLDING_REGISTERS,starting_address=162,quantity_of_x=8)

            return motion
        except Exception as e:
            print(e)   


    def set_reg_int(self,num = 0,value=0):
        # 设置整形寄存器的值
        try:
            start_add = 162 + num
            self.master.execute(1,cst.WRITE_SINGLE_REGISTER,starting_address=start_add,output_value=value)

        except Exception as e:
            robot_logger.error(e,exc_info=True)

    def get_button_reg(self,):
        try:
            # 得到10个寄存器的值 整形控制寄存器
            motion = self.master.execute(1,cst.READ_HOLDING_REGISTERS,starting_address=170,quantity_of_x=11)

            return motion
        except Exception as e:
            print(e)   


    def set_button_reg(self,num = 0,value=0):
        # 设置整形寄存器的值
        try:
            start_add = 170 + num
            self.master.execute(1,cst.WRITE_SINGLE_REGISTER,starting_address=start_add,output_value=value)

        except Exception as e:
            robot_logger.error(e,exc_info=True)




    def int2float(self,a,b):
        value=0
        try:
            z0=hex(a)[2:].zfill(4) #取0x后边的部分 右对齐 左补零
            z1=hex(b)[2:].zfill(4) #取0x后边的部分 右对齐 左补零
            z=z0+z1 #高字节在前 低字节在后
            value=struct.unpack('!f', bytes.fromhex(z))[0] #返回浮点数
            if value is None:
                return value
            if isinstance(value, float):
                # 精确到小数点后两位数
                return round(value , 2)
            else:
                return value
        except BaseException as e:
            print(e)
        return value

    def float_to_int16s(self,f):
        # 将浮点数打包成32位二进制数据
        b = struct.pack('f', f)
        # 将32位二进制数据拆分成两个16位二进制数据
        i1, i2 = struct.unpack('HH', b)
        return i2, i1
    

class WlkataMirobotTool(Enum):
    NO_TOOL = 0         # 没有工具
    SUCTION_CUP = 1     # 气泵吸头
    GRIPPER = 2         # 舵机爪子
    FLEXIBLE_CLAW = 3   # 三指柔爪

  
class WlkataMirobot(AbstractContextManager):
    '''Wlkata Python SDK'''
    # 气泵PWM值
    AIR_PUMP_OFF_PWM_VALUE = 0
    AIR_PUMP_BLOWING_PWM_VALUE = 500
    AIR_PUMP_SUCTION_PWM_VALUE = 1000
    # 电磁阀PWM值
    VALVE_OFF_PWM_VALUE = 65
    VALVE_ON_PWM_VALUE = 40 
    # 机械爪张开与闭合的PWM值
    GRIPPER_OPEN_PWM_VALUE = 40
    GRIPPER_CLOSE_PWM_VALUE = 60
    # 爪子间距范围(单位mm)
    GRIPPER_SPACING_MIN = 0.0
    GRIPPER_SPACING_MAX = 30.0
    # 爪子运动学参数定义(单位mm)
    GRIPPER_LINK_A = 9.5    # 舵机舵盘与中心线之间的距离
    GRIPPER_LINK_B = 18.0   # 连杆的长度
    GRIPPER_LINK_C = 3.0    # 平行爪向内缩的尺寸
    
    def __init__(self, hostname=None, debug=False, connection_type='serial', \
        autoconnect=True, autofindport=True, exclusive=True, \
        default_speed=2000, reset_file=None, wait_ok=False,id=None):
        '''初始化'''
          # 设置日志等级
        self.logger = logging.getLogger(__name__)
        if (debug):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)

        self.host = hostname
        self.device = None
        self.id = id
        
        '''创建从机对象'''
        self.Master = master_io(host=self.host)
        # self.Slave = Slaves_Driver()

        # 末端默认运动速度
        self.default_speed = default_speed
        # 默认是否等待回传数据'ok'
        self.wait_ok = wait_ok



        # 设置末端工具
        self.tool = WlkataMirobotTool.NO_TOOL
        # 自动连接
        ########################数据库存储状态############################
        filename = 'ktr6.db'
        filename_ = 'ktr4.db'
        file_dir = "/home/cat/gm/data/"
        # # 使用系统分隔符连接目录和文件
        # file_path = os.sep.join([file_dir, filename])
        # 使用路径模块连接
        file_path = os.path.join(file_dir, filename)
        file_path_ = os.path.join(file_dir, filename_)
        self.conn = sqlite3.connect(file_path,timeout=10,check_same_thread=False)
        self.conn_  = sqlite3.connect(file_path_,timeout=10,check_same_thread=False)

        self.status = MirobotStatus()

    def __exit__(self, *exc):
        """ Magic method for contextManagers """
        pass

    def Wait_Idle(self,):
        try:
            # time.sleep(1)
            if self.id == 1:
                c = self.conn.cursor()
                state_o = c.execute(f'''SELECT STATE from Robot_state''')
                state = state_o.fetchall()
                while state[0][0] != "Idle":
                    state_o = c.execute(f'''SELECT STATE from Robot_state''')
                    state = state_o.fetchall()
                    time.sleep(0.2)
            
            elif self.id == 2:
                c = self.conn_.cursor()
                state_o = c.execute(f'''SELECT STATE from Robot_state2''')
                state = state_o.fetchall()
                while state[0][0] != "Idle":
                    state_o = c.execute(f'''SELECT STATE from Robot_state2''')
                    state = state_o.fetchall()
                    time.sleep(0.2)
            return True

        except Exception as e:
            print(f"Wait_Idle error is {e}")


    def send_msg(self, data, var_command=False, disable_debug=False, terminator=os.linesep, wait_ok=None, wait_idle=False):
        '''给Mirobot发送指令'''
        try :
            if self.id == 1:
                c = self.conn.cursor()
                c.execute(f'''UPDATE Robot_state set GCODE ='{data}' where ID=1''')
                c.execute(f"UPDATE Robot_state set EN = 1 where ID=1")

                # c.execute(f'''UPDATE Robot_state set GCODE ='{data}' where ID={self.id}''')
                # # c.execute("UPDATE Robot_state set EN = 1 where ID={robot_id}")
                # c.execute(f"UPDATE Robot_state set EN = 1 where ID={self.id}")
                self.conn.commit()
                if wait_idle:
                    self.Wait_Idle()
            
            elif self.id == 2:
                c = self.conn_.cursor()
                c.execute(f'''UPDATE Robot_state2 set GCODE ='{data}' where ID=1''')
                c.execute(f"UPDATE Robot_state2 set EN = 1 where ID=1")
                self.conn_.commit()
                if wait_idle:
                    self.Wait_Idle()


        except Exception as e:
            print(e)

    

    def home(self, has_slider=False):
        '''机械臂Homing'''
        if has_slider:
            return self.home_7axis()
        else:
            print("home")
            return self.home_6axis()
    
    def home_slider(self):
        '''滑台单独Homing'''
        return self.home_1axis(7)
    
    def home_1axis(self, axis_id):
        '''单轴Homing'''
        if not isinstance(axis_id, int) or not (axis_id >= 1 and axis_id <= 7):
            return False
        msg = f'$h{axis_id}'
        return self.send_msg(msg, wait_ok=False, wait_idle=True)
    
    def home_6axis(self):
        '''六轴Homing'''
        msg = f'$h'
        return self.send_msg(msg, wait_ok=False, wait_idle=True)
    
    def home_6axis_in_turn(self):
        '''六轴Homing, 各关节依次Homing'''
        msg = f'$hh'
        return self.send_msg(msg, wait_ok=False, wait_idle=True)
    
    def stop(self):
        '''6轴暂停'''
        msg = f'!'
        self.send_msg(msg, wait_ok=False, wait_idle=False)
        time.sleep(0.5)
        msg = f'%'
        return self.send_msg(msg, wait_ok=False, wait_idle=False)
    
    def home_7axis(self):
        '''七轴Homing(本体 + 滑台)'''
        msg = f'$h0'
        return self.send_msg(msg, wait_ok=False, wait_idle=True)
        
    def unlock_all_axis(self):
        '''解锁各轴锁定状态'''
        msg = 'M50'
        return self.send_msg(msg, wait_ok=True, wait_idle=True)
        
    def go_to_zero(self):
        '''回零-运动到名义上的各轴零点'''
        msg = 'M21 G90 G00 X0 Y0 Z0 A0 B0 C0 F2000'
        return self.send_msg(msg, wait_ok=True, wait_idle=True)
    
    def set_speed(self, speed):
        '''设置转速'''
        # 转换为整数
        speed = int(speed)
        # 检查数值范围是否合法
        if speed <= 0 or speed > 3000:
            self.logger.error((f"Illegal movement speed {speed}"))
            return False
        # 发送指令
        msg = f'F{speed}'
        return self.send_msg(msg, wait_ok=None, wait_idle=None)
    
    def set_hard_limit(self, enable):
        '''
        开启硬件限位
        '''
        msg = f'$21={int(enable)}'
        return self.send_msg(msg, var_command=True, wait_ok=None)

    def set_soft_limit(self, enable):
        '''开启软限位
        注: 请谨慎使用
          '''
        msg = f'$20={int(enable)}'
        return self.send_msg(msg, var_command=True, wait_ok=None)
    
    def format_float_value(self, value):
        if value is None:
            return value
        if isinstance(value, float):
            # 精确到小数点后两位数
            return round(value , 2)
        else:
            return value
    
    def generate_args_string(self, instruction, pairings):
        '''生成参数字符'''
        args = [f'{arg_key}{self.format_float_value(value)}' for arg_key, value in pairings.items() if value is not None]

        return ' '.join([instruction] + args)


    def set_joint_angle(self, joint_angles=None,P=None, speed=None, is_relative=False, wait_ok=None):
        '''
        设置机械臂关节的角度
        joint_angles 目标关节角度字典, key是关节的ID号, value是角度(单位°)
            举例: {1:45.0, 2:-30.0}
        '''
        if joint_angles is not None:
            for joint_i in range(1, 8):
                # 补齐缺失的角度
                if joint_i not in joint_angles:
                    joint_angles[joint_i] = None
        elif P is not None:
            joint_angles = {1:P[0],2:P[1],3:P[2],4:P[3],5:P[4],6:P[5],7:0}
        else :
            for joint_i in range(1, 8):
                joint_angles[joint_i] = None

        return self.go_to_axis(x=joint_angles[1], y=joint_angles[2], z=joint_angles[3], a=joint_angles[4], \
            b=joint_angles[5], c=joint_angles[6], d=joint_angles[7], is_relative=is_relative, speed=speed, wait_ok=wait_ok)

    def go_to_axis(self, x=None, y=None, z=None, a=None, b=None, c=None, d=None, speed=None, is_relative=False, wait_ok=True):
        '''设置关节角度/位置'''
        instruction = 'M21 G90'  # X{x} Y{y} Z{z} A{a} B{b} C{c} F{speed}
        if is_relative:
            instruction = 'M21 G91'
        if not speed:
            speed = self.default_speed
        if speed:
            speed = int(speed)

        pairings = {'X': x, 'Y': y, 'Z': z, 'A': a, 'B': b, 'C': c, 'D': d, 'F': speed}
        msg = self.generate_args_string(instruction, pairings)

        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)

    def set_slider_posi(self, d, speed=None, is_relative=False, wait_ok=True):
        '''设置滑台位置, 单位mm'''
        if not is_relative:
            return 	self.go_to_axis(d=d,
                                    speed=speed, wait_ok=wait_ok)
        else:
            return 	self.go_to_axis(d=d,
                                    speed=speed, wait_ok=wait_ok, is_relative=True)
    
    def set_conveyor_range(self, d_min=-30000, d_max=30000):
        '''设置传送带的位移范围'''
        # 约束范围
        if d_min < -30000:
            d_min = -30000
        if d_max > 30000:
            d_min = 30000
        # 设置传动带负方向最大行程
        msg = f"$143={d_min}"
        self.send_msg(msg, wait_ok=True, wait_idle=True)
        # 设置传送带正方向最大行程
        msg = f'$133={d_max}'
        self.send_msg(msg, wait_ok=True, wait_idle=True)

    def set_conveyor_posi(self, d, speed=None, is_relative=False, wait_ok=True):
        '''设置传送带位置, 单位mm'''
        if not is_relative:
            return 	self.go_to_axis(d=d,
                                    speed=speed, wait_ok=wait_ok)
        else:
            return 	self.go_to_axis(d=d,
                                    speed=speed, wait_ok=wait_ok, is_relative=True)
 
    def set_tool_pose(self, x=None, y=None, z=None, roll=None, pitch=None, yaw=None, P = None,mode='p2p', speed=None, is_relative=False, wait_ok=True):
        '''设置工具位姿'''

        if P is not None:
            x = P[6]
            y = P[7]
            z = P[8]
            roll = P[9]
            pitch = P[10]
            yaw = P[11]

        if mode == "p2p":
            # 点控模式 Point To Point
            self.p2p_interpolation(x=x, y=y, z=z, a=roll, b=pitch, c=yaw, speed=speed, is_relative=is_relative, wait_ok=wait_ok)
        elif mode == "linear":
            # 直线插补 Linera Interpolation
            self.linear_interpolation(x=x, y=y, z=z, a=roll, b=pitch, c=yaw, speed=speed,is_relative=is_relative, wait_ok=wait_ok)
        else:
            # 默认是点到点
            self.p2p_interpolation(x=x, y=y, z=z, a=roll, b=pitch, c=yaw, speed=speed, wait_ok=wait_ok)


    def p2p_interpolation(self, x=None, y=None, z=None, a=None, b=None, c=None, speed=None, is_relative=False, wait_ok=None):
        '''点到点插补'''
        instruction = 'M20 G90 G0'  # X{x} Y{y} Z{z} A{a} B{b} C{c} F{speed}
        if is_relative:
            instruction = 'M20 G91 G0'

        if not speed:
            speed = self.default_speed
        if speed:
            speed = int(speed)

        pairings = {'X': x, 'Y': y, 'Z': z, 'A': a, 'B': b, 'C': c, 'F': speed}
        msg = self.generate_args_string(instruction, pairings)

        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
    
    def linear_interpolation(self,P1,speed=None, is_relative=False, wait_ok=None):
        self.linear_interpolation_o( x=P1[6], y=P1[7], z=P1[8], a=P1[9], b=P1[10], c=P1[11],
                            speed=speed,is_relative=is_relative,wait_ok=wait_ok)
    
    def linear_interpolation_o(self, x=None, y=None, z=None, a=None, b=None, c=None, speed=None, is_relative=False, wait_ok=None):
        '''直线插补'''
        instruction = 'M20 G90 G1'  # X{x} Y{y} Z{z} A{a} B{b} C{c} F{speed}
        if is_relative:
            instruction = 'M20 G91 G1'
        if not speed:
            speed = self.default_speed
        if speed:
            speed = int(speed)

        pairings = {'X': x, 'Y': y, 'Z': z, 'A': a, 'B': b, 'C': c, 'F': speed}
        msg = self.generate_args_string(instruction, pairings)
        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
    
    def circular_interpolation(self, ex, ey, radius, is_cw=True, speed=None, wait_ok=None):
        '''圆弧插补
          在XY平面上, 从当前点运动到相对坐标(ex, ey).半径为radius
        `is_cw`决定圆弧是顺时针还是逆时针.
        '''
        # 判断是否合法
        distance = math.sqrt(ex**2 + ey**2)
        if distance > (radius * 2):
            self.logger.error(f'circular interpolation error, target posi is too far')
            return False

        instruction = None
        if is_cw:
            instruction = 'M20 G91 G02'
        else:
            instruction = 'M20 G91 G03'
        
        pairings = {'X': ex, 'Y': ey, 'R': radius, 'F': speed}
        msg = self.generate_args_string(instruction, pairings)
        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
    
    def set_door_lift_distance(self, lift_distance):
        '''设置门式轨迹规划抬起的高度'''
        msg = f"$49={lift_distance}"
        return self.send_msg(msg, wait_ok=True, wait_idle=True)

    def door_interpolation(self, x=None, y=None, z=None, a=None, b=None, c=None, speed=None, is_relative=False, wait_ok=None):
        '''门式插补'''
        instruction = 'M20 G90 G05'  # X{x} Y{y} Z{z} A{a} B{b} C{c} F{speed}
        if is_relative:
            instruction = 'M20 G91 G05'
        
        if not speed:
            speed = self.default_speed
        if speed:
            speed = int(speed)

        pairings = {'X': x, 'Y': y, 'Z': z, 'A': a, 'B': b, 'C': c, 'F': speed}
        msg = self.generate_args_string(instruction, pairings)
        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)

    def set_tool_type(self, tool, wait_ok=True):
        '''选择工具类型'''
        self.tool = tool
        self.logger.info(f"set tool {tool.name}")
        # 获取工具的ID
        tool_id = tool.value

        if type(tool_id) != int or not (tool_id >= 0 and tool_id <= 3):
            self.logger.error(f"Unkown tool id {tool_id}")
            return False
        msg = f'$50={tool_id}'
        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
    
    def set_tool_offset(self, offset_x, offset_y, offset_z, wait_ok=True):
        '''设置工具坐标系的偏移量'''
        # 设置末端x轴偏移量
        msg = f"$46={offset_x}"
        ret_x = self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
        # 设置末端y轴偏移量
        msg = f"$47={offset_y}"
        ret_y = self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
        # 设置末端z轴偏移量
        msg = f"$48={offset_z}"
        ret_z = self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
        return ret_x and ret_y and ret_z
    
    def pump_suction(self):
        '''气泵吸气'''
        self.set_air_pump(self.AIR_PUMP_SUCTION_PWM_VALUE) 
    
    def pump_blowing(self):
        '''气泵吹气'''
        self.set_air_pump(self.AIR_PUMP_BLOWING_PWM_VALUE)
    
    def pump_on(self, is_suction=True):
        """
        气泵开启, 吸气/吹气
        """
        if is_suction:
            self.set_air_pump(self.AIR_PUMP_SUCTION_PWM_VALUE)
        else:
            self.set_air_pump(self.AIR_PUMP_BLOWING_PWM_VALUE) 
    
    def pump_off(self):
        """
        气泵关闭, 电磁阀开启, 放气
        """
        self.set_air_pump(self.AIR_PUMP_OFF_PWM_VALUE, wait_ok=False)
        self.set_valve(self.VALVE_ON_PWM_VALUE, wait_ok=False)
        time.sleep(1)
        self.set_valve(self.VALVE_OFF_PWM_VALUE, wait_ok=False)
        
    def set_air_pump(self, pwm, wait_ok=None):
        '''设置气泵的PWM信号'''
        if pwm not in self.pump_pwm_values:
            self.logger.exception(ValueError(f'pwm must be one of these values: {self.pump_pwm_values}. Was given {pwm}.'))
            pwm = self.AIR_PUMP_OFF_PWM_VALUE
        msg = f'M3S{pwm}'
        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)

    def set_valve(self, pwm, wait_ok=None):
        '''设置电磁阀的PWM'''
        if pwm not in self.valve_pwm_values:
            self.logger.exception(ValueError(f'pwm must be one of these values: {self.valve_pwm_values}. Was given {pwm}.'))
            pwm = self.VALVE_OFF_PWM_VALUE
        msg = f'M4E{pwm}'
        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
    
    def gripper_inverse_kinematic(self, spacing_mm):
        '''爪子逆向运动学'''
        d1 = (spacing_mm / 2) + self.GRIPPER_LINK_C - self.GRIPPER_LINK_A
        theta = math.degrees(math.asin(d1/self.GRIPPER_LINK_B))
        return theta
    
    def set_gripper_spacing(self, spacing_mm):
        '''设置爪子间距'''
        # 判断是否是合法的spacing约束下
        spacing_mm = max(self.GRIPPER_SPACING_MIN, min(self.GRIPPER_SPACING_MAX, spacing_mm))
        # 逆向运动学
        theta = self.gripper_inverse_kinematic(spacing_mm)
        angle_min = self.gripper_inverse_kinematic(self.GRIPPER_SPACING_MIN)
        angle_max = self.gripper_inverse_kinematic(self.GRIPPER_SPACING_MAX)
        # 旋转角度转换为PWM值
        ratio = ((theta - angle_min) / (angle_max - angle_min))
        pwm = int(self.GRIPPER_CLOSE_PWM_VALUE + ratio * (self.GRIPPER_OPEN_PWM_VALUE - self.GRIPPER_CLOSE_PWM_VALUE))
        # print(f"爪子逆向运动学 角度:{theta}  angle_min: {angle_min} angle_max: {angle_max} PWM: {pwm}")
        # 设置爪子的PWM
        self.set_gripper(pwm)
        
    def gripper_open(self):
        '''爪子开启'''
        self.set_gripper(self.GRIPPER_OPEN_PWM_VALUE)
    
    def gripper_close(self):
        '''爪子闭合'''
        self.set_gripper(self.GRIPPER_CLOSE_PWM_VALUE)
    
    def set_gripper(self, pwm, wait_ok=None):
        '''设置爪子的PWM'''
        # 类型约束
        if isinstance(pwm, bool):
            if pwm == True:
                pwm = self.GRIPPER_CLOSE_PWM_VALUE
            else:
                pwm = self.GRIPPER_OPEN_PWM_VALUE
        pwm = int(pwm)
        # 数值约束
        lowerb = min([self.GRIPPER_OPEN_PWM_VALUE, self.GRIPPER_CLOSE_PWM_VALUE])
        upperb = max([self.GRIPPER_OPEN_PWM_VALUE, self.GRIPPER_CLOSE_PWM_VALUE])
        pwm = max(lowerb, min(upperb, pwm))
        
        msg = f'M3S{pwm}'
        return self.send_msg(msg, wait_ok=wait_ok, wait_idle=True)
    
    def start_calibration(self, wait_ok=None):
        '''开始进行机械臂标定'''
        instruction = 'M40'
        return self.send_msg(instruction, wait_ok=wait_ok)

    def finish_calibration(self, wait_ok=None):
        '''完成机械臂标定'''
        instruction = 'M41'
        return self.send_msg(instruction, wait_ok=wait_ok)

    def reset_configuration(self, reset_file=None, wait_ok=None):
        '''重置机械臂的配置'''
        output = {}

        def send_each_line(file_lines):
            nonlocal output
            for line in file_lines:
                output[line] = self.send_msg(line, var_command=True, wait_ok=wait_ok)

        reset_file = reset_file if reset_file else self.reset_file

        if isinstance(reset_file, str) and '\n' in reset_file or \
           isinstance(reset_file, bytes) and b'\n' in reset_file:
            # if we find that we have a string and it contains new lines,
            send_each_line(reset_file.splitlines())

        elif isinstance(reset_file, (str, Path)):
            if not os.path.exists(reset_file):
                self.logger.exception(MirobotResetFileError("Reset file not found or reachable: {reset_file}"))
            with open(reset_file, 'r') as f:
                send_each_line(f.readlines())

        elif isinstance(reset_file, Collection) and not isinstance(reset_file, str):
            send_each_line(reset_file)

        elif isinstance(reset_file, (TextIO, BinaryIO)):
            send_each_line(reset_file.readlines())

        else:
            self.logger.exception(MirobotResetFileError(f"Unable to handle reset file of type: {type(reset_file)}"))

        return output


