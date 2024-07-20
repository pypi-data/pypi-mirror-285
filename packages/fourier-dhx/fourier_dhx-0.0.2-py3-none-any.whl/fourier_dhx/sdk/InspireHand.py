from .Hand import *

class InspireHand(Hand):
    def __init__(self, ip, timeout=0.1):
        super().__init__(ip, timeout = timeout)
        self.kSend_Frame_Head1 = 0xEB
        self.kSend_Frame_Head2 = 0x90
        self.ID = 1
        self.kRcv_Frame_Head1 = 0x90
        self.kRcv_Frame_Head2 = 0xEB
        self.kCmd_Handg3_Read = 0x11  
        self.kCmd_Handg3_Write = 0x12


    def Send_Messages(self, tx_messages):
        """
        send message using udp socket for inspire hand
        
        Args : tx_messages, list of bytes

        Returns:
            FunctionResult in dexhand.py        
        """ 
        try:
            ret = self.s.SendData(tx_messages, self.ctrl_port)
            rec_data = self.s.ReceiveData(1024)[1]
            if ret != FunctionResult.SUCCESS:
                raise Exception("SendData failed")
            if rec_data is None or tx_messages[4:6] != rec_data[4:6]:
                raise Exception("ReceiveData failed")
            return FunctionResult.SUCCESS
        except Exception as e:
            logger.print_trace_error("send_message failed: {}".format(e))
            return FunctionResult.FAIL


    def Get_Messages(self, tx_messages, type = "6short"):
        """
        get message using udp socket from inspire hand
        
        Args : tx_messages, list of bytes

        Returns:
            FunctionResult in dexhand.py        
        """ 
        try:
            ret = self.s.SendData(tx_messages, self.ctrl_port)
            rec_data = self.s.ReceiveData(1024)[1]
            if ret != FunctionResult.SUCCESS:
                raise Exception("SendData failed")
            if rec_data is None or tx_messages[4:6] != rec_data[4:6]:
                raise Exception("ReceiveData failed")
            integers = []
            if type == "6short":
                for i in range(7, len(rec_data)-1, 2):  
                    value = struct.unpack_from('<h', rec_data, i)[0]
                    integers.append(value)
            elif type == "6byte":
                for i in range(7, len(rec_data)-1, 1):  
                    value = struct.unpack_from('<B', rec_data, i)[0]
                    integers.append(value)
            else:
                raise ValueError("Unsupported type: {}".format(type))
            return integers    
        except Exception as e:
            logger.print_trace_error("get_message failed: {}".format(e))
            return None


    def set_ip(self, ip):
        """
        set ip of current or hand
        
        Args : New ip

        Returns:
            FunctionResult in dexhand.py        
        """ 
        data = {
            "method": "SET", "reqTarget" : "/config", "property":"", 
            "static_IP": ip
        }
        json_str = json.dumps(data)
        self.s.SendData(str.encode(json_str), self.comm_port)
        try:
            rec_data = self.s.ReceiveData(1024)[1]
            json_ = json.loads(rec_data.decode("utf-8"))
            if json_["status"] == "OK":
                return FunctionResult.SUCCESS
        except:
            return FunctionResult.FAIL

    def get_ip(self):
        """
        Broadcasting on port comm_port to get ip of inspirehand
        Returns:
            string ip address
        """
        message = b"get ip"
        s = HandSocket("192.168.137.255", timeout=0.1)
        s.s.bind(("", self.comm_port))
        s.SendData(message, self.comm_port)
        data, addr = s.ReceiveData(1024)[1], s.ReceiveData(1024)[2]   
        print(f"Received message from {addr}: {data}")
        return addr


    def clean_error(self):
        """
        clean errors of current or  Electric Cylinder.

        Returns:
            FunctionResult in dexhand.py        
        """
        tx_messages = struct.pack('<BBBBBBBB', 
                          self.kSend_Frame_Head1, 
                          self.kSend_Frame_Head2, 
                          int(self.ID), 
                          0x04, 
                          self.kCmd_Handg3_Write, 
                          0xEC, 
                          0x03,
                          0x01)
        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)  
        return self.Send_Messages(tx_messages)
        

    def save_config_flash(self):
        """
        save parameters to flash.

        Returns:
            FunctionResult in dexhand.py        
        """ 
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Write, 
                    0xED, 
                    0x03,
                    0x01)
        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)  
        return self.Send_Messages(tx_messages)


    def reset(self):
        """
        reset to factory defaults.

        Returns:
            FunctionResult in dexhand.py        
        """ 
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Write, 
                    0xEE, 
                    0x03,
                    0x01)
        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)  
        return self.Send_Messages(tx_messages)


    def calibration(self):
        """
        Force sensor calibration, continue for about 10 seconds.

        Returns:
            FunctionResult in dexhand.py        
        """  
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Write, 
                    0xF1, 
                    0x03,
                    0x01)
        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)  
        return self.Send_Messages(tx_messages)

    

    def set_current_limit(self, current_limit):
        """
        Set the default current limit information when starting.
        
        Args:
            List : [current little finger, current ring finger, ..]
            Limit : 0-1500 mA
        
        Returns:
            FunctionResult in dexhand.py
            
        """  
        tx_messages = struct.pack('<BBBBBBBhhhhhh', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x0F, 
                    self.kCmd_Handg3_Write, 
                    0xFC, 
                    0x03, 
                    int(current_limit[0]),
                    int(current_limit[1]),
                    int(current_limit[2]),
                    int(current_limit[3]),
                    int(current_limit[4]), 
                    int(current_limit[5]))

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Send_Messages(tx_messages)


    # [0 -1000]
    def set_default_speed(self, default_speed):
        """
        Set the default speed limit information when starting.
        
        Args:
            List : [default speed little finger, default speed ring finger, ..]
            Limit : 0-1000
        
        Returns:
            FunctionResult in dexhand.py
            
        """  
        tx_messages = struct.pack('<BBBBBBBhhhhhh', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x0F, 
                    self.kCmd_Handg3_Write, 
                    0x08, 
                    0x04, 
                    int(default_speed[0]),
                    int(default_speed[1]),
                    int(default_speed[2]),
                    int(default_speed[3]),
                    int(default_speed[4]), 
                    int(default_speed[5]))

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Send_Messages(tx_messages)

 
    def set_default_force(self, default_force):
        """
        Set the default force limit information when starting.
        
        Args:
            List : [default force little finger, default force ring finger, ..]
            Limit : 0-1000
        
        Returns:
            FunctionResult in dexhand.py
            
        """  
        tx_messages = struct.pack('<BBBBBBBhhhhhh', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x0F, 
                    self.kCmd_Handg3_Write, 
                    0x14, 
                    0x04, 
                    int(default_force[0]),
                    int(default_force[1]),
                    int(default_force[2]),
                    int(default_force[3]),
                    int(default_force[4]), 
                    int(default_force[5]))

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Send_Messages(tx_messages)


    def set_pos(self, pos):
        """
        Set the position while moving fingers.
        
        Args:
            List : [position little finger, position ring finger, ..]
            Limit : 0-2000 / -1 : no move
        
        Returns:
            FunctionResult in dexhand.py
            
        """  
        tx_messages = struct.pack('<BBBBBBBhhhhhh', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x0F, 
                    self.kCmd_Handg3_Write, 
                    0xC2, 
                    0x05, 
                    int(pos[0]),
                    int(pos[1]),
                    int(pos[2]),
                    int(pos[3]),
                    int(pos[4]), 
                    int(pos[5]))

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Send_Messages(tx_messages)

 
    def set_angle(self, angle):
        """
        Set the angle while moving fingers.
        
        Args:
            List : [angle little finger, angle ring finger, ..]
            Limit : 0-1000 / -1 : no move
        
        Returns:
            FunctionResult in dexhand.py
            
        """  
        tx_messages = struct.pack('<BBBBBBBhhhhhh', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x0F, 
                    self.kCmd_Handg3_Write, 
                    0xCE, 
                    0x05, 
                    int(angle[0]),
                    int(angle[1]),
                    int(angle[2]),
                    int(angle[3]),
                    int(angle[4]), 
                    int(angle[5]))

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Send_Messages(tx_messages)


    def set_force_limit(self, force):
        """
        Set the force limit information while moving fingers.
        
        Args:
            List : [force little finger, force ring finger, ..]
            Limit : 0-1000
        
        Returns:
            FunctionResult in dexhand.py
            
        """  
        tx_messages = struct.pack('<BBBBBBBhhhhhh', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x0F, 
                    self.kCmd_Handg3_Write, 
                    0xDA, 
                    0x05, 
                    int(force[0]),
                    int(force[1]),
                    int(force[2]),
                    int(force[3]),
                    int(force[4]), 
                    int(force[5]))

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Send_Messages(tx_messages)


    # [0-1000]
    def set_speed(self, speed):
        """
        Set the speed status information while moving fingers.
        
        Args:
            List : [speed little finger, speed ring finger, ..]
            Limit : 0-1000
        
        Returns:
            FunctionResult in dexhand.py
            
        """  
        tx_messages = struct.pack('<BBBBBBBhhhhhh', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x0F, 
                    self.kCmd_Handg3_Write, 
                    0xF2, 
                    0x05, 
                    int(speed[0]),
                    int(speed[1]),
                    int(speed[2]),
                    int(speed[3]),
                    int(speed[4]), 
                    int(speed[5]))

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Send_Messages(tx_messages)


    def get_pos(self):
        """
        Get the position status information.

        Returns:
            List : [position little finger, position ring finger, ..]
            Limit : 0-1000
        """  
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Read, 
                    0xFE, 
                    0x05,
                    0x0C)

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Get_Messages(tx_messages)


    def get_angle(self):
        """
        Get the angle status information.

        Returns:
            List : [angle little finger, angle ring finger, ..]
            Limit : 0-1000
        """        
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Read, 
                    0x0A, 
                    0x06,
                    0x0C)

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Get_Messages(tx_messages)


    def get_force(self):
        """
        Get the force status information.

        Returns:
            List : [force little finger, force ring finger, ..]
            Limit : 0-1500
        """        
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Read, 
                    0x2E, 
                    0x06,
                    0x0C)

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Get_Messages(tx_messages)


    def get_current(self):
        """
        Get the current status information.

        Returns:
            List : [force little finger, force ring finger, ..]
            Limit : 0-1500
        """
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Read, 
                    0x3A, 
                    0x06,
                    0x0C)

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Get_Messages(tx_messages)


    def get_errorcode(self):
        """
        get error code of 6 fingers
        0 means no error 

        Returns:
            List : [error code little finger, error code ring finger, ..]

        """        
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Read, 
                    0x46, 
                    0x06,
                    0x06)

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Get_Messages(tx_messages, type="6byte")


    def get_status(self):
        """
        get status 0-7 of 6 fingers
        0: Releasing 1: Grasping 2: Stop 3: Force Stop 4: Stop due to Current Protection 
        5: Stop due to Electric Cylinder Stall 6: Stop due to Electric Cylinder Malfunction

        Returns:
            List : [status little finger, status ring finger, ..]

        """
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Read, 
                    0x4C, 
                    0x06,
                    0x06)

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Get_Messages(tx_messages, type="6byte")


    def get_temperature(self):
        """
        get temperature of 6 fingers

        Args:
            None

        Returns:
            List : [temperature little finger, temperature ring finger, ..]
            Limit : 0-100

        """        
        tx_messages = struct.pack('<BBBBBBBB', 
                    self.kSend_Frame_Head1, 
                    self.kSend_Frame_Head2, 
                    int(self.ID), 
                    0x04, 
                    self.kCmd_Handg3_Read, 
                    0x52, 
                    0x06,
                    0x06)

        checksum = sum(tx_messages[2:]) & 0xFF
        tx_messages += struct.pack('>B', checksum)
        return self.Get_Messages(tx_messages, type="6byte")

 