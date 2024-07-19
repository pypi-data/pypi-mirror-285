import json
import argparse
import multiprocessing

from pathlib import Path
from vmpp_api_enc import *
from vmpp_log_init import *
from concurrent.futures import ThreadPoolExecutor,wait,ALL_COMPLETED,FIRST_COMPLETED, as_completed


def enc_perf():
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
        >>> python EncodePerf.py  -i path -o out.hevc -d /dev/va_video0 -if 12 -s 1920x1088 -c 1 -perf 2
        Encode 1080p NV12 raw YUV into elementary bitstream using H.264 codec
    """
    parser = argparse.ArgumentParser(
        "This sample application illustrates encoding of frames using vastai device buffers as input."
    )

    parser.add_argument("-i", "--raw_file_path", type=Path, required=True, help="Raw video file (read from)", )
    parser.add_argument("-o", "--encoded_file_path", type=Path, required=True, help="Encoded video file (write to)", )
    parser.add_argument("-s", "--size", type=str, required=True, help="width x height of raw frame. Eg: 1920x1080", )
    parser.add_argument("-if", "--format", type=str, required=True, help="Format of input file", )
    parser.add_argument("-c", "--codec", type=str, required=True, help="0:h264, 1:hevc, default 0", default=0)
    parser.add_argument("-d", "--device", help="vastai device (default /dev/va_video0)", required=True, default = "/dev/va_video0")
    parser.add_argument("-json", "--config_file", type=str, default='', help="path of json config file", )
    parser.add_argument("-perf", "--perf_thread", type=int, default=0, help="(opt) Number of parallel runs for perf threading")

    args = parser.parse_args()
    
    logger = init_log()

    config = {}
    if len(args.config_file):
        with open(args.config_file) as jsonFile:
            json_content = jsonFile.read()
        config = json.loads(json_content)
        config["preset"] = config["preset"].upper()

    args.codec = args.codec.lower()
    args.format = args.format.upper()
    size = args.size.split("x")
    
    if args.perf_thread > 1:
        threads = []
        # 创建并启动线程
        for i in range(args.perf_thread):
            t = multiprocessing.Process(target=vmpp_enc, args=(
                args.raw_file_path.as_posix(),
                args.encoded_file_path.as_posix(),
                int(size[0]),
                int(size[1]),
                args.format,
                args.codec,
                args.device,
                logger))
            
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        logger.info("All Threading exit")
    else:
        vmpp_enc(args.raw_file_path.as_posix(),
                args.encoded_file_path.as_posix(),
                int(size[0]),
                int(size[1]),
                args.format,
                args.codec,
                args.device,
                logger)


if __name__ == "__main__":
    enc_perf()
