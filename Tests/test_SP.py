import sys
import pytest
import IP150MQTTv2

global client
mqttresult = {}

class dummy_mqtt(object):
    pass
    def publish(self,topic,payload, qos=1, retain=True):
        print ('Posted: ' + topic + ' Payload: ' + payload)
        mqttresult[topic] = payload
        


class dummy_comms(object):
    pass
    def send(self,data):
        print "SND -->" + data
        pass
    def recv(self,buff_size):
        print "REC <--" + str(buff_size)
        pass

def create_device():
    #Alarm_Model = ParadoxMG5050             ;Currently not used
    #Alarm_Registry_Map = ParadoxMG5050      ;This is used to map to the correct dictionary class within the ParadoxMap.py package. The word "Registers" is appended before loading.
    #Alarm_Event_Map = ParadoxMG5050  
    comms = dummy_comms()
    client = dummy_mqtt()
    myAlarm = IP150MQTTv2.paradox(comms, client,0, 3, 'ParadoxMG5050', 'ParadoxMG5050')
    myAlarm.partitions = {1:'Partition1',2:'BottomFloor'}
    return myAlarm


#def test_panel_connect():
#    device = create_device()
#    device.login("test","test",0)
#    pass


def test_panel_received_heartbeat0():
    device = create_device()
    
    messages = '\x52\x00\x80\x00\x00\x00\x00\x00\x00\x14\x13\x02\x0f\x0f\x1c\xd0\x9a\x97\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    device.keepAliveStatus0(messages,2,0)
    if mqttresult["Paradox/Status/0"] == '{"battery": 13.5, "vdc": 16.8, "dc": 13.8, "paneldate": "2019-02-15 15:28"}':
        assert True
    else:
        assert False

def test_panel_received_heartbeat1():
    device = create_device()
    
    #              0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16 0x01 Armed                                                                     
    messages = '\x52\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd4'
    device.keepAliveStatus1(messages,2,0)
    if mqttresult.has_key("Paradox/Partition/Partition1/Status") and mqttresult["Paradox/Partition/Partition1/Status"] == 'ARMED':
        assert True
    else:
        assert False

    #              0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16 0x00 disarmed                                                                     
    messages = '\x52\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd4'
    device.keepAliveStatus1(messages,2,0)
    if mqttresult.has_key("Paradox/Partition/Partition1/Status") and mqttresult["Paradox/Partition/Partition1/Status"] == 'DISARMED':
        assert True
    else:
        assert False

def test_panel_keepalive1_DISARMED_use_OPEN_CLOSED():
    device = create_device()
    IP150MQTTv2.ZonesOff = "CLOSED"
    IP150MQTTv2.ZonesOn = "OPEN"
    messages = []
    #              0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16 0x00 disarmed                                                                     
    messages = '\x52\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd4'
    device.keepAliveStatus1(messages,2,0)
    if mqttresult.has_key("Paradox/Partition/Partition1/Status") and mqttresult["Paradox/Partition/Partition1/Status"] == 'DISARMED':
        assert True
    else:
        assert False

def test_panel_received_Event_OK():
    device = create_device()
    messages = []
    messages.append('\xe0\x14\x11\x09\x04\x07\x10\x01\x04\x00\x00\x00\x00\x00\x00\x42\x65\x64\x20\x72\x6f\x6f\x6d\x20\x50\x49\x52\x20\x20\x20\x20\x00\x00\x00\x00\x00\xa1')
    device.testForEvents(0,0,data=messages)
    if mqttresult["Paradox/Zone/Bed room PIR"] == "OFF":
        assert  False
    else:   
        assert True
    
def test_panel_received_Event_CLOSED():
    device = create_device()
    messages = []
    messages.append('\xe0\x14\x11\x09\x04\x07\x10\x01\x04\x00\x00\x00\x00\x00\x00\x42\x65\x64\x20\x72\x6f\x6f\x6d\x20\x50\x49\x52\x20\x20\x20\x20\x00\x00\x00\x00\x00\xa1')
    device.testForEvents(0,0,data=messages)
    
    if mqttresult["Paradox/Zone/Bed room PIR"] == "OFF":
        assert  False
    else:   
        assert True


def test_panel_received_Event_ARMING():
    device = create_device()
    messages = []
    # Arming event for "Area 1"
    messages.append('\xe0\x14\x11\x09\x04\x07\x10\x02\x09\x00\x00\x00\x00\x00\x00\x41\x72\x65\x61\x20\x31\xa1')
    
    #Default ARMING message
    device.testForEvents(0,0,data=messages)
    if mqttresult.has_key("Paradox/Partition/Area 1/Status") and mqttresult["Paradox/Partition/Area 1/Status"] == "ARMING":
        assert  True
    else:   
        assert False
    
    #Changed to arming
    device.Alarm_Partition_States['ARMING'] = 'arming'
    device.testForEvents(0,0,data=messages)
    if mqttresult.has_key("Paradox/Partition/Area 1/Status") and mqttresult["Paradox/Partition/Area 1/Status"] == "arming":
        assert  True
    else:   
        assert False

def test_panel_received_long_partition_name_Event_ARMING():
    device = create_device()
    messages = []
    # Arming event for "Area 1"
    messages.append('\xe0\x14\x11\x09\x04\x07\x10\x02\x09\x00\x00\x00\x00\x00\x00\x41\x72\x65\x61\x20\x31\x20\x42\x6f\x74\x74\x6f\x6d\x20\x66\x6c\x6f\x6f\x72\xa1')
    
    #Default ARMING message
    device.testForEvents(0,0,data=messages)
    if mqttresult.has_key("Paradox/Partition/Area 1 Bottom floor/Status") and mqttresult["Paradox/Partition/Area 1 Bottom floor/Status"] == "ARMING":
        assert  True
    else:   
        assert False


    