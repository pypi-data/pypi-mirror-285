from enum import Enum, auto

class ZABBIX:
    
    class Commands(Enum):
        
        get_host_list = auto() 
        get_item_list = auto() 
        get_value_list = auto() 
        send_value = auto()