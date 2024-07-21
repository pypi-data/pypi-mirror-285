"""All constants"""

import platform

FONT: str = None
SIZE: int = None
SYSTEM: str = None

__all__ = [
    "FONT",
    "SIZE",
    "SYSTEM",
    "reset",
]


def reset() -> None:
    """Reset all constants to default value"""
    global FONT, SIZE, SYSTEM
    SIZE = -20
    if (SYSTEM := platform.system()) == "Windows":
        # SYSTEM = f"Windows{platform.win32_ver()[0]}"  # Will get incorrect version info under Python 3.10
        if int(platform.win32_ver()[1].split(".")[-1]) >= 22000:
            SYSTEM = "Windows11"
        else:
            SYSTEM = "Windows10"
    FONT = "Microsoft YaHei" if SYSTEM.startswith(
        "Windows") else "PingFang SC" if SYSTEM == "Darwin" else "Noto Sans"


reset()
