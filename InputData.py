"""
pack wire format of controls

see http://libdrc.org/docs/re/sc-input.html

TODO tests
"""
from construct import (
        ULint8, 
        ULint16, 
        Array, 
        Struct, 
        BitStruct, 
        BitField, 
        Byte, 
        SLInt16, 
        Padding,
        Rename
        )

u16 = ULint16
s16 = SLInt16
u8 = ULint8

AccelerometerData = Struct("AccelerometerData",
        s16("x_accel"),
        s16("y_accel"),
        s16("z_accel"))

Dummy24Bits = BitStruct("s24",
        BitField("value", 24))

GyroscopeData = Struct("AccelerometerData",
        Rename("roll", Dummy24Bits),
        Rename("yaw", Dummy24Bits),
        Rename("pitch", Dummy24Bits))

MagnetData = Struct("MagnetData", Array(6, Byte("unknown")))

### Some notes on the Point field usage
## Touchscreen Pressure
# Stored as a 12 bit integer in the extra data of the first two points. It is
# not yet known how to translate this value to a usable pressure value -
# currently it is assumed to be a resistance value reading.
## UIC firmware version
# 16 bit integer stored in the extra data of points 6 to 8 (only one bit of the
# first coordinate of point 6 is used).
Point = Struct("Point", Array(2, BitStruct("Coordinate",
    Padding(1),
    BitField("extra", 3),
    BitField("value", 12))))

TouchscreenData = Struct("TouchscreenData", Array(10, Point))

# the real shebang
InputData = Struct("InputData",
        u16("seq_id"),
        u16("buttons"), # bitmask, TODO lay out.
        u8("power_status"), # bitmask, TODO lay out
        u16("left_stick_x"),
        u16("left_stick_y"),
        u16("right_stick_x"),
        u16("right_stick_y"),
        u8("audio_volume"),
        Rename("accelerometer", AccelerometerData),
        Rename("gyro", GyroscopeData),
        Rename("magnet", MagnetData),
        Rename("touchscreen", TouchscreenData),
        Array(4, Byte("unkown0")),
        u8("extra_buttons"),
        Array(46, Byte("unknown1")),
        u8("fw_version_neg")) # ~fw_version
