import os
import platform

def restart():
    """
    Restarts the computer based on the detected operating system.
    """
    current_os = platform.system()
    
    if current_os == "Windows":
        os.system("shutdown /r /t 0")
    elif current_os == "Linux" or current_os == "Darwin":
        os.system("sudo reboot")
    else:
        raise NotImplementedError(f"Restart functionality is not implemented for {current_os}")
