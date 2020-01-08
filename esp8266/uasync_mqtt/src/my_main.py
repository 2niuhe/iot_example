

from machine import UART
from mqtt_as import MQTTClient,config
import gc
import uasyncio
import uos
import network
import machine
import time
import ubinascii
import usocket
import uselect
import gc
import ure
import tinyweb
import logging



gc.collect()
wifi = network.WLAN(network.STA_IF)

loop = uasyncio.get_event_loop()

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
SERVER = '' #已经在config文件配置过

PUB_TOPIC = CLIENT_ID + b'/state'# TOPIC的ID, TOPIC需要byte类型
SUB_TOPIC = CLIENT_ID + b'/set'
MSG_INTERVAL = 5   # MQTT消息间隔5s
MQTTClient.DEBUG = False  # Optional: print diagnostic messages
uart = UART(0)
sreader = uasyncio.StreamReader(uart)
swriter = uasyncio.StreamWriter(uart,{})
config['subs_cb'] = sub_callback
config['connect_coro'] = conn_han
config['server'] = SERVER
config['user'] = ''
config['port'] = 1883
config['password'] = ''


import esp
esp.osdebug(None)
uos.dupterm(None,1)
uos.dupterm(None)

async def my_callback(topic,msg,retained):
    global swriter
    await swriter.awrite(msg)
    await uasyncio.sleep(0)


def sub_callback(topic, msg, retained):
    loop = uasyncio.get_event_loop()
    loop.create_task(my_callback(topic,msg,retained))

async def conn_han(client):
    global SUB_TOPIC
    await client.subscribe(SUB_TOPIC, 1)

async def do_connect(ssid, password=None):
    global wifi
    wifi.active(True)
    #if wifi.isconnected():
    #    wifi.disconnect()
    print('Trying to connect to %s...' % ssid)
    wifi.connect(ssid, password)
    await uasyncio.sleep(1)
    for retry in range(20):
        connected = wifi.isconnected()
        if connected:
            break
        await uasyncio.sleep(0.5)
        print('.', end='')
    if connected:
        print('\nConnected. Network config: ', wifi.ifconfig())
    else:
        print('\nFailed. Not Connected to: ' + ssid)
    return connected

def restart_machine():
# 重启并restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(1)
    machine.reset()

gc.collect()



client = MQTTClient(config)

async def mqtt_main(client):
    global wifi,PUB_TOPIC,sreader,loop
    # global uart
    while True:
        if wifi.isconnected():    # avoid dead loop when no ssid config
            break
        await uasyncio.sleep(3)

    await client.connect(loop)
    # n=0
    #sreader = uasyncio.StreamReader(sys.stdin)
    n = 0
    while True:
        res = await sreader.readline()
        await client.publish(PUB_TOPIC, res, qos = 1)
        await uasyncio.sleep(0)

gc.collect()

loop.create_task(mqtt_main(client))


app = tinyweb.webserver(external_loop=loop,debug=True)
# Index page
@app.route('/')
async def index(request, response):
    global wifi
    wifi.active(True)
    # Start HTTP response with content-type text/html
    ssids = sorted(ssid.decode('utf-8') for ssid, *_ in wifi.scan()[:10])
    gc.collect()
    await response.start_html()
    # Send actual HTML page
    await response.send("""
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
            <h1 style="color: #5e9ca0; text-align: center;">
                <span style="color: #ff0000;">
                    Wi-Fi 配置
                </span>
            </h1>

            <form  action="/configure" method="get">
                <table style="margin-left: auto; margin-right: auto;">
                    <tbody>
    """)
    while ssids:
        ssid = ssids.pop(0)
        await response.send("""
                        <tr>
                            <td colspan="2">

                                <input type="radio" name="ssid" value="{0}" />{0}
                            </td>
                        </tr>
        """.format(ssid))
    await response.send("""
                        <tr>
                            <td>密码:</td>
                            <td><input name="password" type="password" /></td>
                        </tr>
                    </tbody>
                </table>
                <hr />
                <p style="text-align: center;">
                    <input type="submit" value="提交" />
                </p>
            </form>
            <hr />
        </html>
        """)

@app.route('/configure')
async def configure(request, response):
    # Start HTTP response with content-type text/html
    match = ure.search("ssid=([^&]*)&password=(.*)", request.query_string)
    await response.start_html()
    await response.send("""
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">

    """)
    if match is None:
        await response.send("请输入有效网络名和密码<html/>")
        return False
    # version 1.9 compatibility
    try:
        ssid = match.group(1).decode("utf-8").replace("%3F", "?").replace("%21", "!")

        password = match.group(2).decode("utf-8").replace("%3F", "?").replace("%21", "!")
    except Exception:
        ssid = match.group(1).replace("%3F", "?").replace("%21", "!")
        password = match.group(2).replace("%3F", "?").replace("%21", "!")

    if len(ssid) == 0:
        await response.send("必须提供SSID</html>")
        return False
    result = await do_connect(ssid, password)
    if result:
        html = """
                <center>
                    <br><br>
                    <h1 style="color: #5e9ca0; text-align: center;">
                        <span style="color: #ff0000;">
                            您的花盆成功连接"{0}"网络
                        </span>
                    </h1>
                </center>
            </html>
        """.format(ssid)
        await response.send(html)
        return True
    else:
        html = """
                <center>
                    <h1 style="color: #5e9ca0; text-align: center;">
                        <span style="color: #ff0000;">
                            花盆无法连接到网络 {0}.
                        </span>
                        <span style="color: #ff0000;">
                            请重新输入配置网络.
                        </span>
                    </h1>

                    <form>
                        <input type="button" value="重新配置" onclick="history.back()"></input>
                    </form>
                </center>
            </html>
        """.format(ssid)

        await response.send(html)
        return False

gc.collect()

try:
    
    # Create web server application
    app.run(host='0.0.0.0', port=80,loop_forever=False)
    loop.run_forever()
finally:
    client.close()
    loop.close()
    restart_machine()



