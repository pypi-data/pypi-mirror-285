from ctypes import *
import copy
from vmpp_platform import get_platform


class PythonStructure(Structure):
  _fields_ = [('input_file', c_char_p), ('output_file', c_char_p), ('width', c_int), ('height', c_int),
            ('stride', c_int), ('device', c_char_p), ('pixel_format', c_int), ('loop', c_int),
            ('store', c_int), ('buffer_count', c_int), ('codec', c_int), ('core_mode', c_int),
            ('profile', c_uint), ('level', c_uint), ('frameRateNum', c_uint), ('frameRateDen', c_uint),
            ('bitDepthLuma', c_uint), ('bitDepthChroma', c_uint), ('gopSize', c_uint), ('gdrDuration', c_uint),
            ('lookaheadDepth', c_uint), ('qualityMode', c_uint), ('tune', c_uint), ('keyInt', c_uint),
            ('crf', c_int), ('cqp', c_uint), ('llRc', c_uint), ('bitRate', c_uint), ('initQp', c_uint),
            ('vbvBufSize', c_uint), ('vbvMaxRate', c_uint), ('intraQpDelta', c_int), ('qpMinI', c_uint),
            ('qpMaxI', c_uint), ('qpMinPB', c_uint), ('qpMaxPB', c_uint), ('vbr', c_uint),
            ('aqStrength', c_float), ('P2B', c_uint), ('bBPyramid', c_uint), ('maxFrameSizeMultiple', c_float),
            ('maxFrameSize', c_int), ('outbufNum', c_uint), ('roiType', c_uint), ('roiInt', c_uint),
            ('roiParam', c_char_p), ('extSEIInt', c_uint), ('forceIDRInt', c_uint), ('logLevel', c_uint),
            ('roiMapDeltaQpBlockUnit', c_uint), ('roiMapQpDeltaVersion', c_uint), ('enableDynamicBitrate', c_uint),
            ('enableDynamicFrameRate', c_uint), ('maxBFrames', c_uint), ('hrd', c_uint), ('pictureSkip', c_uint),
            ('colorConversionType', c_uint), ('vfr', c_uint), ('svcTLayers', c_uint), ('svcExtractMaxTLayer', c_uint),
            ('sliceSize', c_uint), ('enableDynamicCrf', c_uint), ('enableCalcPSNR', c_int), ('ltrInterval', c_uint),
            ('ltrQpDelta', c_int), ('ltrRefGap', c_uint), ('ltrInsertTest', c_uint)]


class PythonStruct(Structure):
  _fields_ = [('width', c_int), ('height', c_int), ('store', c_int)]


def read_nv12_file(yuv_file, width, height):
    y_size = width * height
    uv_size = y_size // 2
    yuv = yuv_file.read(y_size + uv_size)
    
    return yuv


def vmpp_enc(input_file, output_file, width, height, fmt, codec, device, logger):
    # init log, init lib dll.
    lib = get_platform("enc")  
    lib.initialize.restype = c_int
    lib.encode.restype = c_int

    enc_stru = PythonStructure()
    lib.default_params(byref(enc_stru))
    enc_stru.width = width
    enc_stru.height = height
    enc_stru.pixel_format = int(fmt)  # 12
    enc_stru.store = 0
    enc_stru.codec = int(codec)
    enc_stru.device = device.encode()
    enc_stru.forceIDRInt = 1

    pic_size = enc_stru.width * enc_stru.height * 3 / 2

    ret_api = c_int32(10)
    ret_api = lib.test()
    ret_api = lib.initialize(enc_stru)
    logger.info(f"vastai device {enc_stru.device}")
    logger.info(f"initialize return {ret_api}")
    
    yuv_file = open(input_file, 'rb')
    encoded_data = (c_ubyte*100000).from_buffer_copy(b'0'*100000)
    stream_len = c_int(0)
    stream_pts = c_int(0)
    stream_frame_type = c_int(0)
    py_encoded_data = open(output_file, 'wb')
    while True:
        yuv = read_nv12_file(yuv_file, enc_stru.width, enc_stru.height)
        if len(yuv) == 0:
            break
            
        frame_data = (c_ubyte*int(pic_size)).from_buffer_copy(yuv)
        ret_api = lib.encode(byref(frame_data), 
                             byref(encoded_data), 
                             byref(stream_len), 
                             byref(stream_pts), 
                             byref(stream_frame_type), 0)
        
        enc_data = (c_ubyte*int(stream_len.value)).from_buffer_copy(encoded_data)
        py_encoded_data.write(enc_data)
        
        logger.info(f"encode return: {ret_api}")
        logger.info(f"len {stream_len.value}, pts {stream_pts.value}, frame_type {stream_frame_type.value}")

    lib.send_end(byref(encoded_data), byref(stream_len), byref(stream_pts), byref(stream_frame_type))
    enc_data = (c_ubyte*int(stream_len.value)).from_buffer_copy(encoded_data)
    py_encoded_data.write(enc_data)
    py_encoded_data.close()

    lib.uninitialize()
    logger.info("lib uninitialized!")

