import platform

from ctypes import *
from vmpp_log_init import *

 
def get_server_architecture():
    architecture = platform.machine()
    system = platform.system()
    
    return system, architecture
 

def get_platform(vmpp): 
    logger = init_log()

    sys, arch = get_server_architecture()
    ### decodec lib path
    if vmpp == "dec":
        if sys == "Linux" and arch == "aarch64":
            logger.info(f"system:{sys}, architecture:{arch}")
            lib = cdll.LoadLibrary(r'../../arm64/libvideo_dec_so.so')
            
        elif sys == "Linux" and arch == "x86_64":
            logger.info(f"system:{sys}, architecture:{arch}")
            lib = cdll.LoadLibrary(r'../../x86/libvideo_dec_so.so')
                
        else:
            logger.error(f"system:{sys}, architecture:{arch} is not support!")
            return 
    ### encodec lib path  
    elif vmpp == "enc":
        if sys == "Linux" and arch == "aarch64":
            logger.info(f"system:{sys}, architecture:{arch}")
            lib = cdll.LoadLibrary(r'../../arm64/libvideo_enc_so.so')
            
        elif sys == "Linux" and arch == "x86_64":
            logger.info(f"system:{sys}, architecture:{arch}")
            lib = cdll.LoadLibrary(r'../../x86/libvideo_enc_so.so')
        
        ### windows AMD64系统时，使用windowsv版本so
        elif sys == "Windows" and arch == "AMD64":
            logger.info(f"system:{sys}, architecture:{arch}")
            lib = cdll.LoadLibrary(r'../../windows_dll/video_enc_so.dll')
           
        else:
            logger.error(f"system:{sys}, architecture:{arch} is not support!")
            return 
    ### transcodec lib path  
    elif vmpp == "transc":
        if sys == "Linux" and arch == "aarch64":
            logger.info(f"system:{sys}, architecture:{arch}")
            lib = cdll.LoadLibrary(r'../../arm64/libtranscode_so.so')
            
        elif sys == "Linux" and arch == "x86_64":
            logger.info(f"system:{sys}, architecture:{arch}")
            lib = cdll.LoadLibrary(r'../../x86/libtranscode_so.so')
            
        else:
            logger.error(f"system:{sys}, architecture:{arch} is not support!")
            return 
    else:
        logger.error(f"{vmpp} is not support!")
        return


    return lib
