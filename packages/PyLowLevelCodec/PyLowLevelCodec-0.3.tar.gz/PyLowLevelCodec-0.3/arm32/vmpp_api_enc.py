from ctypes import *
import copy
# import numpy as np
#usbport=ctypes.c_uint16(0)
#count=ctypes.c_uint16(0)


# ?????,???ctypes.Structure
class PythonStructure(Structure):
  _fields_=[('input_file', c_char_p), ('output_file', c_char_p), ('width', c_int), ('height', c_int), ('stride', c_int), ('device', c_char_p), ('pixel_format', c_int), ('loop', c_int), ('store', c_int), ('buffer_count', c_int), ('codec', c_int), ('core_mode', c_int), ('profile', c_uint), ('level', c_uint), ('frameRateNum', c_uint), ('frameRateDen', c_uint), ('bitDepthLuma', c_uint), ('bitDepthChroma', c_uint), ('gopSize', c_uint), ('gdrDuration', c_uint), ('lookaheadDepth', c_uint), ('qualityMode', c_uint), ('tune', c_uint), ('keyInt', c_uint), ('crf', c_int), ('cqp', c_uint), ('llRc', c_uint), ('bitRate', c_uint), ('initQp', c_uint), ('vbvBufSize', c_uint), ('vbvMaxRate', c_uint), ('intraQpDelta', c_int), ('qpMinI', c_uint), ('qpMaxI', c_uint), ('qpMinPB', c_uint), ('qpMaxPB', c_uint), ('vbr', c_uint), ('aqStrength', c_float), ('P2B', c_uint), ('bBPyramid', c_uint), ('maxFrameSizeMultiple', c_float), ('maxFrameSize', c_int), ('outbufNum', c_uint), ('roiType', c_uint), ('roiInt', c_uint), ('roiParam', c_char_p), ('extSEIInt', c_uint), ('forceIDRInt', c_uint), ('logLevel', c_uint), ('roiMapDeltaQpBlockUnit', c_uint), ('roiMapQpDeltaVersion', c_uint), ('enableDynamicBitrate', c_uint), ('enableDynamicFrameRate', c_uint), ('maxBFrames', c_uint), ('hrd', c_uint), ('pictureSkip', c_uint), ('colorConversionType', c_uint), ('vfr', c_uint), ('svcTLayers', c_uint), ('svcExtractMaxTLayer', c_uint), ('sliceSize', c_uint), ('enableDynamicCrf', c_uint), ('enableCalcPSNR', c_int), ('ltrInterval', c_uint), ('ltrQpDelta', c_int), ('ltrRefGap', c_uint), ('ltrInsertTest', c_uint)]

def read_nv12_file(yuvfile, width, height):
    
    y_size = width * height 
    uv_size = y_size // 2
    # yuv_size = np.zero((width, height*3//2))
    yuv = yuvfile.read(y_size + uv_size)
    # yuvfile.close()
    return yuv


if __name__ == "__main__":
    lib=PyDLL(r'sample/build/out/libvideo_enc_so.so')
    # lib.initialize.argtypes = [c_int, c_int, c_int]
    lib.initialize.restype = c_int
    #lib.encode.argtypes = [POINTER(c_ubyte*312400), POINTER(c_ubyte*100000), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    lib.encode.restype = c_int

    enc_stru = PythonStructure()
    ret = lib.default_params(byref(enc_stru))
    enc_stru.width = 1920
    enc_stru.height = 1080
    enc_stru.pixel_format = 12
    enc_stru.store = 0
    # enc_stru.keyInt = 100
    enc_stru.forceIDRInt = 1

    pic_size = enc_stru.width * enc_stru.height * 3 / 2

    ret_api = c_int32(10)
    ret_api = lib.test()
    print("test() return:", ret_api)
    ret_api = lib.initialize(enc_stru)
    print("initialize() return:", ret_api)
    yuvfile = open(r"/video-case/lowlevel_SDK/res_UT/cdzj_1080p_nv12.yuv", 'rb')

    # yuv = read_nv12_file(yuvfile, 1920, 1080)
    # frame_data = (c_ubyte*3110400).from_buffer_copy(yuv)
    encoded_data = (c_ubyte*100000).from_buffer_copy(b'0'*100000)
    stream_len = c_int(0)
    stream_pts = c_int(0)
    stream_frametype = c_int(0)
    py_encoded_data = open("encoded_py.h264", 'wb')
    for i in range(100):
        yuv = read_nv12_file(yuvfile, enc_stru.width, enc_stru.height)
        if (len(yuv) == 0): break
        frame_data = (c_ubyte*int(pic_size)).from_buffer_copy(yuv)
        ret_api = lib.encode(byref(frame_data), byref(encoded_data), byref(stream_len), byref(stream_pts), byref(stream_frametype), 0)
        # enc_data = encoded_data
        enc_data = (c_ubyte*int(stream_len.value)).from_buffer_copy(encoded_data)
        py_encoded_data.write(enc_data)
        print("encode() return:", ret_api)
        print("len, pts, frametype:", stream_len.value, stream_pts.value, stream_frametype.value)

    lib.send_end(byref(encoded_data), byref(stream_len), byref(stream_pts), byref(stream_frametype))
    enc_data = (c_ubyte*int(stream_len.value)).from_buffer_copy(encoded_data)
    py_encoded_data.write(enc_data)
    py_encoded_data.close()
    print("before uninit")
    lib.uninitialize()
    print("after uninit")

