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
    return myAlarm


#def test_panel_connect():
#    device = create_device()
#    device.login("test","test",0)
#    pass


def test_panel_received_heartbeat0():
    device = create_device()
    
    messages = '\x00\x00\x80\x00\x00\x00\x00\x00\x00\x14\x13\x02\x0f\x0f\x1c\xd0\x9a\x97\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    device.keepAliveStatus0(messages,2,0)
    if mqttresult["Paradox/Status/0"] == '{"battery": 13.5, "vdc": 16.8, "dc": 13.8, "paneldate": "2019-02-15 15:28"}':
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