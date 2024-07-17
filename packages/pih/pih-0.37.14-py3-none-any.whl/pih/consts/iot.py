from enum import Enum, auto

class IOT:
    
    class Commands(Enum):
        
        device_list = auto() 
        device_status_properties = auto() 
        device_status = auto() 
