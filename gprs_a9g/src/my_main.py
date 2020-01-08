import sys
import uasyncio
import cellular
from my_simple import MQTTClient
import timep
import gc
from machine import UART
import machine
from ubinascii import hexlify
import gps

mqtt_server = ''
mqtt_port = 1883
mqtt_user = ''
mqtt_password = ''

uart = UART(1)
c = MQTTClient("umqtt_client",mqtt_server,mqtt_port,mqtt_user,mqtt_password)
sreader = uasyncio.StreamReader(uart)
swriter = uasyncio.StreamWriter(uart,{})
led = machine.Pin(27,machine.Pin.OUT,0) 

def is_connected():
    try:
        if True == cellular.gprs():
            return True
        else:
            #print("set apn")
            cellular.gprs('CMNET','','')
            return True == cellular.gprs()
    except OSError:
          return False

def reconnect():
    global c
    try: 
        while is_connected() == False:
            time.sleep(2)
    except OSError:
        pass
    finally:
        c.connect()
        
def connection_init(): 
    global c
    try: 
        n = 5
        time.sleep(3)
        while is_connected() == False:
            time.sleep(3)
            n = n-1
            if n==0:
                machine.reset()
    except OSError:
        pass
    finally:
        c.connect()


def get_gps():
    if gps.get_satellites()[0] <1:
        print("satellite disconnect")
        return None     # 卫星数量不足，无法定位
    longtitude = round(gps.get_location()[1],6)
    latitue = round(gps.get_location()[0],6)
    return latitue,longtitude# tuple,纬度，经度

async def upload_gps():
    global c
    while True:
        gps.on()
        location = None
        while location is None:
            location = get_gps()
            await uasyncio.sleep(10)
        gps.off()
        # G0纬度,G1经度
        location_str0 = 'G0\t' + str(location[0]) 
        location_str1 = 'G1\t' + str(location[1])
        c.publish(b'gps_node',location_str0)
        c.publish(b'gps_node',location_str1)
        await uasyncio.sleep(3600)
      
async def pull():
    global swriter，led
    try:
        if cellular.SMS.poll():
            led.value(1)
            await swriter.awrite(str(cellular.SMS.list()[-1]))
            led.value(0)
    except OSError:
        pass
    #print('i m working')
    await uasyncio.sleep(3)
        
async def upload_data():
    global uart,c
    c.connect()
    buf = bytearray(15)
    mv = memoryview(buf)
    idx = 0
    while True:
        if idx < len(buf) :
            if uart.any():
                bytes_read = uart.readinto(mv[idx:])
                #print('Got {} bytes of data'.format(bytes_read), hexlify(buf[idx:idx+bytes_read], b':'))
                idx += bytes_read
        else:
            led.value(1)
            c.publish(b'foo_info',buf)
            led.value(0)
            idx = 0
        await pull()
        gc.collect()


        
async def keep_network():
    global c
    while True:
        await uasyncio.sleep(18000)  #5小时检查一次连接
        if is_connected():
            pass
        else:
            reconnect()
        c.connect()    

try: 
    connection_init()
    loop = uasyncio.get_event_loop()
    loop.create_task(upload_data())
    loop.create_task(keep_network())
    loop.run_forever()
finally:
    c.disconnect()
    machine.reset()
  
