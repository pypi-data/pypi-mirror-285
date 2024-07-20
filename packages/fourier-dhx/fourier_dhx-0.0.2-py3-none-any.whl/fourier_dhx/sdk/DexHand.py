from .Hand import *

class DexHand(Hand):
    def __init__(self, ip, timeout=0.1):
        super().__init__(ip=ip, timeout=timeout)

    def Send_Messages(self, tx_messages, port):
        """
        send message using udp socket for dexhand
        
        Args : tx_messages, list of bytes

        Returns:
            FunctionResult in dexhand.py        
        """ 
        try:
            ret = self.s.SendData(tx_messages, port)
            if ret != FunctionResult.SUCCESS:
                raise Exception("SendData failed")
            return FunctionResult.SUCCESS
        except Exception as e:
            logger.print_trace_error("send_message failed: {}".format(e))
            return FunctionResult.FAIL
        

    def Get_Messages(self, tx_messages):
        """
        get message using udp socket from dexhand
        
        Args : tx_messages, list of bytes

        Returns:
            FunctionResult in dexhand.py        
        """ 
        try:
            ret = self.s.SendData(tx_messages, self.comm_port)
            rec_data = self.s.ReceiveData(1024)[1]
            if ret != FunctionResult.SUCCESS:
                raise Exception("SendData failed")
            return rec_data    
        except Exception as e:
            logger.print_trace_error("get_message failed: {}".format(e))
            return None 

    def string2int(self, val):
        ret_list = []
        str_data = str(val)
        str_data = str_data[2:]
        while True:
            index = str_data.find(' ')
            if index != -1:
                ele = int(str_data[:index])
                ret_list.append(int(ele))
                str_data = str_data[index+1:]
            else:
                return ret_list

    def string2float(self, val):
        ret_list = []
        str_data = str(val)
        str_data = str_data[2:]
        while True:
            index = str_data.find(' ')
            if index != -1:
                ele = float(str_data[:index])
                ret_list.append(float(ele))
                str_data = str_data[index+1:]
            else:
                return ret_list

    #### get meassage from dexhand ####
    def get_cnt(self):
        """
        Get encoder count params 

        Returns:
            6 fingers count params : [index, middle, ring, little, thumb-1, thumb-2]
        """
        tx_messages = struct.pack('>B', 0x01)
        data = self.Get_Messages(tx_messages)
        return self.string2int(data)


    def get_angle(self):
        """
        GetHandPostion, get joint motor move position params, not joint angle

        Returns:
            6 fingers motor position params: [index, middle, ring, little, thumb-1, thumb-2], defaut position is -0.5
        
        """
        tx_messages = struct.pack('>B', 0x02)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)
        
    
    def get_current(self):
        """
        GetHandCurrent, get hand motor current params
    
        Returns:
            6 fingers motor current params: [index, middle, ring, little, thumb-1, thumb-2]
    
        """
        tx_messages = struct.pack('>B', 0x04)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)


    def get_velocity(self):
        """
        GetHandVelocity, get hand motor velocity params

        Returns:
            6 fingers motor velocity params: [index, middle, ring, little, thumb-1, thumb-2]
        
        """
        tx_messages = struct.pack('>B', 0x03)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)


    def get_errorcode(self):
        """ 
        Get Errorcode of 6 fingers in dexhand
        0 : no error 
        1 : error in position control
        2 : error in velocity control
        3 : error in current control
        Returns:
            list of errorcode : [errorcode index, errorcode middle, ...]
        """ 
        tx_messages = struct.pack('>B', 0x06)
        data = self.Get_Messages(tx_messages)
        return self.string2int(data)


    def get_status(self):
        """
        GetHandStatus, get hand motor status

        Returns:
            6 fingers status params : [index, middle, ring, little, thumb-1, thumb-2], 
      
        """
        tx_messages = struct.pack('>B', 0x05)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)


    def get_pos_limited(self):
        """
        GetHandLimited (Position mode)
        get hand position limited bound, low is 0.0, high is 12.0
        
        Returns:
            6 fingers position high bound params : [index_low, index_high, middle_low, middle_high, ring_low, ring_high, little_low, little_high, thumb-1_low, thumb-1_high, thumb-2_low, thumb-2_high]   
        """
        tx_messages = struct.pack('>B', 0x0b)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)


    def get_velocity_limited(self):
        """
        GetHandLimited (Position mode),get hand position limited bound, low is 0.0, high is 12.0
        Returns:
            FunctionResult in dexhand.py        
        """
        tx_messages = struct.pack('>B', 0x0c)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)
    

    def get_current_limited(self):
        """
        GetHandLimited (Velocity mode), pget hand velocity limited bound, high bound is 10000.0

        Returns:
            6 fingers velocity params : [index, middle, ring, little, thumb-1, thumb-2], 
       
        """
        tx_messages = struct.pack('>B', 0x0d)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)
    

    def get_ip(self):
        """
        Broadcasting on port comm_port to get ip of dexhand
        Returns:
            string ip address
        """
        tx_messages = struct.pack('>B', 0x0f)
        s = HandSocket("192.168.137.255", timeout=0.1)
        s.s.bind(("", self.comm_port))
        s.SendData(tx_messages, self.comm_port)
        _, addr = s.ReceiveData(1024)[1], s.ReceiveData(1024)[2]   
        return addr[0]


    def get_firmware_version(self):
        """
        GetHandFirmwareVersion
        Returns:
            hand version string        
        """
        tx_messages = struct.pack('>B', 0x0e)
        return self.Get_Messages(tx_messages)


    def get_pos_pid(self):
        """ 
        get position mode pid default params : [p, i, d] 
        Returns:
            list of pid : [pid index, pid middle, ...]
        """ 
        tx_messages = struct.pack('>B', 0x08)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)


    def get_velocity_pid(self):
        """ 
        get velocity mode pid default params : [p, i, d] 
        Returns:
            list of pid : [pid index, pid middle, ...]
        """ 
        tx_messages = struct.pack('>B', 0x09)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)


    def get_current_pid(self):
        """ 
        get current mode pid default params : [p, i, d] 
        Returns:
            list of pid : [pid index, pid middle, ...]
        """ 
        tx_messages = struct.pack('>B', 0x0a)
        data = self.Get_Messages(tx_messages)
        return self.string2float(data)



    ### set parameters for dexhand ####

    def set_hand(self, name):
        """ 
        set new dexhand name string < 16byte 
        Returns:
            FunctionResult in dexhand.py 
        """ 
        tx_messages = struct.pack('>B16s', 0x21, name.encode())
        return self.Send_Messages(tx_messages, port=self.comm_port)


    def set_type(self, type = "right"):
        """ 
        set hand type 
        
        Args:
            string left / right 
        
        Returns:
            FunctionResult in dexhand.py 
        """ 
        if type == "right":
            tx_messages = struct.pack('>BB', 0x22, 0x01)
        elif type == "left":
            tx_messages = struct.pack('>BB', 0x22, 0x00)
        return self.Send_Messages(tx_messages, port=self.comm_port)


    def set_ip(self, ip):
        """ 
        set dexhand new ip adress : 192.xxx.xxx.xxx
        Returns:
            FunctionResult in dexhand.py 
        """ 
        try:
            parts = ip.split(".")
            s = HandSocket("192.168.137.255", timeout=0.1)
            s.s.bind(("", self.comm_port))
            tx_messages = struct.pack('>BBBBB', 0x23, *map(int, parts))    
            s.SendData(tx_messages, self.comm_port)
            return FunctionResult.SUCCESS
        except Exception as e:
            print(f"An error occurred: {e}")
            return FunctionResult.FAILURE


    def set_mac(self, mac):
        """ 
        set dexhand new mac (6 byte)
        Returns:
            FunctionResult in dexhand.py 
        """ 
        try:
            parts = mac.split(".")
            s = HandSocket("192.168.137.255", timeout=0.1)
            s.s.bind(("", self.comm_port))
            tx_messages = struct.pack('>BBBBB', 0x24, *map(int, parts))    
            s.SendData(tx_messages, self.comm_port)
            return FunctionResult.SUCCESS
        except Exception as e:
            print(f"An error occurred: {e}")
            return FunctionResult.FAILURE



    def set_SN(self, sn):
        """ 
        set dexhand new SN (6 byte)
        Returns:
            FunctionResult in dexhand.py 
        """ 
        try:
            parts = sn.split(".")
            s = HandSocket("192.168.137.255", timeout=0.1)
            s.s.bind(("", self.comm_port))
            tx_messages = struct.pack('>BBBBB', 0x25, *map(int, parts))    
            s.SendData(tx_messages, self.comm_port)
            return FunctionResult.SUCCESS
        except Exception as e:
            print(f"An error occurred: {e}")
            return FunctionResult.FAILURE

    def reset(self):
        """ 
        reset hand to factory defaults.

        Returns:
            FunctionResult in dexhand.py        
        """ 
        tx_messages = struct.pack('>B', 0x26)
        return self.Send_Messages(tx_messages, port=self.comm_port)


    def calibration(self):
        """
        HandCalibration, parameters reset to default
        Returns:
            FunctionResult in dexhand.py        
        """
        tx_messages = struct.pack('>BB', 0x01, 0x01)
        return self.Send_Messages(tx_messages, port=self.ctrl_port)



    def reset_pid_default(self):
        """ 
        set pid to default values.
        Returns:
            FunctionResult in dexhand.py        
        """ 
        tx_messages = struct.pack('>BB', 0x01, 0x0b)
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_angle(self, id, angle):
        """
        SetControlConfig (Position mode) : set Position move for one finger /all fingers 
        
        Limit:[0 - 12]
        Args:
            one finger :
            id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            angle Params : angle

            multi finger :
            id : 0 (default)
            angle Params : List [index angle, middle angle, ring angle, little angle, thumb-1 angle, thumb-2 angle]

        Returns:
            FunctionResult in dexhand.py  
        """
        if id != 0:
            tx_messages = struct.pack('>BBBBf', 0x01, 0x02, 0x00, int(id), float(angle))
        else:
            tx_messages = struct.pack('>BBBBffffff', 0x01, 0x11, 0x00, 0x00, float(angle[0]), float(angle[1]), float(angle[2]), float(angle[3]), float(angle[4]), float(angle[5]))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_velocity(self, id, velocity):
        """
        SetControlConfig (velocity mode) : set velocity move for one finger /all fingers 
        Limit:[0 - 10000]
        
        Args:
            one finger :
                one finger id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
                velocity Params : velocity     

            multi finger :
                id : 0 (default)
                velocity Params : List [index velocity, middle velocity, ring velocity, little velocity, thumb-1 velocity, thumb-2 velocity]

        Returns:
            FunctionResult in dexhand.py  
        """
        if id != 0:
            tx_messages = struct.pack('>BBBBf', 0x01, 0x03, 0x00, int(id), float(velocity))
        else:
            tx_messages = struct.pack('>BBBBffffff', 0x01, 0x12, 0x00, 0x00, float(velocity[0]), float(velocity[1]), float(velocity[2]), float(velocity[3]), float(velocity[4]), float(velocity[5]))

        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_current(self, id, current):
        """
        SetControlConfig (current mode) : set current move for one finger /all fingers 
        Limit:[0 - 1000]
        
        Args:
            one finger :
                id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
                current Params : current       
            
            multi finger :
                id : 0 (default)
                current Params : List [index current, middle current, ring current, little current, thumb-1 current, thumb-2 current]
                             
        Returns:
            FunctionResult in dexhand.py  
        """
        if id != 0:
            tx_messages = struct.pack('>BBBBf', 0x01, 0x04, 0x00, int(id), float(current))
        else:
            tx_messages = struct.pack('>BBBBffffff', 0x01, 0x13, 0x00, 0x00, float(current[0]), float(current[1]), float(current[2]), float(current[3]), float(current[4]), float(current[5]))

        return self.Send_Messages(tx_messages, port=self.ctrl_port)



    def set_pos_pid(self, id, pid):
        """
        SetPIDParams (Position mode) : set PID Position control config params 
        Limit:[0 - 12]
        
        Args:
            one finger id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            PID Params : [p, i, d]

        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBfff', 0x01, 0x05, 0x00, id, float(pid[0]), float(pid[1]), float(pid[2]))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_velocity_pid(self, id, pid):
        """
        SetPIDParams (velocity mode) : set PID velocity control config params 
        Limit:[0 - 10000]

        Args:
            one finger id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            PID Params : [p, i, d]
            
        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBfff', 0x01, 0x06, 0x00, id, float(pid[0]), float(pid[1]), float(pid[2]))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_current_pid(self, id, pid):
        """
        SetPIDParams (current mode) : set PID current control config params 
        Limit:[0 - 1000]

        Args:
            one finger id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            PID Params : [p, i, d]
            
        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBfff', 0x01, 0x07, 0x00, id, float(pid[0]), float(pid[1]), float(pid[2]))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_pos_limit(self, id, limit):
        """
        SetLimitedParams (Position mode) : set position control config params 
        Limit:[0 - 12]

        Args:
            one finger id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            limit : [angle_low, angle_high]

        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBff', 0x01, 0x08, 0x00, id, float(limit[0]),  float(limit[1]))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)



    def set_velocity_limit(self, id, limit):
        """
        SetLimitedParams (velocity mode) : set velocity control config params 
        Limit:[0 - 10000]

        Args:
            one finger id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            limit : max velocity

        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBf', 0x01, 0x09, 0x00, id, float(limit))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_current_limit(self, id, limit):
        """
        SetLimitedParams (Current mode) : set Current control config params 
        Limit:[0 - 1000]

        Args:
            one finger id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            limit : max current

        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBf', 0x01, 0x0a, 0x00, id, float(limit))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_pwm(self, target):
        """
        SetControlConfig (PWM mode) : set PWM move for one finger 
        Limit : [ -200 - 200 ]
        Args:
            List []: 6 fingers PWM Params 
            [index_pwm, middle_pwm, ring_pwm, little_pwm, thumb-1_pwm, thumb-2_pwm]
        
        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBffffff', 0x01, 0x14, 0x00, 0x00, float(target[0]), float(target[1]), float(target[2]), 
                                float(target[3]), float(target[4]), float(target[5]))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)


    def set_force(self, force):
        """
        Set force through voltage
        Args:
            List []: 6 fingers force Params 
            [index_force, middle_force, ring_force, little_force, thumb-1_force, thumb-2_force]
        
        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBffffff', 0x01, 0x15, 0x00, 0x00, float(force[0]), float(force[1]), float(force[2]), float(force[3]), float(force[4]), float(force[5]))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)
    


    def set_pd_control(self, id, target, w):
        """
        SetControlConfig (PD control mode)
        target limit : [0 - 12]
        Args:
            id : [1: index, 2: middle, 3: ring, 4: little, 5: thumb-1, 6: thumb-2]
            target : position 
            w : omega         
        Returns:
            FunctionResult in dexhand.py  
        """
        tx_messages = struct.pack('>BBBBff', 0x01, 0x21, 0x00, int(id), float(target), int(w))
        return self.Send_Messages(tx_messages, port=self.ctrl_port)



    def clean_error(self):
        """
        clean errors of current or  Electric Cylinder.

        Returns:
            FunctionResult in dexhand.py        
        """ 
        tx_messages = struct.pack('>BBBB', 0x01, 0xf1, 0x00, 0x00)
        return self.Send_Messages(tx_messages, port=self.ctrl_port)
