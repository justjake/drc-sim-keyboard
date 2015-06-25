import array
from app import App
import InputData
from controls.mouse import KeyboardMouse
from controls.base import (
    Controls, button_mask, inspect_mask, BUTTONS, scale,
    extra_button_mask,
    wiiu_axis
)
from construct import (
    Container
)


def button_container(controls):
    c = Container()
    for button in BUTTONS.iterkeys():
        setattr(c, button.lower(), controls.invoke(button.lower()))
    return c


def build_controls(controls):
    return InputData.Buttons.build(button_container(controls))


class DummyControls(Controls):
    def a(self):
        return True

    def zl(self):
        return True

    def l(self):
        return True


def int_of_bytes(bytestring):
    return int(bytestring.encode('hex'), 16)


controller = DummyControls()

reg = inspect_mask(button_mask(controller))
newer = inspect_mask(int_of_bytes(build_controls(controller)))
print "{0} regular".format(reg)
print "{0} construct".format(newer)


def create_response(ctlr, seq_id=0):
    report = array.array('H', '\0\0' * 0x40)

    # 16bit LE @ 0 seq_id
    # seems to be ignored
    report[0] = seq_id()
    # 16bit @ 2
    button_bits = button_mask(ctlr)

    # save sticks around for rendering joystick fiddling
    left_stick = ctlr.left_stick()
    right_stick = ctlr.right_stick()

    # bada bing bada boom engineer sticks
    l_horiz, l_vert = left_stick
    r_horiz, r_vert = right_stick
    report[3 + 0] = wiiu_axis(l_horiz)
    report[3 + 1] = wiiu_axis(l_vert)
    report[3 + 2] = wiiu_axis(r_horiz)
    report[3 + 3] = wiiu_axis(r_vert)

    report[1] = (button_bits >> 8) | ((button_bits & 0xff) << 8)

    # 0   u16 seq_id;
    # 1   u16 buttons;  // see ButtonsMask
    # 2   u8 power_status;  // see PowerStatusMask
    #     u8 battery_charge;
    # 3   u16 left_stick_x;
    # 4   u16 left_stick_y;
    # 5   u16 right_stick_x;
    # 6   u16 right_stick_y;
    # 7   u8 audio_volume;
    # 7.5 AccelerometerData accelerometer; // FUCK (this is why looking into structs)
    #     GyroscopeData gyro;
    #     MagnetData magnet;
    #     TouchscreenData touchscreen;
    #     char unk0[4];
    #     u8 extra_buttons;  // see ExtraButtonsMask
    #     char unk1[46];
    #     u8 fw_version_neg;  // ~fw_version


    # touchpanel crap @ 36 - 76
    byte_18 = 0
    byte_17 = 3
    byte_9b8 = 0
    byte_9fd = 6
    umi_fw_rev = 0x40
    byte_9fb = 0
    byte_19 = 2
    # TODO use controller for thisj
    touch = ctlr.touch()
    if touch is not None:
        in_x, in_y = touch
        x = int(scale(in_x, 0, 854, 200, 3800))
        y = int(scale(in_y, 0, 480, 200, 3800))
        z1 = 2000

        for i in xrange(10):
            report[18 + i * 2 + 0] = 0x80 | x
            report[18 + i * 2 + 1] = 0x80 | y

        report[18 + 0 * 2 + 0] |= ((z1 >> 0) & 7) << 12
        report[18 + 0 * 2 + 1] |= ((z1 >> 3) & 7) << 12
        report[18 + 1 * 2 + 0] |= ((z1 >> 6) & 7) << 12
        report[18 + 1 * 2 + 1] |= ((z1 >> 9) & 7) << 12

    report[18 + 3 * 2 + 1] |= ((byte_17 >> 0) & 7) << 12
    report[18 + 4 * 2 + 0] |= ((byte_17 >> 3) & 7) << 12
    report[18 + 4 * 2 + 1] |= ((byte_17 >> 6) & 3) << 12

    report[18 + 5 * 2 + 0] |= ((byte_9fd >> 0) & 7) << 12
    report[18 + 5 * 2 + 1] |= ((byte_9fd >> 3) & 7) << 12
    report[18 + 6 * 2 + 0] |= ((byte_9fd >> 6) & 3) << 12

    report[18 + 7 * 2 + 0] |= ((umi_fw_rev >> 4) & 7) << 12

    # not my comment. spooky.
    # TODO checkout what's up with | 4
    report[18 + 9 * 2 + 1] |= ((byte_19 & 2) | 4) << 12

    # 8bit @ 80
    # i didn't want to move this up because I'm
    # worried its location here is important. TODO
    # think about it.
    report[40] |= extra_button_mask(ctlr)
    # log('report 40 = {n}'.format(n=report[40]))

    report[0x3f] = 0xe000
    return report


def accel_container(ctlr):
    return Container(
        x_accel=0,
        y_accel=0,
        z_accel=0)


def gyro_container(ctlr):
    return Container(
        roll=0,
        yaw=0,
        pitch=0,
    )


def touch_container(ctlr):
    in_x, in_y = ctlr.touch()
    x = int(scale(in_x, 0, 854, 200, 3800))
    y = int(scale(in_y, 0, 480, 200, 3800))
    raise NotImplementedError # got bored



def controller_container(ctlr, seq_id):
    l_x, l_y = ctlr.left_stick()
    r_x, r_y, = ctlr.right_stick()
    return Container(
        seq_id=seq_id,
        buttons=button_container(ctlr),
        power_status=0,
        left_stick_x=wiiu_axis(l_x),
        left_stick_y=wiiu_axis(l_y),
        right_stick_x=wiiu_axis(r_x),
        right_stick_y=wiiu_axis(r_y),
        audio_volume=0,
        accelerometer=accel_container(ctlr),
        gyro=gyro_container(ctlr),
        magnet=None,
        touchscreen=touch_container(ctlr),
        unknown0=0,
        extra_buttons=extra_buttons_container(ctlr),
        unknown1=0,
        fw_version_neg=0xe000
    )
