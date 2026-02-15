import os

# ====================== Global Timeout Configuration ======================
# Unified timeout for implicit wait (used in photos_page and conftest)
TIMEOUT = 30

# ====================== Test Data Configuration ======================
INPUT_TEXT = "Today is a sunny day!"
MAX_RETURN_TIMES = 5

# ====================== Appium Server Configuration ======================
APPIUM_REMOTE_URL = os.getenv("APPIUM_URL", "http://127.0.0.1:4723")

# ====================== Project Path Configuration ======================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = "API_Demo"
LOG_DIR = os.path.join(PROJECT_ROOT, f"{PROJECT_NAME}_logs")
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, f"{PROJECT_NAME}_screenshots")
REPORTS_DIR = os.path.join(PROJECT_ROOT, f"{PROJECT_NAME}_reports")

# ====================== Android Desired Capabilities ======================
DESIRED_CAPS = {
    "platformName": "Android",
    "deviceName": os.getenv("DEVICE_NAME", "Android Emulator"),
    "appPackage": "io.appium.android.apis",
    "appActivity": "io.appium.android.apis.ApiDemos",
    "automationName": "UiAutomator2",
    "noReset": False,
    "udid": os.getenv("DEVICE_UDID", ""),
    "newCommandTimeout": 30,
    "platformVersion": os.getenv("PLATFORM_VERSION", ""),
    "app": os.getenv("APP_PATH", os.path.join(PROJECT_ROOT, "apps/ApiDemos-debug.apk"))
}

# ====================== Element Locator Configuration ======================
HOME_ELEMENT = ("xpath", "//android.widget.TextView[@text='Accessibility']")

