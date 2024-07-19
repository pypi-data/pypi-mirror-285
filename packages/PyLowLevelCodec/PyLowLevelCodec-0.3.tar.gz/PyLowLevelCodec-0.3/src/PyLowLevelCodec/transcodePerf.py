import argparse
import multiprocessing  


from pathlib import Path
from ctypes import *
from vmpp_platform import get_platform
from vmpp_log_init import *


def param_list(input_file,
               output_file,
               device,
               encodec,
               codec,
               save,
               md5,
               Loop,
               loop,
               logger):
    
    params_dirt = {}
    params_dirt["i"] = input_file
    params_dirt["o"] = output_file
    params_dirt["r"] = device
    params_dirt["C"] = encodec
    params_dirt["c"] = codec
    params_dirt["s"] = save
    params_dirt["m"] = md5
    params_dirt["L"] = Loop
    params_dirt["l"] = loop


    logger.info(params_dirt)    
    params_list, args = package_params(params_dirt, logger)

    # t_lib = cdll.LoadLibrary(r'../arm64/libtranscode_so.so')
    t_lib = get_platform("transc")  
    t_lib = t_lib.main
    
    t_lib.argtypes = [c_int, (c_char_p * len(params_list))]
    t_lib(len(params_list), args)     
    
    return 0       
    
    
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


def transc_perf():
    """
    This function demonstrates transcoding of an input video stream.

        Parameters:
            - in_file_path (str): Path to
        file to be decoded
            - out_file_path (str): Path to output file into which raw frames are stored

        Returns: - None.

        Example:
        >>> python transcodePerf.py -i path -r /dev/va_video2 -o out.hevc -C hevc -c h264 -s 1 -l 0 -L 0  -m 0 -perf 2
    """
                    
    parser = argparse.ArgumentParser(
        'This sample application demonstrates transcoding of an input video stream.'
    )
    parser.add_argument(
        "-r", "--device", help="(opt) render device name, MUST if you did not spicify render device in the input json file. While, if you have spicified it in a json file, this option will be ignored", required=True, default = "/dev/va_video0")
    parser.add_argument(
        "-i", "--input_file", required=True, type=Path, help="url for input file/directory or a json file with device/urls list")
    parser.add_argument(
        "-o", "--output_file", required=True, type=Path, help="(opt) output directory or file name, default is: NULL, directory must exist")
    parser.add_argument(
        "-C", "--encodec", type=str, required=True, help="(opt) encode codec type('h264','hevc','av1','jpeg'), MUST if encoder is enabled")
    parser.add_argument(
        "-c", "--codec", required=True, type=str, help=" (opt) codec type('h264','hevc','av1','jpeg'), MUST if not using ffmpeg for demuxing", )
    parser.add_argument(
        "-s", "--save", required=True, type=str, help="(opt) whether to save YUV data from decoder and data from encoder, default: 0", default=0)
    parser.add_argument(
        "-m", "--md5", required=True, type=str, help="(opt) whether to check md5, default: 0 ", default=0)
    parser.add_argument(
        "-L", "--Loop", type=int, default=1, help="(opt) loop count for list in json, default: 0, negative value for infinite loop")
    parser.add_argument(
        "-l", "--loop", type=int, default=1, help="(opt) loop count for file, default:0, negative value for infinite loop")
    parser.add_argument(
        "-perf", "--perf_thread", type=int, default=0, help="(opt) Number of parallel runs for perf threading")

    ### init log
    logger = init_log()
    
    ### init parse
    ### init ThreadPoolExecutor
    args = parser.parse_args()
    if args.perf_thread > 1:
        threads = []
        # 创建并启动线程
        for i in range(args.perf_thread):
            t = multiprocessing.Process(target=param_list, args=(args.input_file,
                args.output_file,
                args.device,
                args.encodec,
                args.codec,
                args.save,
                args.md5,
                args.Loop,
                args.loop,
                logger))
            
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        logger.info("All Threading exit")
    else:
        param_list(args.input_file,
                args.output_file,
                args.device,
                args.encodec,
                args.codec,
                args.save,
                args.md5,
                args.Loop,
                args.loop,
                logger)

if __name__ == "__main__":
    transc_perf()