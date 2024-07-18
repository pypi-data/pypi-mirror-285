import platform
from types import ModuleType

def check_os() -> ModuleType:
    if platform.system() == 'Darwin':
        from ..OS_control import macos_system_control as OS
        return OS
    elif platform.system() == 'win32' or platform.system() == 'Windows':
        from ..OS_control import window_system_control as OS
        return OS