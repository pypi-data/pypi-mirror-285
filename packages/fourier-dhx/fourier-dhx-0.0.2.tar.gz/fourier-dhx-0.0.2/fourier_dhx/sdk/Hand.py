import sys
import os
import time
import socket
import platform
import logging
import struct, json

class Logger:
    STATE_OFF = 0x00
    STATE_ON = 0x01

    LEVEL_NONE = 0x00
    LEVEL_TRANCE = 0x01
    LEVEL_DEBUG = 0x02
    LEVEL_WARNING = 0x03
    LEVEL_ERROR = 0x04

    def __init__(self, enable_log_file=False):
        self.state = 0x01
        self.level = 0x00

        if enable_log_file:
            self.__init_log()

    def __init_log(self):

        LOG_FORMAT = "%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s"
        DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
        # INFO DEBUG WARNING ERROR CRITICAL
        LOG_LEVEL = logging.INFO

        project_path = os.path.dirname(os.path.abspath(__file__))  # 
        exe_file_path = project_path
        print(exe_file_path)

        sysstr = platform.system()

        if (sysstr == "Windows"):
            self.is_windows_flag = True
        else:
            self.is_windows_flag = False

        if self.is_windows_flag == True:
            path = exe_file_path + "\\log\\"
            name = str("{:02d}\{:02d}\\".format(time.localtime().tm_year, time.localtime().tm_mon))
        else:
            path = './log/'
            name = str("{:02d}/{:02d}/".format(time.localtime().tm_year, time.localtime().tm_mon))

        self.log_dir_path = path + name

        isExists = os.path.exists(self.log_dir_path)
        if not isExists:
            os.makedirs(self.log_dir_path)
            print('Log Created', self.log_dir_path)
        else:
            print('Log Already Existed', self.log_dir_path)
        self.log_name = str(
            "{:02d}_{:02d}_{:02d}_{:02d}.{:02d}.{:02d}".format(time.localtime().tm_year, time.localtime().tm_mon,
                                                               time.localtime().tm_mday, time.localtime().tm_hour,
                                                               time.localtime().tm_min, time.localtime().tm_sec))
        self.log_dir = self.log_dir_path + self.log_name + ".log"

        logging.basicConfig(filename=self.log_dir, level=LOG_LEVEL, format=LOG_FORMAT, datefmt=DATE_FORMAT)
        logging.log(logging.INFO, "\n\n########## The robot is starting !!! ##########\n\n\n")

    def print_log_file_debug(self, str_temp):
        logging.log(logging.DEBUG, str_temp)

    def print_log_file_info(self, str_temp):
        logging.log(logging.INFO, str_temp)

    def print_log_file_warning(self, str_temp):
        logging.log(logging.WARNING, str_temp)

    def print_log_file_error(self, str_temp):
        logging.log(logging.ERROR, str_temp)

    def print_log_file_critical(self, str_temp):
        logging.log(logging.CRITICAL, str_temp)

    # unit='us' 'ms' 's'
    def __time(self, unit='us'):
        if unit == 'ms' or unit == 'us':
            t = time.time()
            tmid = int(t * 1000000 % 1000000)
            tms = int(tmid / 1000 % 1000)
            t_get = time.localtime(t)
            if unit == 'us':
                tus = int(tmid % 1000)
                t_usr = [t_get.tm_year, t_get.tm_mon, t_get.tm_mday, t_get.tm_hour, t_get.tm_min, t_get.tm_sec, tms,
                         tus]
                t_usr_time_str = str(t_usr[0]).rjust(4) + '.' + str(t_usr[1]).rjust(2, '0') + '.' + str(t_usr[2]).rjust(
                    2, '0') + ' ' + str(t_usr[3]).rjust(2, '0') + ':' + str(t_usr[4]).rjust(2, '0') + ':' + str(
                    t_usr[5]).rjust(2, '0') + '.' + str(t_usr[6]).rjust(3, '0') + '.' + str(t_usr[7]).rjust(3, '0')
            else:
                t_usr = [t_get.tm_year, t_get.tm_mon, t_get.tm_mday, t_get.tm_hour, t_get.tm_min, t_get.tm_sec, tms]
                t_usr_time_str = str(t_usr[0]).rjust(4) + '.' + str(t_usr[1]).rjust(2, '0') + '.' + str(t_usr[2]).rjust(
                    2, '0') + ' ' + str(t_usr[3]).rjust(2, '0') + ':' + str(t_usr[4]).rjust(2, '0') + ':' + str(
                    t_usr[5]).rjust(2, '0') + '.' + str(t_usr[6]).rjust(3, '0')
            return '[' + t_usr_time_str + ']'
        else:
            now = '[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']'
        return now

    def print(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_line(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            print(*objects, sep=sep, end=end, file=file, flush=flush)


    def print_trace(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            if self.level <= Logger.LEVEL_TRANCE:
                now = self.__time()
                print(now, "\033[0m Info:   \033[0m", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_trace_debug(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            if self.level <= Logger.LEVEL_DEBUG:
                now = self.__time()
                print(now, "\033[0;31m Debug:  \033[0m", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_trace_warning(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            if self.level <= Logger.LEVEL_WARNING:
                now = self.__time()
                print(now, "\033[0;34;43m Warning:\033[0m", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_trace_error(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            if self.level <= Logger.LEVEL_ERROR:
                now = self.__time()
                print(now, "\033[0;32;41m Error:  \033[0m", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_file(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_file_trace(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.state == Logger.STATE_ON:
            print(*objects, sep=sep, end=end, file=file, flush=flush)

logger = Logger()

class FunctionResult:
    SUCCESS = 0
    FAIL = -1
    RUNNING = 1
    PREPARE = 2
    EXECUTE = 3
    NOT_EXECUTE = 4
    TIMEOUT = 5

class SocketResult:
    SOCKET_SEND_FAILED = -10001,
    SOCKET_SEND_SIZE_WRONG = -10002,
    SOCKET_RECEIVE_FAILED = -10003,
    SOCKET_RECEIVE_SIZE_WRONG = -10004,


class HandSocket:
    def __init__(self, ip, timeout = 0.1):
        self.ip = ip
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(timeout)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        
    def SendData(self, send_data, port):
        ret = self.s.sendto(send_data, (self.ip, port))
        if ret < 0:
            return SocketResult.SOCKET_SEND_FAILED
        if ret != len(send_data):
            return SocketResult.SOCKET_SEND_SIZE_WRONG
        return FunctionResult.SUCCESS
    
    def ReceiveData(self, size):
        try:
            data, address = self.s.recvfrom(size)
            return FunctionResult.SUCCESS, data, address
        except socket.timeout:
            return FunctionResult.TIMEOUT, None, None
        except:
            return FunctionResult.FAIL, None, None


class Hand:
    def __init__(self, ip, ctrl_port = 2333, comm_port = 2334, timeout = 0.1):
        self.ctrl_port = ctrl_port
        self.comm_port = comm_port
        self.s = HandSocket(ip, timeout)
    
    def Send_Messages(self, tx_messages):
        pass

    def Get_Messages(self, tx_messages):
        pass

    def clean_error(self):
        pass

    def save_config_flash(self):
        pass

    def reset(self):
        pass

    def calibration(self):
        pass

    def set_ip(self, ip):
        pass

    
    def get_ip(self):
        pass


    def set_current_limit(self, current_limit):
        pass
    
    def set_force_limit(self, force_limit):
        pass

    def set_speed(self, speed):
        pass
    
    def set_pos(self, pos):
        pass

    def set_angle(self, angle):
        pass

    def get_pos(self):
        pass

    def get_angle(self):
        pass

    def get_force(self):
        pass

    def get_current(self):
        pass

    def get_errorcode(self):
        pass

    def get_status(self):
        pass

    def get_temperature(self):
        pass






    
        
    