from win32.lib import win32con
import win32api, win32gui, win32print
import ctypes
from ctypes import wintypes

def get_real_resolution():
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    wide = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    high = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return {"wide": wide, "high": high}

def get_screen_size():
    """获取缩放后的分辨率"""
    wide = win32api.GetSystemMetrics(0)
    high = win32api.GetSystemMetrics(1)
    return {"wide": wide, "high": high}


def get_scaling():
    """获取屏幕的缩放比例"""
    real_resolution = get_real_resolution()
    screen_size = get_screen_size()
    proportion = round(real_resolution["wide"] / screen_size["wide"], 2)
    return proportion

def get_desktop_path():
    """获取桌面路径"""
    CSIDL_DESKTOP = 0
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf
    )
    return buf.value
if __name__ == "__main__":
    scaling = get_scaling()
    print("scaling: ", scaling)


