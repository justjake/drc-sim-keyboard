import cffi
from cffi import FFI
import pygame
from util import log

# TODO static alloc in_data and make interface for reading/writing directly to it
#   remove array.array usage of calling code

class H264Decoder:
    def __init_ffi(s):
        s.ffi = FFI()
        s.ffi.cdef('''
            // AVCODEC
            
            enum PixelFormat { PIX_FMT_YUV420P, PIX_FMT_RGB24, ... };
            
            void avcodec_register_all(void);
            
            struct AVPacket { ...; uint8_t *data; int size; ...; };
            void av_init_packet(struct AVPacket *pkt);
            
            enum AVCodecID { AV_CODEC_ID_H264, ... };
            struct AVCodec *avcodec_find_decoder(enum AVCodecID id);

            struct AVCodecContext *avcodec_alloc_context3(struct AVCodec *codec);
            
            int avcodec_open2(struct AVCodecContext *avctx, struct AVCodec *codec,
                            struct AVDictionary **options);
            
            struct AVFrame { uint8_t *data[8]; int linesize[8]; ...; int key_frame; ...; };
            struct AVFrame *av_frame_alloc(void);
            
            int avcodec_decode_video2(struct AVCodecContext *avctx, struct AVFrame *picture,
                                    int *got_picture_ptr, struct AVPacket *avpkt);
            
            int avcodec_close(struct AVCodecContext *avctx);
            
            void av_free(void *ptr);
            
            int avpicture_get_size(enum PixelFormat pix_fmt, int width, int height);
            
            int avpicture_fill(struct AVPicture *picture, uint8_t *ptr,
                            int pix_fmt, int width, int height);
            
            // SWSCALE
            
            #define SWS_BILINEAR ...
            #define SWS_FAST_BILINEAR ...
            struct SwsContext *sws_getContext(int srcW, int srcH, enum PixelFormat srcFormat,
                                            int dstW, int dstH, enum PixelFormat dstFormat,
                                            int flags, struct SwsFilter *srcFilter,
                                            struct SwsFilter *dstFilter, const double *param);
            
            int sws_scale(struct SwsContext *c, const uint8_t *const srcSlice[],
                        const int srcStride[], int srcSliceY,
                        int srcSliceH, uint8_t *const dst[],
                        const int dstStride[]);
            
            void sws_freeContext(struct SwsContext *c);
        ''')
        s.ns = s.ffi.verify(source = '''
            #include <libavcodec/avcodec.h>
            #include <libswscale/swscale.h>
            ''', libraries=['avcodec', 'swscale'])

    def __init_avcodec(s):
        s.ns.avcodec_register_all()

        s.av_packet = s.ffi.new('struct AVPacket *')
        s.ns.av_init_packet(s.av_packet)

        s.codec = s.ns.avcodec_find_decoder(s.ns.AV_CODEC_ID_H264)
        if not s.codec:
            raise Exception('avcodec_alloc_context3')
        s.context = s.ns.avcodec_alloc_context3(s.codec)
        if not s.context:
            raise Exception('avcodec_alloc_context3')
        if s.ns.avcodec_open2(s.context, s.codec, s.ffi.NULL) < 0:
            raise Exception('avcodec_open2')
        s.frame = s.ns.av_frame_alloc()
        if not s.frame:
            raise Exception('av_frame_alloc')
        s.got_frame = s.ffi.new('int *')
        s.out_frame = s.ns.av_frame_alloc()

    def __init__(s, (in_x, in_y), (out_x, out_y), output_surface):
        s.sws_context = None
        try:
            s.__init_ffi()
            s.__init_avcodec()
        except cffi.ffiplatform.VerificationError:
            log('FATAL C FFI COMPILATION ERROR', 'H264')
            log('make sure you have libavcodec-dev and libswscale-dev', 'H264')
            exit(1)
        s.update_dimensions((in_x, in_y), (out_x, out_y))
        s.output_surface = output_surface

    def close(s):
        s.ns.sws_freeContext(s.sws_context)
        s.ns.av_free(s.out_frame)
        
        s.ns.avcodec_close(s.context)
        s.ns.av_free(s.context)
        s.ns.av_free(s.frame)

    def update_dimensions(s, (in_x, in_y), (out_x, out_y)):
        s.in_x, s.in_y = in_x, in_y
        s.out_x, s.out_y = out_x, out_y
        
        if s.sws_context != None:
            s.ns.sws_freeContext(s.sws_context)
        s.sws_context = s.ns.sws_getContext(
            s.in_x, s.in_y, s.ns.PIX_FMT_YUV420P,
            s.out_x, s.out_y, s.ns.PIX_FMT_RGB24,
            s.ns.SWS_FAST_BILINEAR,
            s.ffi.NULL,
            s.ffi.NULL, s.ffi.NULL)
        
        bytes_req = s.ns.avpicture_get_size(s.ns.PIX_FMT_RGB24, s.out_x, s.out_y)
        s.out_buffer = s.ffi.new('uint8_t [%i]' % bytes_req)
        s.ns.avpicture_fill(
            s.ffi.cast('struct AVPicture *', s.out_frame),
            s.out_buffer,
            s.ns.PIX_FMT_RGB24,
            s.out_x, s.out_y)

    def display_frame(s, encoded_nalu):
        in_data = s.ffi.new('uint8_t []', encoded_nalu)
        s.av_packet.data = in_data
        s.av_packet.size = len(encoded_nalu)
        
        length = s.ns.avcodec_decode_video2(s.context, s.frame, s.got_frame, s.av_packet)
        if length < 0:
            raise Exception('avcodec_decode_video2')
        elif length != s.av_packet.size:
            raise Exception('expected to decode a single complete frame')
        elif s.got_frame[0]:
            log('keyframe {key}'.format(key=s.frame.key_frame), 'H264')
            # convert from YUV to RGB
            out_height = s.ns.sws_scale(
                s.sws_context,
                s.frame.data, s.frame.linesize,
                0, s.in_y,
                s.out_frame.data, s.out_frame.linesize)
            
            #print out_height
            surface = pygame.image.frombuffer(
                s.ffi.buffer(s.out_frame.data[0], s.out_frame.linesize[0] * s.out_y),
                (s.out_x, s.out_y),
                'RGB')
            # I guess this is an extra copy...?
            s.output_surface.blit(surface, (0, 0))
            # prev implementation just wrote out to the main display and did the flip:
            # pygame.display.get_surface().blit(surface, (0, 0))
            # pygame.display.flip()
