from ctypes import *
from multiprocessing import Process, Pipe
from threading import Thread
from vmpp_platform import get_platform

# lib = cdll.LoadLibrary(r'../arm64/libvideo_dec_so.so')


class DecStructure(Structure):
    _fields_ = [('input', c_char_p), ('output', c_char_p), ('device', c_char_p), ('codec', c_char_p),
              ('pix_fmt', c_char_p), ('vframes', c_int), ('save', c_int), ('md5', c_int), ('loop', c_int),
              ('core_mode', c_int), ('memory_mode', c_int), ('output_align', c_uint), ('decode_mode', c_uint),
              ('log_level', c_uint), ('crop', c_uint), ('crop_detail', c_char_p), ('width', c_int), ('height', c_int)]


def receive_thread(lib, file, buff_size, logger):
    out_yuv = (c_ubyte * int(buff_size)).from_buffer_copy(b'0' * int(buff_size))
    ret = 0
    ret = lib.receive_frame(byref(out_yuv))
    logger.info(f"out_yuv {out_yuv}")
    if ret == 0:
        logger.info("received a frame.")
        file.write(out_yuv)
    elif ret == 100:
        logger.info("receive more data.")
    elif ret == 101:
        logger.info("received all frame finished!")
    elif ret == -9:
        logger.info("receive frame error!")
        return
    else:
        logger.info("receive_thread ret err")
        return

    return ret


def vmpp_dec(input_file, output_file, device, logger):
    lib = get_platform("dec")  
    lib.initialize.restype = c_int
    dec_stru = DecStructure()               # init params struct
    lib.default_params(byref(dec_stru))     # lib default

    dec_stru.input = input_file.encode()    # input
    dec_stru.codec = "h264".encode()        # input encode
    dec_stru.vframes = 1000                 # 0: decode all yuv
    dec_stru.save = 0
    dec_stru.device = device.encode()

    ret_api = lib.initialize(byref(dec_stru))
    logger.info(f"initialize return: {ret_api}")

    buff_size = dec_stru.width * dec_stru.height * 3 / 2
    logger.info(buff_size)

    dec_status = 1
    ret = 0
    file_out = open(output_file, 'wb')
    while True:
        logger.info("=============== while ===============")
        if dec_status:
            ret = lib.send_stream()
        if ret == 0:
            logger.info("send a stream.") 
        elif ret == 1:
            logger.info("send stream all completed.")
            lib.send_end()
            dec_status = 0
        else:
            logger.error("send stream err.")
            break
        
        ret = receive_thread(lib, file_out, buff_size, logger)
        if ret == 101:
            break
        elif ret < 0:
            logger.error("receive frame err")
            break

    lib.uninitialize()
    file_out.close()

