# OpenEStimCtrl Python Binding with cffi

## How to use

Download dynamic library from `OpenEStimCtrl` repository and put it in the same directory for your script.

```python
from openestimctrl import YokoNexES01

def send_ble_data(service, characteristic, data):
    pass

# Pass the path to the dynamic library and a callback function to send data to BLE device
protocol = YokoNexES01('OpenEstimCtrl.dll', send_ble_data)
```


## 如何使用

从 `OpenEStimCtrl` 仓库下载动态库并将其放在脚本的相同目录中。

```python
from openestimctrl import YokoNexES01

def send_ble_data(service, characteristic, data):
    pass

# 传递动态库的路径和一个回调函数，用于将数据发送到BLE设备
protocol = YokoNexES01('OpenEstimCtrl.dll', send_ble_data)
```