### A9g远程mqtt控制



- 搭建交叉编译环境：

  ```shell
  git clone git@github.com:pulkin/micropython.git
  git submodule update --init --recursive lib/axtls lib/GPRS_C_SDK lib/csdtk42-linux
  cd micropython
  make -C mpy-cross
  cd ports/gprs_a9
  make
  ```

- 修改module文件夹下代码，加入自己的python文件，进行预编译

  ```shell
  make clean && make
  ```

  

  > 编译完成后会有两个.lod文件，在hex目录下：
  >
  > - firmware_debug_flash.lod
  > - firmware_debug_flash.lod

- 烧录.lod程序
  ，

  > 使用[烧录工具](http://wiki.ai-thinker.com/_media/gprs/tools/firmwarw_tool_v2.1.7z)来烧录，第一次烧micropython编译的.lod文件，需要先烧firmware_debug_full.lod，然后烧写firmware_debug_flash.lod，后续更新只需要烧写firmware_debug_flash.lod

- 使用uPyCraft【Windows】，miniterm【Linux】进行测试/开发

------------

示例程序功能：

- 读取串口数据，publish到指定的服务器上

- 异步读取最新一条收到的SMS短信，写入串口
- 读取GPS数据上传到mqtt服务区上

