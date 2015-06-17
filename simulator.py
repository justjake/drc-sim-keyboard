import construct
import select
import array
import pygame
import time

import services
from H264Decoder import H264Decoder
from app import App
from controls.base import (
    button_mask, extra_button_mask, UnionController, scale
)
from controls.wireless import ProMap360
from controls.mouse import KeyboardMouse
from assets import ASSET_DICT
from controller_viewer import Visualizer
from util import log, GAMEPAD_DIM


# JOYSTICK = False
JOYSTICK = True
EVT_SEND_HID = pygame.USEREVENT


def wiiu_axis(orig):
    """
    given a joystick axis motion, scale into Wii U space
    """
    if abs(orig) < 0.0001:
        # unsure why this starts as this value 0x800
        return 0x800
    return int(scale(orig, -1, 1, 900, 3200))


class Simulator(App):
    """
    customized DRC simulator using drc-sim-keyboard clases and following pep8
    """
    def __init__(self):
        super(Simulator, self).__init__("DRC Simulator")
        self.vid_offset = (409, 247)
        self.vid_frame = pygame.Surface(GAMEPAD_DIM)
        self.vid_rect = pygame.Rect(self.vid_offset, GAMEPAD_DIM)
        self.bg = ASSET_DICT['gamepad']

        controllers = []

        if JOYSTICK:
            # set up joystick
            pygame.joystick.init()
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            # self.ctlr = Xbox360Wireless(joystick)
            controllers.append(ProMap360(joystick))

        controllers.append(KeyboardMouse())
        self.ctlr = UnionController(controllers)

        self.decoder = H264Decoder(
            GAMEPAD_DIM,
            GAMEPAD_DIM,
            # pygame.display.get_surface().get_size(),
            self.vid_frame)

        self.service_handlers = {
            services.MSG_S: services.ServiceMSG(),
            services.VID_S: services.ServiceVSTRM(self.decoder),
            services.AUD_S: services.ServiceASTRM(),
            services.CMD_S: services.ServiceCMD()
        }

        self.l_stick_prev = (0, 0)
        self.r_stick_prev = (0, 0)
        self.vis = Visualizer(self)

        self._hid_seq_id = 0
        pygame.time.set_timer(EVT_SEND_HID, int((1. / 180.) * 1000.))

    def seq_id(self):
        """
        returns the current hid_seq_id and then increments it.
        """
        hid_seq_id = self._hid_seq_id
        self._hid_seq_id = (hid_seq_id + 1) % 65535  # max unsigned short
        return hid_seq_id

    def hid_snd(self):
        report = array.array('H', '\0\0' * 0x40)
        
        # 16bit LE @ 0 seq_id
        # seems to be ignored
        report[0] = self.seq_id()
        # 16bit @ 2
        button_bits = button_mask(self.ctlr)

        # save sticks around for rendering joystick fiddling
        self.l_stick_prev = self.ctlr.left_stick()
        self.r_stick_prev = self.ctlr.right_stick()

        # bada bing bada boom engineer sticks
        l_horiz, l_vert = self.l_stick_prev
        r_horiz, r_vert = self.r_stick_prev
        report[3 + 0] = wiiu_axis(l_horiz)
        report[3 + 1] = wiiu_axis(l_vert)
        report[3 + 2] = wiiu_axis(r_horiz)
        report[3 + 3] = wiiu_axis(r_vert)

        report[1] = (button_bits >> 8) | ((button_bits & 0xff) << 8)
        
        # touchpanel crap @ 36 - 76
        byte_18 = 0
        byte_17 = 3
        byte_9b8 = 0
        byte_9fd = 6
        umi_fw_rev = 0x40
        byte_9fb = 0
        byte_19 = 2
        # jakenote: these changes are untested!!! beware.
        if (pygame.mouse.get_pressed()[0] and 
                not pygame.event.get_grab() and
                # mouse was over the "screen" when clicked
                self.vid_rect.collidepoint(self.mouse.get_pos())):
            point = pygame.mouse.get_pos()
            in_x = point[0] - self.vid_offset[0]
            in_y = point[1] - self.vid_offset[1]
            log('touchscreen click at {x, y}'.format(x, y), 'HID')
            x = int(scale(point[0], self.vid_rect.left, self.vid_rect.right, 200, 3800))
            y = int(scale(point[1], self.vid_rect.top, self.vid_rect.bottom, 200, 3800))
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
        report[40] |= extra_button_mask(self.ctlr)
        
        report[0x3f] = 0xe000
        #print report.tostring().encode('hex')
        services.HID_S.sendto(report, ('192.168.1.10', services.PORT_HID))

    def handle_event(self, event):
        self.quit_if_needed(event)
        self.ctlr.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSLASH:
                # TODO: What message is this?
                services.MSG_S.sendto('\1\0\0\0', ('192.168.1.10', services.PORT_MSG))

        elif event.type == EVT_SEND_HID:
            self.hid_snd()

    def render(self):
        self.screen.fill(15)
        self.screen.blit(self.bg, self.offset)
        self.vis.render(self.l_stick_prev, self.r_stick_prev)
        self.screen.blit(self.vid_frame, self.vid_offset)

        # this stuff came from the default event loop in drc-sim.py
        # TODO see if I'm mis-managing it somehow such that video never works
        rlist, wlist, xlist = select.select(
            self.service_handlers.keys(), (), (), 1)

        if not rlist:
            return

        for sock in rlist:
            self.service_handlers[sock].update(sock.recvfrom(2048)[0])

    def clean_up(self):
        for s in self.service_handlers.itervalues():
            s.close()

if __name__ == '__main__':
    app = Simulator()
    app.main()
