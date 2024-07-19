import argparse

from vmpp_api_dec import vmpp_dec
from vmpp_log_init import *


def decode():
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
        >>> python Decode.py -i path/file -o out.yuv -d /dev/va_video0
        Function to decode media file and write raw frames into an output file.
    """
    
    parser = argparse.ArgumentParser(
        description="This sample application illustrates decoding of a media file."
    )

    parser.add_argument("-i", "--input", help="Encoded video file (read from)", required=True)
    parser.add_argument("-o", "--output", help="Raw NV12 video file (write to)", required=True)
    parser.add_argument("-d", "--device", help="vastai device (/dev/va_video0)", required=True)

    logger = init_log()
    args = parser.parse_args()
    vmpp_dec(args.input,
             args.output,
             args.device,
             logger)


if __name__ == "__main__":
    decode()
