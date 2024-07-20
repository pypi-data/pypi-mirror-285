from enum import Enum
from cffi import FFI
import struct
import traceback

ffi = FFI()
ffi.cdef("""
typedef void (*SendDataCallback)(const char* serviceUuid, const char* characteristicUuid, uint8_t* data, int length, void* userData);

struct YokoNexES01Status {
    uint8_t connection;
    bool enabled;
    uint16_t strength;
    uint8_t mode;
};
                 
struct YokoNexES01Accel {
    uint16_t accX;
    uint16_t accY;
    uint16_t accZ;
    uint16_t gyroX;
    uint16_t gyroY;
    uint16_t gyroZ;
};

typedef void (*OnChannelStatusChange)(struct YokoNexES01Status status, void* userData);
typedef void (*OnMotorStatusChange)(const uint8_t status, void* userData);
typedef void (*OnBatteryStatusChange)(const uint8_t battery, void* userData);
typedef void (*OnStepStatusChange)(const uint16_t step, void* userData);
typedef void (*OnAngleStatusChange)(struct YokoNexES01Accel accel, void* userData);
typedef void (*OnException)(const uint8_t code, void* userData);

void* YokoNexES01_new(void* sendDataCallback);
void YokoNexES01_delete(void* yokoNexES01);
void YokoNexES01_parseBLEData(void* yokoNexES01, const uint8_t* data, int length);
void YokoNexES01_setEStim(void* yokoNexES01, uint8_t channel, bool enabled, uint16_t strength, uint8_t mode, uint8_t frequency, uint8_t pulseWidth);
void YokoNexES01_triggerMotor(void* yokoNexES01, uint8_t mode);
void YokoNexES01_setStep(void* yokoNexES01, uint8_t mode);
void YokoNexES01_setAngle(void* yokoNexES01, uint8_t mode);
void YokoNexES01_query(void* yokoNexES01, uint8_t query);
void YokoNexES01_setUserData(void* yokoNexES01, void* userData);
void* YokoNexES01_getUserData(void* yokoNexES01);
void YokoNexES01_setOnChannelAStatusChange(void* yokoNexES01, OnChannelStatusChange callback);
void YokoNexES01_setOnChannelBStatusChange(void* yokoNexES01, OnChannelStatusChange callback);
void YokoNexES01_setOnMotorStatusChange(void* yokoNexES01, OnMotorStatusChange callback);
void YokoNexES01_setOnBatteryStatusChange(void* yokoNexES01, OnBatteryStatusChange callback);
void YokoNexES01_setOnStepStatusChange(void* yokoNexES01, OnStepStatusChange callback);
void YokoNexES01_setOnAngleStatusChange(void* yokoNexES01, OnAngleStatusChange callback);
void YokoNexES01_setOnException(void* yokoNexES01, OnException callback);
uint8_t YokoNexES01_getLastException(void* yokoNexES01);
uint8_t YokoNexES01_getBattery(void* yokoNexES01);
uint16_t YokoNexES01_getStep(void* yokoNexES01);
void YokoNexES01_getAccel(void* yokoNexES01, struct YokoNexES01Accel* accel);
void YokoNexES01_getChannelA(void* yokoNexES01, struct YokoNexES01Status* status);
void YokoNexES01_getChannelB(void* yokoNexES01, struct YokoNexES01Status* status);
uint8_t YokoNexES01_getMotor(void* yokoNexES01);
 """)

class YokoNexES01:
    @staticmethod
    def meta_service():
        return "0000ff30-0000-1000-8000-00805f9b34fb"
    
    @staticmethod
    def meta_service_characteristic_tx():
        return "0000ff31-0000-1000-8000-00805f9b34fb"
    
    @staticmethod
    def meta_service_characteristic_rx():
        return "0000ff32-0000-1000-8000-00805f9b34fb"
    
    class Channel(Enum):
        A = 0x01
        B = 0x02
        BOTH = 0x03

    class Mode(Enum):
        MODE_INTERNAL_1 = 0x01
        MODE_INTERNAL_2 = 0x02
        MODE_INTERNAL_3 = 0x03
        MODE_INTERNAL_4 = 0x04
        MODE_INTERNAL_5 = 0x05
        MODE_INTERNAL_6 = 0x06
        MODE_INTERNAL_7 = 0x07
        MODE_INTERNAL_8 = 0x08
        MODE_INTERNAL_9 = 0x09
        MODE_INTERNAL_10 = 0x0A
        MODE_INTERNAL_11 = 0x0B
        MODE_INTERNAL_12 = 0x0C
        MODE_INTERNAL_13 = 0x0D
        MODE_INTERNAL_14 = 0x0E
        MODE_INTERNAL_15 = 0x0F
        MODE_INTERNAL_16 = 0x10
        MODE_CUSTOM = 0x11
    
    class Motor(Enum):
        OFF = 0x00
        ON = 0x01
        INTERNAL_1 = 0x11
        INTERNAL_2 = 0x12
        INTERNAL_3 = 0x13
    
    class Step(Enum):
        OFF = 0x00
        ON = 0x01
        CLEAR = 0x02
        PAUSE = 0x03
        RESUME = 0x04

    class Angle(Enum):
        OFF = 0x00
        ON = 0x01
    
    class Query(Enum):
        CHANNEL_A = 0x01
        CHANNEL_B = 0x02
        MOTOR = 0x03
        BATTERY = 0x04
        STEP = 0x05
        ANGLE = 0x06

    class ChannelState(Enum):
        NOT_PLUG_IN = 0x00
        PLUG_IN_RUNNING = 0x01
        PLUG_IN_IDLE = 0x02

    callback_channel_a_status = None
    callback_channel_b_status = None
    callback_motor_status = None
    callback_battery_status = None
    callback_step_status = None
    callback_angle_status = None
    callback_exception = None
    
    def __init__(self, library_path, callback):
        self.callback = callback
        self.handler = ffi.new_handle(self)
        self.lib = ffi.dlopen(library_path)
        self.device = self.lib.YokoNexES01_new(self.lib_callback)
        self.lib.YokoNexES01_setUserData(self.device, self.handler)
        self.lib.YokoNexES01_setOnChannelAStatusChange(self.device, self.lib_callback_channel_a_status)
        self.lib.YokoNexES01_setOnChannelBStatusChange(self.device, self.lib_callback_channel_b_status)
        self.lib.YokoNexES01_setOnMotorStatusChange(self.device, self.lib_callback_motor_status)
        self.lib.YokoNexES01_setOnBatteryStatusChange(self.device, self.lib_callback_battery_status)
        self.lib.YokoNexES01_setOnStepStatusChange(self.device, self.lib_callback_step_status)
        self.lib.YokoNexES01_setOnAngleStatusChange(self.device, self.lib_callback_angle_status)
        self.lib.YokoNexES01_setOnException(self.device, self.lib_callback_exception)

    
    @ffi.callback("void(const char*, const char*, uint8_t*, int, void*)")
    def lib_callback(service_uuid, characteristic_uuid, data, data_len, userData):
        self = ffi.from_handle(userData)
        if self.callback:
            try:
                self.callback(ffi.string(service_uuid).decode(), ffi.string(characteristic_uuid).decode(), ffi.unpack(data, data_len))
            except:
                traceback.print_exc()

    @ffi.callback("void(struct YokoNexES01Status, void*)")
    def lib_callback_channel_a_status(status, userData):
        self = ffi.from_handle(userData)
        if self.callback_channel_a_status:
            try:
                self.callback_channel_a_status(YokoNexES01.ChannelState(status.connection), status.enabled, status.strength, YokoNexES01.Mode(status.mode))
            except:
                traceback.print_exc()

    @ffi.callback("void(struct YokoNexES01Status, void*)")
    def lib_callback_channel_b_status(status, userData):
        self = ffi.from_handle(userData)
        if self.callback_channel_b_status:
            try:
                self.callback_channel_b_status(YokoNexES01.ChannelState(status.connection), status.enabled, status.strength, YokoNexES01.Mode(status.mode))
            except:
                traceback.print_exc()

    @ffi.callback("void(const uint8_t, void*)")
    def lib_callback_motor_status(status, userData):
        self = ffi.from_handle(userData)
        if self.callback_motor_status:
            try:
                self.callback_motor_status(YokoNexES01.Motor(status))
            except:
                traceback.print_exc()

    @ffi.callback("void(const uint8_t, void*)")
    def lib_callback_battery_status(battery, userData):
        self = ffi.from_handle(userData)
        if self.callback_battery_status:
            try:
                self.callback_battery_status(battery)
            except:
                traceback.print_exc()

    @ffi.callback("void(const uint16_t, void*)")
    def lib_callback_step_status(step, userData):
        self = ffi.from_handle(userData)
        if self.callback_step_status:
            try:
                self.callback_step_status(step)
            except:
                traceback.print_exc()

    @ffi.callback("void(struct YokoNexES01Accel, void*)")
    def lib_callback_angle_status(accel, userData):
        self = ffi.from_handle(userData)
        if self.callback_angle_status:
            try:
                self.callback_angle_status(accel.accX, accel.accY, accel.accZ, accel.gyroX, accel.gyroY, accel.gyroZ)
            except:
                traceback.print_exc()

    @ffi.callback("void(const uint8_t, void*)")
    def lib_callback_exception(code, userData):
        self = ffi.from_handle(userData)
        if self.callback_exception:
            try:
                self.callback_exception(code)
            except:
                traceback.print_exc()

    def __del__(self):
        self.lib.YokoNexES01_delete(self.device)

    def parse_ble_data(self, data):
        packed_data = None
        if type(data) == bytearray:
            packed_data = ffi.new("uint8_t[]", bytes(data))
        else:
            packed_data = ffi.new("uint8_t[]", data)
        self.lib.YokoNexES01_parseBLEData(self.device, packed_data, len(data))
    
    def set_on_channel_a_status_change(self, callback):
        self.callback_channel_a_status = callback
    
    def set_on_channel_b_status_change(self, callback):
        self.callback_channel_b_status = callback

    def set_on_motor_status_change(self, callback):
        self.callback_motor_status = callback

    def set_on_battery_status_change(self, callback):
        self.callback_battery_status = callback

    def set_on_step_status_change(self, callback):
        self.callback_step_status = callback

    def set_on_angle_status_change(self, callback):
        self.callback_angle_status = callback

    def set_on_exception(self, callback):
        self.callback_exception = callback

    def set_estim(self, channel: Channel, enabled, strength, mode: Mode, frequency, pulse_width):
        self.lib.YokoNexES01_setEStim(self.device, channel.value, enabled, strength, mode.value, frequency, pulse_width)

    def trigger_motor(self, mode: Motor):
        self.lib.YokoNexES01_triggerMotor(self.device, mode.value)

    def set_step(self, mode: Step):
        self.lib.YokoNexES01_setStep(self.device, mode.value)

    def set_angle(self, mode: Angle):
        self.lib.YokoNexES01_setAngle(self.device, mode.value)

    def query(self, query: Query):
        self.lib.YokoNexES01_query(self.device, query.value)

    def get_last_exception(self):
        return self.lib.YokoNexES01_getLastException(self.device)
    
    def get_battery(self):
        return self.lib.YokoNexES01_getBattery(self.device)
    
    def get_step(self):
        return self.lib.YokoNexES01_getStep(self.device)
    