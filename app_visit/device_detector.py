# app_visit/device_detector.py
import re
from typing import Optional


class DeviceDetector:
    """تشخیص نوع دستگاه، سیستم‌عامل، مرورگر و مدل دستگاه از User-Agent"""

    # الگوهای تشخیص سیستم‌عامل
    OS_PATTERNS = [
        ("windows", r"Windows NT"),
        ("android", r"Android"),
        ("ios", r"iPhone|iPad|iPod"),
        ("mac", r"Macintosh|Mac OS X"),
        ("linux", r"Linux"),
    ]

    # الگوهای تشخیص مرورگر (ترتیب مهم است)
    BROWSER_PATTERNS = [
        ("edge", r"Edg/|Edge/"),
        ("opera", r"OPR/|Opera"),
        ("chrome", r"Chrome/"),
        ("firefox", r"Firefox/"),
        ("safari", r"Safari/"),
        ("ie", r"MSIE|Trident"),
    ]

    # الگوهای تشخیص نوع دستگاه
    MOBILE_PATTERNS = r"Mobile|Android.*Mobile|iPhone|iPod|BlackBerry|IEMobile|Opera Mini"
    TABLET_PATTERNS = r"iPad|Android(?!.*Mobile)|Tablet|Kindle|Silk"

    # الگوهای تشخیص مدل دستگاه
    DEVICE_MODEL_PATTERNS = [
        # iPhone
        (r"iPhone(?:\s|;)(\d+(?:,\d+)?)", "iPhone {}"),
        # iPad
        (r"iPad(?:\s|;)(\d+(?:,\d+)?)?", "iPad {}"),
        # Samsung
        (r"SM-([A-Z0-9]+)", "Samsung SM-{}"),
        (r"SAMSUNG[- ]([A-Z0-9]+)", "Samsung {}"),
        # Huawei
        (r"(?:HUAWEI|Huawei)[- ]([A-Z0-9\-]+)", "Huawei {}"),
        # Xiaomi
        (r"(?:Redmi|Mi|POCO)[- ]([A-Z0-9]+)", "Xiaomi {}"),
        # Google Pixel
        (r"Pixel(?:\s|/)(\d+[A-Za-z]*)", "Google Pixel {}"),
        # OnePlus
        (r"ONEPLUS[- ]([A-Z0-9]+)", "OnePlus {}"),
        # LG
        (r"LG[- ]([A-Z0-9]+)", "LG {}"),
        # Sony
        (r"Sony[- ]([A-Z0-9]+)", "Sony {}"),
        # Nokia
        (r"Nokia[- ]([A-Z0-9]+)", "Nokia {}"),
    ]

    @classmethod
    def detect_os(cls, user_agent: str) -> str:
        if not user_agent:
            return "unknown"
        for os_name, pattern in cls.OS_PATTERNS:
            if re.search(pattern, user_agent, re.I):
                return os_name
        return "other"

    @classmethod
    def detect_browser(cls, user_agent: str) -> str:
        if not user_agent:
            return "unknown"
        for browser_name, pattern in cls.BROWSER_PATTERNS:
            if re.search(pattern, user_agent, re.I):
                return browser_name
        return "other"

    @classmethod
    def detect_device_type(cls, user_agent: str, is_bot: bool = False) -> str:
        if is_bot:
            return "bot"
        if not user_agent:
            return "unknown"
        if re.search(cls.TABLET_PATTERNS, user_agent, re.I):
            return "tablet"
        if re.search(cls.MOBILE_PATTERNS, user_agent, re.I):
            return "mobile"
        if re.search(r"Mozilla|Chrome|Safari|Firefox|Edge|Opera", user_agent, re.I):
            return "desktop"
        return "unknown"

    @classmethod
    def detect_device_model(cls, user_agent: str) -> str:
        if not user_agent:
            return ""
        for pattern, template in cls.DEVICE_MODEL_PATTERNS:
            match = re.search(pattern, user_agent, re.I)
            if match:
                groups = match.groups()
                if groups and groups[0]:
                    return template.format(groups[0])
                # برای iPad بدون شماره مدل
                return template.format("").strip()
        return ""

    @classmethod
    def detect_all(cls, user_agent: str, is_bot: bool = False) -> dict:
        """تشخیص کامل همه اطلاعات دستگاه"""
        return {
            "device_type": cls.detect_device_type(user_agent, is_bot),
            "os": cls.detect_os(user_agent),
            "browser": cls.detect_browser(user_agent),
            "device_model": cls.detect_device_model(user_agent),
        }