## 智能花盆开发笔记

### ESP8266配网

1. 获取mac地址作为唯一标识

   ```python
   import network
   sta_if = network.WLAN(network.STA_IF)
   sta_if.active(True)
   print(sta_if.ifconfig())    #获取IP、网关等信息
   s = sta_if.config('mac')
   mymac = ('%02x%02x%02x%02x%02x%02x') %(s[0],s[1],s[2],s[3],s[4],s[5]) # 获取mac地址
   mymac = ('%02x-%02x-%02x-%02x-%02x-%02x') %(s[0],s[1],s[2],s[3],s[4],s[5])  #带分隔符的mac地址
   
   
   def get_mac(wifi):
       s = wifi.config('mac')
       mymac = ('%02x%02x%02x%02x%02x%02x') %(s[0],s[1],s[2],s[3],s[4],s[5])
       #mymac = ('%02x-%02x-%02x-%02x-%02x-%02x') %(s[0],s[1],s[2],s[3],s[4],s[5])
       return mymac
   ```

2. 配置开放AP

   ```python
   import network
   
   ap = network.WLAN(network.AP_IF) # 创建一个热点
   ap.active(True)         # 激活热点
   ap.config(essid='Flower_Pot',authmode=0) # 为热点配置essid（即热点名称）
   
   # 启动AP热点   
   def init_ap():
       ap_ssid = "Pot_" + CLIENT_ID.decode('utf-8')
       ap_authmode = 0  # 0 Open,3 WPA
       wlan_ap = network.WLAN(network.AP_IF)
       wlan_ap.active(True)
       wlan_ap.config(essid=ap_ssid,authmode=ap_authmode)
   ```

   

3. 配置STA模式

   pass

4. 多线程



### web_server

> picoweb的example可以看一下
>
> 暂时用tinyweb异步框架，串口用异步读写，MQTT也是异步，MQTT和串口是chain，异步链。

### ESP8266 串口通信

>  http://www.1zlab.com/wiki/micropython-esp32/uart/ 
>
> > - uart.read(length) 
> >
> >   读取指定字节数，若未指定length，则读取所有字节
> >
> > - uart.readline()
> >   读取一行数据
> >
> > - uart.readinto(buf)
> >   读入指定缓冲区
> >
> > - uart.write(data)
> >   向串口写入数据，返回数据长度
> >   uart.write('abc')
> >
> > - uart.any()
> >   检测串口缓冲区是否有可读数据，返回数据长度

```python
from machine import UART
# 构造函数UART(id, baudrate, databits, parity, rx, tx, stopbit, timeout)
# d = UART(2, baudrate=115200, rx=13, tx=12, timeout=10)
uart = UART(1,rx=13, tx=12)

# 创建一个Timer，使用timer的中断来轮询串口是否有可读数据
timer = Timer(1)
timer.init(period=50, mode=Timer.PERIODIC, callback=lambda t: read_uart(uart))


def read_uart(uart):
    if uart.any():
        print('received: ' + uart.read().decode() + '\n')


if __name__ == '__main__':
    try:
        for i in range(10):
            uart.write(input('send: '))
            time.sleep_ms(50)
    except:
        timer.deinit()
```



### UART 异步非阻塞

> ESP8266只有一个UART,dupterm函数可以动态的将UART附加到REPL或者使其分离。
>
> print()函数会阻塞串口，因为print是用于REPL的

```python
# attach to REPL
# UART(0)的所有输入都会直接到stdin，因此uart.read()永远返回None
# 必要时 ，可以使用sys.stdin.read()来读取UART(0)的输入字符
# 默认是将UART(0)attach 到REPL的
# 关闭REPL，才能正常使用UART
import uos, machine
    uart = machine.UART(0, 115200)
    uos.dupterm(uart, 1)
# uos.dupterm(stream_object, index=0)
# dupterm函数用来复制/切换Micropython终端REPL到对应的流对象，
"""Duplicate or switch the MicroPython terminal (the REPL) on the given stream-like object. The stream_object argument must be a native stream object, or derive from uio.IOBase and implement the readinto() and write() methods. The stream should be in non-blocking mode and readinto() should return None if there is no data available for reading.

After calling this function all terminal output is repeated on this stream, and any input that is available on the stream is passed on to the terminal input.

The index parameter should be a non-negative integer and specifies which duplication slot is set. A given port may implement more than one slot (slot 0 will always be available) and in that case terminal input and output is duplicated on all the slots that are set.

If None is passed as the stream_object then duplication is cancelled on the slot given by index.

The function returns the previous stream-like object in the given slot.
"""

# and to detach use:

    uos.dupterm(None, 1)
```



### ESP8266 收发MQTT数据包

> 使用umqtt.simple类库，增加代码mqtt.py

```python
from simple import MQTTClient
from machine import Pin
import machine,time, math
import micropython
#选择G4引脚
led_blue = machine.PWM(machine.Pin(2), freq=1000)  # 设置 GPIO2 为输出
led_blue.duty(1024)
# MQTT服务器地址域名为：49.235.173.142,不变
SERVER = "49.235.173.142"
#设备ID
CLIENT_ID = "umqtt_client"
#随便起个名字
TOPIC = b"ledctl"
TOPIC2 = b"pwmled"
TOPIC3 = b"ledstatus"
username="123123"
password="321321"
pwm_old = 0
pwmval = 0
c=None
 
def delay(t):
    for i in range(t):
    k=0;
 
def sub_cb(topic, msg):
	do_something()
 
 
def main(server=SERVER):
    #端口号为：6002
    c = MQTTClient(CLIENT_ID, server)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    c.subscribe(TOPIC2)   
    print("Connected to %s, subscribed to %s topic" % (server, TOPIC))
    try:
        while 1:
            c.wait_msg()
            global pwm_old,pwmval
 
            if pwmval == 1024 :
                c.publish(TOPIC3,'ledoff')
            elif pwmval < 1024 :
                c.publish(TOPIC3,'ledon');
 
            if pwmval > pwm_old :
                for i in range(pwm_old,pwmval,1):
                    led_blue.duty(i)
                    delay(30)
            elif pwmval < pwm_old :
                for i in range(pwm_old,pwmval,-1):
                    led_blue.duty(i)
                    delay(30)
            pwm_old = pwmval
 
    finally:
            c.disconnect()
```

### socket异步多任务

> 实现方式：
>
> - uselect

```python
import usocket as socket
import uselect as select

def do_something_else():
    # script besides of socket

def client_handler(client_obj):
    # excute this script when there is a socket connetion

server_port = 5000
incoming_addr = ""
address = (incoming_addr, server_port)
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.bind(address)
server_socket.listen(4)

while True:
    # 因为socket是阻塞的，使用select设置超时
    r, w, err = select.select((server_socket,), (),1)
    if r:
        for readable in r:
            client,client_addr = server_socket.accept()
            try:
                client_handler(client)
            except OSError as e:
                pass
            
    do_something_else()
```

```python
# select非阻塞读取UART(0)
import sys
import select
import time

while 1:
  time.sleep(0.1)
   
  while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    ch = sys.stdin.read(1)
    print(ch)
    
  print("prove it doesn't block")
```



### MicroPython类库

> - ujson
> - urequests
> - network
> - machine
> - usocket
> - ussl
> - uselect



### Micropython  uselect库

> 相关函数如下：

- uselect.poll()
- uselect.select(rlist,wlist,xlist[,timeout])
  推荐使用poll()

> Poll类

- poll.register(obj[,eventmask])
  注册轮询的stream对象，eventmask可以是uselect.POLLIN或者uselect.POLLOUT
- poll.unregister(obj)
- poll.modify(obj,eventmask)
  修改对象的eventmask,如果对象没有注册轮询，OSError is raised with error of ENOENT.
- poll.poll(timeout=-1)
  等待至少一个已注册的对象准备就绪或处于异常状态，以毫秒为单位进行超时，未指定或为-1，则没有超时。



```python
import ntptime
npttime.time() #测试连接到公网并同步时间

str(3).encode('ascii')
bytes(str(3),'acii')

import micropython
micropython.mem_info() #查看堆栈内存
```



### Micropyhton预编译

> 将脚本放在esp8266/script下就可以编译自己的bin文件

libffi-dev

 https://www.youtube.com/watch?v=jG7WBY_vmpE 



每次import 后，加入gc.collect()降低heap 碎片 fragment



在所有import进来之后，执行

```python
gc.collect()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
```

有助于减少heap fragment.



#### 编译esp-open-sdk

```shell
sudo apt-get install make unrar-free autoconf automake libtool gcc g++ gperf flex bison texinfo gawk ncurses-dev libexpat-dev python-dev python python-serial sed git unzip bash help2man wget bzip2 libtool-bin

git clone --recursive https://github.com/pfalcon/esp-open-sdk.git
cd esp-open-sdk/crosstool-NG/.build/tarballs  #没有目录就新建一个
# 手动下载ftp://sourceware.org/pub/newlib/newlib-2.0.0.tar.gz
# 将其放在tarballs目录下
#终端挂代理
cd esp-open-sdk/
make
#-------------------------
export PATH=/home/niuhe/smartpot/esp-open-sdk/xtensa-lx106-elf/bin/:$PATH

# 编译micropython
sudo apt-get install pkg-config python-pip libffi-dev
git clone --recursive https://github.com/micropython/micropython.git
cd micropython
make -C mpy-cross
cd micropython/ports/esp8266
# 把你的Python代码放在module文件夹下
make
# 在build***目录下找固件
# esptool烧写固件
# ------------------------
# 【可选】编译时适当增加堆的大小
# https://gioorgi.com/2019/uasyncio-esp8266/
# 编辑main.c文件将heap size从36KB,增加到44KB
// From 38Kb....
STATIC char heap[38 * 1024];
// to whoppy 44Kb
STATIC char heap[44 * 1024];

# 还可以在预编译时修改一下package,
# 比如去掉web_REPL，加入uasyncio.cor,uasyncio,logging等
```

#### 预编译main.py

```python
# 编辑esp8266/modules目录下的inisetup.py文件
# 在文件setup()函数最后添加import mymain
# mymain.py文件中不能有
if __name__ == '__main__'
#代码块，mymain.py中的代码在import的时候被执行
```

#### 扩大固件空间

> firmware默认ESP8266有1M的Flash，给文件系统预留了一些空间，剩下空间留给固件。
>
> 而对于有4M的Flash，可以调整文件系统的大小。方法如下：

```c
# esp8266/esp8266.ld 第8行修改为
irom0_0_seg :  org = 0x40209000, len = 0xa7000
# esp8266/modesp.c 就变成了
STATIC mp_obj_t esp_flash_user_start(void) {
    if (IS_OTA_FIRMWARE()) {
        return MP_OBJ_NEW_SMALL_INT(0x3c000 + 0x90000);
    } else {
        return MP_OBJ_NEW_SMALL_INT(0xb0000);
    }
}
```





------------

```python\
"""
global mqtt_client

async def mqtt_connect_and_subscribe():
    global mqtt_client
    mqtt_client = MQTTClient(CLIENT_ID, SERVER,8883,"sammy","111111",ssl=True)
    mqtt_client.set_callback(sub_callback)
    await mqtt_client.connect()
    await mqtt_client.subscribe(SUB_TOPIC)
    print('Connected to MQTT Broker,subscribed to %s topic',(SUB_TOPIC,))
    

async def mqtt_publish(content):
    global mqtt_client
    await mqtt_client.publish(PUB_TOPIC,content)
    '''
    while True:
        try:
            client.check_msg()
            if (time.time() - last_message) > message_interval:
            msg = b'Hello #%d' % counter
            client.publish(topic_pub, msg)
            last_message = time.time()
            counter += 1
        except OSError as e:
    restart_and_reconnect()
    '''
    

def sub_callback(topic,msg):
    print(topic,msg)
    if topic == b'kongzhi/' + CLIENT_ID and msg == b'foo':
        # uart.send(something)
        pass
"""
```



