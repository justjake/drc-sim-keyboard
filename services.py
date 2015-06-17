import array
import construct
import socket
import pyaudio
import pygame
from util import log, GAMEPAD_DIM


def service_addend(ip):
    if int(ip.split('.')[3]) == 10:
        return 0
    else:
        return 100


def udp_service(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    actual_port = port + service_addend(ip)
    try:
        sock.bind((ip, actual_port))
    except:
        log("couldn't bind {ip}:{port}".format(ip=ip, port=actual_port),
            "NETWORK")
        log("trying {ip}:{port} instead".format(
            ip='0.0.0.0',
            port=actual_port),
            "NETWORK")
        sock.bind(('0.0.0.0', actual_port))
    return sock

PORT_MSG = 50010
PORT_VID = 50020
PORT_AUD = 50021
PORT_HID = 50022
PORT_CMD = 50023

# hack for now, replace with dhcp result
# Perhaps switch to '0.0.0.0' by default
LOCAL_IP = '192.168.1.11'

MSG_S = udp_service(LOCAL_IP, PORT_MSG)
VID_S = udp_service(LOCAL_IP, PORT_VID)
AUD_S = udp_service(LOCAL_IP, PORT_AUD)
HID_S = udp_service(LOCAL_IP, PORT_HID)
CMD_S = udp_service(LOCAL_IP, PORT_CMD)


class ServiceBase(object):
    def __init__(s):
        s.seq_id_expect = None

    def update_seq_id(s, seq_id):
        ret = True
        if s.seq_id_expect is None:
            s.seq_id_expect = seq_id
        elif s.seq_id_expect != seq_id:
            ret = False
        s.seq_id_expect = (seq_id + 1) & 0x3ff
        return ret

    def close(s):
        pass


class ServiceASTRM(ServiceBase):
    def __init__(s):
        super(ServiceASTRM, s).__init__()
        s.header_base = construct.BitStruct('ASTRMBaseHeader',
            construct.BitField('fmt', 3),
            construct.Bit('channel'),
            construct.Flag('vibrate'),
            construct.Bit('packet_type'),
            construct.BitField('seq_id', 10),
            construct.BitField('payload_size', 16)
        )
        s.header_aud = construct.Struct('ASTRMAudioHeader',
            construct.ULInt32('timestamp'),
        #    construct.Array(lambda ctx: ctx.payload_size, construct.UBInt8("data"))
        )
        s.header_msg = construct.Struct('ASTRMMsgHeader',
            # This is kind of a hack, (there are two timestamp fields, which one is used depends on packet_type
            construct.ULInt32('timestamp_audio'),
            construct.ULInt32('timestamp'),
            construct.Array(2, construct.ULInt32('freq_0')), # -> mc_video
            construct.Array(2, construct.ULInt32('freq_1')), # -> mc_sync
            construct.ULInt8('vid_format'),
            construct.Padding(3)
        )
        s.header = construct.Struct('ASTRMHeader',
            construct.Embed(s.header_base),
            construct.Switch('format_hdr', lambda ctx: ctx.packet_type,
                {
                    0 : construct.Embed(s.header_aud),
                    1 : construct.Embed(s.header_msg),
                },
                default = construct.Pass
            )
        )
        s.is_streaming = False
        s.p = pyaudio.PyAudio()
        s.stream = None

        s.pa_num_bufs = 15
        s.pa_ring = [array.array('H', '\0' * 416 * 2)] * s.pa_num_bufs
        s.pa_wpos = s.pa_rpos = 0

    def close(s):
        if s.stream is not None:
            # hangs the process, dunno why
            # s.stream.stop_stream()
            s.stream.close()
            s.stream = None
        if s.p is not None:
            s.p.terminate()
            s.p = None
        s.is_streaming = False

    def __pa_callback(s, in_data, frame_count, time_info, status):
        samples = s.pa_ring[s.pa_wpos]
        s.pa_wpos += 1
        s.pa_wpos %= s.pa_num_bufs
        samples.extend(s.pa_ring[s.pa_wpos])
        s.pa_wpos += 1
        s.pa_wpos %= s.pa_num_bufs
        return (samples, pyaudio.paContinue)

    def update(s, packet):
        h = s.header.parse(packet)

        # ignore vid_format packets for now
        if h.packet_type == 0:
            seq_ok = s.update_seq_id(h.seq_id)
            if not seq_ok:
                log('bad seq_id', name='ASTRM')
            if h.fmt != 1 or h.channel != 0:
                raise Exception(
                    'astrm currently only handles 48kHz PCM stereo')
            if len(packet) != 8 + h.payload_size:
                raise Exception('astrm bad payload_size')

            if h.vibrate:
                # TODO: play a tone! :)
                log('******* vibrate ********, ''ASTRM')

            s.pa_ring[s.pa_rpos] = array.array('H', packet[8:])
            s.pa_rpos += 1
            s.pa_rpos %= s.pa_num_bufs

            if s.is_streaming and not s.stream.is_active():
                s.stream.close()
                s.is_streaming = False

            if s.is_streaming == False:
                s.stream = s.p.open(
                    format=pyaudio.paInt16,
                    channels=2,
                    rate=48000,
                    output=True,
                    frames_per_buffer=416 * 2,
                    stream_callback=s.__pa_callback)
                s.stream.start_stream()
                s.is_streaming = True


class ServiceVSTRM(ServiceBase):
    def __init__(s, decoder):
        super(ServiceVSTRM, s).__init__()
        s.decoder = decoder
        s.header = construct.BitStruct('VSTRMHeader',
            construct.Nibble('magic'),
            construct.BitField('packet_type', 2),
            construct.BitField('seq_id', 10),
            construct.Flag('init'),
            construct.Flag('frame_begin'),
            construct.Flag('chunk_end'),
            construct.Flag('frame_end'),
            construct.Flag('has_timestamp'),
            construct.BitField('payload_size', 11),
            construct.BitField('timestamp', 32)
        )
        s.frame = array.array('B')
        s._is_streaming = False
        s.is_streaming = False
        s.frame_decode_num = 0

    @property
    def is_streaming(self):
        return self._is_streaming

    @is_streaming.setter
    def is_streaming(self, streaming):
        self._is_streaming = streaming
        log('is_streaming = {streaming}'.format(streaming=streaming),
            'VSTRM')

    def close(s):
        s.decoder.close()

    def packet_is_idr(s, packet):
        return packet[8:16].find('\x80') != -1

    def h264_nal_encapsulate(s, is_idr, vstrm):
        slice_header = 0x25b804ff if is_idr else (0x21e003ff | ((s.frame_decode_num & 0xff) << 13))
        s.frame_decode_num += 1
        
        nals = array.array('B')
        # TODO shouldn't really need this after the first IDR
        # TODO hardcoded for gamepad for now
        # allow decoder to know stream parameters
        if is_idr:
            nals.extend([
                # sps
                0x00, 0x00, 0x00, 0x01,
                0x67, 0x64, 0x00, 0x20, 0xac, 0x2b, 0x40, 0x6c, 0x1e, 0xf3, 0x68,
                # pps
                0x00, 0x00, 0x00, 0x01,
                0x68, 0xee, 0x06, 0x0c, 0xe8
            ])
        
        # begin slice nalu
        nals.extend([0x00, 0x00, 0x00, 0x01])
        nals.extend([(slice_header >> 24) & 0xff,
                     (slice_header >> 16) & 0xff,
                     (slice_header >>  8) & 0xff,
                      slice_header & 0xff])
        
        # add escape codes
        nals.extend(vstrm[:2])
        for i in xrange(2, len(vstrm)):
            if vstrm[i] <= 3 and nals[-2] == 0 and nals[-1] == 0:
                nals.extend([3])
            nals.extend([vstrm[i]])
        
        return nals

    def update(s, packet):
        h = s.header.parse(packet)
        is_idr = s.packet_is_idr(packet)
        
        seq_ok = s.update_seq_id(h.seq_id)
        
        if not seq_ok:
            s.is_streaming = False
        
        if h.frame_begin:
            s.frame = array.array('B')
            if s.is_streaming is False:
                if is_idr:
                    s.is_streaming = True
                else:
                    # request a new IDR frame
                    MSG_S.sendto('\1\0\0\0', ('192.168.1.10', PORT_MSG))
                    return
        
        s.frame.fromstring(packet[16:])
        
        if s.is_streaming and h.frame_end:
            nals = s.h264_nal_encapsulate(is_idr, s.frame)
            s.decoder.display_frame(nals.tostring())

    def resize_output(s, (x, y)):
        d = GAMEPAD_DIM
        fit = pygame.Rect((0, 0), d).fit(pygame.display.get_surface().get_rect())
        s.decoder.update_dimensions(d, fit.size)


class ServiceCMD(ServiceBase):
    PT_REQ      = 0
    PT_REQ_ACK  = 1
    PT_RESP     = 2
    PT_RESP_ACK = 3
    
    CMD0_OK = 0
    
    def __init__(s):
        s.header_cmd0 = construct.Struct('CMD0Header',
            construct.UBInt8('magic'),
            construct.UBInt8('unk_0'),
            construct.UBInt8('unk_1'),
            construct.UBInt8('unk_2'),
            construct.UBInt8('unk_3'),
            construct.UBInt8('flags'),
            construct.UBInt8('id_primary'),
            construct.UBInt8('id_secondary'),
            construct.UBInt16('error_code'),
            construct.UBInt16('payload_size_cmd0')
        )
        s.header_cmd1 = construct.Struct('CMD1Header',
            construct.Padding(48)
        )
        s.header_cmd2 = construct.Struct('CMD2Header',
            construct.ULInt16('JDN_base'),
            construct.Padding(2),
            construct.ULInt32('seconds')
        )
        s.header = construct.Struct('CMDHeader',
            construct.ULInt16('packet_type'),
            construct.ULInt16('cmd_id'),
            construct.ULInt16('payload_size'),
            construct.ULInt16('seq_id'),
            construct.Switch('cmd_hdr', lambda ctx: ctx.cmd_id,
                {
                    0 : construct.If(lambda ctx: ctx.payload_size >= s.header_cmd0.sizeof(), construct.Embed(s.header_cmd0)),
                    1 : construct.If(lambda ctx: ctx.payload_size == s.header_cmd1.sizeof(), construct.Embed(s.header_cmd1)),
                    2 : construct.If(lambda ctx: ctx.payload_size == s.header_cmd2.sizeof(), construct.Embed(s.header_cmd2))
                },
                default = construct.Pass
            )
        )
        s.cmd_handlers = {
            0 : s.cmd0,
            1 : s.cmd1,
            2 : s.cmd2
        }
        s.cmd0_handlers = {
            5 : { 6 : s.cmd0_5_6 },
        }

    def cmd0_5_6(s, h, packet):
        r = '\x02\x00\x00\x00\x10\x03\x11\x00\x7e\x01\x02\x38\x00\x09\x05\x06\x00\x00\x03\x04\x1f\x00\x00\x40\x00\x57\x69\x69\x55\x34\x30\x66\x34\x30\x37\x38\x33\x39\x32\x35\x63\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x80\x03\x39\x62\x64\x62\x31\x38\x37\x31\x30\x39\x64\x64\x62\x36\x35\x33\x65\x30\x62\x39\x64\x36\x32\x36\x65\x36\x34\x35\x35\x62\x37\x39\x31\x32\x61\x34\x38\x38\x35\x30\x33\x35\x34\x30\x66\x34\x34\x61\x62\x62\x64\x63\x32\x65\x33\x39\x38\x36\x32\x32\x62\x31\x39\x63\x40\x51\x32\x00\x02\x06\x2a\xb1\x16\x06\x57\x65\x67\x27\xd3\xd4\x57\xc5\x99\xd9\x2d\x2a\xa5\xc0\x3b\xe2\x40\xf4\x07\x83\x92\x5c\xba\xbe\x01\x0e\x1e\x30\x04\x3e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x1c\x3d\x8b\x5c\x35\x01\x0e\x1e\x15\xab\x48\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x31\xe1\x04\xff\xa0\x98\xbc\xff\xc0\xff\xb1\x00\xe8\x1f\x68\x1f\x90\x1f\x55\x07\xb0\xff\xff\x8a\xff\xff\x8d\x00\x00\x7d\x58\x02\x77\x55\x02\x1e\x57\x02\xc8\xd9\x4c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x35\x00\x1e\x00\x22\x03\xc3\x01\x50\x01\x61\x0e\xa1\x0e\x97\x01\xea\x9e\xe4\x17\x03\xa0\xb5\x43\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8b\x5c\x35\x01\x0e\x1e\x15\xab\x48\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x31\xe1\x04\xff\xa0\x98\xbc\xff\xc0\xff\xb1\x00\xe8\x1f\x68\x1f\x90\x1f\x55\x07\xb0\xff\xff\x8a\xff\xff\x8d\x00\x00\x7d\x58\x02\x77\x55\x02\x1e\x57\x02\xc8\xd9\x4c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x35\x00\x1e\x00\x22\x03\xc3\x01\x50\x01\x61\x0e\xa1\x0e\x97\x01\xea\x9e\xe4\x17\x03\xa0\xb5\x43\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x2a\x58\x00\x87\x0f\x00\x87\x0f\x01\x0e\x1e\x00\x00\x00\x00\x00\x19\x00\x16\x1d\x6f\xbc\xff\xc0\xff\xb1\x00\xe8\x1f\x68\x1f\x90\x1f\x55\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x35\x00\x1e\x00\x22\x03\xc3\x01\x50\x01\x61\x0e\xa1\x0e\x97\x01\xea\x9e\x00\x00\x00\x13\x3b\x21\x00\x00\x00\x03\xba\x31\xe4\x17\x03\xa0\xb5\x43\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x87\x0f\x15\x01\x2d\x01\x4d\x01\x7a\x01\xb7\x01\xff\x01\x03\x26\x8c\x04\xa3\x49\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x73\x8f\x00\x87\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\xa3\x49'[20:]
        s.send_response_cmd0(h, r)

    def cmd0(s, h, packet):
        log('CMD0:%i:%i' % (h.id_primary, h.id_secondary), 'CMD')
        if h.id_primary not in s.cmd0_handlers or h.id_secondary not in s.cmd0_handlers[h.id_primary]:
            log('unhandled', packet.encode('hex'), 'CMD')
            return
        s.cmd0_handlers[h.id_primary][h.id_secondary](h, packet)

    def cmd1(s, h, packet):
        log('CMD1', packet[8:].encode('hex'), 'CMD')
        s.send_response(h, '\x00\x16\x00\x19\x9e\x00\x00\x00\x40\x00\x40\x00\x00\x00\x01\xff')

    def cmd2(s, h, packet):
        log('TIME base {:04x} seconds {:08x}'.format(h.JDN_base, h.seconds), 'CMD')
        s.send_response(h)

    def ack(s, h):
        ack = s.header.build(
            construct.Container(
                packet_type = s.PT_REQ_ACK if h.packet_type == s.PT_REQ else s.PT_RESP_ACK,
                cmd_id = h.cmd_id,
                payload_size = 0,
                seq_id = h.seq_id
            )
        )
        CMD_S.sendto(ack, ('192.168.1.10', PORT_CMD))

    def send_request(s, h, data=''):
        s.send_cmd(h, s.PT_REQ, data)

    def send_response(s, h, data=''):
        s.send_cmd(h, s.PT_RESP, data)

    def send_response_cmd0(s, h, data='', result=CMD0_OK):
        assert h.cmd_id == 0
        h.flags = ((h.flags >> 3) & 0xfc) | 1
        h.error_code = result
        h.payload_size_cmd0 = len(data)
        s.send_response(h, data)

    def send_cmd(s, h, type, data):
        h.packet_type = type
        h.payload_size = len(data)
        # compensate for the fact that data doesn't include cmd0 header
        if h.cmd_id == 0:
            h.payload_size += s.header_cmd0.sizeof()
        CMD_S.sendto(s.header.build(h) + data, ('192.168.1.10', PORT_CMD))

    def update(s, packet):
        h = s.header.parse(packet)
        # don't track acks from the console for now
        if h.packet_type in (s.PT_REQ, s.PT_RESP):
            #print 'CMD', packet.encode('hex')
            s.ack(h)
            s.cmd_handlers[h.cmd_id](h, packet)


class ServiceMSG(ServiceBase):
    def update(s, packet):
        log(packet.encode('hex'), 'MSG')


class ServiceNOP(ServiceBase):
    def update(s, packet):
        pass
