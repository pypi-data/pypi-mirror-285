""" Vision System interface - main
 
 
@author:    kais, misil.
@created:   2024-07-03

vision_ip : camera IP
vision_port : camera Port

Functions:
CalibStart() -- 
CalibX() -- 
CalibEnd() -- 
ModelPos() -- 
ModelLeg() -- 
Trigger() -- Trigger
                       
"""

import socket
# import requests
import xhost
from typing import Optional


idx: int = 8
currnet : int = 0
valueList: list = ['x', 'y', 'z', 'rx', 'ry', 'rz']
delimiter: str = ','

# global variables
raddr : tuple
sock : Optional[socket.socket] = None

# vision_ip : str = "192.168.10.148"
# vision_port : int = 2006

vision_ip : str = "192.168.100.102"
vision_port : int = 2006


class cmd:
    # VISOR Control
    TRR = "TRR"     # Trigger Robotics
    
    # VISOR Job settings
    SPP = "SPP"     # Set Parameter
    
    # VISOR calibration
    CCD = "CCD"     # Initialization
    CAI = "CAI"     # Add image
    CRP = "CRP"     # Robotics multi-image
    
    TRR_default: str = "TRR104Part0"
    CAI_default: str = "CAI120001020"
    CRP_default: str = "CRP1140"
    SPP_default: str = "SPP001030000013"
    SPP_default_res: str = "SPP001035000480"
    
    fail:str = "Fail"
    calibStart_return: str = "CalibReady"
    calibX_return: str = "Next"
    calibEnd_return: str = "Complete"
    
    
    @staticmethod
    def GetSPPT(key):
        # signed(정수), unsigned(음수)
        if key == "SI08":
            return "SignedInteger08"
        elif key == "UI08":
             return "UnsignedInteger08"
        elif key == "SI16":
            return "SignedInteger16"
        elif key == "UI16":
             return "UnsignedInteger16"
        elif key == "SI32":
            return "SignedInteger32"
        elif key == "UI32":
            return "UnsignedInteger32"
        elif key == "SI40":
            return "SignedInteger40"
        elif key == "UI40":
            return "UnsignedInteger40"
        elif key == "FLOT":
            return "Float"
        elif key == "DOBL":
            return "Double"
        elif key == "STRG":
            return "String"
        elif key == "BOOL":
            return "Boolean"
        elif key == "SP08":
            return "SpecialSigned8"
        elif key == "UDEF":
            return "Undefined"
        elif key == "IARR":
            return "IntegerArray"
        elif key == "ZERO":
            return "DefaultZeroParameter"
        

class socketFunc:
    def __init__(self):
        self.ip = vision_ip
        self.port = vision_port
 
    def get_ip(self):
        return self.ip
    
    def set_ip(self, addr: str):
        self.ip = addr
    
    def get_port(self):
        return self.port
    
    def set_port(self, _port: int):
        self.port = _port
    

    def is_open(self):
        return (sock is not None)


    def open(self):
        global raddr, sock, ip_addr, port
        
        if sock is not None: 
            return False
        
        try:
            raddr = (self.ip, self.port)
            sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            sock.connect(raddr)
            
        except socket.error as e:
            logd("[Failed][vision] open failed")
            return False
        
        logd("[vision] open")
        return True



    def is_close(self):
        if sock is not None:
            self.close()


    def close(self):
        global sock
        if sock is None: 
            return
        
        logd("[vision] close")
        sock.close()
        sock = None
    
    
    def send_msg(self, msg):
        if sock is None: 
            return -1
        
        try:
            logd("[vision] send : " + msg)
            bts = bytes(msg.encode())
            return sock.send(bts) 
        except Exception as e:
            logd("[Failed][vision] " + str(e))
            return ""

    
    def recv_msg(self):
        if sock is None: 
            return ""

        try:
            recv_data = sock.recv(1024).decode()
            logd("[vision] recv : " + recv_data)
            return recv_data
        
        except Exception as e:
            logd("[Failed][vision] " + str(e))
            return ""



def Set_CCD():
    msg = cmd.CCD
    return msg


def Get_CCD(recv_data):
    # CCDP
    recv = list(recv_data)
    recv, cmd = Get_Data(recv, 0, 3)
    recv, result = Get_Data(recv, 0, 1)
    
    if result == "P":
        return True
    else:
        return False


def Set_CAI(value):
    #  CAI104Part000040040000500500006006000070070000800800009009
    _cmd = cmd.CAI_default
    result = Get_Value(value)
    return _cmd+result if result != None else None
    

def Get_CAI(recv_data):
    # CAIP00000100021
    recv = list(recv_data)
    recv, cmd = Get_Data(recv, 0, 3)
    recv, result = Get_Data(recv, 0, 1)

    if result == "P":
        return True
    elif result =="F":
        return False


def Set_CRP():
    #  CRP1140
    return cmd.CRP_default


def Get_CRP(recv_data):
    # CRPP00009201349012004000010010000200200003003000040040000500500006006
    recv = list(recv_data)
    recv, cmd = Get_Data(recv, 0, 3)
    recv, result = Get_Data(recv, 0, 1)

    if result == "P":
        return True
    elif result =="F":
        return False
    
    
def Set_TRR(value):
    #  TRR104Part000040040000500500006006000070070000800800009009
    _cmd = cmd.TRR_default
    result = Get_Value(value)
    return _cmd+result if result != None else None


def Get_TRR(recv_data):
    # TRRP00004PartR00000026P,-1,2410,689,72,405,-2515
    recv = list(recv_data)
    recv, cmd = Get_Data(recv, 0, 3)
    recv, result = Get_Data(recv, 0, 1)

    if result == "P":
        return True
    elif result =="F":
        return False
    

def Shift(recv_data):
    recv = list(recv_data)
    recv, cmd = Get_Data(recv, 0, 3)
    recv, result = Get_Data(recv, 0, 1)

    if result == "P":
        recv, _ = Get_Data(recv, 0, 19)
        recv, positionData = Get_Data(recv, 0, len(recv) -1)
        
        result = []
        values = ''.join(positionData).split(delimiter)
        for value in values:
                result.append(round(float(value)/1000, 3))
        return result

    elif result =="F":
        return False
    

def Set_SPP():
    # SPP0010010000560000
    msg = cmd.SPP_default
    return msg


def Set_PoseSPP( value):
    _cmd = cmd.SPP_default_res
    result = Get_Value(value)
    return _cmd+result if result != None else None
    

def Get_SPP(recv_data):
    # SPPPSTRG
    recv = list(recv_data)
    recv, cmd = Get_Data(recv, 0, 2)
    recv, pt = Get_Data(recv, 0, 1) # permanent # Temporary
    recv, result = Get_Data(recv, 0, 1)

    if result == "P":   
        recv, msg = Get_Data(recv, 0, 1)
        if msg == "U":
            return True
        elif msg == "S":
            return True
        else:
            return False

    elif result == "F":
        return False     

    
# ---------------------------------------------------------------------------------

def Get_Value(value):
    if(value):
        try:
            if value.get('_type') == "Pose":
                # x, y, z, rx, ry, rz
                # {'nsync': 0, '_type': 'Pose', 'rx': 0.0, 'x': 1067.366, 'ry': 73.248, 'y': -12.859, 'rz': -0.69, 'z': 1609.909, 'mechinfo': 1, 'crd': 'base', 'j1': 0.0, 'j2': 0.0, 'j3': 0.0, 'j4': 0.0, 'j5': 0.0, 'j6': 0.0}
                
                vSendMsg :str = ""
                
                for values in valueList:
                    
                    temp: float = value.get(values)
                    valInt = temp * 10000 
                    vSendMsg += ('%08d' % valInt) 
                
                return vSendMsg
        except:
            return None    
    else:
        return None


def Get_Data(list, start, end):
    temp = end
    for i, str in enumerate(list):
        temp -= len(str.encode())
        if temp == 0:
            end = i + 1
            break
        
    data = ''.join(list[start: end])
    cut = list[end:]
    return cut, data
    
    
    
        

def VisionRecv(recv):
    status = False
    _cmd = ''.join(list(recv)[0:3])
    if recv is not None:
        
        if cmd.CCD == _cmd:
            status = Get_CCD(recv)
            if status:
                logd("[vision] " + "Calibration Initialization Successful")
            else:
                logd("[vision] " + "Calibration Initialization Failed")

        elif cmd.CAI == _cmd:
            status = Get_CAI(recv_data=recv)
            if status:
                logd("[vision] " + "Calibration CAI Successful")
            else:
                logd("[vision] " + "Calibration CAI Failed")
                
        elif cmd.CRP == _cmd:
            status = Get_CRP(recv_data=recv)
            if status:
                logd("[vision] " + "Calibration CPR Successful")
            else:
                logd("[vision] " + "Calibration CPR Failed")  
                
        elif cmd.TRR == _cmd:
            status = Get_TRR(recv_data=recv)
            if status:
                logd("[vision] " + "Trigger Robotics complete")
            else:
                logd("[vision] " + "Trigger Robotics error")    
                
        elif cmd.SPP == _cmd:
            status = Get_SPP(recv_data=recv)
            if status:
                logd("[vision] " + "Set Parameters Successful")
            else:
                logd("[vision] " + "Set Parameters Failed")

    return status




def CalibX_com(socketfunc):
    status = False
    apiResult: dict = res_api(path='/project/robot/po_cur', query={'crd': 0, 'mechinfo': 1})
    visionMsg = Set_CAI(apiResult)
    
    if visionMsg:
        if socketfunc.send_msg(msg=visionMsg):
            status = True
    else:
        logd("[Failed][vision] CalibX_func/send_msg failed")
        return status

    recv = socketfunc.recv_msg()
    if recv:
        if VisionRecv(recv):
            status = True
        else:
            logd("[Failed][vision] CalibX_func/recv_msg/VisionRecv failed")     
    else:
        logd("[Failed][vision] CalibX_func/recv_msg failed")
        
    return status


def CalibStart():
    # vision open
    
    socketfunc = socketFunc()
    try:
        if not socketfunc.open():
            return cmd.fail

        status = CalibStart_func(socketfunc)
        socketfunc.is_close()
        
        if status:
            return cmd.calibStart_return
        else:
            return cmd.fail

    except:
        socketfunc.is_close()
        return cmd.fail
        

def CalibStart_func(socketfunc):
    # visionSend : 'CCD' 전송
    if not socketfunc.send_msg(cmd.CCD):
        logd("[Failed][vision] CalibStart/send_msg failed")
        return False
    
    # visionRecv : CCDP or CCDF 
    recv = socketfunc.recv_msg()
    if recv:
        if not VisionRecv(recv):
            logd("[Failed][vision] CalibStart/recv_msg/VisionRecv failed")
            return False
    else:
        logd("[Failed][vision] CalibStart/vision recv_msg failed")
        return False
    
    if CalibX_com(socketfunc):
        logd(cmd.calibStart_return)
    else:
        logd("[Failed][vision] CalibX_Com failed")
        return False
    
    return True  



def CalibX():
    socketfunc = socketFunc()
    try:
        if not socketfunc.open():
            return cmd.fail
        
        status = CalibX_func(socketfunc);
        socketfunc.is_close()
        if status:
            return cmd.calibX_return
        else:
            logd("[Failed][vision] CalibX failed")
            return cmd.fail
    except:
        socketfunc.is_close()
        return cmd.fail
    



def CalibX_func(socketfunc):
    if CalibX_com(socketfunc):
        return True 
    else:
        logd("[Failed][vision] CalibX_func failed")
        return False



def CalibEnd():
    socketfunc = socketFunc()
    try:
        if not socketfunc.open():
            return cmd.fail

        status = CalibEnd_func(socketfunc)
        socketfunc.is_close()
        
        if status:
            return cmd.calibEnd_return
        else:
            logd("[Failed][vision] CalibEnd failed")
            return cmd.fail
    except:
        socketfunc.is_close()
        return cmd.fail
    


def CalibEnd_func(socketfunc):
    status: bool = False
    if CalibX_com(socketfunc):
        visionMsg = Set_CRP()
        if visionMsg:
            if socketfunc.send_msg(visionMsg):
                status = True
        else:
            logd("[Failed][vision] CalibEnd/send_msg failed")
            return False

        recv = socketfunc.recv_msg()
        if recv:
            if VisionRecv(recv):
                status = True
            else:
                logd("[Failed][vision] recv_msg/VisionRecv failed")
                return False    
        else:
            logd("[Failed][vision] recv_msg failed")
            return False
        
        logd(cmd.calibEnd_return)  
    else:
        logd("[Failed][vision] CalibX failed")
        return False
    
    return status



def ModelPos():
    socketfunc = socketFunc()
    # vision open
    try:
        if not socketfunc.open():
            return cmd.fail

        status = ModelPos_func(socketfunc)
        socketfunc.is_close()
        
        if status:
            # complete
            return cmd.calibEnd_return
        else:
            return cmd.fail
    except:
        socketfunc.is_close()
        return cmd.fail



def ModelPos_func(socketfunc):
    status = False
    apiResult: dict = res_api(path='/project/robot/po_cur', query={'crd': 0, 'mechinfo': 1})
    visionMsg = Set_TRR(apiResult)
    
    if visionMsg:
        if socketfunc.send_msg(visionMsg):
            status = True
    else:
        logd("[Failed][vision] ModelPos_func/send_msg failed")
        return status

    recv = socketfunc.recv_msg()
    if recv:
        if VisionRecv(recv):
            status = True
        else:
            logd("[Failed][vision] ModelPos_func/recv_msg/VisionRecv failed")     
    else:
        logd("[Failed][vision] ModelPos_func/recv_msg failed")

    return status


def ModelLeg():
    # vision open
    socketfunc = socketFunc()
    try:
        if not socketfunc.open():
            return cmd.fail
    
        status = ModelLeg_func(socketfunc)
        socketfunc.is_close()

        if status:
            # complete
            return cmd.calibEnd_return
        else:
            return cmd.fail
        
    except:
        socketfunc.is_close()
        return cmd.fail
    
    


def ModelLeg_func(socketfunc):
    status: bool = False
    status = True
    visionMsg = Set_SPP()
    
    if visionMsg:
        if socketfunc.send_msg(visionMsg):
            status = True
    else:
        logd("[Failed][vision] ModelLeg_func/send_msg failed")
        return False
    
    # SPPPUI08
    recv = socketfunc.recv_msg()
    if recv:
        if VisionRecv(recv):
            status = True
        else:
            logd("[Failed][vision] ModelLeg_func/recv_msg/VisionRecv failed")     
    else:
        logd("[Failed][vision] ModelLeg_func/recv_msg failed")
        return False
    
    apiResult: dict = res_api(path='/project/robot/po_cur', query={'crd': 0, 'mechinfo': 1})
    visionMsg = Set_PoseSPP(apiResult)
    if visionMsg:
        if socketfunc.send_msg(visionMsg):
            status = True
    else:
        logd("[Failed][vision] ModelLeg_func/send_msg failed")
        return False
    
    recv = socketfunc.recv_msg()
    if recv:
        if VisionRecv(recv):
            status = True
        else:
            logd("[Failed][vision] ModelLeg_func/recv_msg/VisionRecv failed")     
    else:
        logd("[Failed][vision] ModelLeg_func/recv_msg failed")
        return False
    
    return status



def Trigger():
    socketfunc = socketFunc()
    try:
        if not socketfunc.open():
            return cmd.fail    
    
        result = Trigger_func(socketfunc)
        socketfunc.is_close()
        
        if result:
            return result
        else:
            return cmd.fail
    
    except:
        socketfunc.is_close()
        return cmd.fail
    


def Trigger_func(socketfunc):
    result = []
    apiResult: dict = res_api(path='/project/robot/po_cur', query={'crd': 0, 'mechinfo': 1})
    visionMsg = Set_TRR(apiResult)
    if visionMsg:
        if socketfunc.send_msg(visionMsg):
            pass
    else:
        logd("[Failed][vision] Trigger_func/send_msg failed")
        return False
    
    recv = socketfunc.recv_msg()
    if recv:
        if VisionRecv(recv):
            result = Shift(recv)
        else:
            logd("[Failed][vision] Trigger_func/recv_msg/VisionRecv failed")     
    else:
        logd("[Failed][vision] Trigger_func/recv_msg failed")
        return False
    
    return result
    



def res_api(path: str, query: dict):
    base_url        = 'http://192.168.1.150:8888'
    path_parameter  = path
    query_parameter = query
    response = {'nsync': 0, '_type': 'Pose', 'rx': 0.0, 'x': 1067.366, 'ry': 73.248, 'y': -12.859, 'rz': -0.69, 'z': 1609.909, 'mechinfo': 1, 'crd': 'base', 'j1': 0.0, 'j2': 0.0, 'j3': 0.0, 'j4': 0.0, 'j5': 0.0, 'j6': 0.0}
    # response = requests.get(url = base_url + path_parameter, params = query_parameter).json()
    return response


def logd(text: str):
    print(text)
    xhost.printh(text)
