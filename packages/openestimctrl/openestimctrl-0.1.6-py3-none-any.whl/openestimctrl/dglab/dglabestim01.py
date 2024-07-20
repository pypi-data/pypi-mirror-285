from enum import Enum
from cffi import FFI
import traceback

ffi = FFI()
ffi.cdef("""
typedef void (*SendDataCallback)(const char* serviceUuid, const char* characteristicUuid, uint8_t* data, int length, void* userData);

typedef void (*OnChannelStrengthChange)(const uint16_t strengthA, const uint16_t strengthB, void* userData);
typedef void (*OnBatteryChange)(const uint8_t level, void* userData);

struct DGLabESTIM01EStimWave {
    uint8_t x; uint16_t y; uint8_t z;
};

void* DGLabESTIM01_new(void* sendDataCallback);
void DGLabESTIM01_delete(void* dglab);
void DGLabESTIM01_parseBLEData(void* dglab, const char* service, const char* characteristic, const uint8_t *data, int length);
void DGLabESTIM01_setStrength(void* dglab, uint16_t strengthA, uint16_t strengthB);
void DGLabESTIM01_sendWave(void* dglab, uint8_t channel, uint8_t x, uint8_t y, uint8_t z);
void DGLabESTIM01_sendWaveStruct(void* dglab, uint8_t channel, struct DGLabESTIM01EStimWave wave);
void DGLabESTIM01_setOnBatteryChange(void* dglab, OnBatteryChange onBatteryChange);
void DGLabESTIM01_setOnStrengthChange(void* dglab, OnChannelStrengthChange onChannelStrengthChange);
uint8_t DGLabESTIM01_getBattery(void* dglab);
uint16_t DGLabESTIM01_getStrengthA(void* dglab);
uint16_t DGLabESTIM01_getStrengthB(void* dglab);
void DGLabESTIM01_setUserData(void* dglab, void* userData);
void* DGLabESTIM01_getUserData(void* dglab);

 """)

class DGLabEStim01:
    @staticmethod
    def meta_service_battary():
        return "955A180A-0FE2-F5AA-A094-84B8D4F3E8AD"
    
    @staticmethod
    def meta_service_estim():
        return "955A180B-0FE2-F5AA-A094-84B8D4F3E8AD"
    
    @staticmethod
    def meta_service_battary_characteristic_battary():
        return "955A1500-0FE2-F5AA-A094-84B8D4F3E8AD"
    
    @staticmethod
    def meta_service_estim_characteristic_strength():
        return "955A1504-0FE2-F5AA-A094-84B8D4F3E8AD"
    
    @staticmethod
    def meta_service_estim_characteristic_pwm_a():
        return "955A1506-0FE2-F5AA-A094-84B8D4F3E8AD"
    
    @staticmethod
    def meta_service_estim_characteristic_pwm_b():
        return "955A1505-0FE2-F5AA-A094-84B8D4F3E8AD"
    
    class Channel(Enum):
        A = 0
        B = 1
    
    def __init__(self, library_path, callback):
        self.callback = callback
        self.lib = ffi.dlopen(library_path)
        self.handler = ffi.new_handle(self)
        self.device = self.lib.DGLabESTIM01_new(self.lib_callback)
        self.lib.DGLabESTIM01_setUserData(self.device, self.handler)
        self.lib.DGLabESTIM01_setOnBatteryChange(self.device, self.lib_callback_battery)
        self.lib.DGLabESTIM01_setOnStrengthChange(self.device, self.lib_callback_strength)
    
    
    @ffi.callback("void(const char*, const char*, uint8_t*, int, void*)")
    def lib_callback(service_uuid, characteristic_uuid, data, data_len, userData):
        self = ffi.from_handle(userData)
        if self.callback:
            try:
                self.callback(ffi.string(service_uuid).decode(), ffi.string(characteristic_uuid).decode(), ffi.unpack(data, data_len))
            except:
                traceback.print_exc()
    
    @ffi.callback("void(const uint8_t, void*)")
    def lib_callback_battery(level, userData):
        self = ffi.from_handle(userData)
        if self.callback_battery:
            try:
                self.callback_battery(level)
            except:
                traceback.print_exc()

    @ffi.callback("void(const uint16_t, const uint16_t, void*)")
    def lib_callback_strength(strengthA, strengthB, userData):
        self = ffi.from_handle(userData)
        if self.callback_strength:
            try:
                self.callback_strength(strengthA, strengthB)
            except:
                traceback.print_exc()

    def parse_ble_data(self, service, characteristic, data):
        self.lib.DGLabESTIM01_parseBLEData(self.device, service.encode(), characteristic.encode(), data, len(data))
    
    def set_strength(self, strengthA, strengthB):
        self.lib.DGLabESTIM01_setStrength(self.device, strengthA, strengthB)

    def send_wave(self, channel: Channel, x, y, z):
        self.lib.DGLabESTIM01_sendWave(self.device, channel.value, x, y, z)

    # def send_wave_struct(self, channel: Channel, wave):
    #     self.lib.DGLabESTIM01_sendWaveStruct(self.device, channel.value, wave)

    def get_battery(self):
        return self.lib.DGLabESTIM01_getBattery(self.device)
    
    def get_strength_a(self):
        return self.lib.DGLabESTIM01_getStrengthA(self.device)
    
    def get_strength_b(self):
        return self.lib.DGLabESTIM01_getStrengthB(self.device)
    