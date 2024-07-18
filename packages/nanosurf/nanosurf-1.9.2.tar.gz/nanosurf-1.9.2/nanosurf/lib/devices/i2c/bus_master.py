
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


import enum
from typing import Union
from nanosurf.lib.spm.com_proxy import Spm
from nanosurf.lib.spm.studio import Studio

class I2CBusID(enum.IntEnum):
    Unassigned = -1
    User      = 0x2000300
    HV        = 0x2000320
    ScanHead  = 0x2000360
    Interface = 0x2000340

class I2CInstances(enum.IntEnum):
    MAIN_APP = 0
    CONTROLLER = 1

class I2CMasterType(enum.IntEnum):
    AUTO_DETECT = -1
    EMBEDDED_AVALON = 0
    ACCESSORY_MASTER = 1
    EMBEDDED_LINUX = 2

class I2CBusSpeed(enum.IntEnum):
    kHz_Default = 0
    kHz_100 = 1
    kHz_200 = 2
    kHz_400 = 3

class I2CSyncing(enum.IntEnum):
    NoSync = 0
    Sync = 1
    
class I2CByteMode(enum.IntEnum):
    SingleByteOff = 0
    SingleByteOn = 1

class I2COffsetMode(enum.IntEnum):
    NoOffset = 0
    U8Bit = 1
    U16Bit_MSBFiRST = 2
    U16Bit_LSBFiRST = 3

class I2CBusMaster():
        
    _active_chip_ref = int(0)
    _next_chip_ref = 1

    def __init__(self, spm_root:Union[Studio, Spm], bus_id: I2CBusID, instance_id: I2CInstances = I2CInstances.CONTROLLER, master_type: I2CMasterType = I2CMasterType.AUTO_DETECT, bus_speed: I2CBusSpeed = I2CBusSpeed.kHz_400):
        self._spm_root = spm_root
        self._spm = spm_root.spm
 
        if self._spm.is_studio:
            self._obj_i2c = self._spm.workflow.i2c
            self._map_bus_type_to_studio_enum = {
                I2CMasterType.ACCESSORY_MASTER: self._obj_i2c.enums.Bus_types.mcp2221,
                I2CMasterType.EMBEDDED_AVALON: self._obj_i2c.enums.Bus_types.cx_user,
                I2CMasterType.EMBEDDED_LINUX: self._obj_i2c.enums.Bus_types.cx_linux,
            }
            self._map_bus_id_to_studio_enum = {
                I2CBusID.User: self._obj_i2c.enums.Bus_ids.user,
                I2CBusID.ScanHead: self._obj_i2c.enums.Bus_ids.hv,
                I2CBusID.Interface: self._obj_i2c.enums.Bus_ids.interface_box,
                I2CBusID.HV: self._obj_i2c.enums.Bus_ids.hv,
            }
            self._map_offset_mode_to_studio_enum = {
                I2COffsetMode.NoOffset: self._obj_i2c.enums.Offset_type.none,
                I2COffsetMode.U16Bit_LSBFiRST: self._obj_i2c.enums.Offset_type.u16lsb,
                I2COffsetMode.U16Bit_MSBFiRST: self._obj_i2c.enums.Offset_type.u16msb,
                I2COffsetMode.U8Bit: self._obj_i2c.enums.Offset_type.u8,
            }
            self._map_sync_mode_to_studio_enum = {
                I2CSyncing.NoSync: self._obj_i2c.enums.I2c_write_sync_mode.nosync,
                I2CSyncing.Sync: self._obj_i2c.enums.I2c_write_sync_mode.sync,
            }
            self._map_byte_mode_to_studio_enum = {
                I2CByteMode.SingleByteOff: self._obj_i2c.enums.I2c_single_byte_mode.off,
                I2CByteMode.SingleByteOn: self._obj_i2c.enums.I2c_single_byte_mode.on,
            }
            self._map_bus_speed_mode_to_studio_enum = {
                I2CBusSpeed.kHz_Default: self._obj_i2c.enums.I2c_speed.khz_default,
                I2CBusSpeed.kHz_100: self._obj_i2c.enums.I2c_speed.khz_100,
                I2CBusSpeed.kHz_200: self._obj_i2c.enums.I2c_speed.khz_200,
                I2CBusSpeed.kHz_400: self._obj_i2c.enums.I2c_speed.khz_400,
            }
        else:
            self._obj_i2c = self._spm.application.CreateTestObj

        self._rx_packet_buffer_len = 50
        self._tx_packet_buffer_len = 50
        self._instance_id = instance_id
        self._master_type = master_type 
        self._bus_id = bus_id
        self._bus_speed = bus_speed
        if self._master_type == I2CMasterType.AUTO_DETECT:
            self._master_type = self._auto_set_bus_master()

    def assign_i2c_bus(self,  bus_id: I2CBusID, bus_speed: I2CBusSpeed):
        self._bus_id = bus_id
        self._bus_speed = bus_speed

    def assign_chip(self, chip: 'I2CChip'):
        chip.setup_bus_connection(self, self.create_unique_chip_id())

    def setup_metadata(self, addr: int, offset_mode: I2COffsetMode, auto_lock: bool = True):
        if self._spm.is_studio:
            try:
                bus_type = self._map_bus_type_to_studio_enum[self._master_type]
            except Exception:
                raise ValueError(f"Selected bus master '{self._master_type}' is not available.")
            try:
                bus_id = self._map_bus_id_to_studio_enum[self._bus_id]
            except Exception:
                raise ValueError(f"Selected bus id '{self._bus_id}' is not available.")
            
            bus_addr = self._obj_i2c.map_bus_id_to_address(bus_type, bus_id)
            self._metadata = self._obj_i2c.create_metadata(bus_type, bus_addr, addr, convert_table=True, parse_tree=True)  
            self._metadata['offset_type'] = self._map_offset_mode_to_studio_enum[offset_mode]      
            self._metadata['auto_lock'] = auto_lock          
            self._metadata['max_length_rx'] = self._rx_packet_buffer_len          
            self._metadata['max_length_tx'] = self._tx_packet_buffer_len          
            self._metadata['write_sync_mode'] = self._map_sync_mode_to_studio_enum[I2CSyncing.NoSync]       
            self._metadata['single_byte_mode'] = self._map_byte_mode_to_studio_enum[I2CByteMode.SingleByteOff]         
            self._metadata['max_speed'] = self._map_bus_speed_mode_to_studio_enum[self._bus_speed]         
                
        else:
            self._obj_i2c.I2CSetupMetaDataEx(self._rx_packet_buffer_len, self._tx_packet_buffer_len, I2CSyncing.NoSync, I2CByteMode.SingleByteOff, self._bus_speed)
            self._obj_i2c.I2CSetupMetaData(self._instance_id, self._master_type, self._bus_id, addr, offset_mode, auto_lock)

    def check_connection(self, chip: 'I2CChip') -> bool:
        self.activate_chip(chip)
        if self._spm.is_studio:
            is_connected = self._obj_i2c.connected(self._metadata) > 0
        else:
            is_connected = self._obj_i2c.I2CIsConnected > 0
        return is_connected

    @classmethod
    def get_active_chip_id(cls) -> int:
        return I2CBusMaster._active_chip_ref

    @classmethod
    def create_unique_chip_id(cls) -> int:
        I2CBusMaster._next_chip_ref += 1
        return I2CBusMaster._next_chip_ref

    def activate_chip(self, chip: 'I2CChip'):
        if chip.get_chip_ref() != I2CBusMaster._active_chip_ref:
            chip.activate()
            I2CBusMaster._active_chip_ref = chip.get_chip_ref()

    def write_bytes(self, offset: int, data: list[int]) -> bool:
        done = False
        try:
            if self._spm.is_studio:
                done = self._obj_i2c.write(self._metadata, offset, data) == 0
            else:
                done: bool = self._obj_i2c.I2CWrite(offset, len(data), data)
        except Exception:
            pass
        return done

    def read_bytes(self, offset:int, data_count:int) -> list[int]:
        try:
            if self._spm.is_studio:
                data: list[int] = list(self._obj_i2c.read(self._metadata, offset, data_count)) 
            else:
                data: list[int] = list(self._obj_i2c.I2CReadEx(offset, data_count)) 
        except Exception:
            data: list[int] = []
        return data

    def _auto_set_bus_master(self) -> I2CMasterType:
        detected_master = I2CMasterType.AUTO_DETECT
        if self._spm.is_studio:
            if self._bus_id == I2CBusID.User:
                detected_master = I2CMasterType.EMBEDDED_AVALON
            else:
                detected_master = I2CMasterType.EMBEDDED_LINUX
        else:
            if self._instance_id == I2CInstances.CONTROLLER:
                if self._spm_root.get_controller_type() == self._spm_root.ControllerType.CX:
                    if self._spm_root.get_firmware_type() == self._spm_root.FirmwareType.LINUX:
                        if self._bus_id == I2CBusID.User:
                            detected_master = I2CMasterType.EMBEDDED_AVALON
                        else:
                            detected_master = I2CMasterType.EMBEDDED_LINUX
                    else:
                        detected_master = I2CMasterType.EMBEDDED_AVALON
            elif self._instance_id == I2CInstances.MAIN_APP:
                detected_master = I2CMasterType.ACCESSORY_MASTER
        return detected_master

class I2CChip():

    def __init__(self, bus_addr: int, offset_mode: I2COffsetMode, name: str = "", bus_master: I2CBusMaster = None, auto_lock: bool = True):
        """ Minimal initialization is bus_addr and offset_mode. connection to bus master can be done later by bus_master.assign_chip() """
        self._bus_master = bus_master
        self._chip_ref = -1
        self.name = name
        self.bus_address = bus_addr
        self.offset_mode = offset_mode
        self.auto_lock = auto_lock
        if self._bus_master is not None:
            self._bus_master.assign_chip(self)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name:str):
        self.__name = name

    @property
    def bus_address(self) -> int:
        return self.__bus_addr

    @bus_address.setter
    def bus_address(self, addr: int):
        self.__bus_addr = addr

    @property
    def offset_mode(self) -> I2COffsetMode:
        return self.__offset_mode

    @offset_mode.setter
    def offset_mode(self, mode: I2COffsetMode):
        self.__offset_mode = mode

    @property
    def auto_lock(self) -> bool:
        return self.__auto_lock

    @auto_lock.setter
    def auto_lock(self, lock:bool):
        self.__auto_lock = lock

    def setup_bus_connection(self, bus_master: I2CBusMaster, chip_ref: int):
        self._bus_master = bus_master
        self._chip_ref = chip_ref

    def activate(self):
        self._bus_master.setup_metadata(self.bus_address, self.offset_mode, self.auto_lock)

    def get_chip_ref(self) -> int:
        return self._chip_ref

    def get_bus(self):
        self._bus_master.activate_chip(self)

    def is_connected(self) -> bool:
        return self._bus_master.check_connection(self)

    def write_bytes_with_offset(self, offset: int, data: list[int]) -> bool:
        self.get_bus()
        done = self._bus_master.write_bytes(offset, data)
        return done

    def write_byte_with_offset(self, offset:int, data:int) -> bool:
        return self.write_bytes_with_offset(offset, [data])

    def write_bytes(self, data: list[int]) -> bool:
        return self.write_bytes_with_offset(0, data)

    def write_byte(self, data: int) -> bool:
        return self.write_bytes_with_offset(0, [data])

    def read_bytes_with_offset(self, offset:int, count: int) -> list[int]:
        self.get_bus()
        data = self._bus_master.read_bytes(offset, count)
        return data

    def read_byte_with_offset(self, offset: int) -> int:
        data = self.read_bytes_with_offset(offset, count=1)
        return data[0]

    def read_bytes(self, count: int) -> list[int]:
        data = self.read_bytes_with_offset(0, count)
        return data

    def read_byte(self) -> int:
        data = self.read_bytes_with_offset(0, count=1)
        return data[0]

