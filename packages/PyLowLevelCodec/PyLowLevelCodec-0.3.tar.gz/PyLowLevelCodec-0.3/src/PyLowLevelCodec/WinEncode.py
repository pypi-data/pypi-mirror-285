import argparse
from pathlib import Path
from ctypes import *
from vmpp_platform import get_platform
from vmpp_log_init import *


def param_list(input_file,
               output_file,
               device,
               codec,
               save,
               pix_fmt,
               width,
               height,
               logger):
    
    params_dirt = {}
    params_dirt["i"] = input_file
    params_dirt["o"] = output_file
    params_dirt["d"] = device
    params_dirt["c"] = codec
    params_dirt["s"] = save
    params_dirt["f"] = pix_fmt
    params_dirt["w"] = width
    params_dirt["h"] = height
    
    logger.info(params_dirt)    
    
    params_list, args = package_params(params_dirt, logger)

    # t_lib = cdll.LoadLibrary(r'../arm64/libtranscode_so.so')
    t_lib = get_platform("enc")  
    t_lib = t_lib.main
    
    t_lib.argtypes = [c_int, (c_char_p * len(params_list))]
    t_lib(len(params_list), args)            
    
    
def package_params(params_dirt, logger):
    params_list = ["".encode("utf-8")]
    for key, value in params_dirt.items():
        params_list.append("-{}".format(key[0]).encode("utf-8"))
        params_list.append(str(value).encode("utf-8"))
        
    logger.info(params_list)

    args_type = (c_char_p * len(params_list))
    args = args_type()

    for key, item in enumerate(params_list):
        args[key] = item
   
    return params_list, args


def win_encodec():
    """
        This function illustrates encoding of frames using vastai device buffers as input.

        Parameters:
            - raw_file_path (str): Path to
        file to be decoded
            - encoded_file_path (str): Path to output file into which raw frames are stored
            - width (int): width of encoded frame
            - height (int): height of encoded frame
            - fmt (str) : surface format string in uppercase, for e.g. NV12

        Returns: - None.

        Example:
        >>> python Encode.py  -i path -o out.hevc -d /dev/va_video0 -if 12 -s 1920x1088 -c 1
        Encode 1080p NV12 raw YUV into elementary bitstream using H.264 codec
    """
    
    parser = argparse.ArgumentParser(
        "This sample application illustrates encoding of frames using windows vastai device buffers as input."
    )
                    
    parser.add_argument(
        "-d", "--device", help="(opt) render device name, MUST if you did not spicify render device in the input json file. While, if you have spicified it in a json file, this option will be ignored", required=True, default = "/dev/va_video0")
    parser.add_argument(
        "-i", "--input_file", required=True, type=Path, help="url for input file/directory or a json file with device/urls list")
    parser.add_argument(
        "-o", "--output_file", required=True, type=Path, help="(opt) output directory or file name, default is: NULL, directory must exist")
    parser.add_argument(
        "-c", "--codec", required=True, type=str, help=" (opt) codec type('h264','hevc','av1','jpeg'), MUST if not using ffmpeg for demuxing", )
    parser.add_argument(
        "-s", "--save", required=True, type=str, help="(opt) whether to save YUV data from decoder and data from encoder, default: 0", default=0)
    parser.add_argument(
        "-f", "--pix_fmt", required=True, type=str, help="pixel format")
    parser.add_argument(
        "-w", "--width", required=True, type=str, help="width")
    parser.add_argument(
        "-height", "--height", required=True, type=str, help="height")   ### 注意如果使用-h参数，会与parser库-h冲突导致报错，使用-s设置分辨率会与-save冲突。
    
    
    args = parser.parse_args()
    logger = init_log()

    param_list(args.input_file,
               args.output_file,
               args.device,
               args.codec,
               args.save,
               args.pix_fmt,
               args.width,
               args.height,
               logger)

if __name__ == "__main__":
    win_encodec()