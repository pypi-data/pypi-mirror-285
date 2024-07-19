import argparse
import multiprocessing  

from vmpp_api_dec import vmpp_dec
from vmpp_log_init import *

from concurrent.futures import ThreadPoolExecutor,wait,ALL_COMPLETED,FIRST_COMPLETED, as_completed


def dec_perf():
    """
        Function to decode media file and write raw frames into an output file.

        Parameters:
            - input (str): Path to
        file to be decoded
            - output (str): Path to output file
            - width (int): width of encoded frame
            - height (int): height of encoded frame
            - fmt (str) : surface format string in uppercase, for e.g. NV12

        Example:
        >>> python DecodePerf.py -i path/file -o out.yuv -d /dev/va_video0 -perf 2
        Function to decode media file and write raw frames into an output file.
    """
    
    parser = argparse.ArgumentParser(
        description="This sample application illustrates decoding of a media file."
    )

    parser.add_argument("-i", "--input", help="Encoded video file (read from)", required=True)
    parser.add_argument("-o", "--output", help="Raw NV12 video file (write to)", required=True)
    parser.add_argument("-d", "--device", help="vastai device (/dev/va_video0)", required=True)
    parser.add_argument("-perf", "--perf_thread", type=int, default=0, help="(opt) Number of parallel runs for perf threading")

    logger = init_log()
    args = parser.parse_args()
    if args.perf_thread > 1:
        threads = []
        # 创建并启动线程
        for i in range(args.perf_thread):
            t = multiprocessing.Process(target=vmpp_dec, args=(
                args.input,
                args.output,
                args.device,
                logger))
            
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        logger.info("All Threading exit")
    else:              
        vmpp_dec(args.input,
                args.output,
                args.device,
                logger)


if __name__ == "__main__":
    dec_perf()
