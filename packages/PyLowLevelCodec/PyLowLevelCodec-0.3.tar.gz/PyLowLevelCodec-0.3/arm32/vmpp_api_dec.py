from ctypes import *
from multiprocessing import Process, Manager
from threading import Thread

# global lib
lib=PyDLL(r'./sample/build/out/libvideo_dec_so.so')
# queue = Queue()
manager = Manager()
queue = manager.Queue()
out_yuv = (c_ubyte*3110400).from_buffer_copy(b'0'*3110400)
# ?????,???ctypes.Structure
class DecStructure(Structure):
    _fields_=[('input', c_char_p), ('output', c_char_p), ('device', c_char_p), ('codec', c_char_p), ('pix_fmt', c_char_p), ('vframes', c_int), ('save', c_int), ('md5', c_int), ('loop', c_int), ('core_mode', c_int), ('memory_mode', c_int), ('output_align', c_uint), ('decode_mode', c_uint), ('log_level', c_uint), ('crop', c_uint), ('crop_detail', c_char_p)]


def receive_thread(file):
    ret = 0
    # while ret >= 0:
    ret = lib.receive_frame(byref(out_yuv))
    print("==============================out_yuv", out_yuv)
    if ret == 0:
        print("received a frame.")
        file.write(out_yuv)
    elif ret == 100:
        print("receive more data.")
    elif ret == 101:
        print("received all frame, goodbay.")
        # break
    elif ret == -9:
        print("receive frame error!")
        return
    else:
        print("ret is err")
        return
        # break
    return ret


def main():
    
    lib.initialize.restype = c_int
    # lib.decode.restype = c_int

    dec_stru = DecStructure()
    ret = lib.default_params(byref(dec_stru))
    dec_stru.input = "/video-case/lowlevel_SDK/res_UT/cdzj.h264".encode()
    dec_stru.codec = "h264".encode()
    dec_stru.vframes = 1000  # 0: decode all yuv
    dec_stru.save = 1

    ret_api = lib.initialize(byref(dec_stru))
    print("initialize() return:", ret_api)
  
    
    # stream_len = c_int(0)
    # stream_pts = c_int(0)
    # stream_frametype = c_int(0)
    
    # print("==============before thread start")
    # process = Process(target=receive_thread, args=(queue,))
    # process.start()

    dec_status = 1
    ret = 0
    file_out = open("out_py.yuv", 'wb')
    while True:
        print("===============while  ")
        if dec_status:
            ret = lib.send_stream()
        if ret == 0:
            print("send a stream.")
        elif ret == 1:
            print("send stream all completed.")
            lib.send_end()
            dec_status = 0
            # break
        else:
            print("send stream err.")
            break
        ret = receive_thread(file_out)
        if ret == 101:
            break
        elif ret < 0:
            print("receive frame err")
            break
        
    lib.uninitialize()
    file_out.close()


if __name__ == "__main__":
    main()